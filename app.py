import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS ปรับแต่ง UI (ขยับชิดบน + แก้สี Expander) ---
st.markdown("""
<style>
    /* พื้นหลังหน้าหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar: สีเขียวหัวเป็ด */
    [data-testid="stSidebar"] { 
        background-color: #006861 !important; 
    }

    /* ขยับส่วน Sidebar Content ให้ชิดขอบบนสุด */
    [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
    }

    /* จัดการ Header: โลโก้อยู่บน ชื่อมหาลัยอยู่ล่าง (ขยับขึ้นชิดบน) */
    .custom-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 5px 5px 15px 5px; 
        margin-top: -35px; /* ขยับขึ้นชิดขอบ */
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img {
        width: 90px;
        height: auto;
        margin-bottom: 10px;
    }
    .header-text {
        color: white !important;
        font-family: 'Tahoma', sans-serif;
    }
    .univ-name { 
        font-size: 22px;
        font-weight: bold;
        line-height: 1.2;
    }

    /* หัวข้อ Dashboard */
    .sidebar-title {
        color: #FFFFFF !important;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 15px 0px 10px 0px;
        text-align: center;
    }

    /* --- แก้ไข Expander ให้เป็นสีขาวตลอดเวลา (ตัวหนังสือดำชัดเจน) --- */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        margin-bottom: 10px;
    }
    
    /* บังคับสีฟอนต์หัวข้อ Expander ให้เป็นสีดำ */
    div[data-testid="stExpander"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* กล่องขาวรายการแบบฟอร์มด้านใน */
    .white-card-content {
        background-color: #FFFFFF;
        border-radius: 0px 0px 12px 12px;
    }
    
    .form-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 8px;
        border-bottom: 1px solid #f0f0f0;
    }
    .form-row:last-child { border-bottom: none; }
    
    .form-label {
        color: #333333 !important;
        font-size: 12px;
        font-weight: 600;
        flex: 1;
        line-height: 1.3;
    }

    /* ปุ่มดาวน์โหลดสีเขียวเข้ม */
    .btn-download {
        background-color: #006861;
        color: white !important;
        padding: 4px 10px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 10px;
        font-weight: bold;
        white-space: nowrap;
        margin-left: 5px;
    }

    /* บังคับสีตัวอักษร Caption ด้านล่างให้เป็นสีขาว */
    .stSidebar .stCaption p {
        color: #FFFFFF !important;
    }

    /* หน้า Chat */
    h2 { color: #006861 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API KEY")
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

# --- 5. ส่วน Sidebar (Dashboard) ---
with st.sidebar:
    # 1. Header (โลโก้บน-ชื่อล่าง)
    if os.path.exists("logo_ku.png"):
        img_data = get_image_base64("logo_ku.png")
        st.markdown(f"""
            <div class="custom-header">
                <img src="data:image/png;base64,{img_data}" class="header-logo-img">
                <div class="header-text">
                    <div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-title">AI KUSRC Dashboard</p>', unsafe_allow_html=True)

    # 2. รายการแบบฟอร์มด่วน (จัดเต็มตามข้อมูลใหม่)
    with st.expander("📄 ลิ้งรายการแบบฟอร์มต่างๆ ", expanded=True):
        st.markdown(f"""
            <div class="white-card-content">
                <div class="form-row">
                    <div class="form-label">ขอลงทะเบียนเรียน</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">คำร้องทั่วไป</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ผ่อนผันค่าเทอม</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ใบลาพักการศึกษา</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ใบลาออก</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ลงทะเบียนเรียน</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">เพิ่ม-ถอน</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
  

# --- 6. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base สำหรับ AI
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

st.markdown("## 🦖 AI TEST")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาคำตอบให้...)*")
        
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                   for m in st.session_state.messages[-6:-1]]
        
        try:
            chat_session = model.start_chat(history=history)
            full_context = f"คุณคือรุ่นพี่ มก.ศรช. ตอบน้องเป็นกันเอง\nข้อมูล:\n{knowledge_base}\n\nคำถาม: {prompt}"
            
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
