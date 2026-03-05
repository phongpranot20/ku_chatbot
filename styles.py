import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&family=Sarabun:wght@300;400;600&display=swap');

    /* 1. พื้นหลังหลักแบบ Dynamic Gradient (มินิมอลแต่ไม่เรียบเกินไป) */
    .stApp {
        background: radial-gradient(circle at top right, #e8f5e9, #ffffff, #f1f8e9) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* 2. Sidebar แบบกระจกฝ้า (Ultra Glass) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(20px) saturate(150%);
        border-right: 1px solid rgba(0, 102, 51, 0.05);
    }

    /* 3. หัวชื่อมหาวิทยาลัยพร้อม Floating Animation */
    .univ-container {
        animation: floating 3s ease-in-out infinite;
        text-align: center;
        padding: 15px 0;
    }

    @keyframes floating {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .univ-name {
        background: linear-gradient(90deg, #006633, #b5a01e, #006633);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 600;
        animation: shineText 4s linear infinite;
    }

    @keyframes shineText {
        to { background-position: 200% center; }
    }

    /* 4. ปุ่มกดแบบ Shine Effect (ลูกเล่นแสงวิ่ง) */
    div.stButton > button {
        background: white !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        border-radius: 18px !important;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        width: 100%;
        position: relative;
        overflow: hidden; /* เพื่อให้แสงไม่หลุดขอบ */
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    }

    /* เอฟเฟกต์แสงวิ่งผ่านปุ่ม */
    div.stButton > button::after {
        content: "";
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: linear-gradient(to bottom right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.4) 50%, rgba(255,255,255,0) 100%);
        transform: rotate(45deg);
        transition: 0.6s;
    }

    div.stButton > button:hover {
        transform: scale(1.05) translateY(-2px);
        background: #006633 !important;
        color: white !important;
        box-shadow: 0 10px 20px rgba(0, 102, 51, 0.2) !important;
    }

    div.stButton > button:hover::after {
        left: 100%;
    }

    /* 5. กล่องแชท (Chat Bubbles) แบบนุ่มนวล */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04) !important;
        padding: 20px !important;
        margin-bottom: 15px !important;
        transition: all 0.3s ease;
    }

    .stChatMessage:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
        transform: translateX(5px);
    }

    /* 6. Input Bar (ช่องพิมพ์) */
    [data-testid="stChatInput"] {
        border-radius: 25px !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        background-color: white !important;
        padding: 5px 15px !important;
        box-shadow: 0 -5px 25px rgba(0,0,0,0.03) !important;
    }

    /* 7. ปรับแต่ง Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 102, 51, 0.1);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #006633; }

    /* ซ่อน Streamlit branding */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ฟังก์ชันจัดการรูปภาพ (เหมือนเดิม)
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# พจนานุกรมภาษา
translation = {
    "TH": {
        "univ_name": "Kasetsart Sriracha",
        "new_chat": "➕ เริ่มบทสนทนาใหม่",
        "chat_hist": "💬 ประวัติการแชท",
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 แบบฟอร์มนิสิต",
        "input_placeholder": "คุยกับพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต!",
        "ai_identity": "พี่นนทรี AI รุ่นพี่ มก.ศรช. พร้อมช่วยแนะนำครับ"
    },
    "EN": {
        "univ_name": "Kasetsart Sriracha",
        "new_chat": "➕ New Chat",
        "chat_hist": "💬 Chat History",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Forms",
        "input_placeholder": "Ask Nontri...",
        "welcome": "Hello Student!",
        "ai_identity": "I'm Nontri AI, your KU Sriracha Senior Buddy."
    }
}

def main():
    apply_custom_css()
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown('<div class="univ-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="univ-name">{translation["TH"]["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        lang = st.radio("Select Language", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("---")
        # ปุ่ม Quick Links จัดเต็มลูกเล่น Shine
        st.button(t["new_chat"])
        st.markdown("### 🎓 Student Tools")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU Smart Assistant v2.0")

    # --- Main Chat ---
    with st.chat_message("assistant"):
        st.write(f"**{t['welcome']}** {t['ai_identity']}")

    # ช่องรับ Input
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
