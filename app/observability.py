import os
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

load_dotenv()

def get_langfuse_handler(user_id: str = "anonymous", session_id: str = None):
    """
    Creates a Langfuse callback handler for LangChain/LangGraph tracing.
    Every LLM call, retrieval, and re-ranking step gets logged automatically.
    """
    base_url = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST")
    if base_url:
        cleaned_host = base_url.strip('"').strip("'")
        os.environ["LANGFUSE_HOST"] = cleaned_host
        os.environ["LANGFUSE_BASE_URL"] = cleaned_host

    pk = os.getenv("LANGFUSE_PUBLIC_KEY")
    if pk:
        os.environ["LANGFUSE_PUBLIC_KEY"] = pk.strip('"').strip("'")

    sk = os.getenv("LANGFUSE_SECRET_KEY")
    if sk:
        os.environ["LANGFUSE_SECRET_KEY"] = sk.strip('"').strip("'")

    try:
        handler = CallbackHandler()
        return handler
    except Exception as e:
        print(f"Warning: Failed to initialize Langfuse callback handler: {e}")
        return None
