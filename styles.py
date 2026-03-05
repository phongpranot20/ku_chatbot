import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    /* 1. นำเข้า Fonts ระดับพรีเมียมจากไฟล์เพิ่มเติม */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* 2. พื้นหลังแบบ Glassmorphism Gradient (นุ่มนวลแต่มีมิติ) */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #fdfdfd 0%, #e8f0eb 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* 3. Sidebar ตกแต่งแบบ Control Center (iOS Style) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(25px) saturate(150%);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* 4. ลูกเล่นชื่อมหาวิทยาลัย: เพิ่มเอฟเฟกต์ Shine และการขยับ */
    .univ-name {
        background: linear-gradient(90deg, #006633, #b5a01e, #006633);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        animation: shineText 3s linear infinite, float 4s ease-in-out infinite;
        padding: 10px 0;
    }

    @keyframes shineText {
        to { background-position: 200% center; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
    }

    /* 5. ปุ่มกด (Buttons) - ลูกเล่นจัดเต็มแบบ Neo-Brutalism + iOS */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.9) !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        border-radius: 18px !important;
        padding: 14px 20px !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
        position: relative;
        overflow: hidden;
    }

    /* เอฟเฟกต์ตอน Hover: ปุ่มจะขยาย, เปลี่ยนสีเป็นเขียวเข้ม และมีเงาสีทองฟุ้ง */
    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.03) !important;
        background: linear-gradient(135deg, #006633 0%, #004d26 100%) !important;
        color: #E2C792 !important; /* ตัวหนังสือสีทอง */
        box-shadow: 0 15px 30px rgba(0, 102, 51, 0.2) !important;
        border: none !important;
    }

    /* 6. กล่องแชท (Chat Bubbles) - ตกแต่งแบบลอยตัว (Floating Card) */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
        padding: 22px !important;
        margin-bottom: 18px !important;
        transition: all 0.3s ease;
    }
    .stChatMessage:hover {
        background: #ffffff !important;
        box-shadow: 0 15px 40px rgba(0, 102, 51, 0.08) !important;
        transform: scale(1.01);
    }

    /* 7. Input Bar (ช่องพิมพ์) - ดีไซน์โค้งมนพร้อมเงาแบบ Soft Glow */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 1px solid rgba(0, 102, 51, 0.15) !important;
        background: white !important;
        padding: 10px 20px !important;
        box-shadow: 0 -10px 25px rgba(0,0,0,0.02) !important;
    }

    /* ซ่อน Header และ Footer ของ Streamlit เพื่อความมินิมอลขั้นสุด */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ตกแต่ง Scrollbar ให้ดูแพง */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 102, 51, 0.2);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ฟังก์ชันจัดการรูปภาพ
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
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรด (GPA)",
        "forms": "📄 ดาวน์โหลดแบบฟอร์ม",
        "input_placeholder": "พิมพ์ถามพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต!",
        "ai_identity": "พี่นนทรี AI รุ่นพี่ มก.ศรช. ยินดีที่ได้พบคุณครับ"
    },
    "EN": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ New Conversation",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Student Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello Student!",
        "ai_identity": "I'm Nontri AI, your friendly KU Sriracha senior buddy."
    }
}

def main():
    apply_custom_css()
    
    with st.sidebar:
        # แสดงชื่อมหาวิทยาลัยพร้อมเอฟเฟกต์ Shine และ Float
        st.markdown(f'<div class="univ-name">{translation["TH"]["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; color:#666; font-size:11px; margin-top:-10px; letter-spacing:2px;">{translation["TH"]["campus"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        lang = st.radio("Language", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("---")
        # ปุ่ม Quick Links พร้อมลูกเล่น Bounce & Hover
        st.button(t["new_chat"])
        st.markdown("#### 🎓 บริการนิสิต")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU SRC Buddy Assistant v2.0")

    # หน้าจอแชทหลัก
    st.markdown(f'<h3 style="color:#006633; font-family:Fredoka;">KU SRC Smart Buddy</h3>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write(f"**{t['welcome']}** {t['ai_identity']}")

    # ช่องรับข้อมูล
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
