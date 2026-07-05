import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("서버에 API 키가 설정되지 않았습니다. Streamlit Secrets에 GEMINI_API_KEY를 설정해 주세요.")
    st.stop()

SYSTEM_INSTRUCTION = """
당신은 학생들의 비판적 사고를 돕는 'DataReasoning' 에이전트입니다.
목표: 학생들이 시각화된 데이터(그래프, 표 등)를 보고, 복사-붙여넣기가 아닌 스스로 비판적 사고를 거쳐 의미 있는 보고서를 작성하도록 돕습니다.
[4단계 대화 프로세스] - 한 번에 하나의 질문만 하세요.
1단계(시각적 관찰) -> 2단계(수치적 연결) -> 3단계(수학적 분석) -> 4단계(보고서 구조화)
제약사항: 정답을 먼저 주지 말고 학생 스스로 생각하게 하세요. '절반씩(2분의 1) 곱해지는 형태'와 같은 직관적인 표현을 사용하세요.
"""

st.title("📊 DataReasoning")

# 파일 업로드 (Session State에 저장하여 새로고침 시에도 유지)
if "uploaded_img" not in st.session_state:
    st.session_state.uploaded_img = None

with st.sidebar:
    st.subheader("데이터 업로드")
    uploaded_file = st.file_uploader("이미지 선택", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.session_state.uploaded_img = Image.open(uploaded_file)
        st.image(st.session_state.uploaded_img, use_column_width=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕! 분석할 그래프를 왼쪽에 올리고 말을 걸어줘!"}]

# 대화 관리 툴바
col1, col2 = st.columns([1, 1])
chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
col1.download_button("📥 대화 기록 다운로드", data=chat_text, file_name="DataReasoning.txt")
if col2.button("🔄 새 분석 시작"):
    st.session_state.messages = [{"role": "assistant", "content": "새롭게 시작합니다! 분석할 데이터를 올려주세요."}]
    st.session_state.uploaded_img = None
    st.rerun()

# 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 채팅 입력
if prompt := st.chat_input("데이터의 어떤 부분이 가장 눈에 띄나요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 모델 설정 (gemini-1.5-flash 권장)
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_INSTRUCTION)
    
    with st.chat_message("assistant"):
        parts = [prompt]
        if st.session_state.uploaded_img:
            parts.insert(0, st.session_state.uploaded_img)
        
        response = model.generate_content(parts)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
