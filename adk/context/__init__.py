"""
Context Engineering - Intelligent context management and compression.
Reduces token usage through summarization and compaction.
"""

from typing import List, Dict, Any, Optional

from ..core.logger import get_logger

logger = get_logger(__name__)


class ContextCompactor:
    """
    Compress and summarize long contexts to reduce token usage.
    
    Strategies:
    - Summarization: Use LLM to summarize long text
    - Deduplication: Remove duplicate information
    - Prioritization: Keep most relevant information
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize context compactor.
        
        Args:
            llm_client: Optional LLM client for summarization
        """
        self.llm_client = llm_client
        logger.info("Context compactor initialized")
    
    async def compact_regulations(
        self,
        regulations: List[Dict[str, Any]],
        max_items: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Compact a list of regulations.
        
        Args:
            regulations: List of regulation documents
            max_items: Maximum number of items to keep
            
        Returns:
            Compacted regulations
        """
        if len(regulations) <= max_items:
            return regulations
        
        logger.info(
            "Compacting regulations",
            original_count=len(regulations),
            target_count=max_items
        )
        
        # Strategy 1: Deduplication
        unique_regs = self._deduplicate(regulations)
        
        if len(unique_regs) <= max_items:
            return unique_regs
        
        # Strategy 2: Prioritization (keep highest relevance scores)
        sorted_regs = sorted(
            unique_regs,
            key=lambda r: r.get('relevance_score', 0),
            reverse=True
        )
        
        compacted = sorted_regs[:max_items]
        
        logger.info(
            "Regulations compacted",
            final_count=len(compacted)
        )
        
        return compacted
    
    async def summarize_text(
        self,
        text: str,
        max_length: int = 500
    ) -> str:
        """
        Summarize long text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        if len(text) <= max_length:
            return text
        
        logger.info(
            "Summarizing text",
            original_length=len(text),
            target_length=max_length
        )
        
        # If LLM available, use it for intelligent summarization
        if self.llm_client:
            try:
                summary = await self._llm_summarize(text, max_length)
                logger.info("LLM summarization completed", summary_length=len(summary))
                return summary
            except Exception as e:
                logger.warning("LLM summarization failed", error=str(e))
        
        # Fallback: Simple truncation with ellipsis
        summary = text[:max_length] + "..."
        logger.info("Fallback summarization used")
        
        return summary
    
    async def _llm_summarize(self, text: str, max_length: int) -> str:
        """
        Use LLM to summarize text.
        
        Args:
            text: Text to summarize
            max_length: Target length
            
        Returns:
            Summary
        """
        prompt = f"""Summarize the following text in approximately {max_length} characters. 
Focus on the key points and maintain clarity.

Text:
{text}

Summary:"""
        
        response = await self.llm_client.generate(prompt)
        return response.strip()
    
    def _deduplicate(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate items based on content.
        
        Args:
            items: List of items
            
        Returns:
            Deduplicated items
        """
        seen = set()
        unique = []
        
        for item in items:
            # Use text content as deduplication key
            key = item.get('text', '')[:100]  # First 100 chars
            
            if key not in seen:
                seen.add(key)
                unique.append(item)
        
        logger.debug(
            "Deduplication completed",
            original=len(items),
            unique=len(unique)
        )
        
        return unique
    
    async def compact_context(
        self,
        context: Dict[str, Any],
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Compact entire context dictionary.
        
        Args:
            context: Context dictionary
            max_tokens: Maximum token budget
            
        Returns:
            Compacted context
        """
        compacted = {}
        
        for key, value in context.items():
            if isinstance(value, str):
                # Summarize long strings
                if len(value) > 500:
                    compacted[key] = await self.summarize_text(value, 500)
                else:
                    compacted[key] = value
                    
            elif isinstance(value, list):
                # Compact lists
                if len(value) > 5:
                    compacted[key] = value[:5]  # Keep first 5 items
                else:
                    compacted[key] = value
                    
            else:
                compacted[key] = value
        
        logger.info("Context compacted", original_keys=len(context), compacted_keys=len(compacted))
        
        return compacted


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Rough approximation: 1 token ≈ 4 characters
    
    Args:
        text: Text to estimate
        
    Returns:
        Estimated token count
    """
    return len(text) // 4


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token budget.
    
    Args:
        text: Text to truncate
        max_tokens: Maximum tokens
        
    Returns:
        Truncated text
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    return text[:max_chars] + "..."
