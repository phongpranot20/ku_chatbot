import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# 🎨 ธีมสีเขียว KU
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ระบบดึง API Key และเลือกโมเดลพร้อม Google Search
# -------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้เครื่องมือ Google Search เพื่อให้ AI ดึงข้อมูลจราจรและข่าวสารล่าสุดได้
        tools = [{"google_search_retrieval": {}}]
        
        # เลือกใช้ gemini-1.5-flash ซึ่งทำงานได้เร็วและรองรับการค้นหาข้อมูล
        return genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=tools
        )
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดโมเดล: {e}")
    return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้ กรุณาตรวจสอบ API Key")
    st.stop()

# -------------------------------------------------------------
# 3. จัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("AI TEST - น้องนนทรี KU SRC")

# ดึงข้อมูลจากฐานความรู้ (Local Knowledge) [cite: 1, 2, 3]
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติการสนทนา
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่... (เช่น 'ทางไป มก. ศรีราชา รถติดไหม?')"):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        # ปรับ Instruction ให้ครอบคลุมเรื่องการเช็กจราจร
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "1. ตอบคำถามอย่างสุภาพและเป็นกันเองแบบรุ่นพี่ "
            "2. หากถามเรื่องตึกหรือสถานที่ในวิทยาเขต ให้ใช้ข้อมูลจาก 'ความรู้ในไฟล์' และส่งลิงก์แผนที่เสมอ [cite: 2, 3, 4, 5, 6] "
            "3. หากถามเรื่องสภาพจราจร การเดินทาง หรือเหตุการณ์ปัจจุบัน ให้ใช้เครื่องมือ Google Search ค้นหาคำตอบที่อัปเดตที่สุด "
            "4. ถ้าข้อมูลในไฟล์ไม่พอ ให้หาจากเน็ตได้เลย"
        )
        
        full_prompt = f"{instruction}\n\nความรู้ในไฟล์: {knowledge_base}\n\nคำถามจากนิสิต: {prompt}"
        
        try:
            # เรียกใช้งานโมเดล
            response = model.generate_content(full_prompt)
            
            # ตรวจสอบและแสดงผลข้อความ
            response_text = response.text if response.text else "ขออภัยครับ พี่หาข้อมูลส่วนนี้ไม่เจอ ลองถามใหม่อีกครั้งนะ"
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"❌ ระบบขัดข้อง: {e}")
