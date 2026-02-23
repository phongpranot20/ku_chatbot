import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="KU Sriracha Bot", page_icon="🐢", layout="wide")

# --- CSS คงเดิมและเพิ่มสไตล์ Sidebar ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; color: black !important; }
    [data-testid="stSidebar"] { background-color: #f2f9f6 !important; }
    h1, h2, h3, p, span, div { color: #00594C; }
    [data-testid="stChatMessage"] { background-color: #f0f2f6; border-radius: 10px; }
    .stMarkdown p { color: #333333 !important; }

    /* ตกแต่ง Sidebar */
    .sidebar-history {
        font-size: 14px;
        color: #4F4F4F;
        padding: 5px;
        border-bottom: 1px solid #ddd;
    }

    .loading-dots {
        font-size: 30px;
        font-weight: bold;
        display: inline-block;
    }
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

# --- ส่วนจัดการ API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ในหน้า Settings > Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in models if "flash" in m), models[0])
        return genai.GenerativeModel(model_name=selected)
    except Exception as e:
        return None

model = load_model()

if not model:
    st.error("❌ ไม่พบโมเดลที่ใช้งานได้")
    st.stop()

# --- ส่วนจัดการ Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ส่วน Sidebar: ประวัติการแชท ---
with st.sidebar:
    st.title("📜 ประวัติการคุย")
    
    # ปุ่มล้างแชท
    if st.button("🗑️ ล้างประวัติการสนทนา"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # แสดงรายการคำถามที่เคยถามใน Sidebar
    if not st.session_state.messages:
        st.write("ยังไม่มีประวัติการคุย")
    else:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                # ตัดคำให้สั้นลงถ้าประโยคยาวเกินไป
                display_text = (msg["content"][:30] + '..') if len(msg["content"]) > 30 else msg["content"]
                st.markdown(f"**{i//2 + 1}.** {display_text}")

# --- หน้าจอหลัก ---
st.title("AI TEST - น้องนนทรี 🦖")

# โหลดข้อมูล Knowledge Base
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูลมหาวิทยาลัยเกษตรศาสตร์ วิทยาเขตศรีราชา"

# แสดงประวัติการคุยในหน้า Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

# ส่วนรับคำถาม
if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.markdown('<div class="loading-dots"></div>', unsafe_allow_html=True)
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา "
            "ตอบคำถามตามข้อมูลที่ให้มาอย่างสุภาพ"
        )
        
        # ส่งประวัติล่าสุดเพื่อบริบทที่ต่อเนื่อง
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
        full_prompt = f"{instruction}\n\nข้อมูล: {knowledge_base}\n\nประวัติ:\n{history_text}\n\nคำถามล่าสุด: {prompt}"
        
        try:
            response = model.generate_content(full_prompt, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # สั่ง rerun เพื่อให้ Sidebar อัปเดตข้อมูลล่าสุดทันที
            st.rerun()
            
        except Exception as e:
            placeholder.empty()
            st.error(f"Error: {str(e)}")
