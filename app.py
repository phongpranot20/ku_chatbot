import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="KU Sriracha Bot",
    page_icon="🐢",
    layout="wide"
)

# 🎨 ธีมสีเขียว KU + บังคับพื้นหลังขาว
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
# 2. ระบบความปลอดภัย (API Key) - แก้ไขตรงนี้
# -------------------------------------------------------------
# ดึง API Key จาก Secrets ของระบบ (ห้ามเขียนรหัสจริงลงในนี้)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # สำหรับรันในเครื่องตัวเอง (Local) ให้สร้างไฟล์ .streamlit/secrets.toml
    api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ไม่พบ API Key กรุณาตั้งค่าใน Secrets (GEMINI_API_KEY)")
    st.stop()

genai.configure(api_key=api_key)

# ⚙️ ระบบ Auto-Switch โมเดล
def get_working_model():
    model_list = ['gemini-1.5-flash', 'gemini-1.5-pro']
    for model_name in model_list:
        try:
            model = genai.GenerativeModel(model_name)
            return model
        except:
            continue
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_working_model()

# -------------------------------------------------------------
# 3. Sidebar
# -------------------------------------------------------------
with st.sidebar:
    st.markdown('<h3 style="text-align: center;">เมนูคำสั่ง</h3>', unsafe_allow_html=True)
    if st.button("🗑️ ล้างประวัติแชท", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------------------
# 4. การจัดการข้อมูลและแชท
# -------------------------------------------------------------
st.title("🐢 น้องนนทรี (AI Assistant)")

# โหลดข้อมูลความรู้จากไฟล์
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
        # คำสั่งคุมสติ AI ให้เป็นรุ่นพี่ที่แนะนำเก่งๆ
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ผู้เชี่ยวชาญของ มก. ศรีราชา (KU SRC) "
            "กฎเหล็ก: 1. ตอบสุภาพเป็นกันเอง 2. หากถามเรื่องตึก ต้องส่งลิ้งค์แผนที่จากข้อมูลอ้างอิงเสมอ "
            "3. ให้คำแนะนำแบบรุ่นพี่ (เช่น ร้านอาหารใกล้ๆ หรือวิธีเดินทาง) "
            "4. ห้ามตอบข้อมูลของมหาวิทยาลัยอื่นเด็ดขาด"
        )
        
        full_prompt = f"{instruction}\n\nข้อมูลอ้างอิง: {knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"ระบบขัดข้อง: {e}")
