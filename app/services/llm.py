import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=120,
    )

    return response.choices[0].message.content.strip()


def generate_reply(review_text: str, similar_reviews: list[str]):
    examples = "\n".join([f"- {t}" for t in similar_reviews])

    prompt = f"""
You are a professional customer support agent.

Customer review:
"{review_text}"

Similar past reviews:
{examples}

Write a polite, empathetic, short reply (max 3 sentences).
Only output the reply text.
"""

    return call_llm(prompt)
