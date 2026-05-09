"""Prompt templates."""

from app.utils.config_loader import load_system_prompt

RAG_PROMPT_TEMPLATE = """Based on the following spicy noodle menu items from our restaurant, provide personalized food recommendations:

Menu Context:
{context}

User Request: {query}

Conversation History:
{history}

Please provide helpful, personalized recommendations based on the user's request and available spicy noodle items.
Include why you think each item matches their preferences."""

QUERY_REWRITE_TEMPLATE = """Given the user's query, expand it to capture their intent better.
Include dietary preferences, price range, cuisine type, etc.

Original Query: {query}
Expanded Query:"""

SUMMARY_TEMPLATE = """Summarize the following spicy noodle items for a user who asked: {query}

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
        return load_system_prompt()