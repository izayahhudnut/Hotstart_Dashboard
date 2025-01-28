import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

# Load environment variables and set up configuration
load_dotenv()
api_key = os.getenv('INSTANTLY_API_KEY')
campaign_id = os.getenv('INSTANTLY_CAMPAIGN_ID')

# Set page configuration
st.set_page_config(
    page_title="Hotstart Campaign Results",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Import a clean, modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #F9FAFB; /* Light background */
        color: #333;
    }

    /* Override Streamlit's default progress bar color */
    .stProgress > div > div > div > div {
        background-color: #3B82F6;
    }

    /* Metric card container */
    .metric-card {
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 4px solid #3B82F6; /* Blue accent on the left */
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }

    .big-number {
        font-size: 2.2rem;
        font-weight: 600;
        color: #3B82F6; /* Blue accent text */
    }

    /* Campaign step containers */
    .campaign-step {
        background-color: #fff;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #1F2937;
        font-weight: 600;
    }

    /* Expanders */
    .streamlit-expander {
        background-color: #fff;
        border-radius: 10px;
    }
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1rem;
    }

    /* Make code blocks or pre elements more readable */
    pre, code {
        background-color: #f0f2f6;
        border-radius: 6px;
        padding: 5px 10px;
    }

    /* Optional: Add a little spacing at the bottom of the page */
    .block-container {
        padding-bottom: 50px;
    }
    </style>
""", unsafe_allow_html=True)

def fetch_campaign_data():
    """Fetch campaign analytics data from the Instantly API."""
    if not api_key or not campaign_id:
        return None
        
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "id": campaign_id,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    try:
        response = requests.get(
            "https://api.instantly.ai/api/v2/campaigns/analytics",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()[0]
    except:
        return None

def main():
    # Header
    st.title("Hotstart Campaign Results")
    
    # Campaign Type and Schedule
    # Add Gmail and LinkedIn logos next to the heading
    gmail_logo = "https://www.gstatic.com/images/branding/product/1x/gmail_2020q4_48dp.png"
    linkedin_logo = "https://cdn-icons-png.flaticon.com/512/3536/3536505.png"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(
            f"""
            <strong>Campaign type:</strong>
            <img src="{gmail_logo}" width="24" style="vertical-align:middle;"> Gmail +
            <img src="{linkedin_logo}" width="24" style="vertical-align:middle;"> LinkedIn
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown("**⏰ Schedule:** From 9:00am to 6:00pm EST, Monday - Friday")
    
    # Fetch campaign data
    campaign_data = fetch_campaign_data()
    
    # Key Metrics
    st.markdown("### Campaign Performance")
    metric_cols = st.columns(3)
    
    with metric_cols[0]:
        st.markdown(
            """
            <div class="metric-card">
                <div>Total Leads</div>
                <div class="big-number">69</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[1]:
        st.markdown(
            """
            <div class="metric-card">
                <div>Invites Sent</div>
                <div class="big-number">0</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[2]:
        st.markdown(
            """
            <div class="metric-card">
                <div>Open Rate</div>
                <div class="big-number">0%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Campaign Progress
    st.markdown("### Campaign Sequence Progress")
    progress = 0  # This would come from your campaign data
    st.progress(progress/100)
    st.markdown(f"**{progress}% Complete**")
    
    # Campaign Steps
    st.markdown("### Campaign Sequence")
    
    with st.expander("Step 1 - Email", expanded=True):
        st.markdown("#### Version A")
        st.markdown("""
        **Subject:** Open to a quick call about HotStart VC?
        
        Hi {{first_name}},
        
        I'm reaching out because I believe {{company_name}} aligns perfectly with HotStart VC's focus on celebrity-founded brands.
        
        HotStart is a $10M seed fund focused on the celebrity-founded ecosystem. With experience founding some of the most successful celebrity-founded brands like The Honest Co. (Jessica Alba) and Feastables (MrBeast) and structuring and investing in 55+ other celebrity-founded brands, our team brings unparalleled industry access, expertise, and proven success.
        
        I'd love to share more details and get your thoughts. Are you available for a 15-minute call?
        
        **Schedule a call**
        """)
        
        st.markdown("#### Version B")
        st.markdown("""
        **Subject:** Can I introduce you to HotStart VC on a quick 15-min call?
        
        Hi {{first_name}},
        
        My name is Scott, and I'm the Founder at Hotstart VC, a $10M seed-stage VC fund focused on celebrity-founded brands.
        
        We're raising our next fund, and I wanted to personally reach out because I believe our thesis and approach could align well with your investment goals.
        
        I'd love to connect and share more about our fund and investment strategy. Are you open to a quick 15-minute call?
        
        Looking forward to hearing from you!
        """)
    
    with st.expander("Step 2 - Follow Up Email"):
        st.markdown("""
        Hi {{first_name}},
        
        I wanted to follow up on my email about HotStart VC. Let me know if you'd be open to a quick 15-minute call to discuss further.
        
        Looking forward to hearing from you!
        """)
    
    with st.expander("Step 3 - LinkedIn Connect"):
        st.markdown("""
        I'm Scott, the GP of HotStart VC, a fund investing in celebrity-founded brands. We've worked with talents like Selena Gomez, DJ Khaled, and Jake Paul. Let's connect—I'd love to learn more about your work and share what we're doing at HotStart!
        """)
    
    # Add engagement metrics if campaign data is available
    if campaign_data:
        st.markdown("### Campaign Engagement")
        col1, col2 = st.columns(2)
        
        with col1:
            create_funnel_chart(campaign_data)
        
        with col2:
            create_engagement_distribution(campaign_data)
            
    st.markdown("### Leads (Google Sheet)")
    
    # Example public embed link (from Publish to the Web):
    sheet_url = "https://docs.google.com/spreadsheets/d/1x-BxEZUJL0cRaCYKwtkidpFl9LBq2kz_UR18RcIbjLk/edit?gid=1465228395#gid=1465228395"

    # If you have a normal share link, ensure it's in the right format for embedding
    # e.g. replace "/edit#gid=" with "/embed?gid=" or "/pubhtml?gid="
    # sheet_url = sheet_url.replace("/edit#gid=", "/embed?gid=")

    st.markdown(
        f"""
        <iframe 
            src="{sheet_url}" 
            width="100%" 
            height="600" 
            frameborder="0"
            style="border: 1px solid #ccc"
        ></iframe>
        """,
        unsafe_allow_html=True
    )

def create_funnel_chart(data):
    """
    Create a funnel chart for campaign progression.
    Note: `go.Funnel` does not allow a list of discrete colors in `marker.colors`.
    We'll use a single color or a colorscale approach.
    """
    funnel_data = {
        'Stage': ['Total Leads', 'Contacted', 'Opened', 'Replied'],
        'Count': [
            data['leads_count'],
            data['contacted_count'],
            data['open_count'],
            data['reply_count']
        ]
    }

    # If you want each stage to have a slightly different shade of one color,
    # you can pass an array of numeric values and apply a colorscale.
    # For a simple single color, just do: marker=dict(color="#3B82F6")
    fig = go.Figure(go.Funnel(
        y=funnel_data['Stage'],
        x=funnel_data['Count'],
        textinfo="value+percent initial",
        marker=dict(
            color=funnel_data['Count'],         # numeric array
            colorscale=[                        # from dark to light blue
                [0.0, '#3B82F6'],
                [1.0, '#93C5FD']
            ],
            line=dict(color='white', width=1)
        )
    ))
    
    fig.update_layout(
        title="Campaign Funnel",
        title_x=0.5,
        showlegend=False,
        height=400,
        paper_bgcolor='#F9FAFB',
        plot_bgcolor='#F9FAFB',
        font=dict(color='#333', size=14)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_engagement_distribution(data):
    """Create a pie chart showing engagement distribution with a modern color palette."""
    engagement_data = {
        'Category': ['Replied', 'Opened (No Reply)', 'No Engagement', 'Bounced'],
        'Count': [
            data['reply_count'],
            data['open_count'] - data['reply_count'],
            data['contacted_count'] - data['open_count'] - data['bounced_count'],
            data['bounced_count']
        ]
    }
    
    # Complementary color palette for categories
    pie_colors = ["#34D399", "#60A5FA", "#FBBF24", "#F87171"]
    
    fig = px.pie(
        values=engagement_data['Count'],
        names=engagement_data['Category'],
        title="Engagement Distribution",
        color_discrete_sequence=pie_colors
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='#F9FAFB',
        plot_bgcolor='#F9FAFB',
        font=dict(color='#333', size=14),
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)
    
    
    

if __name__ == "__main__":
    main()
