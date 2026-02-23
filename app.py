import streamlit as st
import google.generativeai as genai
import uuid

st.set_page_config(page_title="AI TEST", layout="wide")

# CSS เท่าที่จำเป็นเพื่อคงหน้าตาแบบเดิม
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #eee; }
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
        # ใช้ list_models ตามที่ฮอนขอ เพื่อลด 404
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = next((m for m in available if "flash" in m), available[0])
        return genai.GenerativeModel(name)
    except: return None

model = load_model()

if "chat_sessions" not in st.session_state: st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

current_chat = st.session_state.chat_sessions[st.session_state.current_chat_id]

# Sidebar
with st.sidebar:
    if st.button("New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    st.write("---")
    for cid, cdata in reversed(list(st.session_state.chat_sessions.items())):
        if cdata["messages"]:
            if st.button(cdata["title"], key=cid, type="primary" if cid == st.session_state.current_chat_id else "secondary"):
                st.session_state.current_chat_id = cid
                st.rerun()

for m in current_chat["messages"]:
    with st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🦖"):
        st.markdown(m["content"])

if prompt := st.chat_input("พิมพ์ข้อความ..."):
    with st.chat_message("user", avatar="🧑‍🎓"): st.markdown(prompt)
    current_chat["messages"].append({"role": "user", "content": prompt})
    if len(current_chat["messages"]) == 1: current_chat["title"] = prompt[:20]

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        full_res = ""
        try:
            # ไม่ส่งประวัติเลย เพื่อให้ Server คิดคำตอบไวที่สุด
            for chunk in model.generate_content(prompt, stream=True):
                full_res += chunk.text
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            current_chat["messages"].append({"role": "assistant", "content": full_res})
        except Exception as e: st.error(str(e))
