import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- 2. CSS ปรับแต่ง UI (เน้นแก้สีตัวหนังสือใน Sidebar) ---
st.markdown("""
<style>
    /* พื้นหลังหลักและตัวหนังสือหน้า Chat */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* ส่วน Sidebar พื้นหลังเขียว */
    [data-testid="stSidebar"] { 
        background-color: #00594C !important; 
    }
    
    /* หัวข้อหลักใน Sidebar ให้เป็นสีขาวเพื่อให้ตัดกับพื้นเขียว */
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] .stMarkdown h3 { 
        color: #FFFFFF !important; 
    }

    /* --- จุดสำคัญ: ปรับตัวหนังสือใน Widget ให้เป็นสีดำทั้งหมด --- */
    /* ข้อความใน Expander, Label ของ Input และตัวเลขที่กรอก */
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] input {
        color: #000000 !important;
    }

    /* ปรับแต่งกล่อง Expander ให้พื้นหลังเป็นสีขาวสว่างและตัวหนังสือดำ */
    [data-testid="stSidebar"] .st-emotion-cache-1f3w0ih, 
    [data-testid="stSidebar"] .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 10px;
    }

    /* ปรับแต่งปุ่มกดใน Sidebar ให้เป็นสีขาว/ตัวหนังสือเขียวเข้ม */
    .stSidebar .stButton>button {
        background-color: #FFFFFF !important;
        color: #00594C !important;
        border-radius: 10px;
        border: 2px solid #FFFFFF;
        font-weight: bold;
        width: 100%;
    }
    
    /* หน้าจอ Chat */
    h1 { color: #00594C !important; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
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

# --- 4. ส่วน Sidebar: Student Dashboard ---
with st.sidebar:
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", width=150)
    st.markdown("### 🎓 Student Dashboard")
    
    # แบบฟอร์มด่วน (ข้อความข้างในจะเป็นสีดำตาม CSS ด้านบน)
    with st.expander("📄 ลิงก์แบบฟอร์มด่วน"):
        st.link_button("📝 ใบเพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        st.link_button("💰 ใบผ่อนผันค่าเทอม", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf")
        st.link_button("📁 หน้ารวมแบบฟอร์ม", "https://reg2.src.ku.ac.th/download.html")

    st.markdown("---")
    
    # GPA Simulator (ตัวหนังสือจะเป็นสีดำอ่านง่าย)
    st.markdown("### 🔢 GPA Simulator")
    current_gpa = st.number_input("เกรดเฉลี่ยปัจจุบัน", min_value=0.0, max_value=4.0, value=3.00, step=0.01)
    target_gpa = st.number_input("เกรดที่คาดหวังเทอมนี้", min_value=0.0, max_value=4.0, value=3.50, step=0.01)
    
    if st.button("วิเคราะห์โอกาส"):
        if target_gpa > current_gpa:
            st.write(f"✍️ น้องต้องทำเกรดให้ได้มากกว่า {target_gpa} นะครับ!")
        else:
            st.balloons()
            st.write("🌟 เกรดอยู่ในเกณฑ์ดีเยี่ยมแล้วรักษาไว้ครับ!")

    st.markdown("---")
    st.caption("💡 แนะนำ: ลองถามพี่ว่า 'ตึก 17' ดูนะ!")

# --- 5. จัดการ Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. ส่วนการทำงานของ ChatBot ---
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่นนทรี กำลังหาข้อมูลให้ครับ...)*")
        
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
