#!/usr/bin/env python3
"""CLI chatbot using OpenRouter (nvidia/nemotron-3-ultra-550b-a55b:free) with
a custom system prompt.

Demonstrates three prompt-engineering patterns:
  - Zero-shot        : ask directly, no examples, no reasoning scaffold
  - Few-shot         : give labeled examples before the real input
  - Chain-of-thought : ask the model to reason step by step before answering

Usage:
    python chatbot.py            # interactive chat mode
    python chatbot.py demo       # run one example of each pattern and exit
"""

from __future__ import annotations

import argparse
import os
import sys

from openai import OpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
MAX_TOKENS = 1024

SYSTEM_PROMPT = (
    "You are Nova, a friendly and knowledgeable assistant for a coding "
    "bootcamp. You explain concepts clearly, use concrete examples, and "
    "keep answers focused rather than padded. When asked to reason through "
    "a problem, show your steps before giving the final answer."
)

# Few-shot examples: a small labeled set the model can pattern-match against
# before it sees the real input. This is what makes it "few-shot" rather
# than a plain instruction.
FEW_SHOT_EXAMPLES = """Classify the sentiment of each product review as Positive, Negative, or Neutral.

Review: "This laptop is a total waste of money, it overheats constantly."
Sentiment: Negative

Review: "Decent build quality, does what it says, nothing extraordinary."
Sentiment: Neutral

Review: "Absolutely love this phone! Battery lasts two days and the camera is stunning."
Sentiment: Positive
"""


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY is not set.")
        print("Copy .env.example to .env, add your key, then run:")
        print("  export OPENROUTER_API_KEY=your-key-here   (macOS/Linux)")
        print("  $env:OPENROUTER_API_KEY='your-key-here'   (PowerShell)")
        print("Get a free key at https://openrouter.ai/keys")
        sys.exit(1)
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def ask(client: OpenAI, messages: list, label: str | None = None) -> str:
    """Send messages (with the system prompt prepended) and print the reply."""
    if label:
        print(f"\n--- {label} ---")
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
        extra_headers={
            "HTTP-Referer": "https://github.com/rakeshjewargi/claude-cli-chatbot",
            "X-Title": "CLI Chatbot Prompt Patterns Demo",
        },
    )
    text = response.choices[0].message.content
    print(f"Assistant: {text}\n")
    return text


def run_zero_shot(client: OpenAI, question: str) -> str:
    messages = [{"role": "user", "content": question}]
    return ask(client, messages, label=f"ZERO-SHOT\nQ: {question}")


def run_few_shot(client: OpenAI, review: str) -> str:
    prompt = f'{FEW_SHOT_EXAMPLES}\nReview: "{review}"\nSentiment:'
    messages = [{"role": "user", "content": prompt}]
    return ask(client, messages, label=f"FEW-SHOT\nInput: {review}")


def run_chain_of_thought(client: OpenAI, question: str) -> str:
    prompt = (
        f"{question}\n\n"
        "Think through this step by step, showing your reasoning, then give "
        "a final answer on its own line prefixed with 'Answer:'."
    )
    messages = [{"role": "user", "content": prompt}]
    return ask(client, messages, label=f"CHAIN-OF-THOUGHT\nQ: {question}")


def run_demo(client: OpenAI) -> None:
    """Run one canned example of each pattern back to back."""
    run_zero_shot(client, "What is the capital of Australia?")
    run_few_shot(client, "The screen cracked after one week and support never replied.")
    run_chain_of_thought(
        client,
        "A train leaves Station A at 60 km/h. Two hours later, a second train "
        "leaves the same station on the same track at 90 km/h. How long does "
        "it take the second train to catch up to the first?",
    )


HELP_TEXT = (
    "  /zeroshot <question>     zero-shot pattern\n"
    "  /fewshot <review text>   few-shot pattern (sentiment classification)\n"
    "  /cot <question>          chain-of-thought pattern\n"
    "  /demo                    run all three patterns once\n"
    "  /help                    show this message\n"
    "  /exit                    quit\n"
)


def chat_loop(client: OpenAI) -> None:
    print(f"CLI Chatbot (model: {MODEL})")
    print("Type a message to chat normally, or use a pattern command:")
    print(HELP_TEXT)

    history: list = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            print("Goodbye!")
            break
        if user_input == "/help":
            print(HELP_TEXT)
            continue
        if user_input == "/demo":
            run_demo(client)
            continue
        if user_input.startswith("/zeroshot "):
            run_zero_shot(client, user_input[len("/zeroshot "):].strip())
            continue
        if user_input.startswith("/fewshot "):
            run_few_shot(client, user_input[len("/fewshot "):].strip())
            continue
        if user_input.startswith("/cot "):
            run_chain_of_thought(client, user_input[len("/cot "):].strip())
            continue

        # Plain chat turn — keeps running conversation history.
        history.append({"role": "user", "content": user_input})
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, *history],
            extra_headers={
                "HTTP-Referer": "https://github.com/rakeshjewargi/claude-cli-chatbot",
                "X-Title": "CLI Chatbot Prompt Patterns Demo",
            },
        )
        text = response.choices[0].message.content
        print(f"Assistant: {text}\n")
        history.append({"role": "assistant", "content": text})


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI chatbot using OpenRouter")
    parser.add_argument(
        "mode",
        nargs="?",
        default="chat",
        choices=["chat", "demo"],
        help="'chat' for interactive mode (default), 'demo' to run all three "
        "prompt patterns once and exit",
    )
    args = parser.parse_args()

    client = get_client()

    if args.mode == "demo":
        run_demo(client)
    else:
        chat_loop(client)


if __name__ == "__main__":
    main()
