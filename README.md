# Zulip AI Features Assignment

FYI, I did the project on the homeworkBranch. So navigate accordingly.

This homework extends the Zulip development server with two LLM=powered features:

1. **Message Recap** - Generates a concise summary of the user's unread messages and provides links to the original messages.
2. **Topic Title Improver** - Detects when a Zulip topic has drifted from its current title and suggests a new title associated with the drifted conversation.

The LLM functionality uses the Groq API through its OpenAI-compatible API.

## Requirements

- Git
- Vagrant
- Docker Desktop
- A Groq API key

## 1. Clone the Repository

Clone the repository and enter the project directory:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
cd zulip
```

```bash
git checkout homeworkBranch
```

# 2. Start the Vagrant Environment

Start and provision the Zulip development environment:
```bash
vagrant up
```

Connect to development environment:

```bash
vagrant ssh
```

Move to the Zulip repository:

```bash
cd /Users/sai/zulip
```
## 3. Configure the Groq API Key

A Groq API key can be obtained from the Groq developer console.

Do not commit this API key to Git. `zproject/dev-secrets.conf` is ignored by the repository and is intended for local development secrets.

The development configuration uses the Groq OpenAI-compatible API and the configured topic summarization model.

## 4. Run Zulip

Inside the Vagrant environment, run:

```bash
./tools/run-dev
```

After the development server starts, open:

```text
http://localhost:9991/
```
in a web browser.

## 5. Using the Features

## Message Recap

Log in to Zulip and leave some messages unread. Select Message Recap from the left navigation.

The page will:

- rerieve the user's unread messages,
- generate an AI recap,
- display the number of unread messages, and
- provide clickable references to the original Zulip messages.

## Topic Title Improver

Post messages to a channel topic normally. After a stream message is successfully posted, the Topic Title Improver analyzes the recent conversation. If topic drift is detected, a dialog appears with a suggested title.

## Dependencies

No additional dependencies



