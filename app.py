import streamlit as st
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
    df = pd.read_excel(file, header=1)
    df = df.dropna(how='all')
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
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

except:
    # OPTION 2: Load from URL (if configured)
    try:
        if "DATA_URL" in st.secrets:
            df = load_data_from_url(st.secrets["DATA_URL"])
            st.success("✅ Loaded data from URL")
        else:
            raise Exception("No URL")

    except:
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
# KPIs
# -----------------------------
st.subheader("📊 KPI Overview")
col1, col2, col3 = st.columns(3)

total_sub = filtered_df.get('Submissions', pd.Series()).sum()
total_int = filtered_df.get('Interviews', pd.Series()).sum()
total_off = filtered_df.get('Offers', pd.Series()).sum()

col1.metric("Submissions", int(total_sub))
col2.metric("Interviews", int(total_int))
col3.metric("Offers", int(total_off))

# -----------------------------
# Funnel
# -----------------------------
st.subheader("🔄 Conversion Funnel")
funnel_df = pd.DataFrame({
    'Stage': ['Submissions', 'Interviews', 'Offers'],
    'Count': [total_sub, total_int, total_off]
})
fig_funnel = px.funnel(funnel_df, x='Count', y='Stage')
st.plotly_chart(fig_funnel, use_container_width=True)

# -----------------------------
# Leaderboard
# -----------------------------
st.subheader("🏆 Recruiter Leaderboard")
recruiter_group = filtered_df.groupby('Recruiter Name').sum(numeric_only=True).reset_index()
recruiter_group['Score'] = (
    recruiter_group.get('Submissions', 0)*1 +
    recruiter_group.get('Interviews', 0)*2 +
    recruiter_group.get('Offers', 0)*3
)
leaderboard = recruiter_group.sort_values(by='Score', ascending=False)
st.dataframe(leaderboard, use_container_width=True)

# -----------------------------
# Target vs Actual
# -----------------------------
st.subheader("🎯 Target vs Actual")
target_df = pd.DataFrame({
    'Metric': ['Submissions', 'Interviews', 'Offers'],
    'Actual': [total_sub, total_int, total_off],
    'Target': [target_sub, target_int, target_off]
})
fig_target = px.bar(target_df, x='Metric', y=['Actual', 'Target'], barmode='group')
st.plotly_chart(fig_target, use_container_width=True)

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
# Weekly Trend
# -----------------------------
st.subheader("📅 Weekly Trend")
weekly_group = filtered_df.groupby('Week').sum(numeric_only=True).reset_index()
fig_week = px.line(weekly_group, x='Week', y=weekly_group.columns[2:], markers=True)
st.plotly_chart(fig_week, use_container_width=True)

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
