# 🧠 Smart AI Email Agent with Contextual Memory

A professional Agentic AI system that understands natural language instructions to draft and send emails. Built using **LangChain**, **Groq (Llama 3)**, and **Streamlit**, this agent maintains a conversation history to provide a personalized experience.

---

## 🚀 Features
- **Contextual Memory:** Remembers previous interactions (e.g., your name or project details) to make future tasks easier.
- **Autonomous Drafting:** High-quality professional email drafting using Llama 3.3.
- **Tool Integration:** Uses custom Python tools to interface with SMTP servers for real-time email dispatch.
- **Streamlit UI:** A clean, user-friendly web interface for interacting with the agent.
- **Chrome Extension Support:** Can be embedded into a Chrome Extension for quick access.

## 🛠️ Tech Stack
- **Framework:** [LangChain](https://www.langchain.com/)
- **LLM:** [Groq Cloud](https://groq.com/) (Llama-3.3-70b-versatile)
- **Frontend:** [Streamlit](https://streamlit.io/)
- **Language:** Python 3.10+
- **Environment:** Streamlit Cloud / GitHub

## 📂 Project Structure
```text
├── app.py                # Main Streamlit UI & Session Management
├── agent_logic.py        # Agent initialization & custom tool definitions
├── utils.py              # Helper functions (e.g., SMTP email sending)
├── requirements.txt      # List of dependencies
└── .env                  # Environment variables (API Keys)
