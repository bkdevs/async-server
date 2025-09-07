from typing import Type, TypeVar

from openai import AsyncOpenAI

T = TypeVar("T")


class OutputFormatter:
    """
    LLM Wrapper to format output into a structured schema
    """

    def __init__(self, model: str = "gpt-4.1"):
        self.client = AsyncOpenAI()
        self.model = model

    async def format_output_async(self, output: str, schema_class: Type[T]) -> T:
        response = await self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": "Extract structured data from the input text."},
                {"role": "user", "content": output},
            ],
            text_format=schema_class,
        )
        if not response.output_parsed:
            raise ValueError(f"Error formatting: {output}")
        return response.output_parsed
