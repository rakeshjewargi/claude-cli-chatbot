# CLI Chatbot — Prompt Patterns Demo

A command-line chatbot with a custom system prompt, demonstrating three core
prompt-engineering patterns: **zero-shot**, **few-shot**, and **chain-of-thought**.

Built for the W01 session deliverable for [upskill.intelliforge.tech](https://upskill.intelliforge.tech).

> **⚠️ Note on the assignment brief:** the original brief for this deliverable calls
> for the **Claude API** specifically ("Claude API integrated with a system prompt").
> This version runs on **OpenRouter** against the free `nvidia/nemotron-3-ultra-550b-a55b:free`
> model instead, to avoid needing paid Claude API credits. The prompt-pattern logic
> (system prompt, zero-shot, few-shot, chain-of-thought) is identical either way —
> only the API client and model differ — but as written, this repo does **not**
> satisfy the "Claude API" success criterion. See [Using Claude instead](#using-claude-instead)
> below to switch back if the assignment requires it.

## Features

- Interactive CLI chat loop with conversation history
- Custom system prompt (a bootcamp-assistant persona named "Nova")
- Three prompt patterns available both as slash commands in chat and as a one-shot demo
- Runs on OpenRouter's free tier — no paid API credits required

## Setup

**Requirements:** Python 3.9+ and a free [OpenRouter API key](https://openrouter.ai/keys).

```bash
git clone <this-repo-url>
cd claude-cli-chatbot
pip install -r requirements.txt

# Provide your API key
cp .env.example .env      # then edit .env and paste your key
# or, one-off in your shell:
export OPENROUTER_API_KEY=your-api-key-here      # macOS/Linux
$env:OPENROUTER_API_KEY='your-api-key-here'       # Windows PowerShell
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
Assistant: Canberra is the capital of Australia.
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
Assistant: Negative
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
Assistant: The first train has a 2-hour head start, traveling at 60 km/h, so it is 120 km ahead when the second train starts.

Let t be the time (in hours) after the second train starts until it catches up.

Distance traveled by second train: 90t km.
Distance traveled by first train during that same time: 60t km, plus its 120 km head start: 120 + 60t km.

Set the distances equal:
90t = 120 + 60t
30t = 120
t = 4

Answer: 4 hours
```

> Sample outputs above are captured from a real run of `python chatbot.py demo`
> against `nvidia/nemotron-3-ultra-550b-a55b:free`. Exact wording will vary
> between runs.

## Using Claude instead

If you need this to run on the Claude API to satisfy an assignment requirement,
the change is small since the prompt-pattern functions don't change:

1. `pip install anthropic` (instead of `openai`)
2. Replace the client with `anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])`
3. Replace `client.chat.completions.create(model=..., messages=[{"role": "system", ...}, ...])`
   with `client.messages.create(model=..., system=SYSTEM_PROMPT, messages=[...])`
   (Claude takes the system prompt as a separate top-level parameter, not a
   message in the array) and read the reply from `response.content[0].text`
   instead of `response.choices[0].message.content`
4. Default model: `claude-opus-5` (or `claude-haiku-4-5` for a cheaper option)
5. Requires a funded Anthropic account — see [console.anthropic.com/settings/billing](https://console.anthropic.com/settings/billing)

## Project structure

```
claude-cli-chatbot/
├── chatbot.py         # CLI entry point + the three prompt-pattern implementations
├── requirements.txt   # openai SDK (used against OpenRouter's API)
├── .env.example        # template for your API key
├── .gitignore
└── README.md
```

## Configuration

| Env var             | Purpose                                  | Default                                     |
| -------------------- | ----------------------------------------- | -------------------------------------------- |
| `OPENROUTER_API_KEY` | Your OpenRouter API key (required)        | —                                             |
| `OPENROUTER_MODEL`   | Override the model used for all requests  | `nvidia/nemotron-3-ultra-550b-a55b:free`      |

## License

MIT — see [LICENSE](LICENSE).
