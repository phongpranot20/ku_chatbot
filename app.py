import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI ASSISTANT", page_icon="🦖", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS ปรับแต่ง (ขยับ Header ชิดบน + แก้สี Expander) ---
st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar: สีเขียวหัวเป็ด */
    [data-testid="stSidebar"] { 
        background-color: #006861 !important; 
    }

    /* ขยับส่วน Sidebar Content ทั้งหมดให้ชิดขอบบน */
    [data-testid="stSidebarContent"] {
        padding-top: 0rem !important;
    }

    /* จัดการ Header: โลโก้บน ชื่อมหาลัยล่าง (ขยับขึ้นชิดบน) */
    .custom-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 10px 5px 20px 5px; /* ลด Padding บนให้เหลือน้อยที่สุด */
        margin-top: -30px; /* ขยับขึ้นไปชิดขอบ */
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img {
        width: 100px;
        height: auto;
        margin-bottom: 10px;
    }
    .header-text {
        color: white !important;
        font-family: 'Tahoma', sans-serif;
    }
    .univ-name { 
        font-size: 24px;
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

    /* --- แก้ไข Expander ให้เป็นสีขาวตลอดเวลา (ไม่กลืนกับพื้นหลัง) --- */
    .st-emotion-cache-p5mtransition, div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* สีฟอนต์หัวข้อ Expander (ลิงก์แบบฟอร์มต่างๆ) */
    div[data-testid="stExpander"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* กล่องขาวรายการแบบฟอร์มด้านใน */
    .white-card-content {
        background-color: #FFFFFF;
        padding: 5px;
    }
    
    .form-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border-bottom: 1px solid #f0f0f0;
    }
    .form-row:last-child { border-bottom: none; }
    
    .form-label {
        color: #333333 !important;
        font-size: 13px;
        font-weight: 600;
        flex: 1;
    }

    /* ปุ่มดาวน์โหลดสีเขียวเข้ม */
    .btn-download {
        background-color: #006861;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 11px;
        font-weight: bold;
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
    # 1. Custom Header (ขยับชิดบนสุด)
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
    
    

    # 2. รายการแบบฟอร์มด่วน (แก้ปัญหาสีฟอนต์กลืนพื้นหลัง)
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ ", expanded=True):
        st.markdown(f"""
            <div class="white-card-content">
                <div class="form-row">
                    <div class="form-label">ใบคำร้องขอลงทะเบียนเรียน</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ใบคำร้องทั่วไป </div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ใบลาพักการศึกษา </div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">ใบ Add-Drop </div>
                    <a href="https://reg2.src.ku.ac.th/download.html" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ลบส่วน Caption พัฒนาโดยนิสิตออกเรียบร้อย

# --- 6. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

st.markdown("## 🦖 AI ASSISTANT")

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
