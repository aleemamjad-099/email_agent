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

def setup_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Critical Error: GROQ_API_KEY missing in Secrets!")

    # LLM Setup
    llm = ChatGroq(
        api_key=api_key, 
        model_name="llama-3.3-70b-versatile", 
        temperature=0
    )

    # Professional Email Tool Wrapper
    def email_tool_wrapper(input_data):
        try:
            if "," not in input_data:
                return "Error: Please use the format 'recipient@email.com, brief content'."
            
            parts = input_data.split(",", 1)
            recipient_email = parts[0].strip()
            message_context = parts[1].strip()

            # Clean email using Regex
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', recipient_email)
            final_email = email_match.group(0) if email_match else recipient_email

            # Drafting the professional body
            prompt = (
                f"Draft a highly professional corporate email for: {message_context}. "
                "Include a clear Subject and a formal Body. Be concise."
            )
            draft = llm.invoke(prompt).content

            # Sending the email
            status = send_email(final_email, "Automated Professional Update", draft)
            return f"Success: {status} to {final_email}"
        
        except Exception as e:
            return f"Tool Error: {str(e)}"

    # Tool Definition
    tools = [
        Tool(
            name="Email_Sender_Tool",
            func=email_tool_wrapper,
            description="Use this tool ONLY to send emails. Input should be: 'email, brief_task'"
        )
    ]

    # ReAct Prompt & Memory
    prompt = hub.pull("hwchase17/react-chat")
    agent_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Creating the Agent
    agent = create_react_agent(llm, tools, prompt)

    # Agent Executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=agent_memory,
        verbose=True,
        handle_parsing_errors=True
    )
