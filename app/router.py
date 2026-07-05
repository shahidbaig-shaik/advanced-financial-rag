from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from app.config import settings

# 1. Define the Router Output Schema
class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""
    datasource: str = Field(
        description="Given a user question choose to route it to 'vectorstore' or 'sql_database'."
    )

# 2. Build the Router LLM
# We use Gemini 2.5 Flash, forced to output exactly our Pydantic schema
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.gemini_api_key,
    temperature=0,
)
structured_llm_router = llm.with_structured_output(RouteQuery)

# 3. Create the Routing Prompt
system = """You are an expert at routing user questions to the correct system.
The financial analyst system has two datastores:

1. vectorstore: Contains qualitative text from SEC filings, Risk Factors, Strategy, and MD&A narratives.
2. sql_database: Contains tabular financial data like exact quarterly revenue numbers, margin percentages, and EPS.

Route the user's question based on what datastore is most appropriate.
If the question asks for a specific number from an income statement, route to sql_database.
If the question asks about strategy, risks, or "why" something happened, route to vectorstore.
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
    """Returns 'vectorstore' or 'sql_database'"""
    result = question_router.invoke({"question": question})
    return result.datasource
