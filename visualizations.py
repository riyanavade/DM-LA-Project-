import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def get_template(is_light_mode):
    return "plotly_white" if is_light_mode else "plotly_dark"

def get_ipl_colors():
    return {
        'Chennai Super Kings': '#F9CD05',
        'Mumbai Indians': '#004BA0',
        'Royal Challengers Bangalore': '#EC1C24',
        'Kolkata Knight Riders': '#2E0854',
        'Sunrisers Hyderabad': '#FF822A',
        'Rajasthan Royals': '#EA1A85',
        'Delhi Capitals': '#00008B',
        'Punjab Kings': '#ED1B24',
        'Lucknow Super Giants': '#005087',
        'Gujarat Titans': '#1B2133',
        'Unknown': '#888888'
    }

def plot_prediction_bar(df, x_col, y_col, title, color_col=None, is_light_mode=False):
    fig = px.bar(df.head(15), x=x_col, y=y_col, color=color_col, title=title,
                 template=get_template(is_light_mode),
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_auction_trend(df, player_name, is_light_mode=False):
    # Depending on if it's the raw df or processed df, column names might vary
    price_col = 'Auction_Price' if 'Auction_Price' in df.columns else 'sold_price_cr'
    year_col = 'Year' if 'Year' in df.columns else 'year'
    player_col = 'Player_Name' if 'Player_Name' in df.columns else 'player_name'
    
    if price_col not in df.columns:
        price_col = 'auction_price'
        
    player_data = df[df[player_col].str.lower() == player_name.lower()].sort_values(year_col)
    
    fig = px.line(player_data, x=year_col, y=price_col, title=f"Historical Auction Trend", markers=True, template=get_template(is_light_mode))
    fig.update_traces(line_color="#6366f1", line_width=4, marker=dict(size=12, color="#f59e0b", line=dict(width=2, color="white")))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(title="Price (Cr)"))
    return fig

def plot_feature_importance(model, feature_names, is_light_mode=False):
    if not hasattr(model, 'feature_importances_'):
        return go.Figure()
        
    importances = model.feature_importances_
    df_imp = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
    df_imp = df_imp.sort_values('Importance', ascending=True).tail(10)
    
    fig = px.bar(df_imp, x='Importance', y='Feature', orientation='h', title="Top AI Decision Factors", template=get_template(is_light_mode))
    fig.update_traces(marker_color="#3b82f6")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_correlation_heatmap(df, is_light_mode=False):
    cols = df.select_dtypes(include=[np.number]).columns
    corr = df[cols].corr()
    
    fig = px.imshow(corr, text_auto=".1f", aspect="auto", color_continuous_scale="RdBu_r", title="Feature Correlations", template=get_template(is_light_mode))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_model_comparison(metrics_df, metric_name='R2', is_light_mode=False):
    fig = px.bar(metrics_df, x='Model', y=metric_name, color='Model', title=f"Algorithm Comparison ({metric_name})", template=get_template(is_light_mode))
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig

def plot_sold_probability(df, is_light_mode=False):
    fig = px.histogram(df, x='Sold_Probability', nbins=20, title="Market Demand Distribution", template=get_template(is_light_mode),
                       color_discrete_sequence=["#10b981"])
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))
    return fig

def plot_player_radar(player_stats, baseline_stats, is_light_mode=False):
    categories = ['Batting Avg', 'Strike Rate', 'Consistency', 'Form', 'Matches']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=baseline_stats,
        theta=categories,
        fill='toself',
        name='League Avg',
        line_color='rgba(148, 163, 184, 0.5)',
        fillcolor='rgba(148, 163, 184, 0.2)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=player_stats,
        theta=categories,
        fill='toself',
        name='Player Profile',
        line_color='#6366f1',
        fillcolor='rgba(99, 102, 241, 0.4)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(148, 163, 184, 0.2)"),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        template=get_template(is_light_mode),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20)
    )
    return fig

def plot_team_spending(df, is_light_mode=False):
    if 'team' in df.columns:
        team_col = 'team'
    elif 'Team' in df.columns:
        team_col = 'Team'
    else:
        return go.Figure()
        
    price_col = 'auction_price' if 'auction_price' in df.columns else 'Auction_Price'
    if price_col not in df.columns:
        return go.Figure()
        
    team_spending = df.groupby(team_col)[price_col].sum().reset_index()
    team_spending = team_spending.sort_values(price_col, ascending=True)
    
    colors = get_ipl_colors()
    team_spending['color'] = team_spending[team_col].map(lambda x: colors.get(x, colors['Unknown']))
    
    fig = px.bar(
        team_spending,
        x=price_col,
        y=team_col,
        orientation='h',
        title="Franchise Spending Power",
        template=get_template(is_light_mode),
        text=price_col,
    )
    fig.update_traces(
        marker_color=team_spending['color'],
        texttemplate='₹%{x:.2f} Cr',
        textposition='outside',
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Total Spent (Cr)",
        yaxis_title="Franchise",
        yaxis=dict(categoryorder='total ascending'),
        margin=dict(l=90, r=20, t=45, b=20),
        bargap=0.25,
        height=460,
    )
    return fig

