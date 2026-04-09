import streamlit as st
import google.generativeai as genai

# --- CẤU HÌNH HỆ THỐNG ---
API_KEY = "AIzaSyAxoQQELM325tS9voZedDw72fZoyjMc0aA"
genai.configure(api_key=API_KEY)


MODEL_NAME = "gemini-2.5-flash" 

generation_config = {
    "temperature": 0, # Để 0 để AI không cần "suy nghĩ" nhiều, dịch thẳng luôn
    "max_output_tokens": 1000,
}

# Instruction tối giản để tăng tốc
sys_msg = (
    "Bạn là thợ dịch Manga/IT. Dịch Việt -> Nhật lịch sự văn phòng. "
    "Dùng: 写植, レタッチ, 描き込み, 非表示, フォルダ, レイヤー. Dịch thẳng, không giải thích."
)

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=sys_msg,
    generation_config=generation_config
)

# --- GIAO DIỆN WEB ---
st.set_page_config(page_title="Manga Translator Pro", page_icon="🎨")

st.title("🎨 Manga Translator Pro")
st.caption("Nhấn Ctrl + Enter để dịch ngay lập tức")

# Sử dụng FORM để bắt sự kiện Ctrl + Enter
with st.form(key='translation_form', clear_on_submit=False):
    source_text = st.text_area("Nhập tiếng Việt:", height=150)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        mode = st.selectbox("Ngữ cảnh:", ["Văn phòng/Kỹ thuật", "Kính ngữ (Sếp)", "Thân mật"])
    with col2:
        st.write("")
        st.write("")
        # Nút submit trong form
        submit_button = st.form_submit_button("Dịch ngay (Ctrl+Enter)", use_container_width=True)

# Xử lý sau khi nhấn nút hoặc nhấn Ctrl + Enter
if submit_button:
    if source_text.strip():
        st.subheader("Kết quả tiếng Nhật:")
        result_placeholder = st.empty()
        full_response = ""

        # Hiện vòng tròn process (Spinner)
        with st.spinner('Đang kết nối API và dịch...'):
            try:
                response = model.generate_content(f"Context: {mode}. Dịch: {source_text}", stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        # Cập nhật kết quả chạy ra từ từ
                        result_placeholder.code(full_response, language="text")
                
                st.toast('Đã dịch xong!', icon='✅')
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
    else:
        st.warning("Vui lòng nhập văn bản trước khi dịch.")

st.divider()