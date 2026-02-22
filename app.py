import streamlit as st
import google.generativeai as genai
import os

# 1. ตั้งค่าหน้าจอและธีม
st.set_page_config(page_title="KU Sriracha AI Bot", page_icon="🦖", layout="wide")

# 2. ปรับแต่ง CSS ฉบับจัดเต็ม (KU Premium Theme)
st.markdown("""
<style>
    /* พื้นหลังหลักและฟอนต์ */
    .stApp { background-color: #F8FBF9; }
    
    /* ปรับแต่ง Sidebar */
    [data-testid="stSidebar"] {
        background-color: #00594C !important;
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* หัวข้อหลัก */
    h1 { color: #00594C !important; font-weight: 800; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
    
    /* กล่องข้อความแชท */
    .stChatMessage {
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 15px;
        max-width: 85%;
    }
    
    /* แยกสีแชท: ผู้ใช้ (User) */
    div[data-testid="stChatMessage"]:has(span:contains("🧑‍🎓")) {
        background-color: #E6F4EA !important; /* เขียวอ่อน */
        margin-left: auto;
        border: 1px solid #CEEAD6;
    }

    /* แยกสีแชท: AI (Assistant) */
    div[data-testid="stChatMessage"]:has(span:contains("🦖")) {
        background-color: #FFFFFF !important;
        margin-right: auto;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* ปุ่มทางลัด (Quick Reply) */
    .stButton button {
        border-radius: 12px;
        border: 1px solid #00594C;
        background-color: white;
        color: #00594C;
        font-weight: 600;
        height: 3em;
        transition: 0.3s ease;
    }
    .stButton button:hover {
        background-color: #00594C;
        color: white;
        transform: translateY(-2px);
    }

    /* Animation จุดโหลด */
    .loading-dots { font-size: 25px; color: #00594C; font-weight: bold; }
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

# 3. จัดการ API และ Model
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ API Key")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower():
                    return genai.GenerativeModel(model_name=m.name)
        return genai.GenerativeModel(model_name='gemini-1.5-flash')
    except: return None

model = load_model()

# 4. Sidebar (ส่วนควบคุมข้างหน้าจอ)
with st.sidebar:
    st.image("https://www.ku.ac.th/assets/img/logo-ku.png", width=100) # โลโก้ มก. (URL ตัวอย่าง)
    st.title("เมนูใช้งาน")
    if st.button("🗑️ ล้างประวัติการแชท"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.info("น้องนนทรี AI ยินดีให้คำปรึกษาเรื่องอาคารสถานที่และข้อมูลมหาวิทยาลัยครับผม!")

# 5. หน้าจอหลัก
st.title("🦖 น้องนนทรี AI (KU SRC)")

# ปุ่มทางลัด (Quick Reply) - จัดกลุ่มให้น่าสนใจ
st.markdown("#### 💡 น้องอยากถามเรื่องอะไรครับ?")
btn_prompt = None
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("📍 พิกัดตึกเรียน"): btn_prompt = "ขอพิกัดตึกเรียนสำคัญใน มก. ศรีราชา"
with col2:
    if st.button("🍽️ ร้านอาหารเด็ด"): btn_prompt = "แนะนำของกินอร่อยๆ รอบ มก. ศรีราชา"
with col3:
    if st.button("📄 งานทะเบียน"): btn_prompt = "ติดต่อฝ่ายทะเบียนต้องทำยังไงบ้าง"
with col4:
    if st.button("🚌 การเดินทาง"): btn_prompt = "รถตะไลวิ่งยังไง"

# 6. ประวัติการแชท
if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงข้อความแชท
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# 7. ส่วนรับข้อความ
chat_input = st.chat_input("พิมพ์คำถามของน้องที่นี่...")
prompt = chat_input if chat_input else btn_prompt

if prompt:
    # แสดงข้อความผู้ใช้
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI ตอบกลับ
    with st.chat_message("assistant", avatar="🦖"):
        status_placeholder = st.empty()
        status_placeholder.markdown('<div class="loading-dots"></div>', unsafe_allow_html=True)
        
        # โหลดฐานข้อมูล
        if os.path.exists("ku_data.txt"):
            with open("ku_data.txt", "r", encoding="utf-8") as f:
                kb = f.read()
        else: kb = "ข้อมูล มก. ศรีราชา"

        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ของ มก. ศรีราชา (KU SRC) "
            "พูดจาสุภาพ เป็นกันเอง แทนตัวเองว่า 'พี่' และเรียกผู้ใช้ว่า 'น้อง' "
            "จงจำชื่อผู้ใช้หากเขาบอกชื่อมา และใช้ชื่อเขาในการทักทาย "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างแม่นยำ หากถามเรื่องตึก ต้องส่งลิงก์แผนที่เสมอ"
        )
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_p = f"{instruction}\n\nข้อมูล: {kb}\n\nประวัติ: {history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            status_placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            status_placeholder.empty()
            st.error(f"ขออภัยครับ เกิดข้อผิดพลาด: {e}")
