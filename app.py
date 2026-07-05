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
SYSTEM_INSTRUCTION = """
당신은 학생들의 비판적 사고를 돕는 'DataReasoning' 에이전트입니다.
학생들이 시각화된 데이터를 보고, 스스로 생각하여 의미 있는 보고서를 작성하도록 돕습니다.
[대화 규칙]
- 한 번에 하나의 질문만 하세요.
- 1단계(관찰) -> 2단계(수치 연결) -> 3단계(패턴 분석) -> 4단계(결론 구조화) 순서로 대화하세요.
- 정답을 바로 주지 말고 학생이 직접 답하도록 유도하세요.
- 어려운 공식보다는 직관적인 언어를 사용하세요.
"""

st.title("📊 DataReasoning")

# 4. 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "분석할 그래프/표를 왼쪽에 올리고 말을 걸어줘!"}]

# 5. UI 구성
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("데이터 업로드")
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "png", "jpeg"])
    img = None
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_column_width=True)

with col2:
    st.subheader("AI 분석 대화창")
    
    # 툴바
    t1, t2 = st.columns(2)
    chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    t1.download_button("📥 기록 다운로드", data=chat_text, file_name="DataReasoning_log.txt")
    if t2.button("🔄 새로 시작"):
        st.session_state.messages = [{"role": "assistant", "content": "새롭게 시작합니다!"}]
        st.rerun()

    # 메시지 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력 및 처리
    if prompt := st.chat_input("데이터에서 무엇이 보이니?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 모델 호출 (가장 안정적인 flash 모델 사용)
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
        
        with st.chat_message("assistant"):
            try:
                parts = [prompt]
                if img:
                    parts.append(img)
                response = model.generate_content(parts)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
