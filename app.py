import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="AI TEST", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ API Key not found")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
        return model
    except:
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
        except Exception as e:
            st.error(f"Error: {e}")
    return None

model = load_model()

st.title("AI TEST")

if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์ข้อความ..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        status_placeholder = st.empty()
        status_placeholder.markdown("...")
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "1. ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ "
            "2. หากถามเรื่องตึกหรือแบบฟอร์ม ให้ใช้ข้อมูลจากไฟล์และส่งลิงก์เสมอ "
            "3. หากถามเรื่องรถติดหรือสภาพจราจร ให้ใช้ Google Search สรุปคำตอบและระยะทางเป็นกิโลเมตร "
            "4. ห้ามแสดงเลขพิกัด GPS หรือ Latitude/Longitude ในคำตอบเด็ดขาด"
        )
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            if "429" in str(e):
                st.error("⚠️ โควตาเต็ม (Quota Exceeded) กรุณารอสัก 1 นาทีแล้วลองใหม่นะ")
            else:
                st.error(f"Error: {e}")
