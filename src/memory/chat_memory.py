from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from typing import List, Dict, Any

class SPBEChatMemory:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    
    def add_user_message(self, message: str):
        """Add a user message to the chat history"""
        self.memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, message: str):
        """Add an AI message to the chat history"""
        self.memory.chat_memory.add_ai_message(message)
    
    def get_chat_history(self) -> BaseChatMessageHistory:
        """Get the chat history"""
        return self.memory.chat_memory
    
    def clear(self):
        """Clear the chat history"""
        self.memory.clear() 