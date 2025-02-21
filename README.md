# Agentic Life

Agentic Life is an AI-powered tool that scans your life (emails, documents, texts) from the past 12 hours, extracts actionable to-do items, and sends you an aggregated summary email. Built to run as a GitHub Action, it's designed to be extended into a full-fledged automation platform.

## Features

- **Automated Email Processing:** Fetches recent emails from Gmail.
- **AI-Powered Task Extraction:** Uses OpenRouter API to generate to-do lists.
- **Aggregated Reporting:** Sends one summary email with all actionable items.
- **GitHub Actions Deployment:** Scheduled, secure, and automated runs.
- **Extensible:** Easily expanded to support complete email automation workflows.

## Prerequisites

- **Gmail API Credentials:** Follow [Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python) to get your `credentials.json`.
- **OAuth Token:** Generate `token.pickle` (then base64‑encode it).
- **OpenRouter API Key:** Sign up at [OpenRouter](https://openrouter.ai/) for your API key.
- **Python 3.x**

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gmail-todo-bot.git
cd gmail-todo-bot
```
2. Configure GitHub Secrets
Even with a public repository, your sensitive data remains secure via GitHub Secrets. In your repository settings under Settings > Secrets and variables > Actions, add:

- GMAIL_CREDENTIALS: Paste the entire content of your credentials.json.
- GMAIL_TOKEN: Paste the base64‑encoded content of your token.pickle.
- OPENROUTER_API_KEY: Your OpenRouter API key.
- (Optional) YOUR_SITE_URL and YOUR_SITE_NAME for OpenRouter API headers.
- 
3. GitHub Actions Workflow
The workflow file at .github/workflows/email_bot.yml is set to run every 12 hours. It:

- Checks out the code.
- Sets up Python and installs dependencies.
- Writes credentials.json and token.pickle from secrets.
- Executes the email bot script.
4. Running Locally
  
If you prefer to test locally, place your credentials.json and token.pickle in the project root, install dependencies, and run:

bash
```
pip install -r requirements.txt
python email_bot.py
```

###Future Extensions
This project lays the groundwork for a complete email automation tool. Future enhancements could include:
