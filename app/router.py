from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from app.config import settings

# 1. Define the Router Output Schema
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: str = Field(
        description="Given a user question choose to route it to 'vectorstore', 'sql_database', or 'live_market_data'."
    )

# 2. Build the Router LLM with fallback
def get_router_llm():
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )
    except Exception:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

llm = get_router_llm()
structured_llm_router = llm.with_structured_output(RouteQuery)

# 3. Create the Routing Prompt
system = """You are an expert at routing financial questions to the correct specialized system.
The system has three specialized components:

1. live_market_data: Use for real-time stock price, today's market quote, current ticker valuation, live market cap, current trading price, 52-week high/low, P/E ratio, or analyst targets.
2. sql_database: Use for audited annual financial statement tables like exact fiscal year total net sales, gross margin, audited R&D expenditure, or audited diluted EPS comparisons across years.
3. vectorstore: Use for qualitative text from SEC filings, Risk Factors, Apple Intelligence strategy, regulatory inquiries, and business narrative disclosures.

Routing Rules:
- Questions about current stock price, today's market quote, live valuation, or P/E -> 'live_market_data'.
- Questions asking for exact statement table figures or YoY financial numbers -> 'sql_database'.
- Questions asking about risks, strategy, qualitative context, or 'why' -> 'vectorstore'.
"""

route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

# 4. Chain it together using LCEL
question_router = route_prompt | structured_llm_router

def route_question(question: str) -> str:
    """Returns 'vectorstore', 'sql_database', or 'live_market_data'."""
    # Fast regex pre-check for common market terms to preserve quota
    q_lower = question.lower()
    if any(k in q_lower for k in ["stock price", "current price", "market cap", "trading at", "quote", "share price", "p/e ratio", "pe ratio"]):
        return "live_market_data"
        
    try:
        result = question_router.invoke({"question": question})
        chosen = result.datasource.strip()
        if chosen in ["vectorstore", "sql_database", "live_market_data"]:
            return chosen
        return "vectorstore"
    except Exception as e:
        print(f"Router LLM fallback triggered ({e}).")
        if any(w in q_lower for w in ["how much", "what was", "revenue", "sales", "net income", "margin", "eps"]):
            return "sql_database"
        return "vectorstore"
