import streamlit as st
import google.generativeai as genai

# Cấu hình API Key
API_KEY = os.getenv("API_KEY")

# ================== TỐI ƯU HÓA TỐC ĐỘ (CORE) ==================

MODEL_NAME = "gemini-3.1-flash-lite-preview" 

generation_config = {
    "temperature": 0.0,
    "max_output_tokens": 1000,
    "top_p": 1,
    "top_k": 1,
}

# THAY ĐỔI QUAN TRỌNG: Câu lệnh cực ngắn và nghiêm ngặt
sys_msg = (
    "Bạn là máy dịch Việt-Nhật. NHIỆM VỤ DUY NHẤT: Dịch văn bản đầu vào. "
    "KHÔNG giải thích, KHÔNG thêm '作業指示', KHÔNG liệt kê từ vựng. "
    "Ưu tiên dùng: 写植, レタッチ, 描き込み, 非表示, フォルダ, レイヤー."
)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=sys_msg,
    generation_config=generation_config,
)

# ================== GIAO DIỆN & FIX CSS ==================
st.set_page_config(page_title="Manga Translator Pro", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stTextArea textarea { font-size: 16px !important; }
    
    .result-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        font-family: sans-serif;
        font-size: 16px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
        min-height: 100px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 Manga Translator Pro")

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

with st.form(key='translation_form', clear_on_submit=False):
    source_text = st.text_area(
        "Nhập nội dung cần dịch:", 
        value=st.session_state.input_text,
        height=150,
        placeholder="Ctrl + Enter để dịch ngay...",
        key="main_input"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        mode = st.selectbox("Ngữ cảnh:", ["Văn phòng", "Kính ngữ", "Thân mật"])
    with col2:
        submit_button = st.form_submit_button("🚀 Dịch ngay", use_container_width=True, type="primary")

# ================== XỬ LÝ DỊCH ==================
if submit_button:
    if source_text.strip():
        st.session_state.input_text = source_text
        st.subheader("🇯🇵 Kết quả:")
        
        result_placeholder = st.empty() 
        full_response = ""
        
        with st.spinner("Đang xử lý..."):
            try:
                # Thêm chỉ thị trực tiếp vào prompt để ép model tuân thủ
                prompt = f"Dịch nội dung sau sang tiếng Nhật (ngữ cảnh {mode}), chỉ trả về bản dịch: {source_text}"
                response = model.generate_content(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        result_placeholder.markdown(
                            f'<div class="result-box">{full_response}</div>', 
                            unsafe_allow_html=True
                        )
                
                st.toast("Hoàn thành!", icon="✅")
                
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
    else:
        st.warning("Vui lòng nhập nội dung.")

st.divider()
st.info("💡 **Copyright** LinkStoryAsia")
