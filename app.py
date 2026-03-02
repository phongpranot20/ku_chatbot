# app.py (ส่วน Sidebar ที่แก้ไขให้ครบถ้วน)

with st.sidebar:
    # 1. ปุ่มสลับภาษา
    if st.button(f"🌐 {st.session_state.lang}"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

    # 2. โลโก้และชื่อมหาลัย
    img_data = get_image_base64("logo_ku.png")
    if img_data:
        st.markdown(f'<div class="custom-header"><img src="data:image/png;base64,{img_data}" class="header-logo-img"><div class="univ-name">{curr["univ_name"]}</div></div>', unsafe_allow_html=True)
    
    # 3. ปุ่มแชทใหม่
    if st.button(curr["new_chat"]):
        st.session_state.messages = []
        st.session_state.current_chat_id = None
        st.rerun()
    
    # 4. ประวัติการแชท
    if st.session_state.all_chats:
        st.markdown(f'<p style="font-weight:700; margin-top:10px;">{curr["chat_hist"]}</p>', unsafe_allow_html=True)
        for chat_id in list(st.session_state.all_chats.keys()):
            if st.button(f"📄 {chat_id[:18]}...", key=f"hist_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.session_state.messages = st.session_state.all_chats[chat_id]
                st.rerun()

    st.markdown("---")
    st.markdown('<p style="font-weight:700;">Quick Links</p>', unsafe_allow_html=True)
    
    # 5. ค้นหาตารางสอบ 
    with st.expander(curr["exam_table"], expanded=False):
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><span>KU Exam</span><a href="https://reg2.src.ku.ac.th/table_test/" target="_blank" class="btn-action">{curr["btn_find"]}</a></div>', unsafe_allow_html=True)
    
    # 6. คำนวณเกรด (GPA) 
    with st.expander(curr["gpa_calc"], expanded=False):
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><span>GPAX</span><a href="https://fna.csc.ku.ac.th/grade/" target="_blank" class="btn-action">{curr["btn_open"]}</a></div>', unsafe_allow_html=True)
    
    # 7. ลิงก์แบบฟอร์มต่างๆ (ครบถ้วนตามไฟล์ ku_data.txt) 
    with st.expander(curr["forms"], expanded=False):
        forms = [
            ("ใบขอลงทะเบียนเรียน", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Request-for-Registration.pdf"),
            ("ใบคำร้องทั่วไป", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/General-Request.pdf"),
            ("ใบผ่อนผันค่าเทอม", "https://registrar.ku.ac.th/wp-content/uploads/2024/11/Postpone-tuition-and-fee-payments.pdf"),
            ("ใบลาพักการศึกษา", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Request-for-Leave-of-Absence-Request.pdf"),
            ("ใบลาออก", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/Resignation-Form.pdf"),
            ("ใบลงทะเบียนเรียน (KU1)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU1-Registration-Form.pdf"),
            ("ใบเพิ่ม-ถอน (KU3)", "https://registrar.ku.ac.th/wp-content/uploads/2023/11/KU3-Add-Drop-Form.pdf")
        ]
        for name, link in forms:
            st.markdown(f'''
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:0.85rem;">{name}</span>
                    <a href="{link}" target="_blank" class="btn-action">{curr["btn_download"]}</a>
                </div>
            ''', unsafe_allow_html=True)
