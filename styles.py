import streamlit as st
import base64
import os

def apply_custom_css():
    """จัดการ CSS เพื่อความหรูหรา เน้น White Space และความสะอาดตา"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');
    
    /* 1. จัดการพื้นหลังและ Font */
    .stApp {
        background: #FFFFFF; /* ขาวสะอาดตา */
        font-family: 'Sarabun', sans-serif !important;
    }
   /* แก้ไข Top Bar ให้มีเส้นไล่เฉดสี */
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    /* สร้างเส้นขอบล่าง */
    border-bottom: 70px solid !important;
    /* กำหนดสีแบบไล่เฉด */
    border-image-source: linear-gradient(to right, #004D40, #D4AF37, #004D40) !important;
    border-image-slice: 1 !important;
    height: 2rem; /* เพิ่มความสูงนิดหน่อยให้ดูไม่โล่ง */
}

    /* 2. Sidebar ที่เน้นความโปร่ง (Luxury Minimalist) */
    [data-testid="stSidebar"] {
        background: rgba(252, 252, 252, 0.95) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0,0,0,0.03); 
        padding-top: 2rem !important; /* เพิ่มพื้นที่ว่างด้านบน */
    }

    /* จัดการระยะห่างระหว่างปุ่มใน Sidebar */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 12px !important; /* เว้นระยะห่างระหว่างปุ่มไม่ให้เบียดกัน */
    }

    /* 3. Header ที่หรูหราและสะอาด (เน้นใช้ PNG โปร่งใส) */
    .custom-header {
        display: flex;
        align-items: center;
        gap: 25px;
        padding: 25px !important;
        background: transparent; /* ตัดพื้นหลังสีขาวออกเพื่อให้กลืนไปกับจอ */
        border-bottom: 1px solid rgba(0,0,0,0.05); /* เพิ่มเส้นขีดจางๆ ใต้ Header */
        margin-bottom: 40px !important;
    }

    .header-logo-img { 
        max-width: 75px !important; /* ปรับขนาดโลโก้ให้เด่นขึ้นแต่พอดี */
        height: auto !important; 
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05)); /* เงาจางๆ ให้โลโก้ดูมีมิติ */
    }

    .univ-name {
        color: #1A1A1A !important;
        font-size: 1.3rem !important;
        font-weight: 700;
        letter-spacing: 1px;
        line-height: 1.3;
    }
    /* 4. **ปรับปรุงส่วนที่คุณต้องการให้มีมิติ (ค้นหา, เปิดระบบ, โหลด)** */
    /* เน้น class .btn-action ที่ใช้ใน HTML สำหรับลิงก์เหล่านี้ */
    .btn-action {
        display: inline-block !important;
        padding: 8px 24px !important; /* เพิ่ม Padding ให้ดูเป็นปุ่มที่เต็มอิ่ม */
        background: linear-gradient(135deg, #004D40 0%, #00695C 100%) !important; /* เขียวมรกตไล่เฉดสีเพิ่มมิติ */
        color: white !important;
        border-radius: 50px !important; /* ทรงมนดูทันสมัยและน่ากด */
        text-decoration: none !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        
        /* เทคนิคสร้างมิติ (Shadow) */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), /* เงาหลักจางๆ */
                    0 1px 3px rgba(0, 0, 0, 0.08) !important; /* เงาที่คมขึ้นที่ขอบ */
                    
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important; /* อนิเมชั่นที่ Smooth */
        border: 1px solid rgba(255, 255, 255, 0.1) !important; /* เส้นขอบบางๆ สีขาวช่วยให้ปุ่มดูคม */
        text-align: center;
        min-width: 100px;
        margin-top: 10px; /* เว้นระยะจากข้อความด้านบน */
    }

    /* ลูกเล่นเมื่อเมาส์ไปวาง (Hover) */
    .btn-action:hover {
        background: linear-gradient(135deg, #00695C 0%, #004D40 100%) !important; /* สลับสีเฉดให้ดูเคลื่อนไหว */
        color: #ffffff !important;
        
        /* ปรับเงาเมื่อ Hover ให้ดูเหมือนลอยขึ้น */
        box-shadow: 0 7px 14px rgba(0, 0, 0, 0.15), 
                    0 3px 6px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px); /* ลอยขึ้นเล็กน้อย */
    }

    /* ลูกเล่นเมื่อกด (Active) */
    .btn-action:active {
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2), 
                    0 1px 2px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(1px); /* ยุบตัวลงเล็กน้อย */
    }

    div.stButton > button:hover {
        background: #F8F9FA !important;
        border-color: #D4AF37 !important; /* เปลี่ยนขอบเป็นสีทองจางๆ เมื่อชี้ */
        color: #D4AF37 !important;
        transform: translateX(5px); /* เลื่อนขวาเล็กน้อยเมื่อ Hover */
    }

    /* 5. กล่อง Chat ที่ดูละมุนสายตา */
    .stChatMessage {
        background: #F9F9F9 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
    }

    .stChatMessageContent {
        font-size: 1.05rem !important;
        font-weight: 300 !important; /* ใช้ตัวบางเพื่อให้ดูแพง */
        color: #333333 !important;
    }

    /* 6. ตัว Loading ที่ดู Smooth */
    .stMarkdown em {
        color: #D4AF37 !important;
        font-style: normal !important;
        font-weight: 600;
    }
    /* 7. เพิ่มกิมมิคความหรูหราที่หัวข้อ */
    .univ-name {
        background: linear-gradient(to right, #004D40, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* ปรับแต่ง Scrollbar ให้ดูเรียบที่สุด */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 10px; }

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
