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
    # 모든 모델 중 'generateContent'가 가능한 모델만 검색
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # gemini-1.5, gemini-pro 등이 있으면 우선 선택
            return genai.GenerativeModel(m.name)
    raise Exception("사용 가능한 모델을 찾을 수 없습니다.")

st.title("📊 DataReasoning - 멀티 비교 분석")

# 1. 다중 파일 업로드 (accept_multiple_files=True)
with st.sidebar:
    st.subheader("데이터 업로드 (여러 개 가능)")
    uploaded_files = st.file_uploader("분석할 이미지들을 선택하세요", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    images = []
    if uploaded_files:
        for f in uploaded_files:
            images.append(Image.open(f))
        st.write(f"현재 {len(images)}개의 그래프가 업로드되었습니다.")

# 2. 대화창
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

# 3. 채팅 입력
if prompt := st.chat_input("이 그래프들의 차이점이나 공통점은 무엇인가요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 여러 이미지를 리스트에 담아 프롬프트와 함께 전송
            parts = [prompt, "너는 데이터 분석가야. 아래 업로드된 여러 그래프들을 비교 분석해서 한국어로 설명해줘."]
            if images:
                parts.extend(images)
            
            response = model.generate_content(parts)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"분석 오류: {e}")
