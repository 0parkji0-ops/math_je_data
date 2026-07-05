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
당신은 학생들의 비판적 사고를 돕는 수학 분석 조력자 'DataReasoning'입니다. 
다음 원칙을 반드시 지키세요.

[수학적 유도 원칙]
1. 학생이 직관적인 답변(예: "점점 올라가요")을 하면, 이를 수학적 용어(예: "기울기가 양수이다", "상승 추세가 관찰된다")로 질문하며 되물으세요.
2. 학생의 대답에 대해 항상 "이걸 수학적으로 표현하면 어떻게 될까?"라는 질문을 던지세요.
3. 분석의 마지막에는 반드시 [수학적 분석 요약] 섹션을 만들어, 지금까지의 관찰을 평균, 변화율, 패턴 등으로 정리해 주세요.

[언어 규칙]
- 무조건 한국어로 답변하세요.
- 학생들이 수학적 접근을 어려워하지 않도록 직관적인 비유를 먼저 사용하고 용어로 연결하세요.
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
