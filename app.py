import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- 2. CSS ปรับแต่ง UI ให้ดูทันสมัย (Custom Sidebar & Chat) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #00594C !important; }
    .stSidebar [data-testid="stMarkdownContainer"] p, .stSidebar h3, .stSidebar span { color: white !important; font-weight: bold; }
    h1 { color: #00594C !important; font-family: 'Tahoma'; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
    
    /* สไตล์ปุ่มใน Sidebar */
    .stButton>button { width: 100%; border-radius: 10px; border: none; background-color: #ffffff; color: #00594C; font-weight: bold; }
    .stButton>button:hover { background-color: #e0e0e0; color: #00594C; }
</style>
""", unsafe_allow_html=True)

# --- 3. ส่วนจัดการ API และ Dynamic Model Selection ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ใน Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_smart_model():
    try:
        # ฟังก์ชัน List Model เพื่อเลือกตัวที่ดีที่สุดอัตโนมัติ
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามโดยใช้ข้อมูลจาก 'ข้อมูลอ้างอิง' ที่ให้มาเท่านั้น "
            "1. หากถามหาแบบฟอร์ม ให้ส่งชื่อแบบฟอร์มพร้อมลิงก์ PDF ทันที "
            "2. หากถามหาสถานที่ ให้บอกพิกัดจากลิงก์ Google Maps ที่เตรียมไว้ "
            "3. ห้ามแสดงตัวเลขละติจูด/ลองจิจูด (GPS) ให้ผู้ใช้เห็นเด็ดขาด "
            "4. ใช้สรรพนาม พี่-น้อง และตอบอย่างเป็นกันเองแต่สุภาพ"
        )
        return genai.GenerativeModel(model_name=selected_model, system_instruction=instruction)
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_smart_model()

# --- 4. ส่วน Sidebar: Student Dashboard (แทนที่แผนที่) ---
with st.sidebar:
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", width=150)
    st.markdown("### 🎓 Student Dashboard")
    
    # Quick Links (ดึงข้อมูลจาก ku_data.txt มาทำปุ่มลัด)
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน"):
        st.link_button("📝 ใบเพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        st.link_button("💰 ใบผ่อนผันค่าเทอม", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf")
        st.link_button("📁 หน้ารวมแบบฟอร์ม", "https://reg2.src.ku.ac.th/download.html")

    st.markdown("---")
    
    # GPA Simulator (ฟังก์ชันเสริมความว้าว)
    st.markdown("### 🔢 GPA Simulator")
    current_gpa = st.number_input("เกรดเฉลี่ยสะสมปัจจุบัน", min_value=0.0, max_value=4.0, value=3.00, step=0.01)
    target_gpa = st.number_input("เกรดที่อยากได้เทอมนี้", min_value=0.0, max_value=4.0, value=3.50, step=0.01)
    
    if st.button("คำนวณโอกาส"):
        if target_gpa > current_gpa:
            st.warning(f"ต้องขยันขึ้นนะ! น้องต้องทำให้มากกว่า {target_gpa} เพื่อดึงเกรดรวมครับ")
        else:
            st.balloons()
            st.success("ยอดเยี่ยม! รักษามาตรฐานนี้ไว้ได้รับรองเกียรตินิยมอยู่ไม่ไกล")

    st.markdown("---")
    st.info("💡 น้องๆ สามารถถามทางไปตึกเรียน หรือสอบถามเรื่องระเบียบการกับพี่ได้เลยนะ!")

# --- 5. การจัดการฐานข้อมูลและ Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. ส่วนการทำงานของ ChatBot ---
if prompt := st.chat_input("พิมพ์คำถามที่นี่... (เช่น ขอใบ KU3 หรือ ตึก 17 ไปทางไหน?)"):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาคำตอบให้นะ...)*")
        
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
            st.error(f"เกิดข้อผิดพลาด: {e}")
