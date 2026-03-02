import streamlit as st
import base64
import os

def apply_custom_css():
    """จัดการ CSS ทั้งหมดของหน้าเว็บ"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }
    .stMarkdown, .stText, p { color: #2D3436 !important; font-weight: 400; }
    .stChatMessageContent { font-size: 1.1rem !important; line-height: 1.7 !important; font-weight: 400 !important; }
    [data-testid="stSidebar"] { background: rgba(248, 249, 250, 0.8) !important; backdrop-filter: blur(15px); border-right: 1px solid rgba(0,0,0,0.1); box-shadow: 5px 0 15px rgba(0,0,0,0.05); }
    .custom-header { display: flex; align-items: center; gap: 15px; padding: 10px !important; background: rgba(255, 255, 255, 0.9); border-radius: 15px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .header-logo-img { max-width: 60px !important; height: auto !important; }
    .univ-name { color: #333333 !important; font-size: 1.1rem !important; font-weight: 700; line-height: 1.2; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); margin-top: 0 !important; }
    div.stButton > button { border-radius: 50px !important; border: none !important; background: white !important; color: #004D40 !important; font-weight: 600 !important; transition: all 0.3s ease !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    div.stButton > button:hover { background: #004D40 !important; color: white !important; transform: scale(1.02); }
    .stChatMessage { background: rgba(255, 255, 255, 0.8) !important; backdrop-filter: blur(5px); border-radius: 20px !important; }
    .btn-action { background: #FFD700; color: #004D40 !important; padding: 5px 15px; border-radius: 20px; text-decoration: none; font-size: 0.8rem; font-weight: 700; transition: 0.3s; }
    .btn-action:hover { background: #FFC107; transform: translateY(-2px); }
    @keyframes wave-dance { 0%, 100% { transform: rotate(0deg); } 50% { transform: rotate(25deg); } }
    .dino-head { display: inline-block; animation: wave-dance 2s infinite ease-in-out; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    """แปลงรูปภาพเป็น Base64 สำหรับแสดงผลใน HTML"""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

translation = {
    "TH": {
        "univ_name": "มหาวิทยาลัย<br>เกษตรศาสตร์",
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
        "univ_name": "Kasetsart<br>University",
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
