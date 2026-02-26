import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันจัดการรูปภาพโลโก้ ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS ปรับแต่ง UI ให้เหมือนรูปเรฟเฟอเรนซ์ ---
st.markdown("""
<style>
    /* พื้นหลังหน้าหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar: สีเขียวหัวเป็ดตามรูปเป้าหมาย */
    [data-testid="stSidebar"] { 
        background-color: #006861 !important; 
    }

    /* จัดการ Header: โลโก้อยู่บน ชื่อมหาลัยอยู่ล่าง */
    .custom-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 20px 5px;
        margin-bottom: 20px;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    .header-logo-img {
        width: 100px;
        height: auto;
        margin-bottom: 15px;
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
        margin-bottom: 10px;
        text-align: center;
    }

    /* --- กล่องขาวรายการแบบฟอร์ม (White Card Style) --- */
    .white-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 5px;
        margin-top: 5px;
    }
    
    .form-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 10px;
        border-bottom: 1px solid #eeeeee;
    }
    .form-row:last-child { border-bottom: none; }
    
    .form-label {
        color: #333333 !important;
        font-size: 13px;
        font-weight: bold;
        line-height: 1.3;
        flex: 1;
        text-align: left;
    }

    /* ปุ่มดาวน์โหลดสีเขียวในกล่องขาว */
    .btn-download {
        background-color: #006861;
        color: white !important;
        padding: 5px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 11px;
        font-weight: bold;
        white-space: nowrap;
    }

    /* บังคับตัวอักษรใน Sidebar นอกกล่องขาวให้เป็นสีขาว */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label,
    .stSidebar .stCaption p {
        color: #FFFFFF !important;
    }

    /* ปรับแต่ง Expander ใน Sidebar ให้พื้นหลังเป็นสีขาว (Card Look) */
    .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }
    .st-emotion-cache-p5mtransition p {
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    /* หัวข้อ Chat หน้าหลัก */
    h2 { color: #006861 !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. ส่วนจัดการ API และ Model (จากโค้ดเก่า) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API KEY ใน Secrets")
    st.stop()
genai.configure(api_key=api_key)

@st.cache_resource
def load_smart_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามโดยใช้ข้อมูลจาก 'ข้อมูลอ้างอิง' ที่ให้มาเท่านั้น "
            "เน้นความเป็นกันเอง สุภาพ และเรียกผู้ใช้ว่า 'น้อง'"
        )
        return genai.GenerativeModel(model_name=selected_model, system_instruction=instruction)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_smart_model()

# --- 5. ส่วน Sidebar: Dashboard ตามเรฟเฟอเรนซ์ ---
with st.sidebar:
    # 1. Header: โลโก้บน ชื่อมหาลัยล่าง
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

    # 2. รายการแบบฟอร์มด่วนในกล่องขาว (White Card)
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown(f"""
            <div class="white-card">
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

# --- 6. ส่วนหน้า Chat หลัก (จากโค้ดเก่า) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลด Knowledge Base จากไฟล์
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
            full_context = f"ข้อมูลอ้างอิง:\n{knowledge_base}\n\nคำถาม: {prompt}"
            
            response = chat_session.send_message(full_context, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")ห
