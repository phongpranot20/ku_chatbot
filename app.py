import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# --- 3. CSS ปรับแต่ง UI ให้เป๊ะตามเรฟเฟอเรนซ์ ---
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

    /* จัดการ Header: โลโก้อยู่บน ชื่อมหาลัยอยู่ล่าง */
    .custom-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 5px 5px 15px 5px; 
        margin-top: -35px; /* ขยับขึ้นชิดขอบบน */
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

    /* --- ส่วน Expander สีขาว --- */
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
        padding: 5px;
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
        text-align: left;
    }

    /* ปุ่ม Action สีเขียวเข้ม */
    .btn-action {
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

    /* หัวข้อหน้า Chat */
    h2 { color: #006861 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. ส่วนจัดการ API และ AI Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API KEY ใน Secrets")
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
    img_b64 = get_image_base64("logo_ku.png")
    if img_b64:
        st.markdown(f"""
            <div class="custom-header">
                <img src="data:image/png;base64,{img_b64}" class="header-logo-img">
                <div class="header-text">
                    <div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-title">🎓 AI KUSRC Dashboard</p>', unsafe_allow_html=True)

    # 2. รายการแบบฟอร์มด่วน (ปิดไว้ตอนเริ่มต้น expanded=False)
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ", expanded=False):
        forms = [
            ("ขอลงทะเบียนเรียน (Registrar-2)", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("คำร้องทั่วไป (Registrar-1)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ผ่อนผันค่าเทอม (Registrar-3)", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา (Registrar-10)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก (Registrar-16)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ลงทะเบียนเรียน (KU1)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("เพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        st.markdown('<div class="white-card-content">', unsafe_allow_html=True)
        for name, link in forms:
            st.markdown(f"""
                <div class="form-row">
                    <div class="form-label">{name}</div>
                    <a href="{link}" target="_blank" class="btn-action">ดาวน์โหลด</a>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. พิกัดตึกเรียนสำคัญ (ฟีเจอร์แนะนำเพิ่ม)
    with st.expander("📍 พิกัดตึกเรียนสำคัญ", expanded=False):
        places = [
            ("อาคาร 10 (ศร.2)", "https://maps.app.goo.gl/xxx"),
            ("อาคาร 17 (ศร.3)", "https://maps.app.goo.gl/xxx"),
            ("โรงอาหารกลาง", "https://maps.app.goo.gl/xxx")
        ]
        st.markdown('<div class="white-card-content">', unsafe_allow_html=True)
        for name, link in places:
            st.markdown(f"""
                <div class="form-row">
                    <div class="form-label">{name}</div>
                    <a href="{link}" target="_blank" class="btn-action">นำทาง</a>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("💡 พิมพ์ถามพี่นนทรีได้ทุกเรื่องเลยนะ!")

# --- 6. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

st.markdown("## 🐯 AI KUSRC: เพื่อนคู่คิด นิสิต มก.ศรช.")

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ส่วนรับข้อความจากผู้ใช้
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาคำตอบให้...)*")
        
        # ดึงประวัติการคุยย้อนหลัง 5 ข้อความ
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                   for m in st.session_state.messages[-6:-1]]
        
        try:
            chat_session = model.start_chat(history=history)
            full_context = f"คุณคือรุ่นพี่ มก.ศรช. ตอบน้องด้วยความเป็นกันเอง\nข้อมูลอ้างอิง:\n{knowledge_base}\n\nคำถาม: {prompt}"
            
            response = chat_session.send_message(full_context, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
