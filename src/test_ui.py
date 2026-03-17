import streamlit as st
import requests

st.set_page_config(page_title="AI Engineer RAG", layout="wide")

# --- SIDEBAR: QUẢN LÝ FILE ---
with st.sidebar:
    st.header("📁 Tài liệu của bạn")
    uploaded_file = st.file_uploader("Tải lên PDF mới", type="pdf")
    if uploaded_file and st.button("Nạp vào hệ thống"):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        res = requests.post("http://localhost:8000/upload", files=files)
        if res.status_code == 200:
            st.success("Đã nạp tài liệu!")
        else:
            st.error("Lỗi upload")

# --- MAIN: GIAO DIỆN CHAT ---
st.title("💬 RAG Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Hỏi gì đó về tài liệu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Gọi API Chat của bạn
        response = requests.post("http://localhost:8000/chat", json={"query": prompt, "stream": False})
        answer = response.json().get("answer", "Lỗi rồi!")
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})