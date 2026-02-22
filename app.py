import streamlit as st
import google.generativeai as genai
import os
import random
from datetime import date
import time

st.set_page_config(page_title="KU SRC AI - พี่นนทรี", page_icon="🦖", layout="wide")

# --- CUSTOM CSS: FUN & PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    * { font-family: 'Kanit', sans-serif; }
    .stApp { background: radial-gradient(circle at top left, #f0fdf4 0%, #ffffff 100%); }
    
    /* สไตล์ปุ่มแบบกดแล้วมี Feedback */
    div.stButton > button {
        border-radius: 25px !important;
        border: 2px solid #00594C !important;
        transition: all 0.2s ease;
        font-weight: 600 !important;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    /* แถบข้างสไตล์วัยรุ่น */
    [data-testid="stSidebar"] { background-color: #004d43 !important; }
    
    /* หัวข้อขยับได้นิดๆ */
    .main-title {
        font-size: 40px; font-weight: 800;
        background: linear-gradient(90deg, #00594C, #FFA500);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIC SETUP ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ลืมใส่ API Key ใน Secrets นะฮอน")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SIDEBAR (FUN STUFF) ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center;'>🦖</h1>", unsafe_allow_html=True)
    
    # ฟีเจอร์ที่ 1: เซียมซีดิจิทัล (Function 1)
    st.markdown("🔮 **เซียมซีเด็กเกษตร**")
    if st.button("🎋 เสี่ยงทายดวงวันนี้"):
        fortunes = [
            "โชคดี: วันนี้จะไปเรียนสายแต่จารย์ยังไม่เช็คชื่อ!",
            "คำเตือน: ระวังโดนไก่จิกแถวโรง 2",
            "โชคดี: โรงอาหารคนน้อย ได้กินร้านโปรดแน่นอน",
            "คำเตือน: วันนี้แอร์ในห้องเรียนจะหนาวกว่าขั้วโลกเหนือ",
            "โชคดี: สุ่มเลขที่ตอบคำถาม จะไม่โดนชื่อเรา!",
            "ความรัก: จะเจอคนหน้าตาดีแถวตึก 10"
        ]
        st.success(random.choice(fortunes))
    
    st.markdown("---")
    exam_date = date(2026, 3, 2)
    days_left = (exam_date - date.today()).days
    st.warning(f"⚠️ อีก {days_left} วันสอบ! อ่านหนังสือยัง?")
    
    if st.button("✨ ล้างแชท"):
        st.session_state.messages = []
        st.rerun()

# --- MAIN UI ---
st.markdown("<h1 class='main-title'>🦖 พี่นนทรี AI: รุ่นพี่สายปั่น</h1>", unsafe_allow_html=True)

# ปุ่มทางลัด (Function 3 & 5)
col1, col2, col3, col4 = st.columns(4)
btn_prompt = None
with col1:
    if st.button("📍 พิกัดตึกเรียน"): btn_prompt = "ขอพิกัดตึกเรียนและร้านลับๆ ในมอ"
with col2:
    if st.button("🎲 สุ่มเมนูอาหาร"):
        menus = ["ข้าวมันไก่โรง 1", "ก๋วยเตี๋ยวเรือข้างมอ", "ข้าวแกงป้าแดง", "สเต็กเด็กแนว"]
        btn_prompt = f"พี่สุ่มได้ '{random.choice(menus)}' กินอันนี้แหละไม่ต้องคิดเยอะ!"
with col3:
    if st.button("🐣 ความลับ มก."): btn_prompt = "เล่าเรื่องลี้ลับหรือเรื่องตลกๆ ใน มก. ศรีราชา ให้ฟังหน่อย"
with col4:
    if st.button("💖 จีบสาว มก."): btn_prompt = "ขอวิธีจีบสาว/หนุ่ม ใน มก. ศรีราชา สไตล์เด็กเกษตรหน่อยพี่"

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑‍🎓" if m["role"] == "user" else "🦖"):
        st.markdown(m["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("คุยกับพี่นนทรี (ลองถามเรื่องดวง หรือ เรื่องผีดูสิ)"):
    btn_prompt = prompt

if btn_prompt:
    st.chat_message("user", avatar="🧑‍🎓").markdown(btn_prompt)
    st.session_state.messages.append({"role": "user", "content": btn_prompt})

    with st.chat_message("assistant", avatar="🦖"):
        placeholder = st.empty()
        placeholder.markdown("กำลังใช้จิตสัมผัสประมวลผล...")
        
        # Easter Eggs Check (Function 2)
        if "ไก่" in btn_prompt:
            easter_egg = "พูดถึงไก่หรอ? พี่เคยโดนมันวิ่งไล่กวดหน้าตึกเรียนด้วยนะ ขนลุกเลย! 🐔"
        elif "เกรด" in btn_prompt or "F" in btn_prompt:
            easter_egg = "อย่าพูดคำว่า F ในห้องนี้! พี่ใจคอไม่ดี ไปไหว้พระพิรุณกันเถอะน้อง 🙏"
        else:
            easter_egg = ""

        instruction = (
            "คุณคือ 'พี่นนทรี' รุ่นพี่สุดกวนและเป็นกันเองแห่ง มก. ศรีราชา "
            "พูดจาสนิทสนม มีอารมณ์ขัน ชอบใช้คำศัพท์วัยรุ่น แซวผู้ใช้บ้างเป็นครั้งคราว "
            "รู้ลึกเรื่อง มก. ศรีราชา ทั้งเรื่องเรียน เรื่องกิน และเรื่องเที่ยว"
        )
        
        history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]])
        full_p = f"{instruction}\n\n{easter_egg}\n\nประวัติ: {history}\n\nคำถาม: {btn_prompt}"
        
        try:
            response = model.generate_content(full_p)
            placeholder.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            placeholder.error("พี่มึนตึ้บเลยน้อง ลองใหม่สิ!")
