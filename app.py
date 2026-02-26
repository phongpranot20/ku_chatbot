import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- CSS ปรับปรุง UI ให้ดูทันสมัยขึ้น ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: black; }
    [data-testid="stSidebar"] { background-color: #00594C !important; color: white; }
    .stSidebar [data-testid="stMarkdownContainer"] p { color: white !important; font-weight: bold; }
    h1, h2, h3 { color: #00594C !important; }
    
    /* สไตล์ปุ่มลิงก์แผนที่ */
    .map-button {
        display: inline-block;
        padding: 8px 16px;
        background-color: #00594C;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- ส่วนจัดการ API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ กรุณาตั้งค่า GEMINI_API_KEY ใน Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        # ใช้ System Instruction เพื่อคุมบุคลิกตั้งแต่ต้น
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของวิทยาเขตศรีราชา มก. (KU SRC) "
            "หน้าที่ของคุณคือช่วยเหลือรุ่นน้องเกี่ยวกับข้อมูลมหาวิทยาลัย "
            "1. หากรุ่นน้องถามหาแบบฟอร์ม ให้ดึงลิงก์ PDF จากข้อมูลที่ให้มาตอบทันที "
            "2. หากถามหาสถานที่ ให้สรุปข้อมูลและให้ลิงก์แผนที่ "
            "3. ห้ามแสดงเลขพิกัด GPS (Lat, Long) เด็ดขาด ให้บอกเป็นระยะทางหรือเวลาแทน "
            "4. ตอบด้วยความเป็นกันเอง สุภาพ แทนตัวเองว่า 'พี่' และเรียกผู้ใช้ว่า 'น้อง'"
        )
        return genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=instruction)
    except:
        return None

model = load_model()

# --- ส่วน Sidebar: เพิ่มแผนที่ประกอบการใช้งาน ---
with st.sidebar:
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", width=150)
    st.markdown("### 📍 แผนที่ มก.ศรช.")
    # ฝัง Google Maps ของ มก.ศรช.
    map_html = '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m13!1d3882.388836268392!2d100.91745677579698!3d13.113264611202888!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3102b70f0687779f%3A0xc9b039868725d78a!2z4Lih4Lir4Liy4Lin4Li04LiX4Lii4Liy4Lis4Liy4LiZ4LmA4LiB4Lip4Lij4Liy4LiB4Liy4LijIOC4p-C4tOC4l-C4ouC4sOC4quC4o-C4teC5gOC4guC4leC4qOC4o-C4teC4iuC4siAoc3JpcmFjaGEp!5e0!3m2!1sth!2sth!4v1708600000000!5m2!1sth!2sth" width="100%" height="300" style="border:0; border-radius:10px;" allowfullscreen="" loading="lazy"></iframe>'
    st.components.v1.html(map_html, height=320)
    st.info("💡 เคล็ดลับ: น้องๆ สามารถถามทางไปตึกเรียน หรือขอลิงก์โหลดใบ KU3 ได้เลยนะ!")

# --- หน้าจอหลัก ---
st.title("🐯 น้องนนทรี: เพื่อนคู่คิด นิสิต มก.ศรช.")

# โหลดข้อมูลจาก ku_data.txt
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงประวัติการคุย
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ส่วนรับคำถาม
if prompt := st.chat_input("พิมพ์ถามพี่ได้เลย เช่น 'ขอแบบฟอร์มลงทะเบียน' หรือ 'อาคาร 10 ไปทางไหน'"):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่นนทรี กำลังหาคำตอบให้นะ...)*")
        
        # คัดกรองเฉพาะประวัติ 5 รอบล่าสุดเพื่อประหยัด Token
        history = st.session_state.messages[-5:]
        
        # สร้าง Prompt แบบ RAG
        full_context = f"ข้อมูลอ้างอิง:\n{knowledge_base}\n\nคำถาม: {prompt}"
        
        try:
            # ใช้ chat session เพื่อความต่อเนื่อง
            chat = model.start_chat(history=[
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            response = chat.send_message(full_context, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
            
        except Exception as e:
            placeholder.empty()
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
