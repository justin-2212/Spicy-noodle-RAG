"""Prompt templates."""

SYSTEM_PROMPT = """You are a helpful food recommendation assistant for a restaurant.
You help customers find dishes that match their preferences, dietary requirements, and budget.
Always be friendly, professional, and provide personalized recommendations based on the available menu items.

When providing recommendations:
1. Consider the user's dietary preferences and restrictions
2. Suggest items within their budget
3. Explain why each recommendation is suitable
4. Ask follow-up questions if needed for better recommendations
5. Be specific about prices and availability
"""

RAG_PROMPT_TEMPLATE = """Based on the following menu items from our restaurant, provide personalized food recommendations:

Menu Context:
{context}

User Request: {query}

Conversation History:
{history}

Please provide helpful, personalized recommendations based on the user's request and available items.
Include why you think each item matches their preferences."""

QUERY_REWRITE_TEMPLATE = """Given the user's query, expand it to capture their intent better.
Include dietary preferences, price range, cuisine type, etc.

Original Query: {query}
Expanded Query:"""

SUMMARY_TEMPLATE = """Summarize the following food items for a user who asked: {query}

Items:
{items}

Summary:"""


class PromptBuilder:
    """Build prompts from templates."""
    
    @staticmethod
    def build_rag_prompt(
        context: str,
        query: str,
        history: str = ""
    ) -> str:
        """
        Build RAG prompt with context.
        
        Args:
            context: Retrieved documents
            query: User query
            history: Conversation history
            
        Returns:
            Complete prompt
        """
        return RAG_PROMPT_TEMPLATE.format(
            context=context,
            query=query,
            history=history or "None"
        )
    
    @staticmethod
    def build_system_prompt() -> str:
        """Get system prompt."""
        return SYSTEM_PROMPT
