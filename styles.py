import streamlit as st
import base64
import os

def apply_custom_css():
    # นำ CSS และ Google Fonts จากไฟล์เพิ่มเติมมาประยุกต์ใช้
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Nunito:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* กำหนดตัวแปรสีธีม มก.ศรช. (เขียว-ทอง) ในรูปแบบ Modern */
    :root {
        --ku-green: #006633;
        --ku-gold: #E2C792;
        --bg-rgb: 8, 12, 28;
        --surface-rgb: 255, 255, 255;
    }

    /* พื้นหลังแบบ Nebula Effect จากไฟล์เพิ่มเติม */
    .stApp {
        background: radial-gradient(circle at bottom center, #004422, #080c1c) !important;
        color: #FFFFFF !important;
        font-family: 'Nunito', 'Sarabun', sans-serif !important;
    }

    /* ตกแต่ง Sidebar แบบ Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* กล่องแชทสไตล์ iOS + Modern Cyber */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        margin-bottom: 15px !important;
    }

    /* ปุ่ม Quick Links (Widget Style) */
    div.stButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 16px !important;
        color: #FFFFFF !important;
        padding: 12px 20px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        background: rgba(0, 102, 51, 0.4) !important; /* สีเขียว KU เมื่อ Hover */
        border-color: #E2C792 !important; /* ขอบสีทอง */
        box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
    }

    /* หัวข้อภาษาไทย (Sarabun) */
    h1, h2, h3 {
        font-family: 'Fredoka', 'Sarabun', sans-serif !important;
        color: #E2C792 !important; /* สีทองนนทรี */
    }

    /* Input Bar */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* Animation สำหรับชื่อมหาวิทยาลัย */
    .univ-name {
        background: linear-gradient(to right, #E2C792, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
        font-size: 24px;
        animation: pulse-slow 3s infinite;
    }

    @keyframes pulse-slow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    </style>

    <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none;">
        <div style="position: absolute; width: 300px; height: 300px; background: rgba(0, 102, 51, 0.2); filter: blur(100px); top: 10%; left: 10%;"></div>
        <div style="position: absolute; width: 400px; height: 400px; background: rgba(226, 199, 146, 0.1); filter: blur(120px); bottom: 10%; right: 10%;"></div>
    </div>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# พจนานุกรมภาษา (คงเดิม)
translation = {
    "TH": {
        "univ_name": "Kasetsart University Sriracha",
        "new_chat": "➕ แชทใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ลิงก์แบบฟอร์มต่างๆ",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีคุณ",
        "topic": "หัวข้อ",
        "loading": "*(พี่กำลังหาคำตอบให้...)*",
        "btn_find": "ค้นหา",
        "btn_open": "เปิดระบบ",
        "btn_download": "โหลด",
        "ai_identity": "คุณคือรุ่นพี่ มก.ศรช. ใจดี ตอบเป็นภาษาไทยเป็นหลัก"
    },
    "EN": {
        "univ_name": "Kasetsart University Sriracha",
        "new_chat": "➕ New Chat",
        "chat_hist": "💬 Chat History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello",
        "topic": "Topic",
        "loading": "*(Nontri is thinking...)*",
        "btn_find": "Search",
        "btn_open": "Open",
        "btn_download": "Get",
        "ai_identity": "You are a friendly KU Sriracha senior. Please respond in English."
    }
}

# ส่วนแสดงผล Streamlit
def main():
    apply_custom_css()
    
    # เลือกภาษา
    lang = st.sidebar.selectbox("Language / ภาษา", ["TH", "EN"])
    t = translation[lang]

    # แสดงชื่อมหาวิทยาลัยพร้อมตกแต่ง
    st.markdown(f'<p class="univ-name">{t["univ_name"]}</p>', unsafe_allow_html=True)
    
    # ตัวอย่างการใช้งาน Sidebar Widgets
    with st.sidebar:
        st.button(t["new_chat"], use_container_width=True)
        st.markdown("---")
        st.button(t["exam_table"], use_container_width=True)
        st.button(t["gpa_calc"], use_container_width=True)
        st.button(t["forms"], use_container_width=True)

    # ตัวอย่างข้อความแชท
    with st.chat_message("assistant"):
        st.write(f"{t['welcome']}! {t['ai_identity']}")

    # ช่องรับข้อมูล
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
