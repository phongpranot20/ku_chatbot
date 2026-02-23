import streamlit as st
import google.generativeai as genai
import uuid

# --- 1. CSS ขั้นสูงสุด (บังคับขีดน้ำเงินติดหนึบ + New Chat สีขาว) ---
st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    /* สไตล์ Sidebar สีขาวคลีน */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #eee; 
    }
    
    /* สไตล์ปุ่มประวัติ (ทรงสี่เหลี่ยมสีขาว) */
    div.stButton > button {
        width: 100% !important;
        border: none !important;
        background-color: #ffffff !important;
        padding: 15px 10px !important;
        text-align: left !important;
        border-radius: 0px !important;
        border-bottom: 1px solid #f0f0f0 !important;
        color: #444 !important;
        display: block !important;
        transition: 0.1s;
    }

    /* บังคับขีดสีน้ำเงินด้านซ้ายสำหรับห้องที่เลือก (Active) */
    /* ใช้ CSS selector ที่เจาะจงระดับสูงสุดเพื่อให้แถบสีแสดงผล */
    div[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #f8f9fa !important; 
        border-left: 6px solid #007bff !important; /* ขีดน้ำเงินที่ฮอนต้องการ */
        color: #007bff !important;
        font-weight: 600 !important;
    }

    /* ปุ่ม New Chat: สีขาวสะอาดขอบบาง */
    .stSidebar [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #ffffff !important;
        color: #333 !important;
        border-radius: 8px !important;
        text-align: center !important;
        border: 1px solid #ddd !important;
        margin-bottom: 20px !important;
        border-left: none !important; /* ไม่มีขีดซ้าย */
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

# --- 2. Setup Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. Initialization (ใช้แค่ Session State ไม่มีการเซฟลงไฟล์) ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# สร้างแชทเริ่มต้น
if st.session_state.current_chat_id is None:
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

current_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_id]

# --- 4. Sidebar ---
with st.sidebar:
    st.header("เมนูควบคุม")
    # ปุ่ม New Chat (สีขาว)
    if st.button("New Chat", use_container_width=True):
        if len(current_chat["messages"]) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    # วนลูปสร้างปุ่มประวัติแชท
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == current_id)
            
            # ใช้ type="primary" เพื่อให้ CSS ขีดซ้ายทำงาน
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

# --- 5. แสดงผลแชท (🧑‍🎓 บัณฑิต / 🦖 ไดโนเสาร์) ---
for m in current_chat["messages"]:
    avatar = "🧑‍🎓" if m["role"] == "user" else "🦖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    if len(current_chat["messages"]) == 1:
        current_chat["title"] = prompt[:25]

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        history = "\n".join([f"{m['role']}: {m['content']}" for m in current_chat["messages"][-10:]])
        try:
            response = model.generate_content(f"คุณคือพี่นนทรี AI\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}")
            placeholder.markdown(response.text)
            current_chat["messages"].append({"role": "assistant", "content": response.text})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
