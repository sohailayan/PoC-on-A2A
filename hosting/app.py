import streamlit as st
import requests
import uuid

WRITER_RUN = "http://localhost:8000/run"
TRANSLATOR_RUN = "http://localhost:8001/run"

st.title("📝 A2A Blog Generator + Translator")

topic = st.text_input("Enter blog topic:", "")
target_lang = st.selectbox("Translate to:", ["fr", "es", "de", "hi", "zh"], index=0)  # French default
submit = st.button("Generate + Translate")

if submit and topic:
    # Step 1: Call Blog Generator Agent
    with st.spinner("Generating blog post..."):
        blog_task_id = str(uuid.uuid4())
        blog_payload = {
            "jsonrpc": "2.0",
            "id": blog_task_id,
            "method": "tasks/send",
            "params": {
                "task": {"topic": topic},
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": topic}]
                },
                "metadata": {}
            }
        }
        writer_resp = requests.post(WRITER_RUN, json=blog_payload).json()
        if "error" in writer_resp:
            st.error(f"Blog agent error: {writer_resp['error'].get('message', writer_resp['error'])}")
            st.stop()
        try:
            eng_text = writer_resp["result"]["artifacts"][0]["data"]["text"]
        except Exception as e:
            st.error(f"Blog agent response parsing error: {str(e)}")
            st.stop()

    st.markdown("### ✍️ English Blog")
    st.text_area("English Output", eng_text, height=200)

    # Step 2: Call Translator Agent
    with st.spinner(f"Translating blog to {target_lang.upper()}..."):
        trans_task_id = str(uuid.uuid4())
        trans_payload = {
            "jsonrpc": "2.0",
            "id": trans_task_id,
            "method": "tasks/send",
            "params": {
                "task": {
                    "source_lang": "en",
                    "target_lang": target_lang
                },
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": eng_text}]
                },
                "metadata": {}
            }
        }
        trans_resp = requests.post(TRANSLATOR_RUN, json=trans_payload).json()
        if "error" in trans_resp:
            st.error(f"Translator agent error: {trans_resp['error'].get('message', trans_resp['error'])}")
            st.stop()
        try:
            translated_text = trans_resp["result"]["artifacts"][0]["data"]["text"]
        except Exception as e:
            st.error(f"Translator agent response parsing error: {str(e)}")
            st.stop()

    st.markdown(f"### 🌍 Translated Blog ({target_lang.upper()})")
    st.text_area(f"{target_lang.upper()} Output", translated_text, height=200)
