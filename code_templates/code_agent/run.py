import json
from typing import Any

from langchain_core.messages import HumanMessage, ToolMessage
from sasram.agent import Client


def get_b64_images(messages) -> str:
    images = []

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        try:
            outer_payload = json.loads(message.content)
        except (json.JSONDecodeError, TypeError):
            continue

        content_blocks = outer_payload.get("content", [])

        for block in content_blocks:
            if not isinstance(block, dict):
                continue

            if block.get("type")!= "text":
                continue

            inner_text = block.get("text")

            if not isinstance(inner_text, str):
                continue

            try:
                chart_payload = json.loads(inner_text)
            except json.JSONDecodeError:
                continue

            image_base64 = chart_payload.get("image_base64")
            mime_type = chart_payload.get("mime_type", "image/png")

            if image_base64:
                images.append(
                    f"![graph](data:{mime_type};base64,{image_base64})"
                )

    return "\n\n".join(images)


async def exec(
    text: str,
    ram_client: Client,
    options: dict[str, Any],
):
    agent = ram_client.get_langgraph_agent()

    session_history = ram_client.get_session_history_as_langchain()
    messages = session_history + [HumanMessage(content=text)]

    response = await agent.ainvoke(
        {"messages": messages},
        config=options or None,
    )

    response_messages = response["messages"]

    images = get_b64_images(response_messages)

    final_answer = response_messages[-1].content

    if images:
        return f"{images}\n\n{final_answer}"

    return final_answer