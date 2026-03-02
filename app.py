import streamlit as st
from styles import apply_custom_css, get_image_base64, translation
from logic import get_room_info, load_model, get_knowledge_base

# 1. Setup
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
apply_custom_css()

if "lang" not in st.session_state: st.session_state.lang = "TH"
if "messages" not in st.session_state: st.session_state.messages = []
if "all_chats" not in st.session_state: st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None

curr = translation[st.session_state.lang]
model = load_model()

# 2. Sidebar
with st.sidebar:
    if st.button(f"🌐 {st.session_state.lang}"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

    img_data = get_image_base64("logo_ku.png")
    if img_data:
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    if st.button(curr["new_chat"]):
        st.session_state.messages = []; st.session_state.current_chat_id = None; st.rerun()

    st.markdown("---")
    with st.expander(curr["forms"]):
        forms = [("ใบขอลงทะเบียน", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
                 ("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf")]
        for name, link in forms:
            st.markdown(f'<div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span>{name}</span><a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a></div>', unsafe_allow_html=True)

# 3. Chat Interface
st.markdown(f"<h2 style='color: #004D40;'><span class='dino-head'>🦖</span> AI KUSRC</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "🦖"):
        st.markdown(msg["content"])

if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: st.session_state.current_chat_id = prompt[:20]
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)

    with st.chat_message("assistant", avatar="🦖"):
        room_res = get_room_info(prompt, st.session_state.lang)
        if room_res:
            full_res = room_res
            st.markdown(full_res)
        else:
            placeholder = st.empty()
            placeholder.markdown(curr["loading"])
            try:
                kb = get_knowledge_base() # ดึงข้อมูล TXT + PDF จากคลังข้อมูล
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-5:]]
                chat = model.start_chat(history=history)
                full_ctx = f"{curr['ai_identity']}\nKnowledge Base:\n{kb}\n\nQuestion: {prompt}"
                response = chat.send_message(full_ctx, stream=True)
                full_res = ""
                for chunk in response:
                    full_res += chunk.text
                    placeholder.markdown(full_res + "▌")
                placeholder.markdown(full_res)
            except Exception as e:
                full_res = f"Error: {e}"; st.error(full_res)
        
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
    st.rerun()
