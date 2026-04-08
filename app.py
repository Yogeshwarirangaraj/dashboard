import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Recruiter Productivity Pro Dashboard", layout="wide")

st.title("🚀 Recruiter Productivity Pro Dashboard")

# Upload file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=1)
    df = df.dropna(how='all')

    # Convert numeric columns
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Sidebar filters
    st.sidebar.header("🎯 Filters")
    weeks = st.sidebar.multiselect("Week", df['Week'].dropna().unique(), default=df['Week'].dropna().unique())
    recruiters = st.sidebar.multiselect("Recruiter", df['Recruiter Name'].dropna().unique(), default=df['Recruiter Name'].dropna().unique())

    # Targets input
    st.sidebar.header("🎯 Targets")
    target_sub = st.sidebar.number_input("Target Submissions", value=10)
    target_int = st.sidebar.number_input("Target Interviews", value=5)
    target_off = st.sidebar.number_input("Target Offers", value=2)

    filtered_df = df[(df['Week'].isin(weeks)) & (df['Recruiter Name'].isin(recruiters))]

    # KPIs
    st.subheader("📊 KPI Overview")
    col1, col2, col3 = st.columns(3)

    total_sub = filtered_df.get('Submissions', pd.Series()).sum()
    total_int = filtered_df.get('Interviews', pd.Series()).sum()
    total_off = filtered_df.get('Offers', pd.Series()).sum()

    col1.metric("Submissions", int(total_sub))
    col2.metric("Interviews", int(total_int))
    col3.metric("Offers", int(total_off))

    # Conversion funnel
    st.subheader("🔄 Conversion Funnel")
    sub = total_sub if total_sub else 0
    intv = total_int if total_int else 0
    off = total_off if total_off else 0

    funnel_df = pd.DataFrame({
        'Stage': ['Submissions', 'Interviews', 'Offers'],
        'Count': [sub, intv, off]
    })

    fig_funnel = px.funnel(funnel_df, x='Count', y='Stage', title="Hiring Funnel")
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Recruiter leaderboard
    st.subheader("🏆 Recruiter Leaderboard")
    recruiter_group = filtered_df.groupby('Recruiter Name').sum(numeric_only=True).reset_index()

    recruiter_group['Score'] = (
        recruiter_group.get('Submissions', 0)*1 +
        recruiter_group.get('Interviews', 0)*2 +
        recruiter_group.get('Offers', 0)*3
    )

    leaderboard = recruiter_group.sort_values(by='Score', ascending=False)
    st.dataframe(leaderboard, use_container_width=True)

    # Performance vs target
    st.subheader("🎯 Target vs Actual")
    target_df = pd.DataFrame({
        'Metric': ['Submissions', 'Interviews', 'Offers'],
        'Actual': [sub, intv, off],
        'Target': [target_sub, target_int, target_off]
    })

    fig_target = px.bar(target_df, x='Metric', y=['Actual', 'Target'], barmode='group', title="Target Comparison")
    st.plotly_chart(fig_target, use_container_width=True)

    # Alerts
    st.subheader("⚠️ Performance Alerts")
    if sub < target_sub:
        st.warning("Submissions below target!")
    if intv < target_int:
        st.warning("Interviews below target!")
    if off < target_off:
        st.warning("Offers below target!")

    # Weekly trend
    st.subheader("📅 Weekly Trend")
    weekly_group = filtered_df.groupby('Week').sum(numeric_only=True).reset_index()
    fig_week = px.line(weekly_group, x='Week', y=weekly_group.columns[2:], markers=True)
    st.plotly_chart(fig_week, use_container_width=True)

    # Raw data
    st.subheader("📋 Data Table")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("Upload your Excel file to start")

# -----------------------------
# Deployment Ready Enhancements
# -----------------------------

@st.cache_data
def load_data(file):
    df = pd.read_excel(file, header=1)
    df = df.dropna(how='all')
    for col in df.columns[2:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

# Replace earlier loading with cached version
if uploaded_file:
    df = load_data(uploaded_file)

# -----------------------------
# 🌐 DEPLOYMENT GUIDE
# -----------------------------

st.sidebar.markdown("""
## 🚀 Deploy this as Live Web App

### Option 1: Streamlit Cloud (Easiest)
1. Create GitHub repo
2. Add these files:
   - app.py
   - requirements.txt

### requirements.txt:
streamlit
pandas
plotly
openpyxl

3. Go to:
👉 https://share.streamlit.io
4. Connect GitHub
5. Deploy → You get a live URL 🎉

---

### Option 2: Render (Free Hosting)
1. Push code to GitHub
2. Go to https://render.com
3. Create → Web Service
4. Add start command:
   streamlit run app.py --server.port=10000 --server.address=0.0.0.0

---

### Option 3: Internal Company Hosting
- Deploy on Azure / AWS
- Use Docker (ask me if needed)

---

### 🔥 Pro Tips
- Save your Excel as a shared file (Google Drive / SharePoint)
- Replace upload with auto-fetch (I can help you do this)
- Add login for team access

---

👉 Want me to:
- Add login system?
- Connect to live data (no uploads)?
- Deploy it for you step-by-step?
""")
