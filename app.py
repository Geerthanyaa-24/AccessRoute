import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

# Set page config
st.set_page_config(
    page_title="AccessRoute Dashboard",
    page_icon="♿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Custom CSS to match the provided design
st.markdown("""
    <style>
    /* Global Background and Fonts */
    .stApp {
        background-color: #F4F7FB;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0F326D;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Hide top header bar */
    header {visibility: hidden;}
    
    /* Top Metrics Cards */
    .metric-container {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        display: flex;
        align-items: center;
        gap: 15px;
        height: 100px;
    }
    .metric-icon {
        width: 50px;
        height: 50px;
        border-radius: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: white;
    }
    .m-blue { background-color: #3182CE; }
    .m-green { background-color: #38A169; }
    .m-purple { background-color: #805AD5; }
    .m-orange { background-color: #DD6B20; }
    
    .metric-details p { margin: 0; padding: 0; }
    .metric-title { font-size: 14px; color: #718096; }
    .metric-value { font-size: 24px; font-weight: bold; color: #2D3748; }
    .metric-sub { font-size: 12px; color: #38A169; }
    
    /* Card Container for generic sections */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .card h3 {
        margin-top: 0;
        font-size: 16px;
        color: #2D3748;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    
    /* Forms and Buttons */
    .stTextInput>div>div>input {
        border-radius: 8px;
        background-color: #F7FAFC;
        border: 1px solid #E2E8F0;
    }
    .stButton>button {
        background-color: #3182CE;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #2B6CB0;
    }
    
    /* Feature Tags */
    .feature-tags {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    .f-tag {
        background-color: #F7FAFC;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        flex: 1;
        font-size: 12px;
        color: #4A5568;
        border: 1px solid #E2E8F0;
    }
    .f-tag span { font-size: 18px; display: block; margin-bottom: 5px; }
    
    /* Score Circle */
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        border: 8px solid #38A169;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
    }
    .score-circle h2 { margin: 0; font-size: 32px; color: #2D3748; }
    .score-circle p { margin: 0; font-size: 14px; color: #718096; }
    
    /* Lists */
    .list-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 14px;
        color: #4A5568;
    }
    .list-item span.count { font-weight: bold; color: #2D3748; }
    
    /* Progress Bars Custom */
    .prog-container { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13px;}
    .prog-label { width: 80px; color: #4A5568;}
    .prog-bar-bg { flex: 1; height: 8px; background-color: #E2E8F0; border-radius: 4px; overflow: hidden; }
    .prog-bar-fill { height: 100%; border-radius: 4px; }
    .prog-pct { width: 30px; text-align: right; font-weight: bold; color: #2D3748;}
    
    /* Report Item */
    .report-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #E2E8F0;
    }
    .report-item:last-child { border-bottom: none; }
    .report-icon { width: 30px; height: 30px; border-radius: 15px; background-color: #EBF8FF; display:flex; align-items:center; justify-content:center; color: #3182CE;}
    .report-text { flex: 1; margin: 0 15px; }
    .report-text h4 { margin: 0; font-size: 13px; color: #2D3748; }
    .report-text p { margin: 0; font-size: 11px; color: #A0AEC0; }
    .report-badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    .badge-red { background-color: #FED7D7; color: #C53030; }
    .badge-green { background-color: #C6F6D5; color: #276749; }
    
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="sidebar-title">♿ AccessRoute</div><div style="font-size:12px; color:#A0AEC0; margin-top:-20px; margin-bottom:30px;">Navigate Without Barriers</div>', unsafe_allow_html=True)
    
    menu_items = ["🏠 Dashboard", "🔍 Find Route", "📍 Nearby Places", "🏢 Accessible Buildings", "📊 Reports & Ratings", "🔖 Saved Places", "👤 Profile", "⚙️ Settings"]
    selected_menu = st.radio("", menu_items, label_visibility="collapsed")
    
    st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    # Mockup of the illustration at the bottom of sidebar
    st.markdown("""
        <div style="background-color: #EBF8FF; border-radius: 12px; padding: 15px; text-align: center; color: #2D3748; margin-top: auto;">
            <div style="font-size: 40px; margin-bottom: 10px;">🧑‍🦽</div>
            <strong style="font-size:14px; display:block;">Accessibility for Everyone,</strong>
            <span style="font-size:12px;">Independence for All.</span>
        </div>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("<h2 style='color: #0F326D; margin: 0;'>Welcome back, User! 👋</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #718096; margin-bottom: 20px;'>Plan your accessible and comfortable journey</p>", unsafe_allow_html=True)
with col_head2:
    st.markdown("<div style='text-align: right; color: #4A5568; margin-top:10px;'>☀️ 28°C Chennai &nbsp;&nbsp; 🔔 🌙</div>", unsafe_allow_html=True)

# --- TOP METRICS ---
m1, m2, m3, m4 = st.columns(4)
metrics_data = [
    (m1, "Accessible Places", "1,248", "+12% this month", "m-blue", "📍"),
    (m2, "Accessible Routes", "356", "+8% this month", "m-green", "🛤️"),
    (m3, "Avg. Accessibility", "4.2 / 5", "+0.3 this month", "m-purple", "⭐"),
    (m4, "Community Ratings", "2,543", "+15% this month", "m-orange", "👥")
]

for col, title, val, sub, bg_class, icon in metrics_data:
    with col:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-icon {bg_class}">{icon}</div>
            <div class="metric-details">
                <p class="metric-title">{title}</p>
                <p class="metric-value">{val}</p>
                <p class="metric-sub">{sub}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN CONTENT ROW 1 ---
col_main1, col_main2, col_main3 = st.columns([1, 2, 1])

with col_main1:
    st.markdown("""
    <div class="card" style="height: 480px;">
        <h3>Find Accessible Route</h3>
        <div style="margin-bottom: 10px;">
            <label style="font-size: 12px; color: #718096;">From</label>
            <input type="text" value="My Location" style="width: 100%; padding: 8px; border: 1px solid #E2E8F0; border-radius: 6px; margin-top:4px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label style="font-size: 12px; color: #718096;">To</label>
            <input type="text" value="City Library, Anna Salai" style="width: 100%; padding: 8px; border: 1px solid #E2E8F0; border-radius: 6px; margin-top:4px;">
        </div>
        <div style="margin-bottom: 20px;">
            <label style="font-size: 12px; color: #718096;">Preferences</label>
            <select style="width: 100%; padding: 8px; border: 1px solid #E2E8F0; border-radius: 6px; margin-top:4px;">
                <option>♿ Wheelchair User</option>
                <option>🦯 Visually Impaired</option>
            </select>
        </div>
        <button style="width: 100%; padding: 10px; background-color: #3182CE; color: white; border: none; border-radius: 8px; font-weight: bold; cursor:pointer;">Find Route ➔</button>
        
        <div class="feature-tags">
            <div class="f-tag"><span>♿</span>Wheelchair<br>Friendly</div>
            <div class="f-tag"><span>🚫</span>Avoid<br>Stairs</div>
            <div class="f-tag"><span>🛗</span>Elevator<br>Available</div>
            <div class="f-tag"><span>📈</span>Ramp<br>Available</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_main2:
    st.markdown("<div class='card' style='padding: 10px; height: 480px;'><h3 style='margin: 10px;'>Live Accessibility Map</h3>", unsafe_allow_html=True)
    # Generate map
    m = folium.Map(location=[13.06, 80.24], zoom_start=14, tiles="CartoDB positron")
    # Add dummy route (Green = Accessible, Red = Inaccessible)
    folium.PolyLine(locations=[[13.06, 80.23], [13.065, 80.24], [13.06, 80.25]], color="green", weight=5, opacity=0.8).add_to(m)
    folium.PolyLine(locations=[[13.06, 80.25], [13.05, 80.26]], color="red", weight=5, opacity=0.8, dash_array='5, 5').add_to(m)
    
    # Add markers
    folium.Marker([13.06, 80.23], icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
    folium.Marker([13.05, 80.26], icon=folium.Icon(color='green', icon='flag')).add_to(m)
    
    st_folium(m, width=630, height=390, returned_objects=[])
    st.markdown("</div>", unsafe_allow_html=True)

with col_main3:
    st.markdown("""
    <div class="card" style="height: 480px;">
        <h3>Accessibility Score</h3>
        <div class="score-circle">
            <h2>4.2</h2>
            <p>/ 5</p>
        </div>
        <div style="text-align: center; color: #ECC94B; font-size:20px; margin-bottom:5px;">★★★★☆</div>
        <div style="text-align: center; font-weight: bold; color: #3182CE; margin-bottom: 5px;">Good</div>
        <div style="text-align: center; font-size: 11px; color: #A0AEC0; margin-bottom: 25px;">Based on community ratings</div>
        
        <h3 style="font-size: 14px;">Common Features</h3>
        <div class="list-item"><span>♿ Ramps</span> <span class="count">842</span></div>
        <div class="list-item"><span>🛗 Elevators</span> <span class="count">623</span></div>
        <div class="list-item"><span>🅿️ Accessible Parking</span> <span class="count">512</span></div>
        <div class="list-item"><span>🛣️ Smooth Sidewalks</span> <span class="count">742</span></div>
        <div class="list-item"><span>🦯 Tactile Paths</span> <span class="count">318</span></div>
    </div>
    """, unsafe_allow_html=True)


# --- MAIN CONTENT ROW 2 ---
col_bot1, col_bot2, col_bot3 = st.columns(3)

with col_bot1:
    st.markdown("""
    <div class="card" style="height: 250px;">
        <h3>Accessibility Overview</h3>
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-top:20px;">
            <!-- Donut chart mockup via CSS -->
            <div style="width: 120px; height: 120px; border-radius: 50%; background: conic-gradient(#38A169 0% 45%, #ECC94B 45% 80%, #E53E3E 80% 100%); display:flex; align-items:center; justify-content:center;">
                <div style="width: 70px; height: 70px; background-color: white; border-radius: 50%;"></div>
            </div>
            <div style="font-size: 13px;">
                <div style="margin-bottom:8px;"><span style="color:#38A169;">●</span> Highly Accessible <b>45%</b></div>
                <div style="margin-bottom:8px;"><span style="color:#ECC94B;">●</span> Moderate <b>35%</b></div>
                <div><span style="color:#E53E3E;">●</span> Low Accessibility <b>20%</b></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_bot2:
    st.markdown("""
    <div class="card" style="height: 250px;">
        <h3>Top Accessible Categories</h3>
        
        <div class="prog-container"><div class="prog-label">🏛️ Libraries</div><div class="prog-bar-bg"><div class="prog-bar-fill" style="width: 92%; background-color:#38A169;"></div></div><div class="prog-pct">92%</div></div>
        <div class="prog-container"><div class="prog-label">🏥 Hospitals</div><div class="prog-bar-bg"><div class="prog-bar-fill" style="width: 88%; background-color:#38A169;"></div></div><div class="prog-pct">88%</div></div>
        <div class="prog-container"><div class="prog-label">🌲 Parks</div><div class="prog-bar-bg"><div class="prog-bar-fill" style="width: 75%; background-color:#ECC94B;"></div></div><div class="prog-pct">75%</div></div>
        <div class="prog-container"><div class="prog-label">🍽️ Restaurants</div><div class="prog-bar-bg"><div class="prog-bar-fill" style="width: 60%; background-color:#DD6B20;"></div></div><div class="prog-pct">60%</div></div>
        <div class="prog-container"><div class="prog-label">🛍️ Mails</div><div class="prog-bar-bg"><div class="prog-bar-fill" style="width: 55%; background-color:#E53E3E;"></div></div><div class="prog-pct">55%</div></div>
    </div>
    """, unsafe_allow_html=True)

with col_bot3:
    st.markdown("""
    <div class="card" style="height: 250px; overflow-y:auto;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <h3 style="border:none; margin:0; padding:0;">Recent Community Reports</h3>
            <span style="font-size:12px; color:#3182CE; cursor:pointer;">View All</span>
        </div>
        <hr style="border:0; border-top:1px solid #E2E8F0; margin: 10px 0;">
        
        <div class="report-item">
            <div class="report-icon">♿</div>
            <div class="report-text">
                <h4>Broken ramp near Main Gate</h4>
                <p>Anna University, Chennai • 2h ago</p>
            </div>
            <div class="report-badge badge-red">Low</div>
        </div>
        <div class="report-item">
            <div class="report-icon">🛗</div>
            <div class="report-text">
                <h4>Elevator not working</h4>
                <p>City Center Mall • 5h ago</p>
            </div>
            <div class="report-badge badge-red">Low</div>
        </div>
        <div class="report-item">
            <div class="report-icon">🛣️</div>
            <div class="report-text">
                <h4>Smooth and accessible path</h4>
                <p>Public Library, Anna Salai • 1d ago</p>
            </div>
            <div class="report-badge badge-green">High</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
