import streamlit as st
import base64
import os

# --- ส่วนที่ 1: การตกแต่ง (Mix CSS จาก HTML.txt มาไว้ที่นี่) ---
def apply_custom_css():
    st.markdown("""
    <style>
    /* 1. นำเข้า Fonts ระดับพรีเมียม */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* 2. พื้นหลังแบบ Nebula + Glassmorphism (จากไฟล์ HTML ของคุณ) */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #fdfdfd 0%, #e8f0eb 100%) !important;
        font-family: 'Sarabun', sans-serif !important;
    }

    /* 3. Sidebar ตกแต่งแบบ iOS Style */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(25px) saturate(150%);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
    }

    /* 4. ลูกเล่นชื่อมหาวิทยาลัย (Shine & Float) */
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

    @keyframes shineText { to { background-position: 200% center; } }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

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
    }

    div.stButton > button:hover {
        transform: translateY(-5px) scale(1.03) !important;
        background: linear-gradient(135deg, #006633 0%, #004d26 100%) !important;
        color: #E2C792 !important;
        box-shadow: 0 15px 30px rgba(0, 102, 51, 0.2) !important;
    }

    /* 6. กล่องแชท (Chat Bubbles) */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 18px !important;
    }

    /* ซ่อนส่วนเกินของ Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- ส่วนที่ 2: ข้อมูลภาษา (ย้ายมาจาก styles.py เดิม) ---
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

# --- ส่วนที่ 3: โครงสร้าง Python หลัก ---
def main():
    apply_custom_css()
    
    # ระบบเลือกภาษา
    if 'lang' not in st.session_state:
        st.session_state.lang = "TH"

    with st.sidebar:
        st.markdown(f'<div class="univ-name">{translation[st.session_state.lang]["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; color:#666; font-size:11px; margin-top:-10px; letter-spacing:2px;">{translation[st.session_state.lang]["campus"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        if col1.button("TH"): st.session_state.lang = "TH"
        if col2.button("EN"): st.session_state.lang = "EN"
        
        t = translation[st.session_state.lang]
        
        st.markdown("---")
        st.button(t["new_chat"])
        st.markdown("#### 🎓 บริการนิสิต")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU SRC Buddy Assistant v2.0")

    # ส่วนการแชท
    st.markdown(f'<h3 style="color:#006633; font-family:Fredoka;">KU SRC Smart Buddy</h3>', unsafe_allow_html=True)
    
    # ระบบความจำเบื้องต้น
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": f"**{t['welcome']}** {t['ai_identity']}"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input(t["input_placeholder"]):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # ส่วนโต้ตอบ (สามารถนำไปเชื่อมต่อ AI จริงได้ที่นี่)
        response = f"สวัสดีครับนิสิต ผมได้รับเรื่อง '{prompt}' เรียบร้อยแล้ว มีอะไรให้ช่วยอีกไหมครับ?"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)

if __name__ == "__main__":
    main()
