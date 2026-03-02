import streamlit as st
from styles import apply_custom_css, get_image_base64, translation
from logic import get_room_info, load_model, get_knowledge_base

# --- Setup ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
apply_custom_css()

if "lang" not in st.session_state: st.session_state.lang = "TH"
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "นิสิต"

curr = translation[st.session_state.lang]
model = load_model()

# --- Sidebar ---
with st.sidebar:
    if st.button(f"🌐 {st.session_state.lang}"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

    img_data = get_image_base64("logo_ku.png")
    if img_data:
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    if st.button(curr["new_chat"]):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    if st.session_state.all_chats:
        st.markdown(f'<p style="font-weight:700; margin-top:10px;">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    with st.expander(curr["exam_table"]):
        st.markdown(f'<div style="display:flex; justify-content:space-between;"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["gpa_calc"]):
        st.markdown(f'<div style="display:flex; justify-content:space-between;"><span>GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    with st.expander(curr["forms"]):
        forms = [
            ("ใบขอลงทะเบียนเรียน", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ใบผ่อนผันค่าเทอม", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ใบลงทะเบียนเรียน", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("ใบเพิ่ม-ถอน", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        for name, link in forms:
            st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="font-size:0.9rem;">{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# --- Chat Interface ---
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ("แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.markdown(f"<h2 style='color: #004D40;'><span class='dino-head'>🦖</span> AI KUSRC</h2>", unsafe_allow_html=True)
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        room_info = get_room_info(prompt, st.session_state.lang)
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown(curr["loading"])
            try:
                kb = get_knowledge_base()
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                full_context = f"{curr['ai_identity']} คุยกับน้องชื่อ {st.session_state.global_user_nickname} ข้อมูลมหาลัย:\n{kb}\n\nคำถาม: {prompt}"
                response = chat_session.send_message(full_context, stream=True)
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Error: {e}"
                st.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.rerun()
