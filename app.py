import os  # THÊM DÒNG NÀY VÀO ĐẦU FILE
import streamlit as st
import google.generativeai as genai

# Sau đó mới lấy API_KEY
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("Không tìm thấy API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-3.1-flash-lite-preview" 
generation_config = {
    "temperature": 0.0,
    "max_output_tokens": 1000,
}
# ================== CẤU HÌNH NGÔN NGỮ UI ==================
UI_TEXT = {
    "vi_to_jp": {
        "title": "🎨 LSA - Design Team Internal",
        "placeholder": "Nhập nội dung cần dịch... (Ctrl + Enter để dịch)",
        "button": "🚀 Dịch ngay",
        "toast": "Dịch hoàn tất!",
        "label_context": "Ngữ cảnh:",
        "label_input": "Văn bản nguồn:",
        "result_title": "Bản dịch tiếng Nhật:",
        "warning": "Vui lòng nhập nội dung cần dịch.",
        "footer": "💡 Copyright LinkStoryAsia | Dịch thuật nội bộ Design Team Ver 2.0",
        "lang_left": "Tiếng Việt",
        "lang_right": "Tiếng Nhật"
    },
    "jp_to_vi": {
        "title": "🎨 LSA - デザインチーム内部翻訳",
        "placeholder": "翻訳する内容を入力してください... (Ctrl + Enter)",
        "button": "🚀 翻訳する",
        "toast": "翻訳が完了しました！",
        "label_context": "文脈:",
        "label_input": "原文:",
        "result_title": "ベトナム語訳:",
        "warning": "内容を入力してください。",
        "footer": "💡 LinkStoryAsia | デザインチーム翻訳ツール Ver 2.0",
        "lang_left": "日本語",
        "lang_right": "ベトナム語"
    }
}

# ================== QUẢN LÝ TRẠNG THÁI (SESSION STATE) ==================
if "is_jp_to_vi" not in st.session_state:
    st.session_state.is_jp_to_vi = False

current_lang_key = "jp_to_vi" if st.session_state.is_jp_to_vi else "vi_to_jp"
ui = UI_TEXT[current_lang_key]

# Định nghĩa System Instruction động dựa trên hướng dịch
if st.session_state.is_jp_to_vi:
    sys_msg = (
        "Bạn là máy dịch Nhật-Việt chuyên về mảng Design/Manga/Webtoon. "
        "NHIỆM VỤ DUY NHẤT: Dịch văn bản đầu vào sang tiếng Việt tự nhiên, chuyên nghiệp. "
        "KHÔNG giải thích, KHÔNG thêm text thừa."
        "Nếu có gặp từ có từ khóa là Inpainting thì hãy dịch là 削除補完 hoặc là giữ nguyên"
        "Nếu bạn dùng những từ liên quan đến ứng dụng Photoshop thì sử dụng thuật ngữ chuyên môn"
        "- Retouch: レタッチ | Vẽ bù/Vẽ thêm: 加筆する "
        "- Lettering: 写植 (Shashoku) | Làm sạch (Cleaning): ゴミ取り (Gomitori) "
        "- Layer ẩn: 非表示レイヤー | Folder/Group: フォルダ / グループ "
        "- Inpainting: インペイント (Luôn hiểu là một Folder/Layer Set trong Photoshop) "
        "- Script: スクリプト "
        "YÊU CẦU: Dịch tự nhiên theo văn phong kỹ thuật Nhật Bản. KHÔNG giải thích, KHÔNG thêm '作業指示' hay liệt kê từ vựng."
    )
else:
    sys_msg = (
        "Bạn là máy dịch Việt-Nhật. NHIỆM VỤ DUY NHẤT: Dịch văn bản đầu vào. "
        "KHÔNG giải thích, KHÔNG thêm '作業指示', KHÔNG liệt kê từ vựng. "
        "Ưu tiên dùng: 写植, レタッチ, 描き込み, 非表示, フォルダ, レイヤー."
    )

model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=sys_msg
)

# ================== GIAO DIỆN & CSS (Hiệu ứng Gemini) ==================
st.set_page_config(page_title="LSA Translator", page_icon="🎨", layout="centered")

st.markdown("""
    <style>
    @keyframes gemini-sparkle {
        0% { background-position: 0% 50%; transform: scale(1); }
        50% { background-position: 100% 50%; transform: scale(1.1); }
        100% { background-position: 0% 50%; transform: scale(1); }
    }
    .ai-sparkle {
        display: inline-block;
        background: linear-gradient(-45deg, #4285f4, #9b72cb, #d96570, #13abff);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px; font-weight: bold;
        animation: gemini-sparkle 3s ease infinite;
        vertical-align: middle; margin-right: 8px;
    }
    .result-box {
        background-color: #1e1e1e; color: #f0f0f0;
        padding: 22px 24px; border-radius: 16px;
        border: 1px solid #444; font-size: 16.5px;
        line-height: 1.75; white-space: pre-wrap;
        min-height: 120px; box-shadow: 0 10px 35px rgba(0, 0, 0, 0.4);
    }
    footer {visibility: hidden;}
    .stTextArea textarea { font-size: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title(ui["title"])

# ================== BỘ CHUYỂN ĐỔI NGÔN NGỮ (MŨI TÊN) ==================
col_l, col_btn, col_r = st.columns([2, 1, 2])
with col_l:
    st.markdown(f"<h4 style='text-align: right; color: #4285f4;'>{ui['lang_left']}</h4>", unsafe_allow_html=True)
with col_btn:
    if st.button("⇄", use_container_width=True, help="Đảo chiều dịch"):
        st.session_state.is_jp_to_vi = not st.session_state.is_jp_to_vi
        st.rerun()
with col_r:
    st.markdown(f"<h4 style='text-align: left; color: #9b72cb;'>{ui['lang_right']}</h4>", unsafe_allow_html=True)

# ================== FORM NHẬP LIỆU ==================
with st.form(key='translation_form', clear_on_submit=False):
    source_text = st.text_area(
        ui["label_input"], 
        height=150,
        placeholder=ui["placeholder"],
        key="main_input",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([2, 1]) 
    with col1:
        # Tùy chọn ngữ cảnh cũng thay đổi theo ngôn ngữ UI
        contexts = ["Văn phòng", "Kính ngữ", "Thân mật"] if not st.session_state.is_jp_to_vi else ["ビジネス", "丁寧語", "カジュアル"]
        mode = st.selectbox(ui["label_context"], contexts, label_visibility="collapsed")
    with col2:
        submit_button = st.form_submit_button(ui["button"], use_container_width=True, type="primary")

# ================== XỬ LÝ DỊCH ==================
if submit_button:
    if source_text.strip():
        st.markdown(f'<p><span class="ai-sparkle">✨</span><span style="font-size:18px; font-weight:bold;">{ui["result_title"]}</span></p>', unsafe_allow_html=True)
        
        result_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("..."):
            try:
                target_lang = "Vietnamese" if st.session_state.is_jp_to_vi else "Japanese"
                prompt = f"Dịch văn bản sau sang {target_lang} với phong cách {mode}: {source_text}"
                
                response = model.generate_content(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        result_placeholder.markdown(f"""
                            <div class="result-box">
                                {full_response.replace('\n', '<br>')}
                            </div>
                        """, unsafe_allow_html=True)
                
                # Hiệu ứng hoàn tất với border sáng
                result_placeholder.markdown(f"""
                    <div class="result-box" style="border: 1px solid #13abff; box-shadow: 0 0 20px rgba(19, 171, 255, 0.4);">
                        {full_response.replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)
                st.toast(ui["toast"], icon="✨")
                
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
    else:
        st.warning(ui["warning"])

# ================== FOOTER ==================
st.markdown(f"""
    <div style="text-align: center; color: #888; font-size: 13px; margin-top: 30px; border-top: 0.5px solid #333; padding-top: 20px;">
        {ui["footer"]}
    </div>
""", unsafe_allow_html=True)
