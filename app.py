import streamlit as st
import google.generativeai as genai
import os
import base64

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="AI KUSRC", page_icon="🐯", layout="wide")

# --- 2. ฟังก์ชันช่วยแสดงผลรูปภาพแบบคุมขนาด ---
def get_image_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 3. CSS จัดหน้าตาให้เหมือนเรฟเฟอเรนซ์เป๊ะๆ ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar เขียวไล่เฉด (Gradient) แบบในรูป */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #00594C 0%, #003d34 100%) !important;
        padding-top: 0px;
    }

    /* จัดการโลโก้ Header ด้านบนสุด */
    .header-container {
        text-align: center;
        padding: 20px 10px;
        background: transparent;
    }
    .header-logo {
        width: 100%;
        max-width: 250px;
        height: auto;
    }

    /* หัวข้อ Dashboard */
    .sidebar-title {
        color: white !important;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 15px 0px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* กล่องขาวรายการแบบฟอร์ม (White Card) */
    .form-container {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        margin-top: 5px;
    }
    
    /* รายการในกล่องขาว */
    .form-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #eee;
        color: black !important;
    }
    .form-item:last-child { border-bottom: none; }
    
    .form-text {
        font-size: 0.9rem;
        font-weight: 500;
        color: #333 !important;
        line-height: 1.2;
    }

    /* ปุ่มดาวน์โหลดสีเขียวในกล่องขาว */
    .download-btn {
        background-color: #00594C;
        color: white !important;
        padding: 5px 12px;
        border-radius: 5px;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: bold;
        white-space: nowrap;
    }

    /* ปรับแต่ง Expander ให้เป็นสีขาวและดูคลีน */
    .st-emotion-cache-p5mtransition {
        background-color: white !important;
        border-radius: 10px !important;
    }
    .st-emotion-cache-p5mtransition p {
        color: black !important;
        font-weight: bold !important;
    }

    /* Chat UI */
    h2 { color: #00594C !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. ส่วนจัดการ API ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY")
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

# --- 5. ส่วน Sidebar: แดชบอร์ดแบบในรูป ---
with st.sidebar:
    # แสดงโลโก้ที่หัวบนสุด
    if os.path.exists("logo_ku.png"):
        img_base64 = get_image_base64("logo_ku.png")
        st.markdown(f"""
            <div class="header-container">
                <img src="data:image/png;base64,{img_base64}" class="header-logo">
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-title">🎓 น้องนนทรี Student Dashboard</div>', unsafe_allow_html=True)

    # กล่องขาวรายการแบบฟอร์ม
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน (คลิก)", expanded=True):
        st.markdown(f"""
            <div class="form-container">
                <div class="form-item">
                    <div class="form-text">📝 คำร้องขอลงทะเบียน<br>(Registrar-2)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf" target="_blank" class="download-btn">ดาวน์โหลด</a>
                </div>
                <div class="form-item">
                    <div class="form-text">💰 คำร้องทั่วไป<br>(Registrar-1)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf" target="_blank" class="download-btn">ดาวน์โหลด</a>
                </div>
                <div class="form-item">
                    <div class="form-text">📂 ใบลาพักการศึกษา<br>(Registrar-10)</div>
                    <a href="https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf" target="_blank" class="download-btn">ดาวน์โหลด</a>
                </div>
                <div class="form-item">
                    <div class="form-text">📄 Add-Drop (KU3)<br>ออนไลน์</div>
                    <a href="https://reg2.src.ku.ac.th/download.html" target="_blank" class="download-btn">ดาวน์โหลด</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("💚 พัฒนาโดยนิสิตเพื่อนิสิต มก.ศรช.")

# --- 6. ส่วน Chat หน้าหลัก ---
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
