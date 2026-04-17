import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from utils import send_email

# Load environment variables
load_dotenv()

# Global memory
agent_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def setup_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Error: .env file mein GROQ_API_KEY nahi mili!")

    # --- Smart Model Fallback Logic ---
    models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant"]
    llm = None
    for model in models_to_try:
        try:
            temp_llm = ChatGroq(api_key=api_key, model_name=model, temperature=0)
            temp_llm.invoke("test") 
            llm = temp_llm
            break
        except Exception:
            continue

    if not llm:
        raise ValueError("Critical Error: Groq models are not responding.")

    # --- PRO-LEVEL EMAIL WRAPPER ---
    def email_tool_wrapper(input_data):
        try:
            if "," not in input_data:
                return "Error: Use 'email, message' format."
            
            parts = input_data.split(",", 1)
            raw_email = parts[0].strip()
            raw_content = parts[1].strip()

            clean_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_email)
            recipient_email = clean_email_match.group(0) if clean_email_match else raw_email.replace("'", "").replace('"', "").strip()

            # Step 1: Draft
            brainstorm_prompt = (
                f"You are a professional corporate writer. Based on this note: '{raw_content}', "
                "generate a professional email. Return ONLY in this format:\n"
                "SUBJECT: [Subject]\nBODY: [Email Body]"
            )
            draft_output = llm.invoke(brainstorm_prompt).content

            # Step 2: Critic (Strict)
            critic_prompt = (
                f"Review this draft for errors:\n\n{draft_output}\n\n"
                "STRICT RULES: Fix errors but output ONLY 'SUBJECT:' and 'BODY:' sections. "
                "NO notes, NO explanations. Just the raw email data."
            )
            final_output = llm.invoke(critic_prompt).content

            # Parsing
            try:
                subject = re.search(r"SUBJECT:(.*)", final_output, re.IGNORECASE).group(1).strip()
                body_full = re.search(r"BODY:([\s\S]*)", final_output, re.IGNORECASE).group(1).strip()
                body = body_full.split("Note:")[0].split("NOTE:")[0].strip()
            except:
                subject = "Professional Update"
                body = final_output

            status = send_email(recipient_email, subject, body)
            return f"Pro-Report: {status} to {recipient_email} with Subject: {subject}"

        except Exception as e:
            return f"Pro-Tool Error: {str(e)}"

    # --- Tool & Agent Setup (Modern Way) ---
    tools = [
        Tool(
            name="Email_Sender_Tool",
            func=email_tool_wrapper,
            description="MANDATORY for sending emails. Input format: 'recipient@email.com, message'"
        )
    ]

    # Re-Act Prompt pull kar rahe hain (Standard way)
    prompt = hub.pull("hwchase17/react-chat")

    # Agent create kar rahe hain
    agent = create_react_agent(llm, tools, prompt)

    # Agent Executor (Jo agent ko run karega)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=agent_memory, 
        verbose=True, 
        handle_parsing_errors=True
    )
    
    return agent_executor
