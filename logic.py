import re
import os
import PyPDF2
import google.generativeai as genai
import streamlit as st

def get_room_info(room_code, lang):
    """ฟังก์ชันเช็คห้องเรียน"""
    code = re.sub(r'\D', '', str(room_code))
    if len(code) == 5:
        b, f, r = code[:2], code[2], code[3:]
        return f"อ๋อ ห้องนี้อยู่ **ตึก {b} ชั้น {f} ห้อง {r}** ครับน้อง" if lang == "TH" else f"Building {b}, Floor {f}, Room {r}."
    elif len(code) == 4:
        b, f, r = code[0], code[1], code[2:]
        return f"ห้องนี้คือ **ตึก {b} ชั้น {f} ห้อง {r}** ครับผม" if lang == "TH" else f"Building {b}, Floor {f}, Room {r}."
    return None

@st.cache_resource
def load_model():
    """โหลดโมเดล AI"""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key: return None
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = next((m for m in available_models if "1.5-flash" in m), available_models[0])
        return genai.GenerativeModel(model_name=selected)
    except: return None

def get_pdf_content(directory="knowledge_pool"):
    """กวาดอ่านไฟล์ PDF ทั้งหมดและระบุแหล่งที่มา"""
    combined_text = ""
    if not os.path.exists(directory): 
        os.makedirs(directory)
        return ""
    
    # ดึงรายชื่อไฟล์ PDF ทั้งหมดในโฟลเดอร์
    pdf_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    
    for filename in pdf_files:
        try:
            with open(os.path.join(directory, filename), "rb") as f:
                pdf = PyPDF2.PdfReader(f)
                # ใส่ Header กำกับชื่อไฟล์เพื่อให้ AI แยกแยะภาคปกติ/ภาคพิเศษได้ [cite: 10]
                combined_text += f"\n\n--- ข้อมูลจากไฟล์: {filename} ---\n"
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        combined_text += f"[หน้า {i+1}] {page_text}\n"
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return combined_text

def get_knowledge_base():
    """รวมข้อมูล TXT และ PDF"""
    txt_data = ""
    if os.path.exists("ku_data.txt"):
        with open("ku_data.txt", "r", encoding="utf-8") as f: 
            txt_data = f.read()
    
    pdf_data = get_pdf_content()
    return f"{txt_data}\n\n[คลังความรู้เพิ่มเติมจากเอกสาร PDF]:\n{pdf_data}"
