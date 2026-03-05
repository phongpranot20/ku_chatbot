import streamlit as st
import base64
import os

def apply_custom_css():
    st.markdown("""
    <style>
    /* 1. นำเข้า Fonts ทั้งหมดจากไฟล์เพิ่มเติม */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Nunito:wght@400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    /* 2. พื้นหลังแบบ Dynamic Gradient มก.ศรช. */
    .stApp {
        background: linear-gradient(125deg, #f0f7f4 0%, #e2e8e5 50%, #d5e0d8 100%) !important;
        font-family: 'Nunito', 'Sarabun', sans-serif !important;
    }

    /* 3. Sidebar แบบ Ultra-Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(25px) saturate(180%);
        border-right: 1px solid rgba(0, 102, 51, 0.1);
        box-shadow: 10px 0 30px rgba(0,0,0,0.05);
    }

    /* 4. หัวข้อชื่อมหาวิทยาลัยพร้อมเอฟเฟกต์ Shine */
    .univ-container {
        padding: 20px 0;
        text-align: center;
    }
    .univ-name {
        background: linear-gradient(90deg, #006633, #00ab55, #006633);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 28px;
        font-weight: 700;
        animation: shine 3s linear infinite;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* 5. กล่องแชทแบบมีเงาฟุ้ง (Soft Glow) */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 25px 25px 25px 5px !important;
        border: 1px solid rgba(0, 102, 51, 0.1) !important;
        box-shadow: 0 10px 25px rgba(0, 102, 51, 0.05) !important;
        margin-bottom: 20px !important;
        transition: transform 0.3s ease;
    }
    .stChatMessage:hover {
        transform: scale(1.01);
        box-shadow: 0 15px 35px rgba(0, 102, 51, 0.1) !important;
    }

    /* 6. ปุ่มกดแบบ Interactive (ลูกเล่นจัดเต็ม) */
    div.stButton > button {
        width: 100%;
        background: white !important;
        color: #006633 !important;
        border: 1px solid rgba(0, 102, 51, 0.2) !important;
        border-radius: 18px !important;
        padding: 15px 25px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative;
        overflow: hidden;
    }

    /* เอฟเฟกต์เมื่อ Hover ปุ่ม (เปลี่ยนเป็นเขียวทอง) */
    div.stButton > button:hover {
        background: linear-gradient(135deg, #006633 0%, #004d26 100%) !important;
        color: #E2C792 !important; /* ตัวหนังสือสีทอง */
        transform: translateY(-5px) scale(1.05) !important;
        box-shadow: 0 12px 20px rgba(0, 102, 51, 0.2) !important;
        border: none !important;
    }

    /* 7. ช่อง Input ด้านล่างแบบลอย (Floating) */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 2px solid rgba(0, 102, 51, 0.1) !important;
        background: white !important;
        padding: 10px !important;
        box-shadow: 0 -10px 25px rgba(0,0,0,0.03) !important;
    }
    
    /* 8. การตกแต่งเพิ่มเติมให้ดูพรีเมียม */
    .stMarkdown p {
        line-height: 1.6;
    }
    
    /* สัญลักษณ์จุดสีเขียวนนทรีสำหรับสถานะ Online */
    .online-indicator {
        width: 10px;
        height: 10px;
        background: #00ab55;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 10px #00ab55;
    }

    /* ซ่อน Streamlit Elements ที่ไม่สวยงาม */
    header {visibility: hidden;}
    footer {visibility: hidden;}
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
        "exam_table": "📅 ค้นหาตารางสอบ",
        "gpa_calc": "🧮 คำนวณเกรดเฉลี่ย (GPA)",
        "forms": "📄 ดาวน์โหลดแบบฟอร์ม",
        "input_placeholder": "ถามอะไรพี่นนทรีได้เลย...",
        "welcome": "สวัสดีครับนิสิต",
        "ai_identity": "พี่เป็น AI รุ่นพี่ มก.ศรช. พร้อมช่วยแนะนำข้อมูลการเรียนแล้วครับ!"
    },
    "EN": {
        "univ_name": "Kasetsart University",
        "campus": "SRIRACHA CAMPUS",
        "new_chat": "➕ New Conversation",
        "exam_table": "📅 Exam Schedule",
        "gpa_calc": "🧮 GPA Calculator",
        "forms": "📄 Student Forms",
        "input_placeholder": "Ask Nontri anything...",
        "welcome": "Hello Student",
        "ai_identity": "I am your KU Sriracha AI Senior. How can I help you today?"
    }
}

def main():
    apply_custom_css()
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown('<div class="univ-container">', unsafe_allow_html=True)
        st.markdown(f'<p class="univ-name">{translation["TH"]["univ_name"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#666; font-size:12px; margin-top:-15px;">{translation["TH"]["campus"]}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        lang = st.radio("Select Language", ["TH", "EN"], horizontal=True)
        t = translation[lang]
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.button(t["new_chat"])
        
        st.markdown("### 🎓 บริการนิสิต")
        st.button(t["exam_table"])
        st.button(t["gpa_calc"])
        st.button(t["forms"])
        
        st.divider()
        st.markdown(f'<div style="text-align:center; font-size:12px; color:#888;"><span class="online-indicator"></span>ระบบออนไลน์ปกติ</div>', unsafe_allow_html=True)

    # --- Area การสนทนา ---
    st.markdown(f'<h2 style="color:#006633; font-family:Fredoka;">KU SRC Buddy</h2>', unsafe_allow_html=True)
    
    with st.chat_message("assistant"):
        st.write(f"**{t['welcome']}!** {t['ai_identity']}")

    # รับ Input จากนิสิต
    st.chat_input(t["input_placeholder"])

if __name__ == "__main__":
    main()
