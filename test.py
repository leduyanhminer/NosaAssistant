import streamlit as st
from openai import OpenAI

# 1. Cấu hình trang & Giao diện (Phải để ở đầu)
st.set_page_config(page_title="NosaAssistant", page_icon="🤖", layout="centered")

# 2. "Độ" CSS để giao diện đẹp hơn
st.markdown("""
    <style>
    /* Bo góc khung chat và đổi màu nền */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* Tinh chỉnh sidebar */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
        border-right: 1px solid #e0e0e0;
    }
    /* Làm đẹp tiêu đề */
    h1 {
        color: #1E88E5;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    /* Chỉnh input chat nằm gọn gàng */
    .stChatInput {
        border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR CẤU HÌNH ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/6134/6134346.png", width=80)
    st.title("Nosa Settings")
    host = st.text_input("🚀 Ollama Host", "http://localhost:11434/v1")
    model = st.selectbox("🧠 Chọn Model", ["qwen2.5:14b-instruct-q4_K_M", "llama3.1:8b"])
    st.divider()
    if st.button("🗑️ Xóa hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- NỘI DUNG CHÍNH ---
st.title("NosaAssistant")

client = OpenAI(base_url=host, api_key="ollama")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Xử lý Chat
if prompt := st.chat_input("Hỏi Nosa bất cứ điều gì..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"⚠️ Lỗi: {e}")