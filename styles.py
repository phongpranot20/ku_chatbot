import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;600&family=Sarabun:wght@300;400;600&display=swap');

    /* พื้นหลังหลักแบบ iOS */
    .stApp {
        background-color: #F5F5F7 !important;
        font-family: 'SF Pro Display', 'Sarabun', sans-serif !important;
    }

    /* Sidebar แบบโปร่งแสง */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.5) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0,0,0,0.05);
    }

    /* Header ที่ดูคลีนขึ้น */
    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(15px);
        border-bottom: 0.5px solid rgba(0,0,0,0.1) !important;
    }

    /* กล่องแชท (Chat Bubbles) แบบ iOS */
    .stChatMessage {
        background-color: #FFFFFF !important;
        border-radius: 20px !important; /* มนมากขึ้น */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(0,0,0,0.02) !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
    }

    /* ปุ่ม Quick Links ให้เหมือน Widget ใน iOS */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: none !important;
        border-radius: 15px !important;
        color: #1D1D1F !important;
        padding: 12px 16px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
        transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button:hover {
        transform: scale(1.02);
        background-color: #FBFBFF !important;
        border-left: none !important; /* เอาเส้นทองออกเพื่อความ Minimal */
    }

    /* Input Bar ด้านล่าง */
    [data-testid="stChatInput"] {
        border-radius: 25px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        background-color: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
    }

    /* ปรับแต่ง Gradient ที่ชื่อมหาวิทยาลัยให้เบาลง */
    .univ-name {
        background: linear-gradient(to bottom, #333, #000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    """ฟังก์ชันจัดการรูปภาพ (ย้ายมาจากส่วนที่ 3)"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# พจนานุกรมภาษา (ย้ายมาจากส่วนที่ 2)
translation = {
    "TH": {
        "univ_name": "Kasetsart University",
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
        "univ_name": "Kasetsart University",
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
