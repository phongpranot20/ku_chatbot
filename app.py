import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU SRC AI - น้องนนทรี", page_icon="🦖", layout="wide")

# --- CUSTOM CSS: ULTIMATE DESIGN WITH SIDEBAR STYLE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    * { font-family: 'Kanit', sans-serif; }
    .stApp { background: radial-gradient(circle at top left, #f0fdf4 0%, #ffffff 100%); }
    
    /*Sidebar - สไตล์พรีเมียมเข้ม */
    [data-testid="stSidebar"] {
        background-color: #004d43 !important;
        border-right: 1px solid rgba(255,255,255,0.1);
        color: white !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* หัวข้อใน Sidebar */
    .sidebar-title {
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        margin-bottom: 20px;
    }

    /* ตกแต่ง Chat Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        margin-bottom: 10px !important;
    }

    /* จุด Loading */
    .loading-container { display: flex; gap: 5px; padding: 10px; }
    .dot { width: 10px; height: 10px; background: #00594C; border-radius: 50%; animation: wave 1.3s linear infinite; }
    .dot:nth-child(2) { animation-delay: -1.1s; }
    .dot:nth-child(3) { animation-delay: -0.9s; }
    @keyframes wave { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-10px); } }
</style>
""", unsafe_allow_html=True)

# --- AI SETUP ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

@st.cache_resource
def load_ai():
    try:
        # ระบบหาโมเดลอัตโนมัติเพื่อให้ไม่พัง
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if "flash" in m.name.lower(): return genai.GenerativeModel(m.name)
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = load_ai()

# --- SIDEBAR: CHAT HISTORY & INFO ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🦖 พี่นนทรี History</div>", unsafe_allow_html=True)
    
    # ส่วนแสดงประวัติย่อ (ดึงคำถามล่าสุดมาโชว์)
    if "messages" in st.session_state and len(st.session_state.messages) > 0:
        st.markdown("💬 **บทสนทนาล่าสุด:**")
        # ดึงมาโชว์เฉพาะคำถามจาก User 5 อันล่าสุด
        user_msgs = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        for msg in user_msgs[-5:]:
            st.caption(f"• {msg[:30]}..." if len(msg) > 30 else f"• {msg}")
    else:
        st.caption("ยังไม่มีประวัติการคุยในเซสชันนี้")

    st.markdown("---")
    
    # ปุ่มล้างแชทแบบสวยๆ
    if st.button("✨ ล้างประวัติการแชท", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN CONTENT ---
st.title("🦖 น้องนนทรี AI (KU SRC)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# แสดงข้อความแชททั้งหมด (ประวัติการแชทในหน้าหลัก)
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🦖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# รับ Input
if prompt := st.chat_input("พิมพ์ข้อความคุยกับพี่นนทรี..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        status = st.empty()
        status.markdown('<div class="loading-container"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>', unsafe_allow_html=True)
        
        # Load Knowledge Base
        kb = ""
        if os.path.exists("ku_data.txt"):
            with open("ku_data.txt", "r", encoding="utf-8") as f: kb = f.read()

        instruction = (
            "คุณคือ 'พี่นนทรี' รุ่นพี่ของ มก. ศรีราชา "
            "ตอบแบบสุภาพเป็นกันเอง แทนตัวเองว่าพี่ และจำชื่อน้องให้ได้เสมอ"
        )
        
        # ส่งประวัติย้อนหลัง 10 ข้อความเพื่อให้บอทจำได้ (Memory)
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]])
        full_p = f"{instruction}\n\nข้อมูล: {kb}\n\nประวัติ: {history}\n\nคำถาม: {prompt}"
        
        try:
            response = model.generate_content(full_p)
            status.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            # สั่ง rerun เพื่ออัปเดตประวัติใน Sidebar ทันที
            st.rerun()
        except Exception as e:
            status.empty()
            st.error(f"พี่ขัดข้องนิดหน่อย: {e}")
