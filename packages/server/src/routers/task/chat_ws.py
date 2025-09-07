import json
import logging
import traceback

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from langchain_core.messages import AIMessage, AIMessageChunk
from langgraph.checkpoint.memory import InMemorySaver

from src.agent import ChatAgentMetadata
from src.clients import get_firestore_client
from src.model.agent import AsyncConfig
from src.model.app.task import Message, MessageStatus
from src.utils.chat_utils import handle_ai_message_chunk, parse_options_block, trim_options_block
from src.utils.message_utils import get_message_chunk_text, get_message_text
from src.utils.setup_utils import setup_repo_async
from src.utils.task_utils import summarize_requirements

END_OF_MESSAGE = "<end>"

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/chat")
async def chat_async(
    websocket: WebSocket,
    user_id: str,
    org_id: str,
    project_id: str,
    task_id: str,
    is_dev: bool = False,
):
    try:
        await websocket.accept()

        firestore_client = get_firestore_client()
        org = await firestore_client.get_org_async(org_id)
        project = await firestore_client.get_project_async(org_id, project_id)
        repo_directory = await setup_repo_async(org, project)

        checkpointer = InMemorySaver()
        config = AsyncConfig(
            thread_id=task_id,
            repo_directory=repo_directory,
            org=org,
            project=project,
            task_id=task_id,
            user_id=user_id,
            is_dev=is_dev,
        )

        while True:
            try:
                user_message = await websocket.receive_text()
                config["user_message"] = user_message
                await _run_agent_async(websocket, config, checkpointer)
                await _send_text_async(websocket)
            except WebSocketDisconnect as e:
                raise e
            except RuntimeError as e:
                logger.error(f"Encountered error: {e}")
                break
            except Exception:
                traceback.print_exc()
                await _send_text_async(websocket)
    except WebSocketDisconnect as e:
        logger.debug(f"WebSocket disconnected: {e.code}")


async def _send_text_async(websocket: WebSocket, message: str = END_OF_MESSAGE):
    try:
        if websocket and websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)
    except Exception:
        # ignore and let execution finishes
        pass


async def _run_agent_async(websocket: WebSocket, config: AsyncConfig, checkpointer: InMemorySaver):
    agent_metadata = ChatAgentMetadata(config)
    agent = agent_metadata.create_agent(checkpointer)

    parent_message = await _create_streaming_message_async(
        org_id=config["org"].id,
        task_id=config["task_id"],
        author=agent.name,
        title=agent_metadata.get_default_title(),
    )

    partial_match = ""
    options_block = None

    firestore_client = get_firestore_client()

    try:
        async for mode, event in agent.astream(
            input={"messages": agent_metadata.get_input_message()},
            config={"configurable": config, "recursion_limit": 200},
            stream_mode=["messages", "updates", "custom"],
        ):
            if mode == "messages" and isinstance(event[0], AIMessageChunk):
                content = get_message_chunk_text(event[0])
                if not content:
                    continue

                chunk, partial_match, options_block = handle_ai_message_chunk(content, partial_match, options_block)
                if chunk:
                    await _send_text_async(websocket, chunk)
            elif mode == "updates" and "agent" in event:
                for message in event["agent"]["messages"]:
                    if not isinstance(message, AIMessage):
                        continue
                    parent_message.text = trim_options_block(get_message_text(message))
            elif mode == "custom":
                tool_message = f"<tool_call>{event.model_dump_json(exclude={'created_at'})}</tool_call>"
                await _send_text_async(websocket, tool_message)

        message_actions = parse_options_block(options_block)
        if message_actions:
            if any(message_action["label"] == "Execute" for message_action in message_actions):
                config["task_requirements"] = summarize_requirements(parent_message.text)
            await _send_text_async(websocket, f"<actions>{json.dumps(message_actions)}</actions>")

        await firestore_client.update_message_async(
            config["org"].id,
            config["task_id"],
            message_id=parent_message.id,
            status=MessageStatus.COMPLETED,
            text=parent_message.text,
            is_streaming=False,
            actions=message_actions,
        )
    except Exception:
        await firestore_client.update_message_async(
            config["org"].id,
            config["task_id"],
            message_id=parent_message.id,
            status=MessageStatus.FAILED,
            is_streaming=False,
        )
        raise


async def _create_streaming_message_async(org_id: str, task_id: str, author: str, title: str) -> Message:
    message = Message(
        author=author,
        title=title,
        text="",
        status=MessageStatus.IN_PROGRESS,
        is_streaming=True,
    )
    return await get_firestore_client().create_message_async(org_id, task_id, message)
