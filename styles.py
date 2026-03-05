import streamlit as st
import base64
import os

def apply_custom_css():
    # นำ CSS จาก html.txt และ CSS เดิมมา Mix กัน
    st.markdown("""
    <style>
    /* 1. นำเข้า Fonts จากทั้งสองแหล่ง */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Nunito:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* 2. พื้นหลังแบบ Nebula Effect (จาก html.txt) และ Glassmorphism */
    .stApp {
        background: radial-gradient(circle at bottom center, #121c30, #080c1c) !important;
        font-family: 'Sarabun', 'Nunito', sans-serif !important;
        color: #f5faff !important;
    }

    /* สร้างลูกเล่น Nebula Blobs ด้วย CSS */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: 
            radial-gradient(circle at 10% 10%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 90% 90%, rgba(236, 72, 153, 0.15) 0%, transparent 50%);
        z-index: -1;
    }

    /* 3. Sidebar ตกแต่งแบบ iOS Glass (จากโค้ดเดิม) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 4. ชื่อมหาวิทยาลัย: Shine & Float Effect */
    .univ-name {
        background: linear-gradient(90deg, #00ffcc, #f472b6, #00ffcc);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 26px;
        font-weight: 700;
        text-align: center;
        animation: shineText 3s linear infinite, float 4s ease-in-out infinite;
    }

    @keyframes shineText { to { background-position: 200% center; } }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }

    /* 5. ปุ่มกด: Neo-Brutalism + Cyber Neon (Mix ระหว่าง 2 โค้ด) */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #f5faff !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px);
    }
    div.stButton > button:hover {
        transform: translateY(-3px) !important;
        background: linear-gradient(135deg, #06b6d4 0%, #ec4899 100%) !important;
        box-shadow: 0 10px 20px rgba(6, 182, 212, 0.3) !important;
        color: white !important;
    }

    /* 6. กล่องแชท: Floating Card Style */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 15px !important;
    }

    /* 7. Input Bar: Glow Effect */
    [data-testid="stChatInput"] {
        border-radius: 25px !important;
        border: 1px solid rgba(6, 182, 212, 0.3) !important;
        background: rgba(8, 12, 28, 0.8) !important;
        color: white !important;
    }

    /* ซ่อน Streamlit Elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- โครงสร้าง Python เดิมของคุณ ---
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
        # ใช้ลูกเล่น Univ-name จาก CSS ด้านบน
        st.markdown(f'<div class="univ-name">{translation["TH"]["univ_name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; color:#8291aa; font-size:11px; margin-top:-10px; letter-spacing:2px;">{translation["TH"]["campus"]}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        lang = st.radio("Language", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("---")
        st.button(t["new_chat"])
        st.markdown("#### 🎓 บริการนิสิต")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.caption("KU SRC Buddy Assistant v2.0")

    # หน้าจอแชทหลัก (ปรับสีให้เข้ากับ Theme ใหม่)
    st.markdown(f'<h3 style="color:#00ffcc; font-family:Fredoka; text-shadow: 0 0 10px rgba(0,255,204,0.3);">KU SRC Smart Buddy</h3>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write(f"**{t['welcome']}** {t['ai_identity']}")

    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
