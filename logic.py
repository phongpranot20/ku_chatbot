import re
import os
import google.generativeai as genai
import streamlit as st

def get_room_info(room_code, lang):
    """ฟังก์ชันเช็คห้องเรียน (ย้ายมาจากส่วนที่ 3)"""
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building = code[:2]; floor = code[2]; room = code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง" if lang == "TH" else f"This room is in **Building {building}, Floor {floor}, Room {room}**."
    elif len(code) == 4:
        building = code[0]; floor = code[1]; room = code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม" if lang == "TH" else f"It is **Building {building}, Floor {floor}, Room {room}**."
    return None

@st.cache_resource
def load_model():
    """ฟังก์ชันโหลด AI (ย้ายมาจากส่วนที่ 5)"""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except:
        return None

def get_knowledge_base():
    """โหลดข้อมูลจากไฟล์ ku_data.txt"""
    if os.path.exists("ku_data.txt"):
        with open("ku_data.txt", "r", encoding="utf-8") as f:
            return f.read()
    return ""
