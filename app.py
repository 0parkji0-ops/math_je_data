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
    st.error("API 키 설정이 없습니다.")
    st.stop()

def get_model():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            return genai.GenerativeModel(m.name)
    raise Exception("모델을 찾을 수 없습니다.")

st.title("📊 DataReasoning - 수학적 사고 분석기")

# 3. 대화 관리 (초기화)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "데이터를 올리고 분석을 시작해봐! 네 생각을 수학적 언어로 번역해줄게."}]

# --- 툴바 (저장 및 초기화) ---
col_tool1, col_tool2 = st.columns([1, 8])
chat_log = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])

with col_tool1:
    st.download_button(label="💾 기록 저장", data=chat_log, file_name="math_analysis_log.txt", mime="text/plain")
with col_tool2:
    if st.button("🔄 새로 시작"):
        st.session_state.messages = [{"role": "assistant", "content": "새로운 분석을 시작합니다! 그래프를 올려주세요."}]
        st.rerun()

# 4. 사이드바 및 이미지 업로드
with st.sidebar:
    uploaded_files = st.file_uploader("데이터 그래프 업로드 (여러 개 가능)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    images = [Image.open(f) for f in uploaded_files] if uploaded_files else []

if images:
    cols = st.columns(len(images))
    for i, img in enumerate(images):
        cols[i].image(img, use_column_width=True, caption=f"그래프 {i+1}")

# 5. 채팅 처리
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

SYSTEM_INSTRUCTION = """
당신은 특성화고등학교 학생들을 위한 '데이터 분석 페이스메이커'입니다.
목표: 학생들이 시각화된 데이터(그래프, 표 등)를 보고, 복사-붙여넣기가 아닌 스스로 비판적 사고를 거쳐 의미 있는 보고서를 작성하도록 돕습니다.

[4단계 대화 프로세스] - 한 번에 하나의 질문만 하세요.
1단계 (시각적 관찰): 그래프에서 가장 눈에 띄는 특징, 상승/하락 추세 등 직관적인 질문을 던집니다.
2단계 (수치적 연결): "가장 높을 때와 낮을 때의 차이는 대략 얼마인가요?", "몇 배 커졌나요?" 등 눈으로 본 변화를 수치로 연결합니다.
3단계 (수학적 분석): 변화의 원인이나 패턴(평균, 변화율 등)을 분석하도록 유도합니다.
4단계 (보고서 구조화): 지금까지 나눈 대화를 바탕으로 보고서의 한 줄 결론을 직접 써보게 하고, 이를 수학적 표현으로 다듬어 줍니다.

제약사항:
- 정답이나 완성된 보고서 단락을 먼저 주지 마세요.
- 어려운 수학 기호나 공식보다는 직관적인 표현(예: '절반씩 곱해지는 형태')을 사용하세요.
- 무조건 한국어로 답변하고, 질문을 통해 학생 스스로 수학적 사고를 하도록 유도하세요.
"""

if prompt := st.chat_input("이 그래프들의 차이점이나 공통점은 수학적으로 무엇일까?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = get_model()
            full_prompt = f"{SYSTEM_PROMPT}\n\n학생의 관찰: {prompt}\n\n위 내용을 수학적 언어로 해석하고 추가 질문을 던져주세요."
            parts = [full_prompt]
            parts.extend(images)
            
            response = model.generate_content(parts)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.rerun() # 대화 업데이트를 위해 새로고침
        except Exception as e:
            st.error(f"분석 오류: {e}")
