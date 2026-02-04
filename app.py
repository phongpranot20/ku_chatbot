import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="KU Sriracha Bot",
    page_icon="🐢",
    layout="wide"
)

# -------------------------------------------------------------
# 🎨 ธีมสีเขียว KU + บังคับพื้นหลังขาว (แก้แล้ว)
# -------------------------------------------------------------
st.markdown("""
<style>
    /* พื้นหลังขาว */
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    
    /* Sidebar เขียวอ่อน */
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    
    /* ตัวหนังสือสีเขียวเข้ม */
    h1, h2, h3, p, span, div { color: #00594C; }
    
    /* กล่องข้อความ User */
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    
    /* ปรับสีตัวหนังสือในแชทให้เข้มขึ้น (จะได้อ่านง่าย) */
    .stMarkdown p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. ใส่ API Key
# -------------------------------------------------------------
api_key = "AIzaSyC5QQKrjN6trhzAuyXp19jUygmoLO-zVEA"  # <--- ⚠️ ใส่ API Key ใหม่ตรงนี้
genai.configure(api_key=api_key)

# -------------------------------------------------------------
# ⚙️ ระบบ Auto-Switch โมเดล (กุญแจผี)
# -------------------------------------------------------------
def get_working_model():
    # รายชื่อโมเดลที่มีในเครื่องคุณ (เรียงจาก น่าใช้สุด -> ไปน้อยสุด)
    model_list = [
        'gemini-2.0-flash-lite-001', # ตัวนี้เบาและฟรี น่าจะรอด
        'gemini-2.0-flash',          # ตัวรอง
        'gemini-flash-lite-latest',  # ตัวสำรอง
        'gemini-1.5-flash',          # ตัวมาตรฐาน
        'gemini-pro'                 # ตัวสุดท้าย
    ]
    
    for model_name in model_list:
        try:
            model = genai.GenerativeModel(model_name)
            # แอบเทสเงียบๆ ว่าใช้ได้ไหม
            model.generate_content("test")
            return model # ถ้าผ่าน ส่งตัวนี้กลับไปใช้เลย
        except:
            continue # ถ้าพัง ข้ามไปตัวถัดไปเงียบๆ
            
    # ถ้าพังทุกตัว ให้ใช้ตัวสุดท้ายวัดดวง
    return genai.GenerativeModel('gemini-2.0-flash-lite-001')

# เรียกใช้ฟังก์ชันเลือกโมเดล
model = get_working_model()

# -------------------------------------------------------------
# 3. Sidebar (เมนูซ้าย)
# -------------------------------------------------------------
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo_ku.png"):
            st.image("logo_ku.png", use_container_width=True)
    
    st.markdown('<h3 style="text-align: center;">เมนูคำสั่ง</h3>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center;">ระบบช่วยตอบคำถามนิสิต<br>มก. ศรีราชา</p>', unsafe_allow_html=True)
    st.write("") 
    
    if st.button("🗑️ ล้างประวัติแชท", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown('<div style="text-align: center; color: gray;">พัฒนาโดย: นิสิต มก. 💻</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# 4. หน้าจอแชทหลัก
# -------------------------------------------------------------
st.title("🐢 น้องนนทรี (AI Assistant)")
st.caption("สอบถามข้อมูล คณะ, หลักสูตร, หรือสถานที่ในวิทยาเขตศรีราชา ได้เลยครับ")

# โหลดข้อมูล
if not os.path.exists("ku_data.txt"):
    st.info("ℹ️ ไม่พบไฟล์ข้อมูล (ku_data.txt)")
    knowledge_base = ""
else:
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar_icon = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        message_placeholder = st.empty()
        try:
            # ส่งคำถาม
            response = model.generate_content(f"ข้อมูลอ้างอิง: {knowledge_base}\n\nคำถาม: {prompt}")
            message_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            error_msg = f"❌ ขออภัย ระบบขัดข้องชั่วคราว ({e})"
            message_placeholder.error(error_msg)