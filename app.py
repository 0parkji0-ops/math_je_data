import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

# API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API 키 설정이 필요합니다.")
    st.stop()

st.title("📊 DataReasoning")

# 사용 가능한 모델 자동 검색
def get_model():
    # 현재 사용 가능한 모델 리스트를 확인
    models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # flash 모델이 있다면 사용, 없으면 첫 번째 모델 사용
    for m in models:
        if 'gemini-1.5-flash' in m.name:
            return genai.GenerativeModel(m.name)
    return genai.GenerativeModel(models[0].name)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "데이터를 업로드하고 질문해주세요!"}]

uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
img = Image.open(uploaded_file) if uploaded_file else None

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    try:
        model = get_model() # 여기서 자동 검색된 모델 사용
        parts = [prompt]
        if img: parts.append(img)
        
        response = model.generate_content(parts)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"오류: {e}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
