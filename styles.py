import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    /* นำเข้า Font ที่ดูสะอาดตาและทันสมัย */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&family=Sarabun:wght@300;400;600&display=swap');

    /* พื้นหลังแบบไล่เฉดสีอ่อนๆ ให้ดูสบายตา (Minimal Grainy Gradient) */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4ece9 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* --- Sidebar แต่งแบบ Glassmorphism --- */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* --- ลูกเล่นชื่อมหาวิทยาลัยแบบ Animated Gradient --- */
    .univ-name {
        background: linear-gradient(-45deg, #006633, #2e7d32, #b5a01e, #006633);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 26px;
        font-weight: 600;
        text-align: center;
        padding: 10px 0;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* --- ปุ่มกด (Buttons) เพิ่มลูกเล่น Hover ให้เด้งและเงาฟุ้ง --- */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(0, 102, 51, 0.15) !important;
        border-radius: 16px !important;
        color: #006633 !important;
        font-weight: 500 !important;
        padding: 12px 20px !important;
        width: 100%;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
    }

    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        background: #006633 !important;
        color: white !important;
        box-shadow: 0 10px 20px rgba(0, 102, 51, 0.15) !important;
        border: none !important;
    }

    /* --- กล่องแชท (Chat Bubbles) สไตล์ Neumorphism ผสม Glass --- */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(10px);
        border-radius: 22px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.02), -8px -8px 16px rgba(255, 255, 255, 0.5) !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
    }

    /* --- ช่องพิมพ์ข้อความ (Input) --- */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 1px solid rgba(0, 102, 51, 0.2) !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
    }

    /* ซ่อน Header รกๆ เพื่อความ Minimal */
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

translation = {
    "TH": {
        "univ_name": "Kasetsart Sriracha",
        "new_chat": "➕ เริ่มแชทใหม่",
        "exam_table": "📅 ตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด",
        "forms": "📄 แบบฟอร์มนิสิต",
        "input_placeholder": "คุยกับพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต!",
        "ai_identity": "พี่นนทรี AI (KU Sriracha Senior) ยินดีช่วยเหลือครับ"
    },
    "EN": {
        "univ_name": "Kasetsart Sriracha",
        "new_chat": "➕ New Chat",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Forms",
        "input_placeholder": "Ask Nontri...",
        "welcome": "Hello Student!",
        "ai_identity": "I'm Nontri AI, your friendly KU Sriracha senior."
    }
}

def main():
    apply_custom_css()
    
    # เลือกภาษาผ่าน Sidebar
    with st.sidebar:
        st.markdown(f'<div class="univ-name">{translation["TH"]["univ_name"]}</div>', unsafe_allow_html=True)
        lang = st.radio("Language / ภาษา", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("---")
        # ปุ่ม Quick Links พร้อมลูกเล่นใหม่
        st.button(t["new_chat"])
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU SRC Smart Buddy v1.0")

    # ส่วนแสดงหน้าจอแชท
    with st.chat_message("assistant"):
        st.write(f"**{t['welcome']}** {t['ai_identity']}")

    # รับ Input
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
