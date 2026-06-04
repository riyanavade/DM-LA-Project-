import mysql.connector
import pandas as pd
import os
import warnings
import json
import sqlite3

# Suppress pandas warning for using raw MySQL connection instead of SQLAlchemy
warnings.filterwarnings('ignore', category=UserWarning)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "db_config.json")

class SQLiteCursorWrapper:
    def __init__(self, sqlite_cursor):
        self.cursor = sqlite_cursor

    def execute(self, query, params=None):
        query_translated = query.replace("%s", "?")
        
        # Adjust database creation or use
        query_upper = query_translated.strip().upper()
        if query_upper.startswith("CREATE DATABASE") or query_upper.startswith("USE"):
            return None
            
        # Adjust AUTO_INCREMENT
        query_translated = query_translated.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        query_translated = query_translated.replace("INT AUTOINCREMENT", "INTEGER AUTOINCREMENT")
        query_translated = query_translated.replace("INT AUTO_INCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        query_translated = query_translated.replace("INTEGER AUTOINCREMENT PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        
        if params is not None:
            return self.cursor.execute(query_translated, params)
        else:
            return self.cursor.execute(query_translated)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    @property
    def description(self):
        return self.cursor.description


class SQLiteConnectionWrapper:
    def __init__(self, sqlite_conn):
        self.conn = sqlite_conn

    def cursor(self):
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()
        
    def get_server_info(self):
        return f"SQLite {sqlite3.sqlite_version}"


def load_db_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Default fallback
    return {
        "db_type": "MySQL",
        "host": "localhost",
        "user": "root",
        "password": "rakshita_b@2004",
        "database": "ipl_auction_db"
    }

def save_db_config(host, user, password, database, db_type="MySQL"):
    config = {
        "db_type": db_type,
        "host": host,
        "user": user,
        "password": password,
        "database": database
    }
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def test_connection():
    """Test database connection and return status, message."""
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    if db_type == "SQLite":
        try:
            db_file = os.path.join(os.path.dirname(__file__), f"{config['database']}.sqlite")
            conn = sqlite3.connect(db_file)
            conn.close()
            return True, f"Connected to SQLite! (v{sqlite3.sqlite_version})"
        except Exception as e:
            return False, str(e)
    else:
        try:
            conn = mysql.connector.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"]
            )
            server_info = conn.get_server_info()
            conn.close()
            return True, f"Connected to MySQL! (v{server_info})"
        except Exception as e:
            return False, str(e)

def get_connection():
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    if db_type == "SQLite":
        try:
            db_file = os.path.join(os.path.dirname(__file__), f"{config['database']}.sqlite")
            conn = sqlite3.connect(db_file)
            return SQLiteConnectionWrapper(conn)
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return None
    else:
        try:
            conn = mysql.connector.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"]
            )
            return conn
        except Exception as e:
            print(f"Error connecting to MySQL Server: {e}")
            return None

def get_db_connection():
    """Get a connection directly to the IPL database."""
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    if db_type == "SQLite":
        try:
            db_file = os.path.join(os.path.dirname(__file__), f"{config['database']}.sqlite")
            conn = sqlite3.connect(db_file)
            return SQLiteConnectionWrapper(conn)
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return None
    else:
        try:
            conn = mysql.connector.connect(
                host=config["host"],
                user=config["user"],
                password=config["password"],
                database=config["database"]
            )
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

def init_db():
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    db_name = config["database"]
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    # Create DB
    if db_type != "SQLite":
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
    
    # Table 1: players (expanded with role, nationality, age)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name VARCHAR(100) UNIQUE,
            team VARCHAR(50),
            role VARCHAR(50) DEFAULT 'Unknown',
            nationality VARCHAR(50) DEFAULT 'India',
            age INT DEFAULT 25,
            photo_url VARCHAR(512) DEFAULT NULL
        )
    """)
    
    # Table 2: performance (expanded with batting_avg)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance (
            perf_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INT,
            matches INT,
            runs INT,
            wickets INT,
            strike_rate FLOAT,
            economy FLOAT,
            batting_avg FLOAT DEFAULT 0.0,
            year INT,
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)
    
    # Table 3: auction (expanded with base_price)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auction (
            auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INT,
            auction_price FLOAT,
            base_price FLOAT DEFAULT 2.0,
            sold_status BOOLEAN,
            year INT,
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    # Run migrations to ensure all new columns exist
    migrate_db()
    
    return True

def migrate_db():
    """Safely add new columns to existing tables using ALTER TABLE.
    Only adds columns that don't already exist."""
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    db_name = config["database"]
    conn = get_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    if db_type != "SQLite":
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
    
    # Helper: check if column exists
    def column_exists(table, column):
        if db_type == "SQLite":
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [row[1] for row in cursor.fetchall()]
            return column in cols
        else:
            cursor.execute(f"""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{db_name}' 
                AND TABLE_NAME = '{table}' 
                AND COLUMN_NAME = '{column}'
            """)
            return cursor.fetchone()[0] > 0
    
    # Migrate players table
    migrations = [
        ("players", "role", "VARCHAR(50) DEFAULT 'Unknown'"),
        ("players", "nationality", "VARCHAR(50) DEFAULT 'India'"),
        ("players", "age", "INT DEFAULT 25"),
        ("players", "photo_url", "VARCHAR(512) DEFAULT NULL"),
        ("performance", "batting_avg", "FLOAT DEFAULT 0.0"),
        ("auction", "base_price", "FLOAT DEFAULT 2.0"),
    ]
    
    for table, col, col_def in migrations:
        if not column_exists(table, col):
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
                print(f"  Added column '{col}' to '{table}'")
            except Exception as e:
                print(f"  Could not add '{col}' to '{table}': {e}")
        else:
            print(f"  Column '{col}' already exists in '{table}'")
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def upload_data_to_db(df):
    """
    Upload DataFrame to MySQL/SQLite. Handles flexible column naming via mapping.
    Now supports: Role, Nationality, Age, Batting_Avg, Base_Price_CR
    """
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("Could not connect to the database. Please verify settings.")
    cursor = conn.cursor()
    
    # Column mapping for flexibility
    col_map = {
        'Player_Name': ['Player_Name', 'Player', 'player', 'player_name'],
        'Team': ['Team', 'team', 'Franchise'],
        'Year': ['Year', 'year', 'Season'],
        'Matches': ['Matches', 'matches', 'Played'],
        'Runs': ['Runs', 'runs', 'Batting_Runs'],
        'Wickets': ['Wickets', 'wickets', 'Bowling_Wickets'],
        'Strike_Rate': ['Strike_Rate', 'strike_rate', 'SR'],
        'Economy': ['Economy', 'economy', 'Bowling_Economy', 'Econ'],
        'Sold_Status': ['Sold_Status', 'sold_status', 'Status'],
        'Auction_Price': ['Auction_Price', 'auction_price', 'Sold_Price_CR', 'Price'],
        'Role': ['Role', 'role', 'Player_Role'],
        'Nationality': ['Nationality', 'nationality', 'Country'],
        'Age': ['Age', 'age'],
        'Batting_Avg': ['Batting_Avg', 'batting_avg', 'Batting_Average', 'Avg'],
        'Base_Price': ['Base_Price', 'base_price', 'Base_Price_CR', 'Base_Price_Cr'],
        'Photo_URL': ['Photo_URL', 'photo_url', 'Photo', 'photo'],
    }

    def get_val(row, target_col, default=0):
        for alt in col_map.get(target_col, [target_col]):
            if alt in row.index:
                val = row[alt]
                if pd.isna(val):
                    continue
                if target_col == 'Sold_Status' and not isinstance(val, bool):
                    if isinstance(val, (int, float)):
                        return val > 0
                    if isinstance(val, str):
                        return val.lower() in ['sold', 'true', '1', 'yes', 'retained', 'trade']
                return val
        
        # Special logic for Sold_Status if missing but Price exists
        if target_col == 'Sold_Status':
            price = get_val(row, 'Auction_Price', -1)
            if price != -1 and not pd.isna(price):
                return price > 0
        
        # Default Year if missing
        if target_col == 'Year' and default == 0:
            return 2025
            
        return default

    for index, row in df.iterrows():
        name = get_val(row, 'Player_Name', 'Unknown')
        team = get_val(row, 'Team', 'TBD')
        year = get_val(row, 'Year', 2025)
        matches = get_val(row, 'Matches', 0)
        runs = get_val(row, 'Runs', 0)
        wickets = get_val(row, 'Wickets', 0)
        sr = get_val(row, 'Strike_Rate', 0.0)
        econ = get_val(row, 'Economy', 0.0)
        sold = get_val(row, 'Sold_Status', False)
        price = get_val(row, 'Auction_Price', 0.0)
        role = get_val(row, 'Role', 'Unknown')
        nationality = get_val(row, 'Nationality', 'India')
        age = get_val(row, 'Age', 25)
        batting_avg = get_val(row, 'Batting_Avg', 0.0)
        base_price = get_val(row, 'Base_Price', 2.0)
        photo_url = get_val(row, 'Photo_URL', None)

        # Insert or update player
        cursor.execute("SELECT player_id FROM players WHERE player_name = %s", (name,))
        result = cursor.fetchone()
        
        if result:
            player_id = result[0]
            # Update player info with latest data
            cursor.execute("""
                UPDATE players SET team=%s, role=%s, nationality=%s, age=%s, photo_url=%s
                WHERE player_id=%s
            """, (team, role, nationality, int(age), photo_url, player_id))
        else:
            cursor.execute("""
                INSERT INTO players (player_name, team, role, nationality, age, photo_url) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, team, role, nationality, int(age), photo_url))
            player_id = cursor.lastrowid
            
        # Insert performance (with batting_avg)
        cursor.execute("SELECT perf_id FROM performance WHERE player_id = %s AND year = %s", (player_id, int(year)))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO performance (player_id, matches, runs, wickets, strike_rate, economy, batting_avg, year)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (player_id, int(matches), int(runs), int(wickets), float(sr), float(econ), float(batting_avg), int(year)))
            
        # Insert auction (with base_price)
        cursor.execute("SELECT auction_id FROM auction WHERE player_id = %s AND year = %s", (player_id, int(year)))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO auction (player_id, auction_price, base_price, sold_status, year)
                VALUES (%s, %s, %s, %s, %s)
            """, (player_id, float(price), float(base_price), bool(sold), int(year)))
            
    conn.commit()
    cursor.close()
    conn.close()

def clear_all_data():
    config = load_db_config()
    db_type = config.get("db_type", "MySQL")
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    if db_type != "SQLite":
        cursor.execute(f"USE {config['database']}")
    # Delete in reverse order of foreign keys
    cursor.execute("DELETE FROM auction")
    cursor.execute("DELETE FROM performance")
    cursor.execute("DELETE FROM players")
    conn.commit()
    cursor.close()
    conn.close()

def get_all_data():
    """Fetch all data with expanded columns via JOIN."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    query = """
        SELECT p.player_name, p.team, p.role, p.nationality, p.age, p.photo_url,
               perf.matches, perf.runs, perf.wickets, 
               perf.strike_rate, perf.economy, perf.batting_avg, perf.year, 
               a.auction_price, a.base_price, a.sold_status
        FROM players p
        JOIN performance perf ON p.player_id = perf.player_id
        JOIN auction a ON p.player_id = a.player_id AND perf.year = a.year
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_player_list():
    """Get list of all unique players."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    query = "SELECT player_name, role, nationality, age FROM players ORDER BY player_name"
    df = pd.read_sql(query, conn)
    conn.close()
    return df
