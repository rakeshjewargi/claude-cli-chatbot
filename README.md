# Claude CLI Chatbot

A command-line chatbot built on the [Claude API](https://docs.claude.com/) with a custom
system prompt, demonstrating three core prompt-engineering patterns: **zero-shot**,
**few-shot**, and **chain-of-thought**.

Built as the W01 session deliverable for [upskill.intelliforge.tech](https://upskill.intelliforge.tech).

## Features

- Interactive CLI chat loop with conversation history
- Custom system prompt (a bootcamp-assistant persona named "Nova")
- Three prompt patterns available both as slash commands in chat and as a one-shot demo
- No external dependencies beyond the official `anthropic` Python SDK

## Setup

**Requirements:** Python 3.9+ and an [Anthropic API key](https://console.anthropic.com/settings/keys).

```bash
git clone <this-repo-url>
cd claude-cli-chatbot
pip install -r requirements.txt

# Provide your API key
cp .env.example .env      # then edit .env and paste your key
# or, one-off in your shell:
export ANTHROPIC_API_KEY=your-api-key-here      # macOS/Linux
$env:ANTHROPIC_API_KEY='your-api-key-here'       # Windows PowerShell
```

## Usage

```bash
# Interactive chat mode
python chatbot.py

# Run one example of all three prompt patterns and exit
python chatbot.py demo
```

Inside chat mode:

```
  /zeroshot <question>     zero-shot pattern
  /fewshot <review text>   few-shot pattern (sentiment classification)
  /cot <question>          chain-of-thought pattern
  /demo                    run all three patterns once
  /help                    show this message
  /exit                    quit
```

Anything else you type is treated as a normal chat message and keeps the running
conversation history (multi-turn).

## Custom system prompt

Every request — chat and pattern demos alike — is sent with the same system prompt,
defined once in `chatbot.py`:

```
You are Nova, a friendly and knowledgeable assistant for a coding bootcamp.
You explain concepts clearly, use concrete examples, and keep answers focused
rather than padded. When asked to reason through a problem, show your steps
before giving the final answer.
```

This gives the bot a consistent persona and tone across every pattern, separate
from the per-message prompt that changes shape below.

## The three prompt patterns

### 1. Zero-shot

The model is asked directly, with no examples and no reasoning scaffold — just the
system prompt plus the raw question. This is the baseline: it tests what the model
can do from instructions alone.

**Code** (`run_zero_shot` in `chatbot.py`):

```python
messages = [{"role": "user", "content": question}]
```

**Sample run:**

```
$ python chatbot.py demo

--- ZERO-SHOT
Q: What is the capital of Australia? ---
Claude: The capital of Australia is Canberra. It's often mistaken for Sydney
or Melbourne, but Canberra was purpose-built as the capital in the early 20th
century as a compromise between the two larger, rival cities.
```

### 2. Few-shot

The prompt includes several labeled input → output examples *before* the real
input, so the model can pattern-match the expected format and level of judgment
rather than inferring it from an instruction alone. Here it's used for sentiment
classification of product reviews.

**Code** (`run_few_shot` in `chatbot.py`):

```python
FEW_SHOT_EXAMPLES = """Classify the sentiment of each product review as Positive, Negative, or Neutral.

Review: "This laptop is a total waste of money, it overheats constantly."
Sentiment: Negative

Review: "Decent build quality, does what it says, nothing extraordinary."
Sentiment: Neutral

Review: "Absolutely love this phone! Battery lasts two days and the camera is stunning."
Sentiment: Positive
"""

prompt = f'{FEW_SHOT_EXAMPLES}\nReview: "{review}"\nSentiment:'
```

**Sample run:**

```
--- FEW-SHOT
Input: The screen cracked after one week and support never replied. ---
Claude: Negative
```

Note how the few-shot examples pin the output to a single word in the same
format as the examples, rather than a full sentence — that consistency is the
whole point of the pattern.

### 3. Chain-of-thought

The model is explicitly asked to reason through the problem step by step before
committing to a final answer, which improves accuracy on multi-step problems
(arithmetic, logic, multi-hop questions) compared to asking for the answer directly.

**Code** (`run_chain_of_thought` in `chatbot.py`):

```python
prompt = (
    f"{question}\n\n"
    "Think through this step by step, showing your reasoning, then give "
    "a final answer on its own line prefixed with 'Answer:'."
)
```

**Sample run:**

```
--- CHAIN-OF-THOUGHT
Q: A train leaves Station A at 60 km/h. Two hours later, a second train
leaves the same station on the same track at 90 km/h. How long does it
take the second train to catch up to the first? ---
Claude: Let me work through this step by step.

1. When the second train departs, the first train has already been
   traveling for 2 hours at 60 km/h, so it has a head start of
   2 x 60 = 120 km.
2. The second train needs to close that 120 km gap. It travels at
   90 km/h while the first train continues at 60 km/h, so the gap
   closes at a relative speed of 90 - 60 = 30 km/h.
3. Time to close a 120 km gap at 30 km/h = 120 / 30 = 4 hours.

Answer: The second train catches up to the first 4 hours after it departs.
```

> Sample outputs above are representative example runs generated with this
> project's default system prompt and model. Run `python chatbot.py demo`
> yourself to reproduce them (responses will vary slightly run to run).

## Project structure

```
claude-cli-chatbot/
├── chatbot.py         # CLI entry point + the three prompt-pattern implementations
├── requirements.txt   # anthropic SDK
├── .env.example        # template for your API key
├── .gitignore
└── README.md
```

## Configuration

| Env var             | Purpose                                  | Default          |
| -------------------- | ----------------------------------------- | ---------------- |
| `ANTHROPIC_API_KEY`  | Your Claude API key (required)            | —                 |
| `CLAUDE_MODEL`       | Override the model used for all requests  | `claude-opus-5`   |

## License

MIT — see [LICENSE](LICENSE).
