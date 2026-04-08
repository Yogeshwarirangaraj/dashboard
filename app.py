import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Elite Recruiter Dashboard", layout="wide")

# -----------------------------
# 🎨 ELITE GLASS UI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

.glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

.kpi {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border-radius: 14px;
    padding: 25px;
    text-align: center;
    transition: 0.3s;
}

.kpi:hover {
    transform: scale(1.05);
    background: rgba(255,255,255,0.15);
}

</style>
""", unsafe_allow_html=True)

st.title("🚀 Elite Recruiter Intelligence Dashboard")

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
    st.error("❌ Error loading Excel")
    st.stop()

# -----------------------------
# FILTERS TOP BAR
# -----------------------------
f1, f2 = st.columns(2)
weeks = f1.multiselect("Week", df['Week'].unique(), default=df['Week'].unique())
recruiters = f2.multiselect("Recruiter", df['Recruiter Name'].unique(), default=df['Recruiter Name'].unique())

filtered_df = df[(df['Week'].isin(weeks)) & (df['Recruiter Name'].isin(recruiters))]

# -----------------------------
# KPI LOGIC
# -----------------------------
total = filtered_df.select_dtypes(include='number').sum().sum()

leader = filtered_df.groupby('Recruiter Name').sum(numeric_only=True).reset_index()
leader['Score'] = leader.select_dtypes(include='number').sum(axis=1)

top_performer = leader.sort_values('Score', ascending=False).head(1)
low_performer = leader.sort_values('Score', ascending=True).head(1)

# -----------------------------
# KPI UI (GLASS CARDS)
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"<div class='kpi'><h3>Total Activity</h3><h1>{int(total)}</h1></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='kpi'><h3>Recruiters</h3><h1>{filtered_df['Recruiter Name'].nunique()}</h1></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='kpi'><h3>Top Performer</h3><h1>{top_performer['Recruiter Name'].values[0] if not top_performer.empty else '-'}</h1></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='kpi'><h3>Needs Attention</h3><h1>{low_performer['Recruiter Name'].values[0] if not low_performer.empty else '-'}</h1></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# INSIGHTS SECTION
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.subheader("🧠 Insights")

if not leader.empty:
    best = top_performer['Recruiter Name'].values[0]
    worst = low_performer['Recruiter Name'].values[0]

    st.success(f"🏆 {best} is the top performer")
    st.warning(f"⚠️ {worst} needs improvement")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# VISUALS
# -----------------------------
col1, col2 = st.columns(2)

# Leaderboard
fig1 = px.bar(leader, x='Recruiter Name', y='Score', title="Performance")
fig1.update_layout(template="plotly_dark")
col1.plotly_chart(fig1, use_container_width=True)

# Contribution
fig2 = px.pie(leader, names='Recruiter Name', values='Score', title="Contribution")
fig2.update_layout(template="plotly_dark")
col2.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# TREND
# -----------------------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
weekly = filtered_df.groupby('Week').sum(numeric_only=True).reset_index()
fig3 = px.line(weekly, x='Week', y=weekly.select_dtypes(include='number').columns,
               title="Weekly Trend", markers=True)
fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# DATA
# -----------------------------
with st.expander("📋 View Data"):
    st.dataframe(filtered_df, use_container_width=True)
