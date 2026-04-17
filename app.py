import streamlit as st
from agent_logic import setup_agent

st.set_page_config(page_title="Smart AI Assistant", page_icon="🧠", layout="centered")

st.title("🧠 Smart Agent with Memory")
st.info("Aapka Hukm? Main emails bhej sakta hoon aur purani baatein yaad rakh sakta hoon.")

# Session State initialization
if "agent" not in st.session_state:
    with st.spinner("Agent ready ho raha hai..."):
        st.session_state.agent = setup_agent()

user_prompt = st.text_input("Aapka Sawal ya Task:", placeholder="e.g., Send email to aleemamjad099@gmail.com about success")

if st.button("Execute Task"):
    if user_prompt:
        try:
            with st.spinner("Processing..."):
                response = st.session_state.agent.invoke({"input": user_prompt})
                st.subheader("Assistant ka Jawab:")
                st.success(response["output"])
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("Prompt likhna zaroori hai.")

# --- FIXED SIDEBAR ---
with st.sidebar:
    st.header("Chat History")
    if "agent" in st.session_state:
        # LangChain memory access karne ka sahi tareeqa
        messages = st.session_state.agent.memory.chat_memory.messages
        for msg in messages:
            role = "User" if msg.type == "human" else "Assistant"
            st.write(f"**{role}:** {msg.content}")
