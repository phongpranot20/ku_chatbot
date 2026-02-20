import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="KU Sriracha Bot - Diagnostic", layout="wide")

st.title("🐢 ระบบตรวจสอบโมเดล (Diagnostic)")

# 1. เช็คคีย์ใน Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ ไม่พบคีย์ใน Secrets! ตรวจสอบว่าในหน้า Settings > Secrets พิมพ์คำว่า GEMINI_API_KEY ถูกต้องหรือไม่")
    st.stop()

genai.configure(api_key=api_key)

st.write("---")
st.subheader("🔍 รายชื่อโมเดลที่บัญชีของคุณรองรับ:")

try:
    # ดึงรายชื่อโมเดลทั้งหมดที่คีย์นี้ใช้ได้
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if available_models:
        st.success(f"พบโมเดลที่ใช้งานได้ {len(available_models)} ตัว")
        selected_model_name = st.selectbox("เลือกโมเดลที่จะใช้:", available_models)
        
        # ทดสอบการใช้งาน
        if st.button("ทดสอบรันโมเดลนี้"):
            try:
                test_model = genai.GenerativeModel(selected_model_name)
                response = test_model.generate_content("สวัสดี")
                st.write("**AI ตอบกลับ:**", response.text)
                st.balloons()
            except Exception as e:
                st.error(f"รันโมเดลไม่ได้: {e}")
    else:
        st.warning("⚠️ คีย์นี้เชื่อมต่อได้ แต่ Google บอกว่าไม่มีโมเดลไหนที่ใช้ generateContent ได้เลย")
        
except Exception as e:
    st.error(f"❌ คีย์นี้ใช้งานไม่ได้หรือมีปัญหาการเชื่อมต่อ: {e}")
    st.info("แนะนำ: ให้ไปสร้าง API Key อันใหม่ที่ aistudio.google.com แล้วนำมาเปลี่ยนใน Secrets ครับ")
