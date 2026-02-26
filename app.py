import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพ ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS ปรับแต่งสีและเลย์เอาต์ (High Contrast & Custom UI) ---
st.markdown("""
<style>
    /* พื้นหลังหน้าหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar: สีเขียวหัวเป็ดตามรูปเป้าหมาย */
    [data-testid="stSidebar"] { 
        background-color: #006861 !important; 
    }

    /* จัดการ Header Logo (คุมขนาดไม่ให้ใหญ่เกินไป) */
    .header-container {
        text-align: left;
        padding: 5px 0px;
        margin-bottom: 0px;
    }
    .header-img {
        width: 100%;
        max-width: 250px;
        height: auto;
    }

    /* หัวข้อ Dashboard สีขาว */
    .sidebar-title {
        color: #FFFFFF !important;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 15px 0px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* --- กล่องขาวรายการแบบฟอร์ม (White Card Style) --- */
    .white-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 8px;
        margin-top: 5px;
    }
    
    .form-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #eeeeee;
    }
    .form-row:last-child { border-bottom: none; }
    
    .form-label {
        color: #333333 !important; /* ตัวหนังสือในกล่องขาวต้องสีเข้ม */
        font-size: 13px;
        font-weight: bold;
        line-height: 1.3;
        flex: 1;
    }

    /* ปุ่มดาวน์โหลดสีเขียวในกล่องขาว */
    .btn-dl {
        background-color: #00594C;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 11px;
        font-weight: bold;
        white-space: nowrap;
    }

    /* ปรับแต่ง Expander ใน Sidebar ให้เป็นสีขาวและไม่มีไอคอนขยะ */
    .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    .st-emotion-cache-p5mtransition p {
        color: #000000 !important;
        font-weight: bold !important;
    }

    /* ข้อความแจ้งเตือนด้านล่าง (สีขาว Contrast สูง) */
    .stSidebar .stCaption p {
        color: #FFFFFF !important;
        opacity: 0.9;
    }

    /* หน้า Chat */
    h2 { color: #006861 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. ส่วนจัดการ API ---
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
    # 1. แสดงโลโก้ (ใช้ไฟล์ logo_ku.png ที่น้องมี)
    if os.path.exists("logo_ku.png"):
        img_b64 = get_image_base64("logo_ku.png")
        st.markdown(f'<div class="header-container"><img src="data:image/png;base64,{img_b64}" class="header-img"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-title">🎓 AI KUSRC Dashboard</div>', unsafe_allow_html=True)

    # 2. รายการแบบฟอร์มด่วนในกล่องขาว
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown(f"""
            <div class="white-card">
                <div class="form-row">
                    <div class="form-label">📝 คำร้องขอลงทะเบียนเรียน<br>(Registrar-2)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf" target="_blank" class="btn-dl">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">💰 คำร้องทั่วไป (Registrar-1)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="btn-dl">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">📂 ใบลาพักการศึกษา (Registrar-10)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf" target="_blank" class="btn-dl">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">📄 Add-Drop (KU3) ออนไลน์</div>
                    <a href="https://reg2.src.ku.ac.th/download.html" target="_blank" class="btn-dl">ดาวน์โหลด</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("💚 พัฒนาโดยนิสิตเพื่อนิสิต มก.ศรช.")

# --- 6. ส่วนหน้า Chat หลัก ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลดข้อมูลอ้างอิง
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

st.markdown("## 🐯 AI KUSRC")

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
