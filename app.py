import streamlit as st
from agent_logic import setup_agent

st.set_page_config(page_title="Smart AI Agent", page_icon="🧠")

st.title("🧠 Smart Agent with Memory")

# Session state mein agent ko save karna taake memory barqarar rahe
if "agent" not in st.session_state:
    st.session_state.agent = setup_agent()

user_prompt = st.text_input("Aapka Hukm?", key="input")

if st.button("Execute"):
    if user_prompt:
        with st.spinner("Agent soch raha hai..."):
            # Direct agent use karein jo session state mein hai
            response = st.session_state.agent.run(input=user_prompt)
            st.success("Done!")
            st.write(response)
    else:
        st.warning("Kuch likhein to sahi!")

if st.button("Reset Memory"):
    st.session_state.clear()
    st.rerun()