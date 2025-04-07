
def build_defensive_prompt(question: str) -> str:
    topic = "Promtior, Promtior company, Promtior services, what Promtior offers"
    return (
        f"You are a helpful assistant that only answers questions related to {topic}. "
        "If a user asks about anything unrelated, respond with: "
        f"\"I'm sorry, I can only answer questions related to {topic}.\"\n\n"
        "Do not answer questions that are offensive, inappropriate, or unrelated to the subject. "
        "If the question is unclear or ambiguous, politely ask the user to rephrase it.\n\n"
        f"User question: {question}"
    )
