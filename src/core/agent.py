from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.core.tools import query_invoice_database, generate_bilan_report, get_invoice_details, list_all_invoices_summary
from dotenv import load_dotenv

load_dotenv()

def get_agent_executor():
    """Initializes the AI Agent with tools."""
    llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0)
    
    tools = [query_invoice_database, generate_bilan_report, get_invoice_details, list_all_invoices_summary]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an intelligent Invoice Assistant. You can search for information in invoices, generate summary reports (bilan), and get specific invoice details. Use your tools to provide accurate answers."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
