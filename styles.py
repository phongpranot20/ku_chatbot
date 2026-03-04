import streamlit as st
import base64
import os

def apply_custom_css():
    """จัดการ CSS ทั้งหมดเพื่อความหรูหราและพรีเมียม"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    /* พื้นหลังหลักของ App */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
        font-family: 'Sarabun', sans-serif !important;
    }

    /* ตัวอักษรทั่วไป */
    .stMarkdown, .stText, p { 
        color: #2D3436 !important; 
        font-weight: 400; 
    }

    /* Sidebar แบบหรูหรา */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(212, 175, 55, 0.3); /* เส้นขอบสีทองจางๆ */
        box-shadow: 10px 0 30px rgba(0,0,0,0.05);
    }

    /* Header ของมหาวิทยาลัย */
    .custom-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px !important;
        background: white;
        border-radius: 10px !important;
        box-shadow: 0 10px 10px rgba(0,0,0,0.05);
        margin-bottom: 10px !important;
        border-left: 2px solid #D4AF37; /* แถบสีทองด้านข้าง */
    }

    .univ-name {
        color: #004D40 !important;
        font-size: 1.2rem !important;
        font-weight: 800;
        line-height: 1.2;
        letter-spacing: 0.5px;
    }

    /* ปุ่มกด (Buttons) สไตล์ Premium */
    div.stButton > button {
        border-radius: 12px !important;
        border: 1px solid rgba(212, 175, 55, 0.5) !important;
        background: white !important;
        color: #004D40 !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #004D40 0%, #00695C 100%) !important;
        color: #D4AF37 !important; /* อักษรสีทองตอน Hover */
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 77, 64, 0.2);
    }

    /* กล่องข้อความ Chat */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.02) !important;
        border: 1px solid rgba(0,0,0,0.03) !important;
    }

    .stChatMessageContent {
        font-size: 1.05rem !important;
        line-height: 1.8 !important;
    }

    /* ปุ่ม Action ขนาดเล็ก (เช่น Search/Download) */
    .btn-action {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
        color: white !important;
        padding: 6px 18px;
        border-radius: 10px;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        transition: 0.3s;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3);
    }

    .btn-action:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 15px rgba(212, 175, 55, 0.4);
    }

    /* ปรับแต่ง Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #004D40; border-radius: 10px; }

    /* ลูกเล่นไดโนเสาร์ */
    .stApp::before {
        content: "🦖";
        position: fixed;
        bottom: 30px;
        right: 30px;
        font-size: 60px;
        opacity: 0.07;
        z-index: 0;
    }
    
    @keyframes wave-dance {
        0%, 100% { transform: rotate(-5deg); }
        50% { transform: rotate(15deg); }
    }
    .dino-head { 
        display: inline-block; 
        animation: wave-dance 3s infinite ease-in-out; 
        font-size: 1.5rem;
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
