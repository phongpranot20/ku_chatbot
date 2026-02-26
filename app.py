import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. ฟังก์ชันวิเคราะห์เลขห้องเรียน (ตอบแบบธรรมชาติ) ---
def get_room_info(room_code):
    # ล้างค่าให้เหลือแต่ตัวเลข
    code = re.sub(r'\D', '', str(room_code))
    
    # กรณีเลข 5 หลัก เช่น 17203
    if len(code) == 5:
        building = code[:2]
        floor = code[2]
        room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง"
    
    # กรณีเลข 4 หลัก เช่น 1404
    elif len(code) == 4:
        building = code[0]
        floor = code[1]
        room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม"
    
    return None

# --- 4. CSS ปรับแต่ง UI ให้สวยงาม ---
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
        margin-top: -35px;
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

    /* Expander สีขาวสำหรับเมนูต่างๆ */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        margin-bottom: 10px;
    }
    
    div[data-testid="stExpander"] p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* กล่องขาวรายการด้านใน Sidebar */
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
        font-size: 11px;
        font-weight: 600;
        flex: 1;
        line-height: 1.3;
    }

    /* ปุ่ม Action สีเขียวเข้ม */
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

    /* หน้า Chat */
    h2 { color: #006861 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 5. ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None
model = load_model()

# --- 6. ส่วน Sidebar (Dashboard) ---
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

    # 2. ค้นหาตารางสอบ (แยกแถบ)
    with st.expander("📅 ค้นหาตารางสอบ", expanded=False):
        st.markdown(f"""
            <div class="white-card-content">
                <div class="form-row">
                    <div class="form-label">ตรวจสอบวัน-เวลาสอบ</div>
                    <a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-download">ค้นหา</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 3. คำนวณเกรด (GPA) (แยกแถบ)
    with st.expander("🧮 คำนวณเกรด (GPA)", expanded=False):
        st.markdown(f"""
            <div class="white-card-content">
                <div class="form-row">
                    <div class="form-label">ระบบจำลองการตัดเกรด</div>
                    <a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-download">เปิดระบบ</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # 4. รายการแบบฟอร์มด่วน (ครบ 7 รายการ)
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
                    <a href="{link}" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# --- 7. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลดฐานข้อมูล ku_data.txt
knowledge_base = ""
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()

st.markdown("## 🦖 AI TEST")

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# รับข้อความจากผู้ใช้
if prompt := st.chat_input("พิมพ์ถามพี่นนทรีได้เลย..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        # 1. เช็คว่าเป็นเลขห้องเรียนหรือไม่
        room_info = get_room_info(prompt)
        
        if room_info:
            st.markdown(room_info)
            st.session_state.messages.append({"role": "assistant", "content": room_info})
        else:
            # 2. ตอบผ่าน AI Model
            placeholder = st.empty()
            placeholder.markdown("*(พี่กำลังหาคำตอบให้...)*")
            try:
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                           for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                full_context = f"คุณคือรุ่นพี่ มก.ศรช. ตอบน้องเป็นกันเอง ข้อมูลมหาลัย:\n{knowledge_base}\n\nคำถาม: {prompt}"
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
