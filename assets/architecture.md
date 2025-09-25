# AI Code Reviewer - System Architecture

##  Overview

AI Code Reviewer is a web application that provides automated code reviews using AI. It's built with Python/Flask backend, Bootstrap frontend, and integrates with OpenAI's GPT models for intelligent code analysis.

## front end

 templates/
├── base.html           # Main layout template
├── index.html          # Dashboard page
├── review.html         # Code review interface
├── history.html        # Review history
└── results.html        # Detailed results

 static/
├── css/               # Bootstrap + custom styles
└── js/                # Client-side functionality

## backend

 app.py              # Main Flask application
 services/
├── ai_service.py      # OpenAI integration & code analysis
├── github_service.py  # GitHub API integration
└── security.py        # Security scanning utilities

 database/
├── models.py          # Database models (SQLAlchemy)
└── __init__.py        # Database initialization

 utils/
└── helpers.py         # Utility functions & helpers

## Data Flow

# User submits code through web form
User → Browser → Flask Route → Review Controller → AI Service → OpenAI API

# Response flow
OpenAI API → AI Service → Review Controller → Database → Template → Browser → User

## Database Schema

CodeReview:
- id (Primary Key)
- code_snippet (Text)
- language (String)
- review_types (String)
- results (JSON Text)
- score (Integer)
- created_at (DateTime)

ReviewFinding:
- id (Primary Key)
- review_id (Foreign Key)
- severity (String: CRITICAL, HIGH, MEDIUM, LOW, INFO)
- description (Text)
- suggestion (Text)
- file_path (String)
- line_number (Integer)