import streamlit as st
import google.generativeai as genai
import os
import base64
import re

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

# --- 3. ฟังก์ชันวิเคราะห์ห้องเรียน (แบบธรรมชาติ) ---
def get_room_info(room_code):
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5: # เช่น 17203
        building = code[:2]
        floor = code[2]
        room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง"
    elif len(code) == 4: # เช่น 1404
        building = code[0]
        floor = code[1]
        room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม"
    return None

# --- 4. CSS ปรับแต่ง UI ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #006861 !important; }
    [data-testid="stSidebarContent"] { padding-top: 0rem !important; }

    .custom-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 5px 5px 15px 5px; 
        margin-top: -35px;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img { width: 90px; height: auto; margin-bottom: 10px; }
    .univ-name { color: white !important; font-size: 22px; font-weight: bold; line-height: 1.2; }
    .sidebar-title { color: #FFFFFF !important; font-size: 1.1rem; font-weight: bold; margin: 15px 0px 10px 0px; text-align: center; }

    div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 12px !important; margin-bottom: 10px; }
    div[data-testid="stExpander"] p { color: #000000 !important; font-weight: bold !important; }
    .white-card-content { background-color: #FFFFFF; border-radius: 0px 0px 12px 12px; }
    .form-row { display: flex; justify-content: space-between; align-items: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; }
    .form-row:last-child { border-bottom: none; }
    .form-label { color: #333333 !important; font-size: 12px; font-weight: 600; flex: 1; }
    .btn-action { background-color: #006861; color: white !important; padding: 4px 10px; border-radius: 6px; text-decoration: none; font-size: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 5. ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    # ปรับ System Instruction ให้ AI ตอบแบบธรรมชาติและเป็นกันเอง
    instruction = "คุณคือ 'พี่นนทรี' รุ่นพี่ใจดีแห่ง มก.ศรช. ตอบคำถามน้องๆ นิสิตด้วยความสุภาพ เป็นกันเอง และใช้ภาษาที่เป็นธรรมชาติเหมือนรุ่นพี่คุยกับรุ่นน้อง"
    return genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)
model = load_model()

# --- 6. ส่วน Sidebar (Dashboard) ---
with st.sidebar:
    if os.path.exists("logo_ku.png"):
        img_b64 = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_b64}" class="header-logo-img"><div class="univ-name">มหาวิทยาลัย<br>เกษตรศาสตร์</div></div>', unsafe_allow_html=True)
    
    st.markdown('<p class="sidebar-title">🎓 AI KUSRC Dashboard</p>', unsafe_allow_html=True)

    # เมนูคำนวณเกรด (GPA)
    with st.expander("🧮 คำนวณเกรด (GPA)", expanded=False):
        st.markdown(f"""
            <div class="white-card-content">
                <div class="form-row">
                    <div class="form-label">ระบบจำลองการตัดเกรด</div>
                    <a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">เปิดระบบ</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # รายการแบบฟอร์มด่วน
    with st.expander("📄 ลิงก์แบบฟอร์มต่างๆ", expanded=False):
        forms = [
            ("ขอลงทะเบียนเรียน", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("คำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("เพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        st.markdown('<div class="white-card-content">', unsafe_allow_html=True)
        for name, link in forms:
            st.markdown(f'<div class="form-row"><div class="form-label">{name}</div><a href="{link}" target="_blank" class="btn-action">โหลด</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("## 🐯 AI KUSRC")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🐯"):
        st.markdown(message["content"])

if prompt := st.chat_input("ถามพี่นนทรีได้เลย..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        # เช็คว่าเป็นตัวเลขห้องเพียวๆ หรือไม่
        room_info = get_room_info(prompt)
        
        if room_info:
            ans = room_info
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        else:
            placeholder = st.empty()
            placeholder.markdown("*(พี่กำลังคิดคำตอบให้นะ...)*")
            try:
                # โหลดฐานข้อมูล (ถ้ามี)
                knowledge = ""
                if os.path.exists("ku_data.txt"):
                    with open("ku_data.txt", "r", encoding="utf-8") as f:
                        knowledge = f.read()
                
                full_ctx = f"ข้อมูลมหาลัย: {knowledge}\nคำถามน้อง: {prompt}"
                response = model.generate_content(full_ctx)
                placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
