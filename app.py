import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "1.5" in m.name:
                    return genai.GenerativeModel(model_name=m.name, tools=[{"google_search": {}}])
    except:
        pass

    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "1.5" in m.name:
                    return genai.GenerativeModel(model_name=m.name, tools=[{"google_search_retrieval": {}}])
    except:
        pass

    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้")
    st.stop()

st.title("AI TEST")

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        # สร้าง placeholder สำหรับแสดงสถานะกำลังคิด
        status_placeholder = st.empty()
        status_placeholder.markdown("...") 
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ภารกิจ: จงจำชื่อผู้ใช้และสิ่งที่คุยกันก่อนหน้าจากประวัติการสนทนา "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ หากถามเรื่องตึก ต้องส่งลิงก์แผนที่เสมอ "
            "และถ้าเป็นไปได้ ให้ช่วยเช็คสภาพจราจรหรือข้อมูลเรียลไทม์มาตอบด้วย"
        )
        
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nประวัติการคุย:\n{history_text}\n\nคำถามล่าสุด: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            # เมื่อได้คำตอบแล้ว ให้แทนที่จุดด้วยข้อความจริง
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            try:
                base_model = genai.GenerativeModel(model.model_name)
                response = base_model.generate_content(full_prompt)
                status_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e2:
                status_placeholder.empty() # ลบจุดออกถ้าเกิด Error
                st.error(f"❌ ระบบขัดข้อง: {e2}")
