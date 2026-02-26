import streamlit as st
import google.generativeai as genai
import os

# --- 1. ตั้งค่าหน้าจอ (Page Config) ---
st.set_page_config(page_title="น้องนนทรี - KU Sriracha Bot", page_icon="🐯", layout="wide")

# --- 2. CSS ปรับแต่ง UI ให้เหมือนเรฟเฟอเรนซ์ ---
st.markdown("""
<style>
    /* พื้นหลังหน้าจอหลัก */
    .stApp { background-color: #FFFFFF; color: black; }
    
    /* Sidebar สไตล์เขียว มก. */
    [data-testid="stSidebar"] { 
        background-color: #00594C !important; 
        border-right: 1px solid #e0e0e0;
    }
    
    /* บังคับสีข้อความหัวข้อใน Sidebar */
    [data-testid="stSidebar"] h3, .sidebar-title { 
        color: #FFFFFF !important; 
        font-family: 'Tahoma', sans-serif;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    /* กล่องแบบฟอร์มสีขาว (White Card) */
    .form-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .form-info { display: flex; align-items: center; gap: 10px; }
    .form-name { color: #333333 !important; font-weight: bold; font-size: 14px; }
    
    /* ปรับแต่ง Expander ให้เป็นกล่องขาว */
    .st-emotion-cache-p5mtransition {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
    }
    
    /* สีข้อความใน Expander */
    .st-emotion-cache-p5mtransition p, .st-emotion-cache-p5mtransition span {
        color: #000000 !important;
    }

    /* หัวข้อ Chat หน้าหลัก */
    h1 { color: #00594C !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. ส่วนจัดการ API และ Model ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ ไม่พบ GEMINI_API_KEY ใน Streamlit Secrets")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_smart_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected_model = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        
        instruction = (
            "คุณคือ 'น้องนนทรี' AI รุ่นพี่ มก. ศรีราชา (KU SRC) "
            "ตอบคำถามรุ่นน้องด้วยความสุภาพ เป็นกันเอง "
            "เน้นดึงข้อมูลจาก 'ข้อมูลอ้างอิง' มาตอบเป็นหลัก"
        )
        return genai.GenerativeModel(model_name=selected_model, system_instruction=instruction)
    except Exception as e:
        st.error(f"Error: {e}")
        return None

model = load_smart_model()

# --- 4. ส่วน Sidebar: Dashboard พร้อมตรา มก. ---
with st.sidebar:
    # แสดงตรา มก. ศรีราชา (ใช้ URL รูปภาพหรือไฟล์ในโปรเจกต์)
    st.image("https://www.src.ku.ac.th/th/images/logo/KU_Sriracha_Logo.png", use_container_width=True)
    
    st.markdown("<h3 class='sidebar-title'>🎓 น้องนนทรี Student Dashboard</h3>", unsafe_allow_html=True)
    
    # ส่วนของกล่องขาวใส่ลิงก์แบบฟอร์ม
    st.markdown("### 📄 ลิงก์แบบฟอร์มด่วน (คลิก)")
    
    with st.expander("เปิดรายการแบบฟอร์ม", expanded=True):
        # แบบที่ 1: Registrar-2
        st.markdown("""
        <div style="background-color:#f9f9f9; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #ddd;">
            <p style="color:black; font-weight:bold; margin-bottom:5px;">📝 คำร้องขอลงทะเบียน (Registrar-2)</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("📥 ดาวน์โหลด PDF", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf", use_container_width=True)
        
        # แบบที่ 2: Registrar-1
        st.markdown("""
        <div style="background-color:#f9f9f9; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #ddd; margin-top:10px;">
            <p style="color:black; font-weight:bold; margin-bottom:5px;">📑 คำร้องทั่วไป (Registrar-1)</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("📥 ดาวน์โหลด PDF", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf", use_container_width=True)

        # แบบที่ 3: KU3 Online
        st.markdown("""
        <div style="background-color:#f9f9f9; padding:10px; border-radius:8px; margin-bottom:8px; border:1px solid #ddd; margin-top:10px;">
            <p style="color:black; font-weight:bold; margin-bottom:5px;">💻 เพิ่ม-ถอน (KU3) ออนไลน์</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🌐 ไปที่เว็บไซต์", "https://reg2.src.ku.ac.th/download.html", use_container_width=True)

    st.markdown("---")
    st.caption("💡 ถามพี่นนทรีได้เลย เช่น 'ตึก 17 อยู่ไหน' หรือ 'ขอใบดรอปเรียน'")

# --- 5. การจัดการ Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# โหลดฐานข้อมูลจากไฟล์
if os.path.exists("ku_data.txt"):
    with open("ku_data.txt", "r", encoding="utf-8") as f:
        knowledge_base = f.read()
else:
    knowledge_base = "ข้อมูล มก. ศรีราชา"

# แสดง UI หน้าหลัก
st.markdown("## 🐯 น้องนนทรี: เพื่อนคู่คิด นิสิต มก.ศรช.")

for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🐯"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if prompt := st.chat_input("พิมพ์คำถามที่นี่..."):
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🐯"):
        placeholder = st.empty()
        placeholder.markdown("*(พี่กำลังพิมพ์...)*")
        
        history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                   for m in st.session_state.messages[-6:-1]]
        
        try:
            chat_session = model.start_chat(history=history)
            full_context = f"ข้อมูลอ้างอิง:\n{knowledge_base}\n\nคำถาม: {prompt}"
            
            response = chat_session.send_message(full_context, stream=True)
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
