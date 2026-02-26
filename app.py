import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS ปรับแต่ง UI (เน้นตัวอักษรใหญ่และโลโก้ใหญ่) ---
st.markdown("""
<style>
    /* พื้นหลังหน้าหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar: สีเขียวตามเรฟ */
    [data-testid="stSidebar"] { 
        background-color: #006861 !important; 
    }

    /* จัดการ Header: โลโก้ใหญ่ + ชื่อมหาลัยตัวใหญ่ */
    .custom-header {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 15px 5px;
        margin-bottom: 25px;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img {
        width: 80px; /* เพิ่มขนาดโลโก้ให้ใหญ่ขึ้น */
        height: auto;
    }
    .header-text {
        color: white !important;
        font-family: 'Tahoma', sans-serif;
    }
    .univ-name { 
        font-size: 22px; /* ขยายขนาดฟอนต์มหาลัยให้ใหญ่ชัดเจน */
        font-weight: bold;
        line-height: 1.1;
    }

    /* หัวข้อ Dashboard */
    .sidebar-title {
        color: #FFFFFF !important;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
    }

    /* กล่องขาวรายการแบบฟอร์ม */
    .white-card-container {
        background-color: #FFFFFF;
        border-radius: 12px;
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
        font-size: 14px; /* ปรับฟอนต์ในกล่องขาวให้ใหญ่นิดนึง */
        font-weight: 600;
        flex: 1;
    }

    /* ปุ่มดาวน์โหลด */
    .btn-download {
        background-color: #006861;
        color: white !important;
        padding: 6px 14px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 12px;
        font-weight: bold;
    }

    /* บังคับตัวอักษรใน Sidebar ให้เป็นสีขาว */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
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
    # 1. Custom Header: โลโก้ใหญ่ + ชื่อมหาลัย (ตัดชื่อวิทยาเขตออก)
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
    
    st.markdown('<p class="sidebar-title">🎓 AI KUSRC Dashboard</p>', unsafe_allow_html=True)

    # 2. รายการแบบฟอร์มด่วน
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown(f"""
            <div class="white-card-container">
                <div class="form-row">
                    <div class="form-label">📝 คำร้องขอลงทะเบียนเรียน<br>(Registrar-2)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">💰 คำร้องทั่วไป (Registrar-1)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">📂 ใบลาพักการศึกษา (Registrar-10)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf" target="_blank" class="btn-download">ดาวน์โหลด</a>
                </div>
                <div class="form-row">
                    <div class="form-label">📄 Add-Drop (KU3) ออนไลน์</div>
                    <a href="https://reg2.src.ku.ac.th/download.html" target="_blank" class="btn-download">ดาวน์โหลด</a>
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
