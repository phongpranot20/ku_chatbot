import streamlit as st
import base64

# --- 1. ส่วนการตกแต่ง (Mix HTML/CSS จากไฟล์ของคุณ) ---
def apply_custom_design():
    st.markdown("""
    <style>
    /* นำเข้า Font และพื้นหลัง Nebula จากไฟล์ HTML */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@300;400;600;700&family=Sarabun:wght@300;400;600;700&display=swap');

    .stApp {
        background: radial-gradient(circle at bottom center, #121c30, #080c1c) !important;
        background-attachment: fixed !important;
        color: #f5faff;
    }

    /* สร้าง Effect แสงสีชมพู-ฟ้า (Nebula) แบบในไฟล์ HTML */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(6, 182, 212, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(236, 72, 153, 0.15) 0%, transparent 40%);
        z-index: -1;
    }

    /* ตกแต่ง Sidebar แบบ Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* ชื่อมหาวิทยาลัยแบบมี Animation */
    .univ-name {
        background: linear-gradient(90deg, #00ffcc, #f472b6, #00ffcc);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Fredoka', sans-serif;
        font-size: 24px;
        font-weight: 700;
        text-align: center;
        animation: shine 3s linear infinite;
    }
    @keyframes shine { to { background-position: 200% center; } }

    /* ปุ่มกดสไตล์พรีเมียม */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #06b6d4, #ec4899) !important;
        transform: scale(1.02);
        border: none !important;
    }

    /* ช่อง Chat Input */
    [data-testid="stChatInput"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(6, 182, 212, 0.5) !important;
        border-radius: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ส่วนของ Logic (Python โครงเดิมของคุณ) ---
def main():
    apply_custom_design()
    
    # ตั้งค่าภาษา
    if 'lang' not in st.session_state:
        st.session_state.lang = "TH"

    with st.sidebar:
        st.markdown('<div class="univ-name">Kasetsart University</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center; color:#8291aa; font-size:10px;">SRIRACHA CAMPUS</div>', unsafe_allow_html=True)
        st.divider()
        
        col1, col2 = st.columns(2)
        if col1.button("ไทย"): st.session_state.lang = "TH"
        if col2.button("English"): st.session_state.lang = "EN"

    # ระบบจำข้อความ (Chat History)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # แสดงข้อความที่เคยคุยกัน
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ช่องรับข้อความ
    if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # จำลองการตอบกลับของ AI (ส่วนนี้คุณเอาไปเชื่อมต่อ API ได้)
        response = f"พี่นนทรีได้รับข้อความ: '{prompt}' แล้วครับ!"
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
