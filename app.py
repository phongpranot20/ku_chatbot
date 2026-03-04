import streamlit as st
from styles import apply_custom_css, get_image_base64, translation
from logic import get_room_info, load_model, get_knowledge_base

# --- 1. การตั้งค่าหน้าจอ (Setup) ---
st.set_page_config(page_title="AI KUSRC", page_icon="🦖", layout="wide")
apply_custom_css()

# จัดการ Session State
if "lang" not in st.session_state: st.session_state.lang = "TH"
if "all_chats" not in st.session_state: st.session_state.all_chats = {} 
if "messages" not in st.session_state: st.session_state.messages = []
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = None
if "global_user_nickname" not in st.session_state: st.session_state.global_user_nickname = "นิสิต"

curr = translation[st.session_state.lang]
model = load_model()

# --- 2. ส่วนแถบข้าง (Sidebar) ---
with st.sidebar:
    # ปุ่มสลับภาษา
    if st.button(f"🌐 {st.session_state.lang}"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

    # โลโก้และชื่อมหาลัย
    img_data = get_image_base64("logo_ku.png")
    if img_data:
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    # ปุ่มแชทใหม่
    if st.button(curr["new_chat"], key="new_chat_btn"):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    # ประวัติการแชท (Chat History)
    if st.session_state.all_chats:
        st.markdown(f'<p style="font-weight:700; margin-top:10px;">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    st.markdown('<p style="font-weight:700; margin-bottom: 10px;">Quick Links</p>', unsafe_allow_html=True)
    
    # [Quick Link 1] ค้นหาตารางสอบ
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    # [Quick Link 2] คำนวณเกรด (GPAX)
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><span>GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    # [Quick Link 3] ลิงก์แบบฟอร์มต่างๆ (ครบถ้วน 7 รายการตามไฟล์ ku_data.txt)
    with st.expander(curr["forms"], expanded=False):
        forms = [
            ("Registrar-1 คำร้องทั่วไป (General)", "https://regis.src.ku.ac.th/student/news/kamrong/1%20%E0%B8%84%E0%B8%B3%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%97%E0%B8%B1%E0%B9%88%E0%B8%A7%E0%B9%84%E0%B8%9B%20(General)-Revised.pdf"),
            ("Registrar-2 ขอลงทะเบียนเรียน/ถอนรายวิชา (Registration)", "https://regis.src.ku.ac.th/student/news/kamrong/2%20%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%87%E0%B8%97%E0%B8%B0%E0%B9%80%E0%B8%9A%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99(Registration)-Revised.pdf"),
            ("Registrar-3 ขอผ่อนผัน(Postpone tuition)", "https://regis.src.ku.ac.th/student/news/kamrong/3%20%E0%B8%82%E0%B8%AD%E0%B8%9C%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B8%9C%E0%B8%B1%E0%B8%99(Postpone%20tuition)-Revised.pdf"),
            ("Registrar-4 ขอลงทะเบียนเรียนควบ (Continuing course with prerequistie)", "https://regis.src.ku.ac.th/student/news/kamrong/4%20%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%87%E0%B8%97%E0%B8%B0%E0%B9%80%E0%B8%9A%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B8%84%E0%B8%A7%E0%B8%9A(Continuing%20course%20with%20prerequistie)-Revised.pdf"), #
            ("Registrar-5 ขอลงทะเบียนเรียนข้ามวิทยาเขต สถาบัน (Cross campus)", "https://regis.src.ku.ac.th/student/news/kamrong/5%20%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%87%E0%B8%97%E0%B8%B0%E0%B9%80%E0%B8%9A%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A1%E0%B8%A7%E0%B8%B4%E0%B8%97%E0%B8%A2%E0%B8%B2%E0%B9%80%E0%B8%82%E0%B8%95%20%E0%B8%AA%E0%B8%96%E0%B8%B2%E0%B8%9A%E0%B8%B1%E0%B8%99(Cross%20campus)-Revised.pdf"), #
            ("Registrar-6 ขอย้ายหลักสูตรหรือสาขาวิชาเอก (change major)", "https://regis.src.ku.ac.th/student/news/kamrong/6%20%E0%B8%82%E0%B8%AD%E0%B8%A2%E0%B9%89%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%A5%E0%B8%B1%E0%B8%81%E0%B8%AA%E0%B8%B9%E0%B8%95%E0%B8%A3%E0%B8%AB%E0%B8%A3%E0%B8%B7%E0%B8%AD%E0%B8%AA%E0%B8%B2%E0%B8%82%E0%B8%B2%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2%E0%B9%80%E0%B8%AD%E0%B8%81(change%20major)-Revised.pdf") #
            ("Registrar-7 ขอย้ายคณะ (change faculty) ", "https://regis.src.ku.ac.th/student/news/kamrong/7%20%E0%B8%82%E0%B8%AD%E0%B8%A2%E0%B9%89%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%93%E0%B8%B0%20(change%20faculty)-Revised.pdf") #
            ("Registrar-8 ขอเทียบรายวิชา(course transfer)", "https://regis.src.ku.ac.th/student/news/kamrong/8%20%E0%B8%82%E0%B8%AD%E0%B9%80%E0%B8%97%E0%B8%B5%E0%B8%A2%E0%B8%9A%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2(course%20transfer)-Revised.pdf") #
            ("Registrar-9 ขอเทียบรายวิชาและการโอนหน่วยกิต (course and credit transfer)", "https://regis.src.ku.ac.th/student/news/kamrong/9%20%E0%B8%82%E0%B8%AD%E0%B9%80%E0%B8%97%E0%B8%B5%E0%B8%A2%E0%B8%9A%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%82%E0%B8%AD%E0%B8%99%E0%B8%AB%E0%B8%99%E0%B9%88%E0%B8%A7%E0%B8%A2%E0%B8%81%E0%B8%B4%E0%B8%95(course%20and%20credit%20transfer)-Revised.pdf") #
            ("Registrar-10 ขอลาพักการศึกษา (leave of absence)", "https://regis.src.ku.ac.th/student/news/kamrong/10%20%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%B2%E0%B8%9E%E0%B8%B1%E0%B8%81%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%A8%E0%B8%B6%E0%B8%81%E0%B8%A9%E0%B8%B2(leave%20of%20absence)-Revised.pdf") #
            ("Registrar-11 ขอรักษาสถานภาพนิสิต (Maintain student statusMaintain student status) ", "https://regis.src.ku.ac.th/student/news/kamrong/11%20%E0%B8%82%E0%B8%AD%E0%B8%A3%E0%B8%B1%E0%B8%81%E0%B8%A9%E0%B8%B2%E0%B8%AA%E0%B8%96%E0%B8%B2%E0%B8%99%E0%B8%A0%E0%B8%B2%E0%B8%9E%E0%B8%99%E0%B8%B4%E0%B8%AA%E0%B8%B4%E0%B8%95(Maintain%20student%20statusMaintain%20student%20status)-Revised.pdf") #
            ("Registrar-12 ขอกลับเข้าศึกษาต่อ (Re- admission) ", "https://regis.src.ku.ac.th/student/news/kamrong/12%20%E0%B8%82%E0%B8%AD%E0%B8%81%E0%B8%A5%E0%B8%B1%E0%B8%9A%E0%B9%80%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A8%E0%B8%B6%E0%B8%81%E0%B8%A9%E0%B8%B2%E0%B8%95%E0%B9%88%E0%B8%AD%20(Re-%20admission)-Revised.pdf") #
            ("Registrar-13 ขอคืนสภาพนิสิต (Student Reinstatement)", "https://regis.src.ku.ac.th/student/news/kamrong/13%20%E0%B8%82%E0%B8%AD%E0%B8%84%E0%B8%B7%E0%B8%99%E0%B8%AA%E0%B8%A0%E0%B8%B2%E0%B8%9E%E0%B8%99%E0%B8%B4%E0%B8%AA%E0%B8%B4%E0%B8%95(Student%20Reinstatement)-Revised.pdf") #
            ("Registrar-14 ขอสอบชดใช้ (make-up exam)", "https://regis.src.ku.ac.th/student/news/kamrong/14%20%E0%B8%82%E0%B8%AD%E0%B8%AA%E0%B8%AD%E0%B8%9A%E0%B8%8A%E0%B8%94%E0%B9%83%E0%B8%8A%E0%B9%89%20(make-up%20exam)-Revised.pdf") #
            ("Registrar-15 ใบลา (leave) ", "https://regis.src.ku.ac.th/student/news/kamrong/15%20%E0%B9%83%E0%B8%9A%E0%B8%A5%E0%B8%B2%20(leave)-Revised.pdf") #
            ("Registrar-16 ขอลาออกพร้อมขอคืนค่าประกันของเสียหาย (Resignation or refund of Insurance)", "https://regis.src.ku.ac.th/student/news/kamrong/16%20%20%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%B2%E0%B8%AD%E0%B8%AD%E0%B8%81%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%82%E0%B8%AD%E0%B8%84%E0%B8%B7%E0%B8%99%E0%B8%84%E0%B9%88%E0%B8%B2%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B1%E0%B8%99%E0%B8%82%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%AA%E0%B8%B5%E0%B8%A2%E0%B8%AB%E0%B8%B2%E0%B8%A2%20(Resignation%20or%20refund%20of%20Insurance)-Revised.pdf") #
            ("Registrar-17 ขอคืนค่าประกันของเสียหาย (Refund of Insurance)", "https://regis.src.ku.ac.th/student/news/kamrong/17%20%E0%B8%82%E0%B8%AD%E0%B8%84%E0%B8%B7%E0%B8%99%E0%B8%84%E0%B9%88%E0%B8%B2%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B1%E0%B8%99%E0%B8%82%E0%B8%AD%E0%B8%87%E0%B9%80%E0%B8%AA%E0%B8%B5%E0%B8%A2%E0%B8%AB%E0%B8%B2%E0%B8%A2%20(Refund%20of%20Insurance)-Revised.pdf") #
            ("Registrar-18 ขอคืนเงิน (Refund of tuition fee) ", "https://regis.src.ku.ac.th/student/news/kamrong/18%20%E0%B8%82%E0%B8%AD%E0%B8%84%E0%B8%B7%E0%B8%99%E0%B9%80%E0%B8%87%E0%B8%B4%E0%B8%99%20(Refund%20of%20tuition%20fee)-Revised.pdf") #
            ("Registrar-19 คำร้องขอหนังสื่อรับรองรายวิชา(กรณีสอบวิชาชีพครู) (Course Certificate)  ", "https://regis.src.ku.ac.th/student/news/kamrong/19%20%E0%B8%84%E0%B8%B3%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%82%E0%B8%AD%E0%B8%AB%E0%B8%99%E0%B8%B1%E0%B8%87%E0%B8%AA%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%A3%E0%B8%B1%E0%B8%9A%E0%B8%A3%E0%B8%AD%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2(%E0%B8%81%E0%B8%A3%E0%B8%93%E0%B8%B5%E0%B8%AA%E0%B8%AD%E0%B8%9A%E0%B8%A7%E0%B8%B4%E0%B8%8A%E0%B8%B2%E0%B8%8A%E0%B8%B5%E0%B8%9E%E0%B8%84%E0%B8%A3%E0%B8%B9)(Course%20Certificate)-Revised.pdf") #
            ("Registrar-20 คำร้องขอลงทะเบียนเรียนเพิ่ม (Add Registration) ", "https://regis.src.ku.ac.th/student/news/kamrong/20%20%E0%B8%84%E0%B8%B3%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%87%E0%B8%82%E0%B8%AD%E0%B8%A5%E0%B8%87%E0%B8%97%E0%B8%B0%E0%B9%80%E0%B8%9A%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%80%E0%B8%9E%E0%B8%B4%E0%B9%88%E0%B8%A1%20(Add%20Registration).pdf") #
            ("Registrar-KU1 -Registration-Form", "https://regis.src.ku.ac.th/student/news/kamrong/KU1-Registration-Form.pdf") #
            ("Registrar-KU3 -Add-Drop-form", "https://regis.src.ku.ac.th/student/news/kamrong/KU3-Add-Drop-form.pdf") #
            ("Registrar-0 คำร้องขอลงทะเบียนเรียนวิชาเทียบประสบการณ์การเรียนรู้", "https://regis.src.ku.ac.th/student/news/kamrong/68CompareExperiences.pdf") #
        ]
        for name, link in forms:
            st.markdown(f'''
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="font-size:0.85rem;">{name}</span>
                    <a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a>
                </div>
            ''', unsafe_allow_html=True)

# --- 3. หน้าจอการแชท (Chat Interface) ---
current_title = st.session_state.current_chat_id if st.session_state.current_chat_id else ("แชทใหม่" if st.session_state.lang == "TH" else "New Chat")
st.markdown(f"<h2 style='color: #004D40;'><span class='dino-head'>🦖</span> AI KUSRC</h2>", unsafe_allow_html=True)
st.caption(f"👤 {curr['welcome']} {st.session_state.global_user_nickname} | {curr['topic']}: {current_title}")

# แสดงข้อความ
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🦖"):
        st.markdown(message["content"])

# ส่วนรับ Input
if prompt := st.chat_input(curr["input_placeholder"]):
    if st.session_state.current_chat_id is None: 
        st.session_state.current_chat_id = prompt[:20]
    
    st.chat_message("user", avatar="🧑‍🎓").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🦖"):
        # เช็คเลขห้องก่อน
        room_info = get_room_info(prompt, st.session_state.lang) #
        if room_info:
            full_response = room_info
            st.markdown(full_response)
        else:
            placeholder = st.empty()
            placeholder.markdown(curr["loading"])
            try:
                # รวมข้อมูลจาก ku_data.txt และ PDF ใน knowledge_pool
                kb = get_knowledge_base() 
                
                history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[-6:-1]]
                chat_session = model.start_chat(history=history)
                
                # ปรับ Prompt ให้ AI ค้นหาใน PDF อย่างละเอียดขึ้น
                full_context = f"""
                {curr['ai_identity']} คุยกับน้องนิสิตชื่อ {st.session_state.global_user_nickname}
                
                คำสั่งการทำงาน:
                1. ให้ค้นหาคำตอบจาก [คลังความรู้] ด้านล่างนี้ ซึ่งรวมข้อมูลจากไฟล์คู่มือและประกาศต่างๆ แล้ว
                2. หากน้องถามเรื่องค่าเทอม หรือระเบียบการ ให้พยายามสรุปข้อมูลที่พบออกมาเป็นข้อๆ ให้เข้าใจง่าย
                3. หากข้อมูลในคลังความรู้ไม่เพียงพอ ให้บอกน้องอย่างสุภาพว่า "ข้อมูลส่วนนี้พี่ยังไม่มีในระบบ รบกวนน้องตรวจสอบที่เว็บ reg.src.ku.ac.th อีกทีนะจ๊ะ"
                
                [คลังความรู้]:
                {kb}
                
                คำถามจากน้อง: {prompt}
                """
                
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
