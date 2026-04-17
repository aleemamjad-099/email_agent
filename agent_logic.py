import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from utils import send_email

# Load environment variables
load_dotenv()

# Global memory to persist across the session
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

    # --- THE PRO-LEVEL EMAIL WRAPPER (Writer + Critic Logic) ---
    def email_tool_wrapper(input_data):
        try:
            # 1. Parsing & Cleaning
            if "," not in input_data:
                return "Error: Use 'email, message' format."
            
            parts = input_data.split(",", 1)
            raw_email = parts[0].strip()
            raw_content = parts[1].strip()

            # Regex for clean email extraction
            clean_email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_email)
            recipient_email = clean_email_match.group(0) if clean_email_match else raw_email.replace("'", "").replace('"', "").strip()

            # 2. PRO STEP: Brainstorming Subject & Body
            brainstorm_prompt = (
                f"You are a professional corporate writer. Based on this note: '{raw_content}', "
                "generate a professional email. \n"
                "Return the response in this EXACT format:\n"
                "SUBJECT: [Catchy & Professional Subject]\n"
                "BODY: [The entire professional email body]"
            )
            draft_output = llm.invoke(brainstorm_prompt).content

            # 3. PRO STEP: Internal Critic (Strict Correction)
            # Yahan humne strict instruction di hai taake 'Notes' na ayein
            critic_prompt = (
                f"Review this draft for any spelling mistakes or tone issues:\n\n{draft_output}\n\n"
                "STRICT RULES:\n"
                "1. Fix errors but output ONLY the 'SUBJECT:' and 'BODY:' sections.\n"
                "2. DO NOT include any 'Notes', 'Explanations', or 'Original draft was good' comments.\n"
                "3. Just provide the final polished email data in the requested format."
            )
            final_output = llm.invoke(critic_prompt).content

            # 4. Extracting Subject and Body using more flexible Regex
            try:
                # Re.S flag use kiya taake new lines bhi capture hon
                subject_match = re.search(r"SUBJECT:(.*)", final_output, re.IGNORECASE)
                body_match = re.search(r"BODY:([\s\S]*)", final_output, re.IGNORECASE)
                
                subject = subject_match.group(1).strip() if subject_match else "Professional Update"
                body = body_match.group(1).strip() if body_match else final_output
                
                # Agar body mein 'Note:' ab bhi nazar aye to usay remove kardo
                body = body.split("Note:")[0].split("NOTE:")[0].strip()
                
            except Exception:
                subject = "Professional Correspondence"
                body = final_output

            # 5. Final Send
            status = send_email(recipient_email, subject, body)
            return f"Pro-Report: {status} to {recipient_email} with Subject: {subject}"

        except Exception as e:
            return f"Pro-Tool Error: {str(e)}"

    # --- Tool Definition ---
    tools = [
        Tool(
            name="Email_Sender_Tool",
            func=email_tool_wrapper,
            description="MANDATORY for sending emails. Input format: 'recipient@email.com, brief content'"
        )
    ]

    # --- System Message (The Personality Lock) ---
    system_message = (
        "You are an Elite AI Executive Assistant. Your standards are exceptionally high.\n"
        "1. Accuracy: Never send an email with a typo.\n"
        "2. Context: Use chat_history to know who you are talking to.\n"
        "3. Tone: Be polite, formal, and efficient.\n"
        "4. Signature: Always sign off professionally using the sender's name from memory if available."
    )

    # --- Agent Initialization ---
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=agent_memory,
        handle_parsing_errors=True,
        max_iterations=5,
        agent_kwargs={"system_message": system_message}
    )
    
    return agent