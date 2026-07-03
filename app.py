import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_option_menu import option_menu
import database as db
import ml_models as ml
import ml_engine as mle
import visualizations as viz
import os
import time

# ----------------- PLAYER PHOTO LOOKUP -----------------
PLAYER_PHOTOS = {
    # Batsmen / All-rounders
    "Virat Kohli":      "https://upload.wikimedia.org/wikipedia/commons/9/9b/Virat_Kohli_in_PMO_New_Delhi.jpg",
    "Rohit Sharma":     "https://upload.wikimedia.org/wikipedia/commons/1/1e/Prime_Minister_Of_Bharat_Shri_Narendra_Damodardas_Modi_with_Shri_Rohit_Gurunath_Sharma_%28Cropped%29.jpg",
    "KL Rahul":         "https://upload.wikimedia.org/wikipedia/commons/6/69/KL_Rahul_at_Femina_Miss_India_2018_Grand_Finale_%28cropped%29.jpg",
    "Rishabh Pant":     "https://upload.wikimedia.org/wikipedia/commons/7/77/Rishabh_Pant.jpg",
    "Ishan Kishan":     "https://upload.wikimedia.org/wikipedia/commons/d/d7/Ishan_Kishan.jpg",
    "Hardik Pandya":    "https://upload.wikimedia.org/wikipedia/commons/f/fc/Hardik_Pandya_in_PMO_New_Delhi.jpg",
    "Shubman Gill":     "https://upload.wikimedia.org/wikipedia/commons/d/d1/Shubman_Gill.jpg",
    "Sanju Samson":     "https://upload.wikimedia.org/wikipedia/commons/7/70/Sanju_Samson_in_PMO_New_Delhi.jpg",
    "Suryakumar Yadav": "https://upload.wikimedia.org/wikipedia/commons/b/b7/Suryakumar_Yadav_in_PMO_New_Delhi.jpg",
    "Shreyas Iyer":     "https://upload.wikimedia.org/wikipedia/commons/a/ae/Shreyas_Iyer_snapped_at_the_airport_%28Cropped%29.jpg",
    "Devdutt Padikkal": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Devdutt_Padikkal_%28cropped%29.jpg/440px-Devdutt_Padikkal_%28cropped%29.jpg",
    "Axar Patel":       "https://upload.wikimedia.org/wikipedia/commons/a/ad/Axar_Patel_in_PMO_New_Delhi.jpg",
    "Ravindra Jadeja":  "https://upload.wikimedia.org/wikipedia/commons/2/2c/PM_Shri_Narendra_Modi_with_Ravindra_Jadeja_%28Cropped%29.jpg",
    "MS Dhoni":         "https://upload.wikimedia.org/wikipedia/commons/d/d5/MS_Dhoni_%28Prabhav_%2723_-_RiGI_2023%29.jpg",
    "David Warner":     "https://upload.wikimedia.org/wikipedia/commons/2/2c/DAVID_WARNER_%2811704782453%29.jpg",
    "Jos Buttler":      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Jos_Buttler_in_2023.jpg/960px-Jos_Buttler_in_2023.jpg",
    "Faf du Plessis":   "https://upload.wikimedia.org/wikipedia/commons/8/87/Faf_du_Plessis_2019_Boxing_Day.jpg",
    "Glenn Maxwell":    "https://upload.wikimedia.org/wikipedia/commons/d/d4/Glenn_Maxwell_of_Australia.jpg",
    "AB de Villiers":   "https://upload.wikimedia.org/wikipedia/commons/5/5d/AB_de_Villiers_2016.jpg",
    "Chris Gayle":      "https://upload.wikimedia.org/wikipedia/commons/5/5a/Chris_Gayle_2012.jpg",
    "Quinton de Kock":  "https://upload.wikimedia.org/wikipedia/commons/3/3c/Quinton_de_Kock_in_2018.jpg",
    # Bowlers
    "Jasprit Bumrah":   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Jasprit_Bumrah.jpg/440px-Jasprit_Bumrah.jpg",
    "Mohammed Shami":   "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Mohammed_Shami_%28cropped%29.jpg/440px-Mohammed_Shami_%28cropped%29.jpg",
    "Yuzvendra Chahal": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Yuzvendra_Chahal_in_2021.jpg/440px-Yuzvendra_Chahal_in_2021.jpg",
    "Trent Boult":      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Trent_Boult_2015.jpg/440px-Trent_Boult_2015.jpg",
    "Pat Cummins":      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Pat_Cummins_fielding_Ashes_2021_%28cropped%29.jpg/960px-Pat_Cummins_fielding_Ashes_2021_%28cropped%29.jpg",
    "Kagiso Rabada":    "https://upload.wikimedia.org/wikipedia/commons/b/b5/Kingdom_Kome_co-founders_Kagiso_Rabada_and_Cameron_Scott_at_the_first_private_screening_of_The_Ring_of_Beasts_%28cropped%29.jpg",
    "Mitchell Starc":   "https://upload.wikimedia.org/wikipedia/commons/3/38/Mitchell_Starc_2023.jpg",
    "Rashid Khan":      "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Rashid_Khan.jpg/1280px-Rashid_Khan.jpg",
    "Bhuvneshwar Kumar":"https://upload.wikimedia.org/wikipedia/commons/4/4f/Bhuvneshwar_Kumar_%28cropped%29.jpg",
    "Kuldeep Yadav":    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Kuldeep_Yadav_in_2021.jpg/440px-Kuldeep_Yadav_in_2021.jpg",
    "Shardul Thakur":   "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Shardul_Thakur_in_2019.jpg/440px-Shardul_Thakur_in_2019.jpg",
    "Arshdeep Singh":   "https://upload.wikimedia.org/wikipedia/commons/3/36/Prime_Minister_Of_Bharat_Shri_Narendra_Damodardas_Modi_with_Arshdeep_Singh_Family_%28Cropped%29.jpg",
    "Harshal Patel":    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Harshal_Patel_2019.jpg/440px-Harshal_Patel_2019.jpg",
    "Heinrich Klaasen": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Heinrich_Klaasen.jpg/440px-Heinrich_Klaasen.jpg",
    "Liam Livingstone": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Liam_Livingstone_%28cropped%29.jpg/440px-Liam_Livingstone_%28cropped%29.jpg",
    "Nicholas Pooran":  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Nicholas_Pooran_2020.jpg/440px-Nicholas_Pooran_2020.jpg",
    "Ruturaj Gaikwad":  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Ruturaj_Gaikwad.jpg/440px-Ruturaj_Gaikwad.jpg",
    "Travis Head":      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Travis_Head_2016.jpg/440px-Travis_Head_2016.jpg",
    "Washington Sundar":"https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Washington_Sundar_%28cropped%29.jpg/440px-Washington_Sundar_%28cropped%29.jpg",
    "Yashasvi Jaiswal": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Yashasvi_Jaiswal_2023.jpg/440px-Yashasvi_Jaiswal_2023.jpg",
}

TEAM_JERSEY_URLS = {
    "Mumbai Indians": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1b/Mumbai_Indians_Logo.svg/1200px-Mumbai_Indians_Logo.svg.png",
    "Chennai Super Kings": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/Chennai_Super_Kings_Logo.svg/1200px-Chennai_Super_Kings_Logo.svg.png",
    "Royal Challengers Bangalore": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/Royal_Challengers_Bangalore_Logo.svg/1200px-Royal_Challengers_Bangalore_Logo.svg.png",
    "Kolkata Knight Riders": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2d/Kolkata_Knight_Riders_Logo.svg/1200px-Kolkata_Knight_Riders_Logo.svg.png",
    "Sunrisers Hyderabad": "https://upload.wikimedia.org/wikipedia/en/thumb/3/38/Sunrisers_Hyderabad_Logo.svg/1200px-Sunrisers_Hyderabad_Logo.svg.png",
    "Rajasthan Royals": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9b/Rajasthan_Royals_Logo.svg/1200px-Rajasthan_Royals_Logo.svg.png",
    "Delhi Capitals": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0f/Delhi_Capitals_logo.svg/1200px-Delhi_Capitals_logo.svg.png",
    "Punjab Kings": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Punjab_Kings_logo.svg/1200px-Punjab_Kings_logo.svg.png",
    "Lucknow Super Giants": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/Lucknow_Super_Giants_logo.svg/1200px-Lucknow_Super_Giants_logo.svg.png",
    "Gujarat Titans": "https://upload.wikimedia.org/wikipedia/en/thumb/4/49/Gujarat_Titans_Logo.svg/1200px-Gujarat_Titans_Logo.svg.png",
}

TEAM_NAME_ALIASES = {
    "mi": "Mumbai Indians",
    "mumbaiindians": "Mumbai Indians",
    "mumbai_indian": "Mumbai Indians",
    "csk": "Chennai Super Kings",
    "chennaisuperkings": "Chennai Super Kings",
    "rcb": "Royal Challengers Bangalore",
    "royalchallengersbangalore": "Royal Challengers Bangalore",
    "kkr": "Kolkata Knight Riders",
    "kolkataknightriders": "Kolkata Knight Riders",
    "srh": "Sunrisers Hyderabad",
    "sunrisershyderabad": "Sunrisers Hyderabad",
    "rr": "Rajasthan Royals",
    "rajasthanroyals": "Rajasthan Royals",
    "dc": "Delhi Capitals",
    "delhicapitals": "Delhi Capitals",
    "pbks": "Punjab Kings",
    "punjabkings": "Punjab Kings",
    "lsg": "Lucknow Super Giants",
    "lucknowsupergiants": "Lucknow Super Giants",
    "gt": "Gujarat Titans",
    "gujarattitans": "Gujarat Titans",
}

TEAM_ABBREVIATIONS = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Sunrisers Hyderabad": "SRH",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
    "Gujarat Titans": "GT",
}

def get_team_abbr(team_name: str | None) -> str | None:
    """Return the IPL abbreviation for a normalized team name."""
    normalized_name = normalize_team_name(team_name)
    if not normalized_name:
        return None
    return TEAM_ABBREVIATIONS.get(normalized_name)

DEFAULT_PLAYER_IMG = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

def get_local_player_photo(player_name: str) -> str | None:
    """Return a local player photo path if one exists in the images folder."""
    safe_name = ''.join(ch for ch in player_name.lower() if ch.isalnum() or ch in (' ', '_', '-')).replace(' ', '_')
    image_folder = os.path.join(os.path.dirname(__file__), 'images')
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        local_path = os.path.join(image_folder, f"{safe_name}.{ext}")
        if os.path.exists(local_path):
            return local_path
    return None


def normalize_team_name(team_name: str | None) -> str | None:
    """Normalize common IPL team names and abbreviations to a canonical team name."""
    if not team_name:
        return None
    normalized = ''.join(ch for ch in team_name.strip().lower() if ch.isalnum())
    if normalized in TEAM_NAME_ALIASES:
        return TEAM_NAME_ALIASES[normalized]
    for key in TEAM_JERSEY_URLS:
        if ''.join(ch for ch in key.lower() if ch.isalnum()) == normalized:
            return key
    return team_name.strip()


def get_local_team_jersey(team_name: str) -> str | None:
    """Return a local team jersey image path if one exists in the images folder."""
    normalized_name = normalize_team_name(team_name)
    if not normalized_name:
        return None
    safe_team = ''.join(ch for ch in normalized_name.lower() if ch.isalnum() or ch in (' ', '_', '-')).replace(' ', '_')
    image_folder = os.path.join(os.path.dirname(__file__), 'images')
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        local_path = os.path.join(image_folder, f"jersey_{safe_team}.{ext}")
        if os.path.exists(local_path):
            return local_path
    return None


def get_remote_team_jersey(team_name: str) -> str | None:
    """Return a remote team jersey/logo image URL for the given IPL team."""
    normalized_name = normalize_team_name(team_name)
    if not normalized_name:
        return None
    for key, url in TEAM_JERSEY_URLS.items():
        if key == normalized_name:
            return url
    return None


def get_player_photo(player_name: str, team_name: str | None = None) -> str:
    """Return a player portrait first, then team jersey/logo, then a default icon."""
    local_photo = get_local_player_photo(player_name)
    if local_photo:
        return local_photo

    # Exact match first
    if player_name in PLAYER_PHOTOS:
        return PLAYER_PHOTOS[player_name]

    # Fuzzy: check if any key is a substring of the name or vice-versa
    name_lower = player_name.lower()
    for key, url in PLAYER_PHOTOS.items():
        if key.lower() in name_lower or name_lower in key.lower():
            return url

    if team_name:
        local_team_jersey = get_local_team_jersey(team_name)
        if local_team_jersey:
            return local_team_jersey

        remote_team_jersey = get_remote_team_jersey(team_name)
        if remote_team_jersey:
            return remote_team_jersey

    return DEFAULT_PLAYER_IMG

# Setup page Config
st.set_page_config(page_title="IPL Auction Intelligence", layout="wide", page_icon="🏏", initial_sidebar_state="expanded")

# ----------------- THEME CONFIGURATION -----------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8615/8615344.png", width=60) # Small decorative icon
    st.markdown("<br>", unsafe_allow_html=True)
    is_light_mode = st.toggle("☀️ Enable Light Mode", value=False)

# CSS Variable Definitions
if is_light_mode:
    theme_css = """
    :root {
        --bg-main: #f8fafc;
        --bg-card: #ffffff;
        --bg-glass: rgba(255, 255, 255, 0.85);
        --bg-sidebar: rgba(241, 245, 249, 0.95);
        --text-primary: #0f172a;
        --text-muted: #475569;
        --accent-primary: #4f46e5;
        --accent-secondary: #3b82f6;
        --border-glass: rgba(0, 0, 0, 0.1);
        --shadow-soft: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        --glow-color: rgba(79, 70, 229, 0.4);
        --st-dropdown-bg: #ffffff;
    }
    """
else:
    theme_css = """
    :root {
        --bg-main: #0f172a;
        --bg-card: #1e293b;
        --bg-glass: rgba(30, 41, 59, 0.7);
        --bg-sidebar: rgba(11, 17, 32, 0.95);
        --text-primary: #f8fafc;
        --text-muted: #94a3b8;
        --accent-primary: #6366f1;
        --accent-secondary: #818cf8;
        --border-glass: rgba(255, 255, 255, 0.1);
        --shadow-soft: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        --glow-color: rgba(99, 102, 241, 0.5);
        --st-dropdown-bg: #1e293b;
    }
    """

# ----------------- OVERRIDE STREAMLIT DEFAULTS & CUSTOM CSS -----------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

{theme_css}

/* Animations */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

/* Hide Streamlit Branding but keep header toggle */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{background: transparent !important;}}

/* Main Background and Text */
.stApp {{
    background-color: var(--bg-main) !important;
    background-image: radial-gradient(circle at 50% 0%, var(--glow-color) 0%, transparent 40%);
    color: var(--text-primary) !important;
    font-family: 'Poppins', sans-serif !important;
    transition: background-color 0.4s ease, color 0.4s ease;
}}

/* Typography */
h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, p, span {{
    font-family: 'Poppins', sans-serif !important;
    color: var(--text-primary) !important;
}}

/* Header & Subtitle */
.main-header {{
    font-size: 3rem !important;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #38bdf8, var(--accent-primary), #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-top: 1rem;
    margin-bottom: 0px !important;
    animation: fadeIn 0.8s ease-out;
}}

.subtitle {{
    text-align: center;
    color: var(--text-muted) !important;
    font-size: 1.1rem;
    margin-top: 5px;
    margin-bottom: 40px;
    font-weight: 400;
    letter-spacing: 0.5px;
    animation: fadeIn 1s ease-out;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: var(--bg-sidebar) !important;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);

    transition: all 0.4s ease;
}}
[data-testid="stSidebar"] .stMarkdown p {{
    color: var(--text-primary) !important;
}}

/* Glassmorphism Metric Cards */
.metric-container {{
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 30px;
    animation: fadeIn 0.6s ease-out;
}}

.custom-metric {{
    background: var(--bg-glass);
    backdrop-filter: blur(12px);
    border: 1px solid var(--border-glass);
    border-top: 4px solid var(--accent-primary);
    border-radius: 16px;
    padding: 24px;
    flex: 1;
    text-align: left;
    box-shadow: var(--shadow-soft);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-top 0.3s ease;
}}

.custom-metric:hover {{
    transform: translateY(-5px);
    box-shadow: 0 0 20px var(--glow-color);
    border-top: 4px solid #f59e0b;
}}

.metric-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}}

.metric-icon {{
    font-size: 1.5rem;
    color: var(--accent-primary);
}}

.metric-title {{
    font-size: 0.95rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}}

.metric-value {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1.2;
}}

/* Prediction Cards */
.pred-card {{
    background: var(--bg-card);
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    box-shadow: var(--shadow-soft);
    border: 1px solid var(--border-glass);
    transition: transform 0.3s ease;
    height: 100%;
}}
.pred-card:hover {{
    transform: translateY(-4px);
}}
.pred-card h4 {{
    color: var(--text-muted) !important;
    font-size: 0.95rem;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.pred-card .value {{
    font-size: 2rem;
    font-weight: 800;
    margin: 10px 0;
}}

/* Profile Card */
.profile-card {{
    background: var(--bg-glass);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    border: 1px solid var(--border-glass);
    box-shadow: var(--shadow-soft);
}}
.profile-img {{
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 15px;
    border: 4px solid var(--accent-primary);
    padding: 4px;
    box-shadow: 0 0 15px var(--glow-color);
}}
.profile-name {{
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 5px;
    color: var(--text-primary);
}}
.profile-role {{
    color: var(--accent-secondary);
    font-weight: 600;
    font-size: 1.1rem;
}}

/* Custom Streamlit Components */
.stButton>button {{
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
    color: white !important;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
    transition: all 0.3s ease;
}}
.stButton>button:hover {{
    box-shadow: 0 0 20px var(--glow-color);
    transform: translateY(-2px);
    color: white !important;
}}

div[data-testid="stSelectbox"] > div > div {{
    background-color: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border-radius: 10px;
    border: 1px solid var(--border-glass);
}}
div[data-testid="stSelectbox"] label p {{
    color: var(--text-muted) !important;
    font-weight: 500;
}}
ul[data-testid="stVirtualDropdown"] {{
    background-color: var(--st-dropdown-bg) !important;
    color: var(--text-primary) !important;
}}
li[role="option"] span {{
    color: var(--text-primary) !important;
}}

div[data-testid="stDataFrame"] {{
    background: var(--bg-card);
    border-radius: 12px;
    padding: 10px;
    border: 1px solid var(--border-glass);
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 24px;
}}
.stTabs [data-baseweb="tab"] {{
    height: 50px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 4px 4px 0px 0px;
    gap: 1px;
    padding-top: 10px;
    padding-bottom: 10px;
}}
.stTabs [aria-selected="true"] {{
    background-color: transparent;
    color: var(--accent-primary) !important;
    border-bottom: 3px solid var(--accent-primary);
}}

/* Uploader */
[data-testid="stFileUploader"] {{
    background: var(--bg-glass);
    border: 2px dashed var(--accent-primary);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}}
[data-testid="stFileUploader"]:hover {{
    border-color: #f59e0b;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}}
[data-testid="stFileUploader"] section {{
    background: transparent !important;
}}
[data-testid="stFileUploader"] span, [data-testid="stFileUploader"] p {{
    color: var(--text-primary) !important;
}}
</style>
""", unsafe_allow_html=True)


# ----------------- HEADER -----------------
st.markdown("<h1 class='main-header'>IPL Auction Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-Driven Player Valuations & Advanced Auction Analytics</div>", unsafe_allow_html=True)


# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    
    selected_page = option_menu(
        menu_title=None,
        options=["Dashboard", "Player Analysis", "Next Year Predictions", "Upload Data"],
        icons=["grid-fill", "person-bounding-box", "robot", "cloud-upload-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#f59e0b", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "font-family": "Poppins", "text-align": "left", "margin":"5px 0px", "color": "#f8fafc" if not is_light_mode else "#0f172a", "--hover-color": "rgba(99, 102, 241, 0.2)"},
            "nav-link-selected": {"background": "linear-gradient(90deg, #4f46e5 0%, #3b82f6 100%)", "font-weight": "600", "color": "white", "box-shadow": "0 4px 10px rgba(79, 70, 229, 0.3)"},
        }
    )
    
    # Dynamic DB Status
    db_connected, conn_msg = db.test_connection()
    db_status_text = "🟢 Connected" if db_connected else "🔴 Disconnected"
    
    current_config = db.load_db_config()
    db_type_label = current_config.get("db_type", "MySQL")
    
    st.markdown(f"<div style='font-size: 0.85rem; color: var(--text-muted); padding:10px; font-weight:500;'>System Status: 🟢 Online<br>DB Status: {db_status_text} ({db_type_label})</div>", unsafe_allow_html=True)
    
    if not db_connected:
        st.markdown(f"<div style='font-size: 0.8rem; color: #ef4444; padding:0 10px 10px; font-weight:500;'>⚠️ {db_type_label} disconnected. Set credentials below.</div>", unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color: var(--border-glass);'>", unsafe_allow_html=True)
    
    # Collapsible Database Settings Expander
    with st.expander("⚙️ Database Settings", expanded=not db_connected):
        db_types = ["MySQL", "SQLite"]
        selected_db_type = st.selectbox(
            "Database Type", 
            db_types, 
            index=db_types.index(current_config.get("db_type", "MySQL")) if current_config.get("db_type", "MySQL") in db_types else 0,
            key="db_type_input"
        )
        
        if selected_db_type == "MySQL":
            host_input = st.text_input("MySQL Host", value=current_config.get("host", "localhost"), key="db_host_input")
            user_input = st.text_input("Username", value=current_config.get("user", "root"), key="db_user_input")
            pass_input = st.text_input("Password", value=current_config.get("password", ""), type="password", key="db_pass_input")
            db_input = st.text_input("Database Name", value=current_config.get("database", "ipl_auction_db"), key="db_name_input")
        else:
            host_input = "localhost"
            user_input = "root"
            pass_input = ""
            db_input = st.text_input("SQLite Database Name", value=current_config.get("database", "ipl_auction_db"), key="db_name_input")
        
        if st.button("Save & Connect 💾", use_container_width=True, key="db_save_button"):
            # Save the new configuration
            db.save_db_config(host_input, user_input, pass_input, db_input, db_type=selected_db_type)
            
            # Re-test connection
            test_ok, test_msg = db.test_connection()
            if test_ok:
                st.success(f"Connected to {selected_db_type} successfully!")
                if db.init_db():
                    st.info("Database schema validated.")
                st.cache_data.clear()
                time.sleep(1)  # Smooth transition
                st.rerun()
            else:
                st.error(f"Connection failed:\n{test_msg}")

# Ensure DB is initialized if connected
if db_connected:
    db_inited = db.init_db()
else:
    db_inited = False

@st.cache_data
def load_data_from_db():
    if db_inited:
        return db.get_all_data()
    return pd.DataFrame()

df = load_data_from_db()


# =====================================================================
# PAGE 1: DASHBOARD
# =====================================================================
if selected_page == "Dashboard":
    st.markdown(f"""
        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-end; gap:20px; margin-bottom:24px;">
            <div style="flex:1 1 460px; min-width:280px;">
                <h1 style="margin:0; font-size:2.8rem; line-height:1.05; color:var(--text-primary);">IPL Auction Intelligence</h1>
                <p style="margin:10px 0 0; color:var(--text-muted); font-size:1rem; max-width:680px;">A premium executive dashboard for IPL auction analytics, player valuations, and market insights.</p>
            </div>
            <div style="display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
                <div style="background: var(--bg-glass); border:1px solid var(--border-glass); border-radius:16px; padding:16px 22px; min-width:150px; box-shadow: var(--shadow-soft);">
                    <div style="font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.12em;">System Status</div>
                    <div style="font-size:1.05rem; font-weight:700; margin-top:6px; color:#10b981;">Online</div>
                </div>
                <div style="background: var(--bg-glass); border:1px solid var(--border-glass); border-radius:16px; padding:16px 22px; min-width:150px; box-shadow: var(--shadow-soft);">
                    <div style="font-size:0.82rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.12em;">DB Status</div>
                    <div style="font-size:1.05rem; font-weight:700; margin-top:6px; color:#10b981;">Connected</div>
                </div>
            </div>
        </div>
        <div class="metric-container" style="margin-bottom:28px;">
            <div class="custom-metric">
                <div class="metric-header"><span class="metric-icon">👥</span><span class="metric-title">Registered Players</span></div>
                <div class="metric-value">{df['player_name'].nunique():,}</div>
            </div>
            <div class="custom-metric">
                <div class="metric-header"><span class="metric-icon">✅</span><span class="metric-title">Total Auction Entries</span></div>
                <div class="metric-value" style="color: #10b981;">{len(df):,}</div>
            </div>
            <div class="custom-metric">
                <div class="metric-header"><span class="metric-icon">🔥</span><span class="metric-title">Highest Bid</span></div>
                <div class="metric-value" style="color: #f59e0b;">₹ {df['auction_price'].max():.1f} Cr</div>
            </div>
            <div class="custom-metric">
                <div class="metric-header"><span class="metric-icon">💰</span><span class="metric-title">Average Sold Price</span></div>
                <div class="metric-value">₹ {df[df['sold_status']==1]['auction_price'].mean():.2f} Cr</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ No data available in the system. Please upload a dataset first.")
    else:
        df['perf_score'] = ml.calculate_performance_score(df)
        sold_df = df[df['sold_status']==1].copy()

        if sold_df.empty:
            st.warning("⚠️ No sold players found in the dataset. Add auction results to enable market analytics.")
        else:
            left_col, right_col = st.columns([1, 1], gap='large')
            with left_col:
                fig1 = px.scatter(
                    sold_df, x='perf_score', y='auction_price', color='team', hover_name='player_name',
                    hover_data={'year':True, 'runs':True, 'wickets':True, 'perf_score':':.1f'},
                    labels={'perf_score': 'Performance Score', 'auction_price': 'Final Price (Cr.)', 'team': 'Franchise'},
                    color_discrete_map=viz.get_ipl_colors(),
                    title="Price vs Performance",
                    template=viz.get_template(is_light_mode)
                )
                fig1.update_traces(marker=dict(size=12, opacity=0.85, line=dict(width=1, color='rgba(255,255,255,0.15)')))
                fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=430, margin=dict(l=0, r=0, t=45, b=0))
                st.plotly_chart(fig1, use_container_width=True)

            with right_col:
                fig2 = viz.plot_team_spending(sold_df, is_light_mode)
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=430, margin=dict(l=0, r=0, t=45, b=0))
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"<br><hr style='border-color: var(--border-glass);'><br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-size:1.5rem; color:var(--text-primary); margin-bottom:10px;'>Player Market Ecosystem</h3>", unsafe_allow_html=True)

        clusters, X = ml.perform_clustering(df)
        df['Player Tier'] = [f"Tier {c+1}" for c in clusters]

        fig3 = px.scatter(
            df, x=X[:, 0], y=X[:, 1], color='Player Tier', hover_name='player_name',
            labels={'x': 'Performance Index', 'y': 'Economy Index'},
            color_discrete_sequence=['#22c55e', '#38bdf8', '#f97316'],
            template=viz.get_template(is_light_mode)
        )
        fig3.update_traces(marker=dict(size=11, opacity=0.82, line=dict(width=1, color='rgba(255,255,255,0.2)')))
        fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=520, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)


# =====================================================================
# PAGE 2: PLAYER ANALYSIS (PREDICTION)
# =====================================================================
elif selected_page == "Player Analysis":
    if df.empty:
        st.warning("⚠️ No data found. Please upload data first.")
    else:
        # Control Panel
        with st.container():
            st.markdown(f"""
            <div style="background-color: var(--bg-card); padding: 25px; border-radius: 16px; border: 1px solid var(--border-glass); margin-bottom: 30px; box-shadow: var(--shadow-soft);">
                <h3 style="margin-top: 0; color: var(--text-primary); font-size: 1.3rem;">AI Player Valuation & Insights</h3>
                <p style="color: var(--text-muted); font-size: 0.95rem; margin-bottom: 20px;">Deep dive into a player's statistical profile and predict their market demand using Machine Learning.</p>
            """, unsafe_allow_html=True)
            
            c_sel1, c_btn = st.columns([3, 1])
            with c_sel1:
                players = sorted(df['player_name'].unique().tolist())
                search_name = st.text_input("Search Player", value="", placeholder="All players (type to filter)...", key="player_search")
                filtered_players = [p for p in players if search_name.lower() in p.lower()] if search_name else players
                if filtered_players:
                    selected_player = st.selectbox("Select Player Profile", filtered_players, key="player_select")
                else:
                    st.warning("No players found. Change your search text.")
                    selected_player = None
            with c_btn:
                submit_btn = st.button("Generate Report ⚡", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        if submit_btn and selected_player:
            with st.spinner("Analyzing player history & running AI models..."):
                time.sleep(0.5) # Smooth UX
                player_history = df[df['player_name'] == selected_player]
                latest_stats = player_history.sort_values('year').iloc[-1]
                
                rf_clf, lr_clf, acc = ml.train_sold_classification(df)
                rf_reg, mse, r2 = ml.train_price_regression(df)
                
                latest_perf_score = ml.calculate_performance_score(pd.DataFrame([latest_stats]))[0]
                
                # Inference
                is_sold = 0
                price_pred = 0.0
                try:
                    sold_input = pd.DataFrame({'perf_score': [latest_perf_score], 'matches': [latest_stats['matches']], 'economy': [latest_stats['economy']]})
                    is_sold = rf_clf.predict(sold_input)[0]
                    
                    if is_sold == 1:
                        price_input = pd.DataFrame({'perf_score': [latest_perf_score], 'matches': [latest_stats['matches']], 'strike_rate': [latest_stats['strike_rate']]})
                        price_pred = rf_reg.predict(price_input)[0]
                except Exception:
                    pass
                
                trend = ml.get_player_trend(df, selected_player)
                
                # Risk Analysis logic
                std_runs = player_history['runs'].std() if len(player_history) > 1 else 0
                risk_level = "High Risk" if std_runs > 150 else ("Medium Risk" if std_runs > 80 else "Low Risk")
                risk_color = "#ef4444" if risk_level == "High Risk" else ("#f59e0b" if risk_level == "Medium Risk" else "#10b981")
                
                # Baseline for Radar
                baseline = [df['batting_avg'].mean(), df['strike_rate'].mean()/2, df['runs'].mean()/10, df['wickets'].mean(), df['matches'].mean()*5]
                p_stats = [latest_stats['batting_avg'], latest_stats['strike_rate']/2, latest_perf_score/5, latest_stats['wickets'], latest_stats['matches']*5]

            # --- Layout ---
            c_left, c_right = st.columns([1, 2])
            
            with c_left:
                card_bg = "#ffffff" if is_light_mode else "#1e293b"
                glass_bg = "rgba(255,255,255,0.85)" if is_light_mode else "rgba(30,41,59,0.7)"
                text_primary = "#0f172a" if is_light_mode else "#f8fafc"
                text_muted = "#475569" if is_light_mode else "#94a3b8"
                accent_primary = "#4f46e5"
                border_color = "rgba(0,0,0,0.1)" if is_light_mode else "rgba(255,255,255,0.1)"
                shadow = "0 10px 25px -5px rgba(0, 0, 0, 0.05)" if is_light_mode else "0 10px 25px -5px rgba(0, 0, 0, 0.3)"
                value_color = "#10b981" if is_sold else "#ef4444"
                valuation_text = f"₹ {round(price_pred, 2)} Cr" if is_sold else "Unsold"
                photo_url = latest_stats.get('photo_url') or latest_stats.get('Photo_URL')
                team_name = latest_stats.get('team') or latest_stats.get('Team')
                image_source = photo_url if photo_url else get_player_photo(selected_player, team_name)
                team_abbr = get_team_abbr(team_name) or ''
                display_team = team_name or latest_stats.get('team') or latest_stats.get('Team') or 'Unknown Team'

                st.image(image_source, width=320)
                st.markdown(f"""
                <div style="background: {glass_bg}; padding: 22px; border-radius: 24px; border: 1px solid {border_color}; box-shadow: {shadow};">
                  <div style="text-align:center; margin-bottom: 18px;">
                    <div style="font-size:2rem; font-weight:800; color:{text_primary}; line-height:1.1;">{selected_player}</div>
                    <div style="display:inline-flex; align-items:center; gap:10px; margin-top:10px; padding:8px 16px; background: rgba(79, 70, 229, 0.12); border-radius:999px; color:{accent_primary}; font-weight:700; letter-spacing:0.08em; font-size:0.95rem;">
                      <span>{team_abbr}</span>
                      <span style="opacity:0.85;">{display_team}</span>
                    </div>
                  </div>
                  <div style="display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:14px; margin-bottom:20px;">
                    <div style="background: rgba(255,255,255,0.08); padding: 14px; border-radius: 16px;">
                      <div style="font-size:0.8rem; color:{text_muted};">Role</div>
                      <div style="font-size:1.2rem; font-weight:700; color:{text_primary};">{latest_stats['role']}</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.08); padding: 14px; border-radius: 16px;">
                      <div style="font-size:0.8rem; color:{text_muted};">Last Auction</div>
                      <div style="font-size:1.2rem; font-weight:700; color:{value_color};">{valuation_text}</div>
                    </div>
                  </div>
                  <div style="display:flex; justify-content:space-between; gap:10px; margin-bottom:20px;">
                    <div style="flex:1; text-align:center; background: rgba(79, 70, 229, 0.08); padding:12px; border-radius:12px;">
                      <div style="font-size:0.8rem; color:{text_muted};">Age</div>
                      <div style="font-size:1.4rem; font-weight:700; color:{text_primary};">{int(latest_stats['age']) if 'age' in latest_stats else 'N/A'}</div>
                    </div>
                    <div style="flex:1; text-align:center; background: rgba(79, 70, 229, 0.08); padding:12px; border-radius:12px;">
                      <div style="font-size:0.8rem; color:{text_muted};">Nationality</div>
                      <div style="font-size:1.4rem; font-weight:700; color:{text_primary};">{latest_stats.get('nationality', 'N/A')}</div>
                    </div>
                    <div style="flex:1; text-align:center; background: rgba(79, 70, 229, 0.08); padding:12px; border-radius:12px;">
                      <div style="font-size:0.8rem; color:{text_muted};">Year</div>
                      <div style="font-size:1.4rem; font-weight:700; color:{text_primary};">{int(latest_stats['year'])}</div>
                    </div>
                  </div>
                  <hr style="border-color: {border_color}; margin: 20px 0;" />
                  <div style="display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:15px;">
                    <div style="background: rgba(255, 255, 255, 0.06); padding: 14px; border-radius: 14px;">
                      <div style="color:{text_muted}; font-size:0.85rem;">Last Auction</div>
                      <div style="font-size:1.5rem; font-weight:700; color:{value_color};">₹ {latest_stats.get('auction_price', 0):.2f} Cr</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.06); padding: 14px; border-radius: 14px;">
                      <div style="color:{text_muted}; font-size:0.85rem;">Base Price</div>
                      <div style="font-size:1.5rem; font-weight:700; color:{text_primary};">₹ {latest_stats.get('base_price', 0):.2f} Cr</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.06); padding: 14px; border-radius: 14px;">
                      <div style="color:{text_muted}; font-size:0.85rem;">Matches</div>
                      <div style="font-size:1.5rem; font-weight:700; color:{text_primary};">{int(latest_stats.get('matches', 0))}</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.06); padding: 14px; border-radius: 14px;">
                      <div style="color:{text_muted}; font-size:0.85rem;">Sold Status</div>
                      <div style="font-size:1.5rem; font-weight:700; color:{'#10b981' if is_sold else '#ef4444'};">{'Sold' if latest_stats.get('sold_status', latest_stats.get('Status', 0)) else 'Unsold'}</div>
                    </div>
                  </div>
                </div>
                <div style="background:{card_bg}; padding:20px; border-radius:12px; border:1px solid {border_color}; box-shadow:{shadow}; margin-top:20px;">
                  <h4 style="margin-top:0; color:{accent_primary};">🤖 AI Insights</h4>
                  <ul style="color:{text_muted}; font-size:0.9rem; padding-left:20px; margin:0;">
                    <li>Exact strike rate: {latest_stats['strike_rate']:.1f}, which drives power-hitting value.</li>
                    <li>Exact batting average: {latest_stats['batting_avg']:.1f}, great indicator of consistency.</li>
                    <li>Exact wicket count: {int(latest_stats['wickets'])} for the selected season.</li>
                  </ul>
                </div>
                """, unsafe_allow_html=True)

            with c_right:
                r_t1, r_t2 = st.tabs(["📊 Profile Radar", "📈 Market History"])
                with r_t1:
                    fig_radar = viz.plot_player_radar(p_stats, baseline, is_light_mode)
                    st.plotly_chart(fig_radar, use_container_width=True)
                with r_t2:
                    fig_trend = viz.plot_auction_trend(df, selected_player, is_light_mode)
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown(f"<br><h3 style='font-size:1.2rem; color:var(--text-primary);'>Historical Records</h3>", unsafe_allow_html=True)
            clean_df = player_history[['year', 'team', 'matches', 'runs', 'wickets', 'strike_rate', 'economy', 'auction_price']].copy()
            clean_df.columns = [c.replace('_', ' ').title() for c in clean_df.columns]
            st.dataframe(clean_df, use_container_width=True, hide_index=True)


# =====================================================================
# PAGE 3: NEXT YEAR PREDICTIONS
# =====================================================================
elif selected_page == "Next Year Predictions":
    st.markdown(f"<h3 style='font-size:1.8rem; font-weight:700; color:var(--text-primary); margin-bottom:10px;'>🚀 Next Year Forecasting Engine</h3>", unsafe_allow_html=True)
    st.write("Advanced multi-model pipeline forecasting player performance and auction values for the upcoming year.")
    
    if df.empty:
        st.warning("⚠️ No player data available. Please upload a dataset first.")
    else:
        # Initialize Engine (version key forces re-init after code changes)
        _ENGINE_VERSION = 4
        if ('ml_engine' not in st.session_state or
            st.session_state.get('ml_engine_version') != _ENGINE_VERSION or
            'preds_next_year' not in st.session_state):
            with st.spinner("Initializing Advanced ML Pipeline & Engineering Features..."):
                # Format dataframe columns to match what the ML Engine expects
                ml_df = df.rename(columns={
                    'player_name': 'Player_Name', 'team': 'Team', 'role': 'Role',
                    'nationality': 'Nationality', 'age': 'Age', 'matches': 'Matches',
                    'runs': 'Runs', 'wickets': 'Wickets', 'strike_rate': 'Strike_Rate',
                    'economy': 'Bowling_Economy', 'batting_avg': 'Batting_Avg',
                    'year': 'Year', 'auction_price': 'Sold_Price_CR',
                    'base_price': 'Base_Price_CR', 'sold_status': 'Status'
                })
                # Normalize sold status to the expected string values.
                if 'Status' in ml_df.columns:
                    def normalize_status(x):
                        s = str(x).strip().lower()
                        return 'Sold' if s in ['sold', 'retained', 'trade', '1', 'true', 'yes'] else 'Unsold'
                    ml_df['Status'] = ml_df['Status'].apply(normalize_status)
                
                engine = mle.IPLPredictionEngine(ml_df)
                engine.train_all_models()
                st.session_state['ml_engine'] = engine
                st.session_state['preds_next_year'] = engine.generate_next_year_predictions()
                st.session_state['ml_engine_version'] = _ENGINE_VERSION
                
        engine = st.session_state['ml_engine']
        preds_df = st.session_state['preds_next_year']

        # (Debug expander removed per user request)

        # Search bar for predictions
        search_query = st.text_input("Search Players", value="", placeholder="Filter by player or role...", key="pred_search")
        filtered_df = preds_df.copy()
        if search_query:
            query_lower = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df['Player_Name'].str.lower().str.contains(query_lower) |
                filtered_df['Role'].str.lower().str.contains(query_lower)
            ]
        
        tab1, tab2, tab3 = st.tabs(["📊 Prediction Output", "📈 Visual Analytics", "⚙️ Model Diagnostics"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Players Displayed", len(filtered_df))
            with c2:
                highest_price = filtered_df['Predicted_Price'].max() if not filtered_df.empty else 0
                st.metric("Highest Projected Price", f"₹ {highest_price:.2f} Cr")
            with c3:
                sold_count = len(filtered_df[filtered_df['Sold_Probability'] > 50])
                st.metric("Expected Sold Players", sold_count)
            
            st.dataframe(
                filtered_df[['Player_Name', 'Role', 'Predicted_Runs', 'Predicted_Wickets', 'Predicted_Price', 'Sold_Probability']]
                .style.background_gradient(subset=['Predicted_Price'], cmap='Greens')
                .background_gradient(subset=['Sold_Probability'], cmap='Blues'),
                use_container_width=True, hide_index=True
            )
            
        with tab2:
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                fig1 = viz.plot_prediction_bar(preds_df.sort_values('Predicted_Runs', ascending=False), 'Player_Name', 'Predicted_Runs', 'Top 15 Predicted Run Scorers', 'Role', is_light_mode)
                st.plotly_chart(fig1, use_container_width=True)
                
                fig3 = viz.plot_sold_probability(preds_df, is_light_mode)
                st.plotly_chart(fig3, use_container_width=True)
            with v_col2:
                fig2 = viz.plot_prediction_bar(preds_df.sort_values('Predicted_Price', ascending=False), 'Player_Name', 'Predicted_Price', 'Top 15 Valued Players (Cr.)', 'Role', is_light_mode)
                st.plotly_chart(fig2, use_container_width=True)
                
                top_player = preds_df.sort_values('Predicted_Price', ascending=False).iloc[0]['Player_Name']
                fig4 = viz.plot_auction_trend(df, top_player, is_light_mode)
                st.plotly_chart(fig4, use_container_width=True)
                
        with tab3:
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                fig_m1 = viz.plot_model_comparison(engine.metrics['Runs'], 'R2', is_light_mode)
                st.plotly_chart(fig_m1, use_container_width=True)
            with m_col2:
                fig_m2 = viz.plot_model_comparison(engine.metrics['Price'], 'R2', is_light_mode)
                st.plotly_chart(fig_m2, use_container_width=True)
                
            fig_imp = viz.plot_feature_importance(engine.models['Price'], engine.X.columns, is_light_mode)
            st.plotly_chart(fig_imp, use_container_width=True)
            
            fig_corr = viz.plot_correlation_heatmap(engine.processed_df, is_light_mode)
            st.plotly_chart(fig_corr, use_container_width=True)


# =====================================================================
# PAGE 4: UPLOAD DATA
# =====================================================================
elif selected_page == "Upload Data":
    current_config = db.load_db_config()
    db_type_label = current_config.get("db_type", "MySQL")
    
    st.markdown(f"<h3 style='font-size:1.8rem; font-weight:700; color:var(--text-primary); margin-bottom:10px;'>Data Ingestion Pipeline</h3>", unsafe_allow_html=True)
    st.write(f"Securely upload CSV datasets directly into the master {db_type_label} Database.")
    
    st.markdown(f"""
        <div style='background: var(--bg-glass); padding: 40px 20px; border-radius: 20px; border: 2px dashed var(--accent-primary); text-align: center; margin-top:20px; margin-bottom:20px; box-shadow: 0 0 30px rgba(99, 102, 241, 0.15); backdrop-filter: blur(10px);'>
            <h1 style='font-size: 4rem; margin:0; padding:0; background:none; -webkit-text-fill-color: var(--accent-primary); animation: float 3s ease-in-out infinite;'>☁️</h1>
            <h3 style='color: var(--text-primary); margin-top: 15px; font-weight: 600;'>Drag & Drop IPL Statistics CSV</h3>
            <p style='color: var(--text-muted); font-size:0.95rem;'>Files will be automatically validated and ingested into the Data Warehouse.</p>
        </div>
        <style>
        @keyframes float {{
            0% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-15px); }}
            100% {{ transform: translateY(0px); }}
        }}
        </style>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV File", type=['csv'], label_visibility="collapsed")
    st.markdown("<p style='color: var(--text-muted); font-size:0.95rem;'>Optional: include a <code>Photo_URL</code> column with professional player portrait URLs or local image file names in the <code>images/</code> folder.</p>", unsafe_allow_html=True)
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            st.success(f"✔️ Validated: {uploaded_file.name} ({len(uploaded_df)} records)")
            st.write(f"Showing {len(uploaded_df)} record(s)")
            
            st.dataframe(uploaded_df, use_container_width=True)
            
            if st.button(f"Commit to {db_type_label} Database 💾", use_container_width=True):
                with st.spinner(f"Executing {db_type_label} INSERT transactions & Clearing Old Data..."):
                    # 1. Overwrite the local base dataset file with the new dataset
                    uploaded_df.to_csv("ipl_dataset.csv", index=False)
                    
                    # 2. Run multi-year generation pipeline (generates 4 years of history up to 2025)
                    from generate_sample_data import generate_multi_year_dataset
                    generated_df = generate_multi_year_dataset("ipl_dataset.csv", "ipl_dataset_4yr.csv")
                    
                    db.clear_all_data()
                    if generated_df is not None:
                        # 3. Generate 2026 predictions via ML engine
                        import ml_engine as mle
                        
                        # Prepare mapping format
                        ml_df = generated_df.rename(columns={
                            'player_name': 'Player_Name', 'team': 'Team', 'role': 'Role',
                            'nationality': 'Nationality', 'age': 'Age', 'matches': 'Matches',
                            'runs': 'Runs', 'wickets': 'Wickets', 'strike_rate': 'Strike_Rate',
                            'economy': 'Bowling_Economy', 'batting_avg': 'Batting_Avg',
                            'year': 'Year', 'auction_price': 'Sold_Price_CR',
                            'base_price': 'Base_Price_CR', 'sold_status': 'Status'
                        })
                        if 'Status' in ml_df.columns:
                            def normalize_status(x):
                                s = str(x).strip().lower()
                                return 'Sold' if s in ['sold', 'retained', 'trade', '1', 'true', 'yes'] else 'Unsold'
                            ml_df['Status'] = ml_df['Status'].apply(normalize_status)
                            
                        engine = mle.IPLPredictionEngine(ml_df)
                        engine.train_all_models()
                        preds_2026 = engine.generate_next_year_predictions()
                        
                        # Map predictions back to the schema
                        mapped_2026 = pd.DataFrame({
                            'Player_Name': preds_2026['Player_Name'],
                            'Role': preds_2026['Role'],
                            'Nationality': preds_2026['Nationality'],
                            'Age': preds_2026['Age'],
                            'Team': preds_2026['Team'],
                            'Year': preds_2026['Year'],
                            'Base_Price_CR': preds_2026['Base_Price_CR'],
                            'Matches': preds_2026['Predicted_Matches'],
                            'Batting_Avg': preds_2026['Predicted_Batting_Avg'],
                            'Strike_Rate': preds_2026['Predicted_Strike_Rate'],
                            'Runs': preds_2026['Predicted_Runs'],
                            'Bowling_Economy': preds_2026['Predicted_Economy'],
                            'Wickets': preds_2026['Predicted_Wickets'],
                            'Sold_Price_CR': preds_2026['Predicted_Price'],
                            'Status': ['Sold' if p > 50 else 'Unsold' for p in preds_2026['Sold_Probability']]
                        })
                        
                        # Set Unsold values to 0 / empty
                        unsold_mask = mapped_2026['Status'] == 'Unsold'
                        mapped_2026.loc[unsold_mask, 'Sold_Price_CR'] = 0.0
                        mapped_2026.loc[unsold_mask, 'Team'] = ''
                        
                        # Combine generated data and 2026 ML predictions
                        combined_df = pd.concat([generated_df, mapped_2026], ignore_index=True)
                        
                        db.upload_data_to_db(combined_df)
                    else:
                        db.upload_data_to_db(uploaded_df)
                    
                    st.cache_data.clear()
                st.balloons()
                st.success("✅ Architecture Updated & Local Dataset Replaced! Returning to Dashboard to view changes...")
        except Exception as e:
            st.error(f"Integrity Error: {e}")
