import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="น้องนนทรี AI (KU SRC)", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1 { color: #1E4D2B !important; font-size: 24px !important; text-align: center; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; color: #000000; }
    p, span, div { color: #000000 !important; }
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
        return genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{"google_search": {}}]
        )
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

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
            "3. หากถามเรื่องรถติดหรือสภาพจราจร ให้ใช้ Google Search สรุปคำตอบ "
            "4. ห้ามแสดงเลขพิกัด GPS หรือ Latitude/Longitude ในคำตอบเด็ดขาด"
        )
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            res_text = response.text if response.text else "ขออภัย ไม่พบข้อมูลครับ"
            status_placeholder.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
        except Exception as e:
            status_placeholder.empty()
            if "429" in str(e):
                st.error("⚠️ โควตาเต็ม กรุณารอสักครู่")
            else:
                st.error(f"Error: {e}")
