import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import os

st.set_page_config(page_title="College Result Portal", layout="wide")
audio_file = open("music.mp3", "rb")
audio_bytes = audio_file.read()

st.markdown("""
<style>
div[data-testid="stAudio"] {
    width: 200px;   /* size small */
    opacity: 0.2;   /* almost hidden */
    margin-top: -20px;
}
</style>
""", unsafe_allow_html=True)

st.audio(audio_bytes, format="audio/mp3")
# ---------------- ANIMATED COLLEGE HEADER ----------------
st.markdown("""
<style>
/* Animated Gradient Background */
.header-container {
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    background: linear-gradient(270deg, #00ffd5, #0e1117, #00ffd5);
    background-size: 600% 600%;
    animation: gradientMove 8s ease infinite;
    box-shadow: 0px 0px 20px rgba(0,255,213,0.5);
}

/* Text Glow Effect */
.header-title {
    font-size: 40px;
    font-weight: bold;
    color: white;
    text-shadow: 0 0 10px #00ffd5, 0 0 20px #00ffd5;
    animation: slideIn 2s ease-out;
}

/* Subtitle */
.header-sub {
    font-size: 18px;
    color: #cccccc;
    animation: slideIn 3s ease-out;
}

/* Gradient Animation */
@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Slide Animation */
@keyframes slideIn {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
</style>

<div class="header-container">
    <div class="header-title">
        🎓 Technocrats Institute Of Technology Bhopal
    </div>
    <div class="header-sub">
        Smart Result Analysis & Student Performance System 🚀
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- LOGO + THEME ----------------
st.markdown("""
<style>
.main {background-color: #0e1117;}
h1, h2, h3, h4 {color: #00ffd5;}
</style>
""", unsafe_allow_html=True)

st.title("🎓 College Result Portal")
st.caption("National Science Day Project")

# ---------------- ADMIN LOGIN ----------------
with st.sidebar:
    st.header("🔐 Admin Login")
    admin_user = st.text_input("Username")
    admin_pass = st.text_input("Password", type="password")

    admin_logged = (admin_user == "admin" and admin_pass == "1234")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data(file):
    df = pd.read_csv("Mock_sunday_Test.csv")
    df.columns = [c.strip() for c in df.columns]

    numeric_cols = df.columns[6:]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

file_path = "Mock_sunday_Test.csv"
df = load_data(file_path)

# ---------------- ADMIN UPLOAD ----------------
if admin_logged:
    st.sidebar.success("Admin Logged In")
    uploaded = st.sidebar.file_uploader("📤 Upload New Result File", type=["csv", "xlsx"])
    if uploaded:
        if uploaded.name.endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
        st.sidebar.success("File Uploaded Successfully!")

# ---------------- COLUMN MAPPING ----------------
cols = df.columns.tolist()

apt_r = cols[6]
apt_w = cols[7]
ver_r = cols[8]
ver_w = cols[9]
pro_r = cols[10]
pro_w = cols[11]
marks = cols[-1]

# ---------------- PERFORMANCE LOGIC ----------------
def performance(m):
    if m >= 40:
        return "High Performer"
    elif m >= 25:
        return "Average Performer"
    else:
        return "Low Performer"

df["Performance"] = df[marks].apply(performance)
df["Status"] = df[marks].apply(lambda x: "Pass" if x >= 24 else "Fail")

df["Rank"] = df[marks].rank(ascending=False, method="min").astype(int)

# ---------------- SEARCH ----------------
st.subheader("🔎 Search Student by Roll Number")
roll = st.text_input("Enter Roll Number")

if roll:
    student = df[df["Roll Number"].astype(str) == roll]

    if not student.empty:
        s = student.iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.success("Student Found")
            st.write("👤 Name:", s["Name"])
            st.write("🏫 College:", s["College"])
            st.write("📚 Branch:", s["Branch"])
            st.write("🎓 Year:", s["Year"])
            st.write("🏆 Rank:", s["Rank"])

        with col2:
            st.metric("📊 Total Marks", s[marks])
            st.metric("✅ Status", s["Status"])
            st.metric("🔥 Performance", s["Performance"])

        # -------- PDF DOWNLOAD ----------
        if st.button("📄 Download Result PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(0, 10, "Student Result Report", ln=True)

            for col in df.columns:
                if col.lower() != "email":
                    pdf.cell(0, 8, f"{col}: {s[col]}", ln=True)
            pdf.output("result.pdf")
            with open("result.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="result.pdf")

    else:
        st.error("Student Not Found")

# ---------------- RANK PAGE ----------------
st.markdown("## 🏆 Rank List (Top 10 Students)")
rank_df = df.sort_values(by=marks, ascending=False).head(10)
st.dataframe(rank_df[["Rank", "Name", "Roll Number", marks]])

# ---------------- GRAPHS ----------------
st.markdown("## 📊 Subject-wise Performance (Animated)")

avg_df = pd.DataFrame({
    "Subject": ["Aptitude", "Verbal", "Programming"],
    "Average Right": [
        df[apt_r].mean(),
        df[ver_r].mean(),
        df[pro_r].mean()
    ]
})

fig = px.bar(avg_df, x="Subject", y="Average Right", text="Average Right",
             animation_frame=None)
st.plotly_chart(fig, use_container_width=True)

pf_df = df["Status"].value_counts().reset_index()
pf_df.columns = ["Status", "Count"]

fig2 = px.pie(pf_df, names="Status", values="Count", hole=0.4)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- ALL STUDENTS ----------------
st.markdown("## 🧑‍🎓 All Students Data")
safe_df = df.drop(columns=["Email"], errors="ignore")
st.dataframe(safe_df)
st.markdown("""
<style>
.footer {
    position: relative;
    padding: 20px;
    margin-top: 50px;
    text-align: center;
    color: #00ffd5;
    border-top: 1px solid #00ffd5;
    animation: fadeIn 3s ease-in;
}

.footer-text {
    font-size: 16px;
    color: #cccccc;
}

.footer-highlight {
    color: #00ffd5;
    font-weight: bold;
    text-shadow: 0 0 10px #00ffd5;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
</style>

<div class="footer">
    <div class="footer-text">
        🚀 Powered by <span class="footer-highlight">Data Science & AI</span><br><br>
        
        "Data is the new oil, but insight is the real power." 📊<br><br>
        
        Built with ❤️ using Python, Streamlit & Analytics<br>
        
        🎓 Technocrats Institute Of Technology Bhopal
    </div>
</div>
""", unsafe_allow_html=True)
