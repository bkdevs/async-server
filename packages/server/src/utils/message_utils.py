from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage

from src.model.app.task import Message


def has_message(message: AIMessage):
    return isinstance(message.content, str) and message.content


def get_message_chunk_text(event: AIMessageChunk) -> str | None:
    if not event.content:
        return None
    if isinstance(event.content, list):
        if event.content[0]["type"] == "text":
            return event.content[0]["text"]
        else:
            return None
    return event.content


def get_message_text(message: AIMessage) -> str:
    if isinstance(message.content, str):
        return message.content
    elif isinstance(message.content, list):
        return "\n".join([item.get("text", "") for item in message.content])
    else:
        return ""


def firestore_to_langchain(message: Message, user_id: str) -> BaseMessage:
    if message.author == user_id:
        return HumanMessage(content=message.text)
    else:
        return AIMessage(content=message.text)
