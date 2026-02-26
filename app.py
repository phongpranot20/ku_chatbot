import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. CSS ปรับแต่ง Contrast และขนาดโลโก้ ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar Layout */
    [data-testid="stSidebar"] { 
        background-color: #00594C !important; 
    }
    
    /* ปรับแต่งรูปโลโก้ให้เล็กลงและอยู่กึ่งกลาง */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 10px 0px;
    }
    .logo-img {
        max-width: 180px; /* ปรับขนาดความกว้างของโลโก้ที่นี่ */
        height: auto;
    }
    
    /* หัวข้อ Dashboard - ปรับสีให้ขาวชัดเจน (High Contrast) */
    .sidebar-header {
        color: #FFFFFF !important; 
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* กล่องสีขาวสำหรับรายการแบบฟอร์ม */
    .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }

    /* บังคับสีตัวหนังสือใน Widget Sidebar ให้เป็นสีดำเข้มเพื่อให้อ่านง่ายบนพื้นขาว */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    /* ข้อความแจ้งเตือนด้านล่าง Sidebar (สีขาวเพื่อให้เห็นบนพื้นเขียว) */
    .stSidebar .stCaption p {
        color: #E0E0E0 !important;
    }

    /* ปุ่มดาวน์โหลด */
    .stButton>button {
        background-color: #00594C !important;
        color: #FFFFFF !important;
        border-radius: 8px;
        width: 100%;
        border: 2px solid #FFFFFF;
        font-weight: bold;
    }
    
    /* Chat UI หน้าหลัก */
    h2 { color: #00594C !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ใน Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None

model = load_model()

# --- 4. ส่วน Sidebar: Logo & Dashboard ---
with st.sidebar:
    # แสดงโลโก้พร้อมจัดขนาด
    if os.path.exists("logo_ku.png"):
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{st.image("logo_ku.png").data}" class="logo-img"></div>', unsafe_allow_html=True)
        # หมายเหตุ: ถ้าใช้ st.image ปกติแล้วภาพยังใหญ่ ให้ใช้คำสั่งด้างล่างแทน
        st.image("logo_ku.png", width=180) 
    else:
        st.warning("ไม่พบไฟล์ logo_ku.png")

    st.markdown('<p class="sidebar-header">🎓 AI KUSRC Student Dashboard</p>', unsafe_allow_html=True)

    # รายการแบบฟอร์มด่วน
    with st.expander("📂 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown("**📝 คำร้องขอลงทะเบียน (Registrar-2)**")
        st.link_button("📥 ดาวน์โหลด", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf")
        
        st.markdown("---")
        
        st.markdown("**📑 คำร้องทั่วไป (Registrar-1)**")
        st.link_button("📥 ดาวน์โหลด", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")
        
        st.markdown("---")
        
        st.markdown("**💻 เพิ่ม-ถอน (KU3) ออนไลน์**")
        st.link_button("🌐 ไปที่เว็บไซต์", "https://reg2.src.ku.ac.th/download.html")

    st.markdown("---")
    st.caption("💚 พัฒนาโดยนิสิตเพื่อนิสิต มก.ศรช.")

# --- 5. การจัดการหน้า Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# เปลี่ยนชื่อหัวข้อเป็น AI KUSRC
st.markdown("## 🐯 AI KUSRC")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาข้อมูลให้...)*")
        
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                   for m in st.session_state.messages[-6:-1]]
        
        try:
            chat_session = model.start_chat(history=history)
            full_context = f"คุณคือรุ่นพี่ มก.ศรช. ตอบน้องด้วยความเป็นกันเอง\nข้อมูล:\n{knowledge_base}\n\nคำถาม: {prompt}"
            
            response = chat_session.send_message(full_context, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
