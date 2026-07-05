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

# 3. 사용 가능한 모델 자동 선택 함수
def get_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # gemini-1.5-flash 모델을 우선적으로 선택
            return genai.GenerativeModel(m.name)
    raise Exception("사용 가능한 모델을 찾을 수 없습니다.")

st.title("📊 DataReasoning - 멀티 비교 분석")

# 4. 시스템 프롬프트 정의
SYSTEM_PROMPT = """
당신은 학생들의 비판적 사고를 돕는 데이터 분석 조력자 'DataReasoning'입니다.
모든 대화는 반드시 한국어로 진행하며, 1~4단계 대화 프로세스에 따라 학생이 스스로 생각하게 하세요.
"""

# 업로드 로직
with st.sidebar:
    st.subheader("데이터 업로드 (여러 개 가능)")
    uploaded_files = st.file_uploader("이미지 선택", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    images = [Image.open(f) for f in uploaded_files] if uploaded_files else []
    if images: st.write(f"현재 {len(images)}개의 그래프가 업로드되었습니다.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "그래프들을 올리고 비교 분석을 시작해봐!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 채팅 입력 처리
if prompt := st.chat_input("이 그래프들의 차이점이나 공통점은 무엇인가요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 모델 인스턴스 가져오기 (오류 해결 핵심)
            model = get_model()
            
            # 시스템 프롬프트와 학생 질문 결합
            full_prompt = f"{SYSTEM_PROMPT}\n\n질문: {prompt}"
            parts = [full_prompt]
            parts.extend(images)
            
            # 응답 생성
            response = model.generate_content(parts)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"분석 오류: {e}")
