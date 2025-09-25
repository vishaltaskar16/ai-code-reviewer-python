# AI Code Reviewer - Python Edition

A Flask-based web application that provides AI-powered code reviews using OpenAI's GPT models.

## Features

- 🤖 AI-powered code analysis using OpenAI GPT
- 🔒 Security vulnerability detection
- 📊 Code quality assessment
- ⚡ Performance optimization suggestions
- 💾 Review history tracking
- 🔗 GitHub PR integration
- 📱 Responsive Bootstrap UI

## Structure

ai-code-reviewer-python/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database/             # Database models
├── services/             # AI and GitHub services
├── templates/            # HTML templates
├── static/               # CSS/JS assets
└── utils/                # Helper functions

### Prerequisites

- Python 3.8+
- OpenAI API key
- GitHub personal access token (optional)

## ✨ What's This All About?

Tired of spending hours reviewing code? Wish you had an experienced developer looking over your shoulder? Meet **AI Code Reviewer** - your new coding buddy that never sleeps!

We use cutting-edge AI to provide instant feedback on your code, catching issues before they become problems. It's like having a senior developer available 24/7, but without the coffee breaks.


# 1. Grab the code
git clone https://github.com/vishaltaskar16/ai-code-reviewer.git
cd ai-code-reviewer

# 2. Create your coding environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the goodies
pip install -r requirements.txt

# 4. Tell the app your secrets (API keys)
cp .env
# Now edit .env with your favorite text editor