import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

# 2. API 설정 및 모델 초기화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # 가장 안정적인 flash 모델을 명시적으로 사용
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API 설정 오류: {e}")
    st.stop()

# 3. 한국어 답변 강제 시스템 지침
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

st.title("📊 DataReasoning")

# 4. 세션 상태 관리
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕! 분석할 그래프를 왼쪽에 올리고 말을 걸어줘!"}]

# 5. UI 구성
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 데이터 업로드")
    uploaded_file = st.file_uploader("이미지 선택", type=["jpg", "png", "jpeg"])
    img = Image.open(uploaded_file) if uploaded_file else None
    if img:
        st.image(img, use_column_width=True)

with col2:
    st.subheader("2. AI 분석 대화창")
    
    # 기록 다운로드 및 초기화
    t1, t2 = st.columns(2)
    chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    t1.download_button("📥 대화 기록 다운로드", data=chat_text, file_name="DataReasoning_log.txt")
    if t2.button("🔄 새 분석 시작"):
        st.session_state.messages = [{"role": "assistant", "content": "새롭게 시작합니다! 데이터를 올려주세요."}]
        st.rerun()

    # 대화 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력
    if prompt := st.chat_input("데이터에서 무엇이 보이니?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성 (시스템 프롬프트와 한국어 지침을 합쳐서 전송)
        with st.chat_message("assistant"):
            try:
                full_prompt = f"{SYSTEM_PROMPT}\n\n학생의 질문: {prompt}"
                parts = [full_prompt]
                if img:
                    parts.append(img)
                
                response = model.generate_content(parts)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
