import re
from typing import List, Optional

from src.model.app.task import Message, MessageAction

OPTION_PATTERN = re.compile(r"<option>(.*?)</option>", re.DOTALL)
EXECUTE_STRINGS = ["Execute", "Invoke", "Run", "Start", "Begin"]


def handle_ai_message_chunk(chunk: str, partial_match: str, options_block: Optional[str]) -> tuple[str, str, str]:
    """
    Logic here holds onto a chunk (stores it in partial_match) if it potentially a partial match with "<options>"

    If we do end up seeing a successful "<options>" match, we move onto appending all text into the options_block
    If we do not, we flush what we held in the partial_match and move back to flushing chunks to the user
    """

    if options_block is not None:
        # we treat <options> as a separator now, we don't parse </options>
        return None, None, options_block + chunk
    elif "<options>" in chunk:
        # for certain models (gemini), streaming chunks contain the whole <options> tag
        idx = chunk.find("<options>")
        return chunk[:idx], None, chunk[idx:]
    elif partial_match:
        next_match = continue_partial_match(partial_match, chunk, "<options>")
        if partial_match + next_match == "<options>":
            # we fully matched, save what's after options
            return None, None, "<options>" + chunk[len(next_match) :]
        elif next_match == chunk:
            # we fully matched, but not enough for "<options>", don't flush but keep partial
            return None, partial_match + next_match, None
        else:  # flush partial match
            return partial_match + chunk, None, None
    elif partial_match := ends_in_partial_match(chunk, "<options>"):
        # potential partial match, exclude from this chunk and save it
        return chunk[: -len(partial_match)], partial_match, None
    else:
        # no partial match, flush
        return chunk, "", None


def ends_in_partial_match(s: str, target: str) -> Optional[str]:
    """
    If there is a partial match of target at the end of the string, return the prefix

    examples:
        ends_in_partial_match("Hello <options>", "<options>") -> "<options>"
        ends_in_partial_match("Hello <option>", "<options>") -> None
        ends_in_partial_match("Hello <", "<options>") -> "<"
        ends_in_partial_match("Hello <options>asdf", "<options>") -> None
    """

    for i in range(len(target), 0, -1):
        prefix = target[:i]
        if s.endswith(prefix):
            return prefix
    return ""


def continue_partial_match(partial_match: str, s: str, target: str) -> Optional[str]:
    """
    Returns the shortest prefix of `string` such that
    partial_match + prefix == target.

    If no such prefix exists, return None.

    Examples:
        continue_partial_match("<", "options> asdf", "<options>") -> "options>"
        continue_partial_match("<opt", "ions>foo", "<options>") -> "ions>"
        continue_partial_match("<opt", "ics>", "<options>") -> None
    """

    if not target.startswith(partial_match):
        return None

    for i in range(1, len(s) + 1):
        combined = partial_match + s[:i]
        if not target.startswith(combined):
            return s[: i - 1] if i > 1 else ""
    return s


def parse_options_block(options_block: str) -> list[dict]:
    """
    Parse the options block into a list of options, e.g.,

    <options>
        <option>Option 1</option>
        <option>Option 2</option>
        <option>Option 3</option>
    </options>
    """
    if not options_block:
        return []

    options_block = options_block.strip()

    if not options_block.startswith("<options>") or not options_block.endswith("</options>"):
        print(f"Invalid options block: {options_block}")
        return []

    content = options_block[len("<options>") : options_block.rfind("</options>")].strip()
    matches = OPTION_PATTERN.findall(content)
    actions = [MessageAction(label=match.strip()) for match in matches]
    return [action.model_dump() for action in actions]


def trim_options_block(message: str) -> str:
    """
    Removes any content within "<options>" and "</options>" tags, including the tags themselves.
    """
    if "<options>" in message and "</options>" in message:
        start_idx = message.find("<options>")
        end_idx = message.find("</options>") + len("</options>")
        message = message[:start_idx] + message[end_idx:]
    return message.strip()


def get_options_block(message: str) -> str:
    """
    Returns the content within "<options>" and "</options>" tags, including the tags themselves.
    """
    if "<options>" in message and "</options>" in message:
        start_idx = message.find("<options>")
        end_idx = message.find("</options>") + len("</options>")
        return message[start_idx:end_idx]
    return ""


def format_messages(messages: List[Message], user_id: str, user_name: str = "user", agent_name: str = "agent") -> str:
    formatted_messages = []
    for message in messages:
        if message.author == user_id:
            formatted_messages.append(f"{user_name}: {message.text}")
        else:
            formatted_messages.append(f"{agent_name}: {message.text}")
    return "\n".join(formatted_messages)
