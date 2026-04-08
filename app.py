import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Recruiter Dashboard", layout="wide")

# -----------------------------
# 🎨 CLEAN DARK UI
# -----------------------------
st.markdown("""
<style>
.stApp {background: #0f172a; color: white;}
.metric {background:#1e293b; padding:20px; border-radius:12px; text-align:center;}
.section {background:#111827; padding:20px; border-radius:12px; margin-bottom:20px;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Recruiter Productivity Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", header=1)
    df = df.dropna(how='all')
    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        if col not in ['Week', 'Recruiter Name']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

try:
    df = load_data()
except:
    st.error("❌ data.xlsx not loading properly")
    st.stop()

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.header("Filters")
weeks = st.sidebar.multiselect("Week", df['Week'].unique(), default=df['Week'].unique())
recruiters = st.sidebar.multiselect("Recruiter", df['Recruiter Name'].unique(), default=df['Recruiter Name'].unique())

filtered_df = df[(df['Week'].isin(weeks)) & (df['Recruiter Name'].isin(recruiters))]

# -----------------------------
# KPI CALCULATION
# -----------------------------
total_activity = filtered_df.select_dtypes(include='number').sum().sum()

# Try to detect columns
sub_col = [c for c in df.columns if 'sub' in c.lower()]
int_col = [c for c in df.columns if 'interview' in c.lower()]
off_col = [c for c in df.columns if 'offer' in c.lower()]

submissions = filtered_df[sub_col[0]].sum() if sub_col else 0
interviews = filtered_df[int_col[0]].sum() if int_col else 0
offers = filtered_df[off_col[0]].sum() if off_col else 0

# -----------------------------
# KPI UI
# -----------------------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f"<div class='metric'><h3>Submissions</h3><h1>{int(submissions)}</h1></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric'><h3>Interviews</h3><h1>{int(interviews)}</h1></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric'><h3>Offers</h3><h1>{int(offers)}</h1></div>", unsafe_allow_html=True)
col4.markdown(f"<div class='metric'><h3>Total Activity</h3><h1>{int(total_activity)}</h1></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# CHARTS
# -----------------------------

# Leaderboard
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🏆 Recruiter Performance")
leader = filtered_df.groupby('Recruiter Name').sum(numeric_only=True).reset_index()
leader['Score'] = leader.select_dtypes(include='number').sum(axis=1)
fig = px.bar(leader, x='Recruiter Name', y='Score')
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Weekly trend
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📅 Weekly Trend")
weekly = filtered_df.groupby('Week').sum(numeric_only=True).reset_index()
fig2 = px.line(weekly, x='Week', y=weekly.select_dtypes(include='number').columns)
fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Data table
st.subheader("📋 Data")
st.dataframe(filtered_df, use_container_width=True)
