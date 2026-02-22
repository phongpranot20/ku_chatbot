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

    .loading-dots {
        font-size: 30px;
        font-weight: bold;
        display: inline-block;
    }
    .loading-dots:after {
        content: '.';
        animation: dots 1.5s steps(5, end) infinite;
    }
    @keyframes dots {
        0%, 20% { content: '.'; }
        40% { content: '..'; }
        60% { content: '...'; }
        80%, 100% { content: ''; }
    }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    # แก้ไข: ลองใช้ชื่อรุ่นแบบเต็มเพื่อให้รองรับ API ทุกเวอร์ชัน
    try:
        return genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    except:
        try:
            return genai.GenerativeModel(model_name='gemini-1.5-flash-latest')
        except Exception as e:
            st.error(f"❌ ไม่สามารถโหลดโมเดลได้: {e}")
            return None

model = load_model()

if not model:
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
        status_placeholder = st.empty()
        status_placeholder.markdown('<div class="loading-dots"></div>', unsafe_allow_html=True)
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "ภารกิจ: จงจำชื่อผู้ใช้และสิ่งที่คุยกันก่อนหน้าจากประวัติการสนทนา "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ หากถามเรื่องตึก ต้องส่งลิงก์แผนที่เสมอ"
        )
        
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nประวัติการคุย:\n{history_text}\n\nคำถามล่าสุด: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
