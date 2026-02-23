import streamlit as st
import google.generativeai as genai
import uuid

st.set_page_config(page_title="AI TEST", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #eee; 
    }
    
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
    }

    div[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #f8f9fa !important; 
        border-left: 6px solid #007bff !important;
        color: #007bff !important;
        font-weight: 600 !important;
    }

    .stSidebar [data-testid="stVerticalBlock"] > div:nth-child(2) button {
        background-color: #ffffff !important;
        color: #333 !important;
        border-radius: 8px !important;
        text-align: center !important;
        border: 1px solid #ddd !important;
        margin-bottom: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI TEST")

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@st.cache_resource
def load_working_model():
    try:
        # เปลี่ยนมาใช้ชื่อรุ่นที่ครอบคลุม v1 และ v1beta
        return genai.GenerativeModel('gemini-1.5-flash-latest')
    except:
        try:
            # สำรองด้วยชื่อรุ่น gemini-pro ถ้า flash ยังหาไม่เจอ
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            return e

model = load_working_model()

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if st.session_state.current_chat_id is None:
    new_id = str(uuid.uuid4())
    st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat_id = new_id

current_id = st.session_state.current_chat_id
current_chat = st.session_state.chat_sessions[current_id]

with st.sidebar:
    st.header("เมนูควบคุม")
    if st.button("New Chat", use_container_width=True):
        if len(current_chat["messages"]) > 0:
            new_id = str(uuid.uuid4())
            st.session_state.chat_sessions[new_id] = {"title": "New Chat", "messages": []}
            st.session_state.current_chat_id = new_id
            st.rerun()
    
    st.write("---")
    st.subheader("ประวัติการคุย")
    
    for chat_id, chat_data in reversed(list(st.session_state.chat_sessions.items())):
        if len(chat_data["messages"]) > 0:
            is_active = (chat_id == current_id)
            if st.button(
                chat_data["title"], 
                key=chat_id, 
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.current_chat_id = chat_id
                st.rerun()

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
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in current_chat["messages"][-2:]])
        try:
            if isinstance(model, genai.GenerativeModel):
                # ใช้คำสั่งตอบกลับมาตรฐาน
                response = model.generate_content(f"คุณคือพี่นนทรี\n\nประวัติ:\n{history}\n\nคำถาม: {prompt}")
                placeholder.markdown(response.text)
                current_chat["messages"].append({"role": "assistant", "content": response.text})
                st.rerun()
            else:
                st.error(f"Model Load Error: {str(model)}")
        except Exception as e:
            # พ่น Error จริงที่เกิดขึ้นออกมา
            st.error(f"Execution Error: {str(e)}")
