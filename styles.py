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
   /* แก้ไข Top Bar ให้ดูหรูและไม่ทับ Sidebar */
header[data-testid="stHeader"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    /* เปลี่ยนจาก border หนาๆ เป็นเส้นบางๆ ที่ดูแพง */
    border-bottom: 3px solid !important;
    border-image: linear-gradient(to right, #004D40, #D4AF37, #004D40) 1 !important;
    height: 60px !important; /* กำหนดความสูงที่แน่นอน */
}

/* ปรับตำแหน่งปุ่ม Hamburger (เมนูซ้าย) ให้ลอยเด่นขึ้นมา */
button[data-testid="stSidebarCollapseButton"] {
    background-color: white !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    border-radius: 50% !important;
    margin-left: 10px !important;
}

    /* จัดการระยะห่างระหว่างปุ่มใน Sidebar */
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 12px !important; /* เว้นระยะห่างระหว่างปุ่มไม่ให้เบียดกัน */
    }

    /* 3. Header ที่หรูหราและสะอาด (เน้นใช้ PNG โปร่งใส) */
    .custom-header {
        display: flex;
        align-items: center;
        gap: 40px;
        padding: 40px !important;
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
    /* ปรับแต่งช่อง Input ด้านล่าง */
[data-testid="stChatInput"] {
    border-radius: 20px !important;
    border: 1px solid rgba(0, 77, 64, 0.1) !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    background: #ffffff !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #D4AF37 !important;
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.2) !important; /* แสงสีทองจางๆ */
    transform: scale(1.01); /* ขยายใหญ่ขึ้นนิดเดียวให้ดูมีชีวิต */
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

    div.stButton > button {
    border: none !important;
    background: transparent !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    text-align: left !important;
    padding: 10px 15px !important;
}

div.stButton > button:hover {
    background: rgba(212, 175, 55, 0.08) !important; /* สีทองจางๆ */
    color: #004D40 !important;
    padding-left: 25px !important; /* Slide effect */
    border-left: 4px solid #D4AF37 !important; /* เส้นสีทองด้านข้าง */
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
    .btn-action {
    position: relative;
    overflow: hidden; /* จำเป็นสำหรับ Shimmer */
    /* ... (โค้ดเดิมของคุณ) ... */
}

.btn-action::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -60%;
    width: 20%;
    height: 200%;
    background: rgba(255, 255, 255, 0.3);
    transform: rotate(30deg);
    transition: none;
}

.btn-action:hover::after {
    left: 120%;
    transition: all 0.6s ease-in-out;
}

    /* ปรับแต่ง Scrollbar ให้ดูเรียบที่สุด */
  /* เมื่อเอาเมาส์ไปวางที่แถบเลื่อน ให้สีเข้มขึ้นนิดนึงเพื่อให้รู้ว่ากำลังเลื่อนอยู่ */
::-webkit-scrollbar-thumb:hover {
    background: #D4AF37 !important; /* เปลี่ยนเป็นสีทองจางๆ เมื่อใช้งาน */
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
