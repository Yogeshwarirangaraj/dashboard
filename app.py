import streamlit as st

# -----------------------------
# 🎨 NETFLIX-STYLE UI THEME
# -----------------------------
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background: linear-gradient(180deg, #0e1117 0%, #141a2e 100%);
        color: white;
    }
    .metric-card {
        background: #1f2937;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
        text-align: center;
    }
    .section {
        background: #111827;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)
import pandas as pd
import plotly.express as px
import requests
from io import BytesIO

st.set_page_config(page_title="Recruiter Productivity Pro Dashboard", layout="wide")

st.title("🚀 Recruiter Productivity Pro Dashboard")

# -----------------------------
# 🔐 AUTO LOAD EXCEL (MULTIPLE OPTIONS)
# -----------------------------

@st.cache_data
def load_data(file):
    # Read properly (your sheet has headers in row 2)
    df = pd.read_excel(file, header=1)

    # Clean
    df = df.dropna(how='all')

    # Rename columns for clarity
    df.columns = [str(col).strip() for col in df.columns]

    # Convert numeric columns safely
    for col in df.columns:
        if col not in ['Week', 'Recruiter Name']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

@st.cache_data
def load_data_from_url(url):
    response = requests.get(url)
    file = BytesIO(response.content)
    return load_data(file)

# OPTION 1: Load from repo (BEST for private setup)
try:
    df = load_data("data.xlsx")
    st.success("✅ Loaded data from repo (data.xlsx)")

except Exception:
    try:
        # OPTION 2: Load from URL (if configured)
        if "DATA_URL" in st.secrets:
            df = load_data_from_url(st.secrets["DATA_URL"])
            st.success("✅ Loaded data from URL")
        else:
            raise Exception("No URL configured")

    except Exception:
        # OPTION 3: Manual upload fallback
        uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])
        if uploaded_file:
            df = load_data(uploaded_file)
        else:
            st.warning("⚠️ No data source found. Add data.xlsx or upload file.")
            st.stop()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -----------------------------
# Filters
# -----------------------------
st.sidebar.header("🎯 Filters")
weeks = st.sidebar.multiselect("Week", df['Week'].dropna().unique(), default=df['Week'].dropna().unique())
recruiters = st.sidebar.multiselect("Recruiter", df['Recruiter Name'].dropna().unique(), default=df['Recruiter Name'].dropna().unique())

# Targets
st.sidebar.header("🎯 Targets")
target_sub = st.sidebar.number_input("Target Submissions", value=10)
target_int = st.sidebar.number_input("Target Interviews", value=5)
target_off = st.sidebar.number_input("Target Offers", value=2)

filtered_df = df[(df['Week'].isin(weeks)) & (df['Recruiter Name'].isin(recruiters))]

# -----------------------------
# KPIs (Better View)
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📊 KPI Overview")
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='metric-card'><h3>Submissions</h3><h1>{int(total_sub)}</h1></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h3>Interviews</h3><h1>{int(total_int)}</h1></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h3>Offers</h3><h1>{int(total_off)}</h1></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric-card'><h3>Total Activity</h3><h1>{int(total_activity)}</h1></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Funnel
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🔄 Hiring Funnel")
fig_funnel.update_layout(template="plotly_dark")
st.plotly_chart(fig_funnel, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Leaderboard (Cleaner)
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🏆 Leaderboard")
fig_leader.update_layout(template="plotly_dark")
st.plotly_chart(fig_leader, use_container_width=True)
st.dataframe(leaderboard, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Target vs Actual
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🎯 Target vs Actual")
fig_target.update_layout(template="plotly_dark")
st.plotly_chart(fig_target, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Alerts
# -----------------------------
st.subheader("⚠️ Alerts")
if total_sub < target_sub:
    st.warning("Submissions below target")
if total_int < target_int:
    st.warning("Interviews below target")
if total_off < target_off:
    st.warning("Offers below target")

# -----------------------------
# Weekly Trend (Improved)
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📅 Weekly Trend")
fig_week.update_layout(template="plotly_dark")
st.plotly_chart(fig_week, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Data Table
# -----------------------------
st.subheader("📋 Data")
st.dataframe(filtered_df, use_container_width=True)

# -----------------------------
# 🔐 PRIVATE REPO DEPLOY FIX
# -----------------------------
st.sidebar.markdown("""
## 🔐 Using PRIVATE Repo

When deploying on Streamlit:
1. Go to Streamlit Cloud
2. Click your profile → Settings
3. Connect GitHub
4. Grant access to PRIVATE repos

---

## 🔗 Connect Excel Automatically

### Option (Recommended): Google Drive
1. Upload Excel to Google Drive
2. Click Share → Anyone with link
3. Convert link:
   https://drive.google.com/file/d/FILE_ID/view
   →
   https://drive.google.com/uc?export=download&id=FILE_ID

4. Add in Streamlit secrets:

DATA_URL = "your_link_here"

---

Now your app auto-refreshes data 🚀
""")
