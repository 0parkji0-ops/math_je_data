import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

# 2. API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets에 GEMINI_API_KEY를 입력해주세요.")
    st.stop()

# 3. 시스템 프롬프트
SYSTEM_INSTRUCTION = "당신은 학생들의 비판적 사고를 돕는 데이터 분석 조력자입니다. 4단계(관찰-수치 연결-패턴 분석-보고서 구조화)를 준수하며 대화하세요."

st.title("📊 DataReasoning")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "분석할 그래프/표를 왼쪽에 올리고 말을 걸어줘!"}]

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
    img = None
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_column_width=True)

with col2:
    # 채팅 기록 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력
    if prompt := st.chat_input("데이터에서 무엇이 보이니?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 모델 호출 변경: 'gemini-1.5-flash' 대신 더 포괄적인 이름으로 시도
        try:
            # 설정된 키에 따라 가장 최신 모델을 자동으로 잡도록 시도
            model = genai.GenerativeModel(model_name='gemini-pro', system_instruction=SYSTEM_INSTRUCTION)
            
            parts = [prompt]
            if img:
                parts.append(img)
            
            response = model.generate_content(parts)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")
