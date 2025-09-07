from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    label: str = Field(description="A 60 characters or less potential answer to the question")
    requirement: str = Field(description="A one sentence requirement that the answer implies")


class ClarifyingQuestion(BaseModel):
    question: str = Field(description="Clarifying question text")
    reasoning: str = Field(description="1-2 sentences reasoning behind why question cannot be answered from code")
    options: list[QuestionOption] = Field(description="List of potential answers to the question")


class TaskResearchOutput(BaseModel):
    clarifying_questions: list[ClarifyingQuestion] = Field(
        description="List of questions needed to clarify ambiguity in task"
    )

    def format_questions(self) -> str:
        if not self.clarifying_questions:
            return ""
        prefix = "Have a question:" if len(self.clarifying_questions) == 1 else "Have a few questions:"
        return f"{prefix}\n\n" + "\n".join([f"- {q.question}" for q in self.clarifying_questions])
