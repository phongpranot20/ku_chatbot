import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- 2. CSS ปรับแต่ง UI ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #00594C !important; }
    .stSidebar [data-testid="stMarkdownContainer"] p, .stSidebar h3 { color: white !important; font-weight: bold; }
    h1 { color: #00594C !important; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# --- 3. ส่วนจัดการ API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ใน Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_smart_model():
    try:
        # ดึงรายชื่อโมเดลที่ใช้งานได้
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
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

# --- 4. ส่วน Sidebar (แก้ไข Iframe ให้ถูกต้อง) ---
with st.sidebar:
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", width=150)
    st.markdown("### 📍 แผนที่วิทยาเขตศรีราชา")
    
    # พิกัดกลาง มก.ศรช. แบบ Embed ที่ถูกต้องเพื่อเลี่ยง Invalid pb parameter
    map_embed_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3882.4842777353995!2d100.9220021!3d13.1165203!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3102b704207936a5%3A0x67c00e6205e468e!2z4Lih4Lir4Liy4Lin4Li04Lii4Liy4Lil4Lia4Lix4LiZ4LiB4Liy4Lij4LiX4Liy4LiH4LmA4LiB4Liy4Lij4LiX4Lij4Liw4LiI4LiZ4Liy4LiH4LiX4Lix4LiZ4LiB4Liy4Lij!5e0!3m2!1sth!2sth!4v1700000000000"
    st.components.v1.html(f'<iframe src="{map_embed_url}" width="100%" height="300" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>', height=320)
    st.info("💡 น้องๆ ถามทางหรือขอแบบฟอร์มลงทะเบียนกับพี่ได้เลยนะ!")

# --- 5. จัดการ Chat History และ Data ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# แสดงประวัติ
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🐯"):
        st.markdown(message["content"])

# ส่วนรับคำถาม
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังหาข้อมูลให้แป๊บนึงนะ...)*")
        
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
            st.error(f"ขออภัยครับ เกิดข้อผิดพลาด: {e}")
