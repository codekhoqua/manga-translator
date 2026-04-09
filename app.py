import os  # THÊM DÒNG NÀY VÀO ĐẦU FILE
import streamlit as st
import google.generativeai as genai

# Sau đó mới lấy API_KEY
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("Không tìm thấy API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

# ================== TỐI ƯU HÓA TỐC ĐỘ (CORE) ==================

MODEL_NAME = "gemini-3.1-flash-lite-preview" 
generation_config = {
    "temperature": 0.0,
    "max_output_tokens": 1000,
}
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

# ================== GIAO DIỆN & CSS ==================
st.set_page_config(page_title="LSA Translator", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stTextArea textarea { font-size: 15px !important; }
    
    /* Thu gọn khoảng cách giữa các thành phần */
    .block-container { padding-top: 2rem; }
    
    /* Style cho khung kết quả */
    .result-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #333;
        font-family: sans-serif;
        font-size: 15px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-wrap: break-word;
        min-height: 80px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎨 LSA - Design Team Internal")

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ================== FORM NHẬP LIỆU ==================
with st.form(key='translation_form', clear_on_submit=False):
    source_text = st.text_area(
        "Văn bản nguồn:", 
        value=st.session_state.input_text,
        height=120, # Giảm chiều cao một chút cho gọn
        placeholder="Nhập nội dung... (Ctrl + Enter để dịch)",
        key="main_input",
        label_visibility="collapsed" # Ẩn label để UI sạch hơn
    )
    
    # CHỈNH SỬA TẠI ĐÂY: Chia cột nhỏ lại và cho Button lên cùng hàng
    col1, col2 = st.columns([2, 1]) 
    with col1:
        mode = st.selectbox(
            "Ngữ cảnh:", 
            ["Văn phòng", "Kính ngữ", "Thân mật"],
            label_visibility="collapsed" # Ẩn label ngữ cảnh để nằm ngang đẹp hơn
        )
    with col2:
        submit_button = st.form_submit_button("🚀 Dịch ngay", use_container_width=True, type="primary")

# ================== XỬ LÝ DỊCH ==================
if submit_button:
    if source_text.strip():
        st.session_state.input_text = source_text
        st.subheader("🇯🇵 Kết quả:")
        
        result_placeholder = st.empty() 
        full_response = ""
        
        with st.spinner("Đang dịch..."):
            try:
                prompt = f"Dịch sang tiếng Nhật (ngữ cảnh {mode}): {source_text}"
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
st.caption("💡 **Copyright** LinkStoryAsia | Dịch thuật nội bộ Design Team Ver 2.0")
