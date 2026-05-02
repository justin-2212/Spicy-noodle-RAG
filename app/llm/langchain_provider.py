# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config.settings import settings
from app.utils.logger import logger

# class LangChainGroq:
#     """Groq LLM provider using LangChain."""
#     
#     def __init__(self):
#         self.llm = ChatGroq(
#             model_name=settings.llm.groq_model_name,
#             temperature=settings.llm.temperature,
#             groq_api_key=settings.llm.groq_api_key,
#             max_tokens=settings.llm.max_tokens
#         )

class LangChainGemini:
    """Gemini LLM provider using LangChain."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.llm.gemini_model_name,
            temperature=settings.llm.temperature,
            google_api_key=settings.llm.gemini_api_key,
            max_output_tokens=settings.llm.max_tokens
        )

class LangChainLLMProvider:
    """Main LLM provider factory."""
    
    def get_llm(self):
        """Get Gemini LLM based on settings."""
        
        logger.info(f"Using Gemini LLM: {settings.llm.gemini_model_name}")
        return LangChainGemini().llm
