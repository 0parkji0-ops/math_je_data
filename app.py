import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. 페이지 기본 설정
st.set_page_config(page_title="DataReasoning", page_icon="📊", layout="wide")

# 2. API 키 숨겨서 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("서버에 API 키가 설정되지 않았습니다. Streamlit Secrets에 GEMINI_API_KEY를 설정해 주세요.")
    st.stop()

# 3. AI 시스템 프롬프트 (DataReasoning 핵심 지침)
SYSTEM_INSTRUCTION = """
당신은 학생들의 비판적 사고를 돕는 'DataReasoning' 에이전트입니다.
목표: 학생들이 시각화된 데이터(그래프, 표 등)를 보고, 복사-붙여넣기가 아닌 스스로 비판적 사고를 거쳐 의미 있는 보고서를 작성하도록 돕습니다.

[4단계 대화 프로세스] - 한 번에 하나의 질문만 하세요.
1단계 (시각적 관찰): 그래프에서 가장 눈에 띄는 특징, 상승/하락 추세 등 직관적인 질문을 던집니다.
2단계 (수치적 연결): "가장 높을 때와 낮을 때의 차이는 대략 얼마인가요?", "몇 배 커졌나요?" 등 눈으로 본 변화를 수치로 연결합니다.
3단계 (수학적 분석): 변화의 원인이나 패턴(평균, 변화율 등)을 분석하도록 유도합니다.
4단계 (보고서 구조화): 지금까지 나눈 대화를 바탕으로 보고서의 한 줄 결론을 직접 써보게 하고, 이를 수학적 표현으로 다듬어 줍니다.

제약사항:
- 정답이나 완성된 보고서 단락을 먼저 주지 마세요.
- 어려운 수학 기호나 공식보다는 직관적인 표현(예: '나누기 2' 대신 '절반씩(2분의 1) 곱해지는 형태')을 사용하세요.
"""

# 타이틀 및 안내 문구
st.title("📊 DataReasoning")
st.markdown("그래프를 분석하여 나만의 수학적 보고서를 작성해 보세요!")

# 사이드바: 기본 안내
with st.sidebar:
    st.header("⚙️ 시스템 정보")
    st.success("🤖 에이전트가 준비되었습니다.")
    st.info("💡 대화창 상단의 다운로드 버튼을 누르면 전체 대화 내용을 파일로 저장하여 쉽게 복사·붙여넣기할 수 있습니다.")

# 4. 화면을 좌우 1:1 비율로 분할
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. 데이터(그래프/표) 업로드")
    uploaded_file = st.file_uploader("분석할 이미지 파일(JPG, PNG)을 올려주세요.", type=["jpg", "jpeg", "png"])
    
    img = None
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="업로드된 시각화 자료", use_column_width=True)

with col2:
    st.subheader("2. AI와 분석하기")
    
    # 세션 상태(대화 기록) 기본값 설정
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "안녕! 분석하고 싶은 그래프나 표 이미지를 왼쪽에 올리고, 나에게 말을 걸어줘!"}]
    
    # --- 🛠️ 대화 관리 툴바 구성 ---
    tool_col1, tool_col2 = st.columns([1, 1])
    
    # 다운로드용 텍스트 데이터 포맷팅
    chat_download_text = ""
    for msg in st.session_state.messages:
        role_label = "DataReasoning (AI)" if msg["role"] == "assistant" else "학생"
        chat_download_text += f"[{role_label}]\n{msg['content']}\n{'-'*60}\n\n"
        
    with tool_col1:
        # 파일 다운로드 버튼 (텍스트 파일 형태로 내보내기)
        st.download_button(
            label="📥 대화 기록 다운로드 (.txt)",
            data=chat_download_text,
            file_name="DataReasoning_대화기록.txt",
            mime="text/plain",
            help="지금까지 나눈 대화 내용을 텍스트 파일로 다운로드합니다. 파일 안의 내용을 전체 복사하여 보고서에 활용할 수 있습니다."
        )
        
    with tool_col2:
        # 대화 초기화 버튼
        if st.button("🔄 새 분석 시작 (대화 초기화)", help="현재 대화 내용을 지우고 처음부터 다시 시작합니다."):
            st.session_state.messages = [{"role": "assistant", "content": "안녕! 분석하고 싶은 그래프나 표 이미지를 왼쪽에 올리고, 나에게 말을 걸어줘!"}]
            st.rerun()
            
    st.markdown("---") # 툴바와 대화창 구분선
    
    # 기존 대화 내용 화면에 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력창 처리
    if prompt := st.chat_input("데이터의 어떤 부분이 가장 눈에 띄나요?"):
        # 사용자의 질문을 즉시 화면에 추가
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini 모델 설정
        model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=SYSTEM_INSTRUCTION)
        
        # API 전송을 위한 이전 대화 빌드
        history = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [m["content"]]})
        
        chat = model.start_chat(history=history)
        
        # AI 답변 생성 및 화면 출력
        with st.chat_message("assistant"):
            try:
                parts = [prompt]
                # 처음 이미지를 업로드하고 대화를 시작할 때만 이미지를 바이너리로 함께 전송
                if img and len(st.session_state.messages) == 2:
                    parts.insert(0, img)
                    
                response = chat.send_message(parts)
                st.markdown(response.text)
                
                # 답변 보관 후 화면 최신화 (상단 다운로드 버튼 데이터 동기화)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
