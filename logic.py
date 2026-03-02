import re
import os
import google.generativeai as genai
import streamlit as st

def get_room_info(room_code, lang):
    """ประมวลผลรหัสห้องเรียน"""
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        building, floor, room = code[:2], code[2], code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับน้อง" if lang == "TH" else f"This room is in **Building {building}, Floor {floor}, Room {room}**."
    elif len(code) == 4:
        building, floor, room = code[0], code[1], code[2:]
        return f"ห้องนี้คือ **ตึก {building} ชั้น {floor} ห้อง {room}** ครับผม" if lang == "TH" else f"It is **Building {building}, Floor {floor}, Room {room}**."
    return None

@st.cache_resource
def load_gemini_model(api_key):
    """ตั้งค่าและโหลด AI Model"""
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except:
        return None

def get_knowledge_base(file_path="ku_data.txt"):
    """ดึงข้อมูลฐานความรู้จากไฟล์เนื้อหา [cite: 2, 3, 11]"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
