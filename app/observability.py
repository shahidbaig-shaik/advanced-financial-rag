import os
from langfuse.callback import CallbackHandler

def get_langfuse_handler(user_id: str = "anonymous", session_id: str = None):
    """
    Creates a Langfuse callback handler for LangChain/LangGraph tracing.
    Every LLM call, retrieval, and re-ranking step gets logged automatically.
    """
    handler = CallbackHandler(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        user_id=user_id,
        session_id=session_id,
    )
    return handler
