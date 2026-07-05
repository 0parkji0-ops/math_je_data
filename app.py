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

def get_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    raise Exception("사용 가능한 모델을 찾을 수 없습니다.")

st.title("📊 DataReasoning - 멀티 비교 분석")

# 3. 업로드 로직 (사이드바)
with st.sidebar:
    st.subheader("데이터 업로드")
    uploaded_files = st.file_uploader("이미지 선택", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    images = [Image.open(f) for f in uploaded_files] if uploaded_files else []

# 4. [추가된 부분] 업로드한 그래프를 메인 화면에 나란히 보여주기
if images:
    st.subheader("현재 분석 중인 그래프")
    # 업로드된 이미지 개수에 따라 열을 나누어 배치
    cols = st.columns(len(images))
    for i, img in enumerate(images):
        cols[i].image(img, use_column_width=True, caption=f"그래프 {i+1}")
    st.markdown("---")

# 5. 대화창 및 채팅 처리
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "그래프들을 올리고 비교 분석을 시작해봐!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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

if prompt := st.chat_input("이 그래프들의 차이점이나 공통점은 무엇인가요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = get_model()
            full_prompt = f"{SYSTEM_PROMPT}\n\n질문: {prompt}"
            parts = [full_prompt]
            parts.extend(images)
            
            response = model.generate_content(parts)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"분석 오류: {e}")
