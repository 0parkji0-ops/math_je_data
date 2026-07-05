import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

# 2. API 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API 키 설정이 없습니다.")
    st.stop()

SYSTEM_PROMPT = """
당신은 학생들의 비판적 사고를 돕는 데이터 분석 조력자 'DataReasoning'입니다.
모든 대화는 반드시 자연스러운 한국어로 진행하세요.

[대화 프로세스]
1단계: 그래프의 특징을 관찰하도록 유도하세요.
2단계: 데이터의 수치를 연결해 질문하세요.
3단계: 수학적 패턴을 분석하도록 이끄세요.
4단계: 학생의 답변을 바탕으로 보고서 문장을 다듬어주세요.

[원칙]
- 무조건 한국어로 답변하세요.
- 답을 바로 주지 말고 질문을 통해 학생이 생각하게 하세요.
- 어려운 수학 공식보다는 직관적인 언어를 사용하세요.
"""

# 3. 사용 가능한 모델 자동 선택 함수
def get_model():
    # 모든 모델 중 'generateContent'가 가능한 모델만 검색
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # gemini-1.5, gemini-pro 등이 있으면 우선 선택
            return genai.GenerativeModel(m.name)
    raise Exception("사용 가능한 모델을 찾을 수 없습니다.")

st.title("📊 DataReasoning")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "분석할 데이터를 올리고 대화를 시작해줘!"}]

col1, col2 = st.columns([1, 1])

with col1:
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
    img = Image.open(uploaded_file) if uploaded_file else None
    if img: st.image(img, use_column_width=True)

with col2:
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("질문을 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # 모델 자동 선택
                model = get_model()
                
                # 프롬프트 구성 (한국어 강제)
                full_prompt = f"당신은 데이터 분석 조력자입니다. 반드시 한국어로 대답하세요. 질문: {prompt}"
                parts = [full_prompt]
                if img: parts.append(img)
                
                response = model.generate_content(parts)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"오류: {e}")
