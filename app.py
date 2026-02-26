import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- 2. CSS จัดการหน้าตาและสีตัวหนังสือ (Force Black Text) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar Layout */
    [data-testid="stSidebar"] { background-color: #00594C !important; }
    
    /* หัวข้อ Dashboard */
    .sidebar-header {
        color: white !important;
        font-size: 20px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    /* กล่องสีขาวสำหรับรายการแบบฟอร์ม */
    .white-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #ddd;
    }

    /* บังคับสีตัวหนังสือใน Sidebar ให้เป็นสีดำในส่วนที่ต้องการ */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #000000 !important;
        font-weight: 500;
    }

    /* ปรับแต่ง Expander */
    .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }

    /* สไตล์ปุ่มดาวน์โหลด */
    .stButton>button {
        background-color: #00594C !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        border: none;
        font-weight: bold;
    }
    
    /* Chat UI */
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
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
    return genai.GenerativeModel(model_name=selected)

model = load_model()

# --- 4. ส่วน Sidebar: Dashboard & Logo ---
with st.sidebar:
    # แสดงโลโก้จากไฟล์ในเครื่อง
    if os.path.exists("logo_ku.png"):
        st.image("logo_ku.png", use_container_width=True)
    else:
        st.write("🚩 [ไม่พบไฟล์ logo_ku.png]")

    st.markdown('<p class="sidebar-header">🎓 น้องนนทรี Student Dashboard</p>', unsafe_allow_html=True)

    # รายการแบบฟอร์มด่วนในกล่องสีขาว
    with st.expander("📂 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown("---")
        
        # รายการที่ 1
        st.markdown("**📝 คำร้องขอลงทะเบียน (Registrar-2)**")
        st.link_button("📥 ดาวน์โหลด", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf")
        
        st.markdown("---")
        
        # รายการที่ 2
        st.markdown("**📑 คำร้องทั่วไป (Registrar-1)**")
        st.link_button("📥 ดาวน์โหลด", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")
        
        st.markdown("---")
        
        # รายการที่ 3
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

st.markdown("## 🐯 น้องนนทรี: เพื่อนคู่คิด นิสิต มก.ศรช.")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาคำตอบให้...)*")
        
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
