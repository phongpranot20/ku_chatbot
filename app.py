import streamlit as st
import google.generativeai as genai
import uuid

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# CSS ของฮอน (ขีดน้ำเงินติดหนึบ + ปุ่มขาว)
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; border-right: 1px solid #eee; }
    div.stButton > button {
        width: 100% !important; border: none !important;
        background-color: #ffffff !important; padding: 15px 10px !important;
        text-align: left !important; border-radius: 0px !important;
        border-bottom: 1px solid #f0f0f0 !important; color: #444 !important;
    }
    div[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #f8f9fa !important; border-left: 6px solid #007bff !important;
        color: #007bff !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key: genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in models if "flash" in m), models[0])
        return genai.GenerativeModel(selected)
    except: return None

model = load_model()

# --- ระบบจัดการหลายห้องแชท ---
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# สร้างแชทเริ่มต้น
if st.session_state.current_chat_id is None:
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]

# Sidebar แสดงประวัติ
with st.sidebar:
    st.title("ประวัติการแชท")
    if st.button("+ เริ่มแชทใหม่", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.write("---")
    for cid, cdata in reversed(list(st.session_state.chat_sessions.items())):
        if cdata["messages"]: # แสดงเฉพาะห้องที่มีการคุยแล้ว
            is_active = (cid == st.session_state.current_chat_id)
            if st.button(cdata["title"], key=cid, type="primary" if is_active else "secondary"):
                st.session_state.current_chat_id = cid
                st.rerun()

# พื้นที่แสดงแชท
st.title("AI TEST")
for m in current_chat["messages"]:
    with st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🦖"):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    # ตั้งชื่อหัวข้อแชทจากคำถามแรก
    if len(current_chat["messages"]) == 1:
        current_chat["title"] = prompt[:20]

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        try:
            # ส่งประวัติแค่ 3 ข้อความเพื่อให้ประมวลผลไวที่สุด
            history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in current_chat["messages"][-3:]])
            response = model.generate_content(f"คุณคือพี่นนทรี: {history}\nคำถาม: {prompt}", stream=True)
            
            full_res = ""
            for chunk in response:
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            current_chat["messages"].append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Error: {str(e)}")
