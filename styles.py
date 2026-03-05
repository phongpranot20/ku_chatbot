import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600&family=Fredoka:wght@400;600&display=swap');

    /* พื้นหลังหลัก: เน้นความคลีนแบบ Minimal แต่มีมิติ */
    .stApp {
        background: linear-gradient(135deg, #fdfdfd 0%, #f0f4f2 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* Sidebar แบบกระจกฝ้า (Glassmorphism) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* หัวข้อภาษาไทยและอังกฤษ */
    .univ-name {
        font-family: 'Fredoka', 'Sarabun', sans-serif;
        font-weight: 700;
        color: #006633; /* สีเขียวนนทรี */
        font-size: 26px;
        margin-bottom: 5px;
        letter-spacing: -0.5px;
    }

    .sub-title {
        color: #E2C792; /* สีทอง */
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    /* กล่องข้อความแชท: มนเป็นพิเศษและดูเบาตัว */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 24px !important;
        border: 1px solid rgba(0, 102, 51, 0.05) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
        padding: 18px !important;
        transition: all 0.3s ease;
    }
    
    .stChatMessage:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 102, 51, 0.05) !important;
    }

    /* ปุ่มกด: เพิ่มลูกเล่น (Interactive Minimal) */
    div.stButton > button {
        background-color: #ffffff !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        border-radius: 14px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100%;
        text-align: left !important;
    }

    div.stButton > button:hover {
        background-color: #006633 !important; /* เปลี่ยนเป็นสีเขียวเมื่อเลือก */
        color: #ffffff !important;
        border-color: #006633 !important;
        transform: scale(1.03);
        box-shadow: 0 8px 15px rgba(0, 102, 51, 0.15) !important;
    }

    /* ช่อง Input ด้านล่าง */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        background-color: white !important;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.03) !important;
    }

    /* แถบเลื่อน (Scrollbar) ให้เล็กลงแบบมินิมอล */
    ::-webkit-scrollbar {
        width: 5px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 102, 51, 0.2);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

translation = {
    "TH": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ เริ่มบทสนทนาใหม่",
        "exam_table": "📅 เช็คตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรดเฉลี่ย",
        "forms": "📄 ดาวน์โหลดแบบฟอร์ม",
        "input_placeholder": "ถามอะไรพี่นนทรีดีครับ...",
        "welcome": "สวัสดีครับนิสิต",
        "ai_identity": "พี่เป็น AI รุ่นพี่ มก.ศรช. ยินดีที่ได้รู้จักครับ!"
    },
    "EN": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ New Conversation",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Document Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello Student",
        "ai_identity": "I'm your KU Sriracha AI Senior. Nice to meet you!"
    }
}

def main():
    apply_custom_css()
    
    # ส่วนของ Sidebar
    with st.sidebar:
        st.markdown(f'<div class="univ-name">{translation["TH"]["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub-title">{translation["TH"]["campus"]}</div>', unsafe_allow_html=True)
        
        lang = st.radio("Language", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("---")
        st.button(t["new_chat"])
        st.markdown("### Quick Links")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])

    # หน้าจอแชทหลัก
    st.markdown(f'<div class="univ-name">KU SRC Buddy</div>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write(f"{t['welcome']}! {t['ai_identity']}")

    # รับ Input
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
