import streamlit as st
import requests
import json

st.set_page_config(page_title="AI Engineer RAG Chat", layout="wide")

st.title("🤖 Local RAG Assistant")
st.markdown("---")

# Cấu hình URL của FastAPI
API_URL = "http://localhost:8000/chat"

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị các tin nhắn cũ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận câu hỏi từ người dùng
if prompt := st.chat_input("Hỏi tôi về tài liệu của bạn..."):
    # Hiển thị tin nhắn user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi API và hiển thị tin nhắn Assistant (Streaming)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Gọi FastAPI với chế độ stream
        try:
            # Gửi request POST tới FastAPI
            with requests.post(API_URL, json={"query": prompt, "stream": True}, stream=True) as r:
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        # Giải mã và cập nhật giao diện
                        text = chunk.decode("utf-8")
                        full_response += text
                        response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Lỗi kết nối API: {e}")