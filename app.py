import streamlit as st
from agent_logic import setup_agent

# Page Config
st.set_page_config(page_title="Smart AI Assistant", page_icon="🧠", layout="centered")

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Smart Agent with Memory")
st.info("Aapka Hukm? Main aapke liye emails bhej sakta hoon aur purani baatein yaad rakh sakta hoon.")

# Agent Initialization in Session State
if "agent" not in st.session_state:
    with st.spinner("Agent jag raha hai..."):
        st.session_state.agent = setup_agent()

# User Input
user_prompt = st.text_input("Aapka Sawal ya Task:", placeholder="e.g., Send a formal email to Mudassar at aleemamjad0@gmail.com about project update")

if st.button("Execute Task"):
    if user_prompt:
        try:
            with st.spinner("AI soch raha hai..."):
                # Modern LangChain Invoke Method
                response = st.session_state.agent.invoke({"input": user_prompt})
                
                st.subheader("Assistant ki Taraf se Jawab:")
                st.success(response["output"])
        except Exception as e:
            st.error(f"Maaf kijiye, masla aa gaya: {str(e)}")
    else:
        st.warning("Pehle kuch likh to lein!")

# Chat History Sidebar (Optional)
with st.sidebar:
    st.header("Chat History")
    if "agent" in st.session_state:
        for msg in st.session_state.agent.memory.chat_history:
            st.write(f"**{msg.type.capitalize()}:** {msg.content}")
