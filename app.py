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

    /* Animation สำหรับจุด Loading */
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
    
    /* ตกแต่งปุ่มทางลัด */
    .stButton button {
        width: 100%;
        border-radius: 20px;
        border: 1px solid #00594C;
        color: #00594C;
        background-color: transparent;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #00594C;
        color: white;
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
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(model_name=m.name)
    except Exception as e:
        st.error(f"❌ ระบบไม่สามารถดึงรายชื่อโมเดลได้: {e}")
    return None

model = load_model()

if not model:
    st.stop()

st.title("🦖 น้องนนทรี AI (KU SRC)")

# --- ระบบปุ่มทางลัด (Quick Reply) ---
st.write("💡 คำถามที่พบบ่อย:")
col1, col2, col3, col4 = st.columns(4)
btn_prompt = None

with col1:
    if st.button("📍 พิกัดตึกเรียน"):
        btn_prompt = "ขอพิกัดตึกเรียนสำคัญๆ ใน มก. ศรีราชา หน่อยครับ"
with col2:
    if st.button("🍽️ ร้านอาหารเด็ด"):
        btn_prompt = "แนะนำร้านอาหารอร่อยๆ รอบมหาลัยหน่อยพี่"
with col3:
    if st.button("📄 งานทะเบียน"):
        btn_prompt = "ติดต่อขอเอกสารการเรียนหรือฝ่ายทะเบียนต้องทำยังไงครับ"
with col4:
    if st.button("🚌 รถตะไล"):
        btn_prompt = "รถตะไลในมอวิ่งเส้นทางไหนบ้างครับ"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

# รับค่าจากทั้งปุ่มและช่องแชท
chat_input = st.chat_input("พิมพ์คำถามที่นี่...")
prompt = chat_input if chat_input else btn_prompt

if prompt:
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        status_placeholder = st.empty()
        status_placeholder.markdown('<div class="loading-dots"></div>', unsafe_allow_html=True)
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "พูดจาสุภาพ เป็นกันเอง แทนตัวเองว่า 'พี่' และเรียกผู้ใช้ว่า 'น้อง' "
            "จงจำชื่อผู้ใช้และสิ่งที่คุยกันก่อนหน้าเสมอ "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างแม่นยำ หากถามเรื่องตึก ต้องส่งลิงก์แผนที่เสมอ"
        )
        
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base if 'knowledge_base' in locals() else 'ข้อมูล มก. ศรีราชา'}\n\nประวัติการคุย:\n{history_text}\n\nคำถามล่าสุด: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            st.error(f"❌ เกิดข้อผิดพลาด: {e}")
