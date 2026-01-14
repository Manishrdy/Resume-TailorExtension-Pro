# Resume Tailor - AI-Powered Resume Optimization Platform

> Transform your resume for every job application with AI-powered tailoring, ATS scoring, and professional PDF generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0.9-green.svg)](https://www.reportlab.com/)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-blue?logo=google)](https://ai.google.dev/)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

**Resume Tailor** is a comprehensive AI-powered platform designed to help job seekers optimize their resumes for specific job applications. The system uses Google's Gemini AI to intelligently tailor resume content, provides ATS (Applicant Tracking System) compatibility scoring, and generates professional PDF resumes.

### What Makes Resume Tailor Unique?

- **AI-Powered Optimization**: Leverages Google Gemini 2.5 Flash for intelligent resume tailoring
- **ATS Scoring**: Provides 0-100 compatibility scores with actionable insights
- **Professional Document Generation**: Creates ATS-friendly PDFs and DOCX files using self-contained Python module
- **Multi-Format Support**: Export resumes in both PDF and DOCX formats
- **Multi-Platform**: Chrome extension, REST API, and standalone web interface
- **Privacy-First**: All data stored locally, no external tracking
- **Production-Ready**: Docker support, comprehensive testing, and monitoring
- **Zero External Dependencies**: No external services required for document generation

### System Components

1. **FastAPI Backend** - REST API serving AI tailoring and document generation
2. **Chrome Extension** - Browser-based UI with job scraping capabilities
3. **Document Generator** - Self-contained Python module for PDF/DOCX generation (ReportLab + python-docx)
4. **Gemini AI Integration** - Intelligent resume optimization engine

---

## Features

### Core Capabilities

#### AI Resume Tailoring
- Intelligent keyword extraction and matching
- Bullet point optimization for job relevance
- Professional summary rewriting
- Skills gap analysis
- ATS compatibility scoring (0-100)
- Actionable improvement suggestions

#### Document Generation
- **PDF Generation**: ATS-friendly PDFs using ReportLab
- **DOCX Generation**: Editable Word documents using python-docx
- Clean, professional single-column layout
- Standard fonts optimized for ATS parsing
- Preserves all factual information (dates, company names)
- Intelligent skill categorization
- Proper spacing and formatting for readability
- Self-contained - no external services required

#### Chrome Extension
- Form-based resume builder
- Multiple resume profile management
- Automated job description scraping (5+ job sites)
- Real-time ATS scoring
- One-click PDF download
- Local history management
- Dark/light theme support
- Import/export functionality

#### Job Site Support
- LinkedIn
- Indeed
- Greenhouse
- Glassdoor
- Ashby
- Manual input for unsupported sites

---

## Architecture

### High-Level System Design

```
┌─────────────────────┐
│  Chrome Extension   │
│  (User Interface)   │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│   FastAPI Backend   │
│  (Orchestration)    │
├─────────────────────┤
│  • Health Checks    │
│  • CORS Handling    │
│  • Logging          │
│  • Validation       │
└──────┬──────┬───────┘
       │      │
       │      └─────────────────┐
       │                        │
       ▼                        ▼
┌──────────────┐      ┌────────────────┐
│  Gemini AI   │      │ Open Resume    │
│  Service     │      │ PDF Service    │
│              │      │                │
│ • Tailoring  │      │ • Rendering    │
│ • Scoring    │      │ • Templates    │
│ • Keywords   │      │ • Fonts        │
└──────────────┘      └────────────────┘
```

### Technology Stack

#### Backend
- **Framework**: FastAPI 0.109.0
- **Server**: Uvicorn (ASGI)
- **AI Engine**: Google Gemini 2.0 Flash
- **HTTP Client**: httpx (async)
- **Data Validation**: Pydantic 2.5.3
- **Logging**: Loguru
- **Testing**: pytest, pytest-asyncio, pytest-cov

#### Frontend (Extension)
- **Language**: Vanilla JavaScript (ES6+)
- **UI**: HTML5/CSS3
- **Storage**: Chrome Storage API
- **Content Scripts**: DOM parsing and job scraping

#### PDF Service
- **Framework**: Next.js 13.5.11
- **Language**: TypeScript 5.0.4
- **PDF Rendering**: React-PDF, jsPDF
- **State Management**: Redux Toolkit
- **Styling**: Tailwind CSS 3.3.2

#### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Multi-container setup with health checks
- **Logging**: Centralized file-based logging with rotation
- **Monitoring**: Health check endpoints with service status

---

## Quick Start

### Prerequisites

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Google Gemini API Key** - [Get API Key](https://ai.google.dev/)
- **Chrome Browser** - [Download Chrome](https://www.google.com/chrome/)
- **Git** - [Download Git](https://git-scm.com/)

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone https://github.com/Manishrdy/resume_tailoring_extension.git
cd resume_tailoring_extension

# 2. Start with Docker (Recommended)
docker-compose up -d

# 3. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 4. Load Chrome Extension
# Open chrome://extensions
# Enable "Developer mode"
# Click "Load unpacked" and select the extension/ folder

# 5. Verify installation
curl http://localhost:8000/api/health
```

---

## Installation

### Option 1: Docker (Recommended)

#### Production Setup

```bash
# Clone repository
git clone https://github.com/Manishrdy/resume_tailoring_extension.git
cd resume_tailoring_extension

# Create environment file
cp backend/.env.example backend/.env

# Edit .env and configure:
# - GEMINI_API_KEY=your_actual_key_here
# - OPEN_RESUME_URL=http://localhost:3000
nano backend/.env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8000/api/health
```

#### Development Setup

```bash
# Use development compose file (enables hot-reload)
docker-compose -f docker-compose.dev.yml up -d

# Backend will reload on code changes
# Frontend will hot-reload automatically
```

### Option 2: Manual Setup

#### Backend Installation

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run backend
cd src
uvicorn app.main:app --reload --port 8000
```

#### Chrome Extension Installation

```bash
cd extension

# If using a build step (optional)
npm install
npm run build

# Load in Chrome
# 1. Open chrome://extensions
# 2. Enable "Developer mode" (top right toggle)
# 3. Click "Load unpacked"
# 4. Select the extension/ folder (or extension/dist if built)
# 5. Pin the extension to your toolbar
```

---

## Configuration

### Backend Configuration

Create `backend/.env` file:

```ini
# Environment
ENVIRONMENT=development

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_URL=http://localhost:8000

# CORS Settings
CORS_ORIGINS=chrome-extension://*,http://localhost:5173,http://localhost:3000

# Open Resume Service
OPEN_RESUME_URL=http://localhost:3000
OPEN_RESUME_API_TIMEOUT=30
OPEN_RESUME_FONT_FAMILY=Open Sans
OPEN_RESUME_FONT_SIZE=11

# Google Gemini AI
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=8192
GEMINI_TIMEOUT=30
GEMINI_RETRY_ATTEMPTS=3

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=console

# Request Settings
REQUEST_TIMEOUT=60
MAX_RESUME_SIZE=5242880  # 5MB
```

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | - | Yes |
| `API_PORT` | Backend API port | 8000 | No |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO | No |
| `GEMINI_MODEL` | Gemini model version | gemini-2.5-flash-exp | No |
| `GEMINI_TEMPERATURE` | AI creativity level (0.0-1.0) | 0.7 | No |

**Note**: `OPEN_RESUME_URL` is no longer required. Document generation now uses a self-contained Python module.

### Extension Configuration

Configure the extension via the Settings panel:

- **API URL**: Backend API endpoint (default: http://localhost:8000)
- **Auto-save**: Enable automatic saving of resume changes
- **Theme**: Choose dark or light mode
- **History Location**: Local directory for PDF storage

---

## Usage Guide

### Creating Your First Resume

1. **Click the Extension Icon**
   - Open any webpage
   - Click the Resume Tailor icon in your Chrome toolbar

2. **Create a New Profile**
   - Click "New Resume" or "Add Profile"
   - Fill in the resume form:
     - Personal information (name, email, phone)
     - Professional summary
     - Work experience (company, role, dates, achievements)
     - Education
     - Skills
     - Projects (optional)
   - Click "Save Profile"

3. **Name Your Profile**
   - Give it a descriptive name (e.g., "Software Engineer - Backend")
   - This helps when managing multiple resumes

### Tailoring for a Job

1. **Navigate to a Job Posting**
   - Visit LinkedIn, Indeed, Greenhouse, Glassdoor, or Ashby
   - Open the specific job listing you want to apply for

2. **Scrape the Job Description**
   - Click the extension icon
   - Select the resume profile to use
   - Click "Scrape Job Description"
   - Review the extracted text (edit if needed)

3. **Tailor Your Resume**
   - Click "Tailor Resume"
   - Wait 10-15 seconds for AI processing
   - View results:
     - **ATS Score**: 0-100 compatibility rating
     - **Matched Keywords**: Keywords found in your resume
     - **Missing Keywords**: Important keywords to add
     - **Suggestions**: Specific improvements to make

4. **Review Changes**
   - See side-by-side comparison of original vs. tailored
   - Tailored content optimized for the job description
   - All factual information preserved

### Generating PDFs

1. **After Tailoring**
   - Review the tailored resume content
   - Click "Download PDF"
   - PDF generates in 2-5 seconds

2. **PDF Features**
   - ATS-friendly formatting
   - Professional design
   - Proper spacing and margins
   - Standard fonts (Open Sans, Roboto, Lato)
   - A4/Letter size support

3. **File Location**
   - PDFs saved to your Downloads folder
   - Named with timestamp and job info
   - Example: `resume_tailored_2026-01-09_Software_Engineer.pdf`

### Managing Resume History

1. **View History**
   - Click "History" tab in extension
   - See all previously tailored resumes
   - Sorted by date (newest first)

2. **Access Past Resumes**
   - Click on any entry to open the PDF
   - Review ATS scores and keywords
   - Re-download if needed

3. **Delete Old Entries**
   - Click "Delete" on unwanted entries
   - Removes from history (PDF file remains in Downloads)

### Managing Multiple Profiles

1. **Create Multiple Resumes**
   - Build different profiles for different job types
   - Examples:
     - "Backend Engineer - Python"
     - "Full Stack Developer - React"
     - "Data Scientist - ML"

2. **Switch Between Profiles**
   - Use the profile dropdown in the extension
   - Current profile is highlighted
   - Changes are auto-saved

3. **Export/Import**
   - Export profiles as JSON backup
   - Import to restore or transfer to another computer
   - Settings → Export/Import

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Endpoints

#### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "fastapi": "running",
    "gemini": "available",
    "open_resume": "available"
  },
  "timestamp": "2026-01-09T10:30:00Z"
}
```

#### Tailor Resume

```http
POST /api/tailor
Content-Type: application/json
```

**Request Body:**
```json
{
  "resume": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-234-567-8900",
    "summary": "Software engineer with 5 years of experience...",
    "experience": [
      {
        "company": "Tech Corp",
        "position": "Senior Developer",
        "startDate": "2020-01",
        "endDate": "2025-01",
        "bullets": [
          "Built scalable microservices using Python and FastAPI",
          "Improved system performance by 40%"
        ]
      }
    ],
    "education": [...],
    "skills": ["Python", "FastAPI", "Docker", "AWS"]
  },
  "jobDescription": "We're looking for a Senior Backend Engineer with Python expertise..."
}
```

**Response:**
```json
{
  "tailored_resume": { /* Optimized resume object */ },
  "ats_score": 87,
  "matched_keywords": ["Python", "FastAPI", "Microservices", "AWS"],
  "missing_keywords": ["Kubernetes", "CI/CD"],
  "suggestions": [
    "Add specific metrics to quantify achievements",
    "Highlight experience with Kubernetes if applicable",
    "Include CI/CD pipeline experience"
  ]
}
```

#### Generate PDF

```http
POST /api/generate-pdf
Content-Type: application/json
```

**Request Body:**
```json
{
  "resume": { /* Resume object */ },
  "settings": {
    "fontFamily": "Open Sans",
    "fontSize": 11,
    "documentSize": "A4",
    "themeColor": "#2563eb"
  }
}
```

**Response:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="resume.pdf"

[PDF Binary Data]
```

### Interactive API Documentation

When running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Development

### Running in Development Mode

#### Backend with Hot Reload

```bash
cd backend/src
uvicorn app.main:app --reload --port 8000 --log-level debug
```

#### Open Resume with Hot Reload

```bash
cd open-resume-service
npm run dev
```

#### Extension Development

```bash
cd extension

# Make changes to source files
# Reload extension in chrome://extensions

# If using a build step
npm run dev  # Starts watch mode
```

### Code Quality

#### Python (Backend)

```bash
cd backend

# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/

# Run all checks
black src/ && flake8 src/ && mypy src/ && pytest
```

#### TypeScript (Open Resume)

```bash
cd open-resume-service

# Lint
npm run lint

# Type check
npm run type-check

# Format
npm run format
```

### Adding New Features

#### Adding a New API Endpoint

1. Create route in `backend/src/app/api/`
2. Define Pydantic models in `backend/src/models/`
3. Implement service logic in `backend/src/services/`
4. Add tests in `backend/tests/`
5. Update API documentation

#### Adding a New Job Site Scraper

1. Identify site's HTML structure
2. Create scraper in `extension/content/scraper.js`
3. Add site detection logic
4. Test on live job postings
5. Handle edge cases (missing fields, dynamic content)

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test file
pytest tests/test_tailor.py

# Run with verbose output
pytest -v

# Run with debug output
pytest -s
```

### Test Coverage

Current coverage: **90%+**

Test files:
- `test_health.py` - Health check endpoints
- `test_tailor.py` - AI tailoring logic
- `test_pdf.py` - PDF generation
- `test_models.py` - Pydantic model validation
- `test_pdf_transformations.py` - Data transformation (23 tests)
- `test_pdf_client_settings.py` - Settings validation

### Integration Testing

```bash
# 1. Start all services
docker-compose up -d

# 2. Run integration tests
cd backend
pytest tests/integration/

# 3. Test complete flow
# - Create test resume
# - Scrape sample job
# - Call /api/tailor
# - Call /api/generate-pdf
# - Verify PDF output
```

### Manual Testing Checklist

- [ ] Backend starts without errors
- [ ] Open Resume service accessible
- [ ] Extension loads in Chrome
- [ ] Can create resume profile
- [ ] Job scraping works on all supported sites
- [ ] AI tailoring completes successfully
- [ ] ATS score is reasonable (0-100)
- [ ] Keywords are accurate
- [ ] PDF downloads successfully
- [ ] PDF content matches resume
- [ ] History tracking works
- [ ] Dark mode toggle works
- [ ] Export/Import functions

---

## Deployment

### Docker Deployment (Recommended)

#### Production Deployment

```bash
# 1. Clone repository on server
git clone https://github.com/Manishrdy/resume_tailoring_extension.git
cd resume_tailoring_extension

# 2. Configure environment
cp backend/.env.example backend/.env
nano backend/.env  # Add production values

# 3. Build and start
docker-compose up -d --build

# 4. Check logs
docker-compose logs -f

# 5. Verify health
curl http://your-server:8000/api/health
```

#### Environment Variables for Production

```ini
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=chrome-extension://*,https://your-frontend.com
LOG_LEVEL=INFO
GEMINI_API_KEY=your_production_key
```

### Cloud Deployment Options

#### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Install Docker and Docker Compose
# 3. Clone repository
# 4. Configure environment
# 5. Run docker-compose up -d
# 6. Configure security groups (ports 8000, 3000)
```

#### Google Cloud Run

```bash
# Build and push containers
docker build -t gcr.io/your-project/resume-tailor-api backend/
docker build -t gcr.io/your-project/resume-tailor-pdf open-resume-service/

docker push gcr.io/your-project/resume-tailor-api
docker push gcr.io/your-project/resume-tailor-pdf

# Deploy to Cloud Run
gcloud run deploy resume-tailor-api --image gcr.io/your-project/resume-tailor-api
gcloud run deploy resume-tailor-pdf --image gcr.io/your-project/resume-tailor-pdf
```

#### Heroku

```bash
# Create Heroku apps
heroku create resume-tailor-api
heroku create resume-tailor-pdf

# Set environment variables
heroku config:set GEMINI_API_KEY=your_key -a resume-tailor-api

# Deploy
git push heroku main
```

### Publishing Chrome Extension

1. **Prepare for Publishing**
   ```bash
   cd extension
   npm run build
   zip -r extension.zip dist/
   ```

2. **Chrome Web Store**
   - Visit [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
   - Create developer account ($5 one-time fee)
   - Upload `extension.zip`
   - Fill in store listing details
   - Submit for review

3. **Update Manifest**
   - Update `manifest.json` with production API URL
   - Add privacy policy URL
   - Add promotional images

---

## Project Structure

```
resume-tailor/
├── backend/                              # FastAPI Backend (1,927 lines)
│   ├── src/
│   │   ├── app/
│   │   │   ├── main.py                  # FastAPI application initialization
│   │   │   ├── config.py                # Pydantic Settings configuration
│   │   │   └── api/
│   │   │       ├── health.py            # Health check endpoints
│   │   │       ├── tailor.py            # AI tailoring endpoint
│   │   │       └── pdf.py               # PDF generation endpoint
│   │   ├── models/
│   │   │   └── resume.py                # Pydantic data models
│   │   ├── services/
│   │   │   ├── gemini.py                # Google Gemini AI integration
│   │   │   └── pdf_client.py            # Open Resume API client
│   │   ├── prompts/
│   │   │   └── tailoring.py             # AI prompt templates
│   │   └── utils/
│   │       ├── logger.py                # Loguru logging configuration
│   │       └── artifacts.py             # Artifact storage utilities
│   ├── tests/                            # Test suite (8 modules, 30+ tests)
│   │   ├── test_health.py
│   │   ├── test_tailor.py
│   │   ├── test_pdf.py
│   │   ├── test_models.py
│   │   ├── test_pdf_transformations.py
│   │   ├── test_pdf_client_settings.py
│   │   └── conftest.py
│   ├── logs/                            # Application logs
│   ├── artifacts/                       # Generated resume artifacts
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile                       # Production container
│   └── .env.example                     # Environment template
│
├── open-resume-service/                 # Next.js PDF Service
│   ├── src/
│   │   └── app/
│   │       ├── api/
│   │       │   └── generate-pdf/        # PDF generation API route
│   │       ├── lib/
│   │       │   └── resume-pdf-generator.tsx
│   │       └── components/
│   │           └── Resume/              # Resume display components
│   ├── public/fonts/                    # Font files for PDF rendering
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── extension/                            # Chrome Extension
│   ├── manifest.json                    # Extension configuration (V3)
│   ├── popup/
│   │   ├── popup.html                   # Extension UI
│   │   └── popup.js                     # Popup logic and state
│   ├── background/
│   │   └── background.js                # Service worker
│   ├── content/
│   │   └── scraper.js                   # Job description scraper
│   └── assets/
│       ├── js/
│       │   ├── api.js                   # FastAPI client
│       │   └── storage.js               # Chrome Storage wrapper
│       ├── css/
│       │   └── styles.css               # Extension styling
│       └── icons/                       # Extension icons (16, 48, 128px)
│
├── docker-compose.yml                   # Production orchestration
├── docker-compose.dev.yml               # Development orchestration
├── .env.example                         # Environment template
├── README.md                            # This file
├── CONTRIBUTING.md                      # Contribution guidelines
├── LICENSE                              # MIT License
└── docs/
    ├── API.md                           # API documentation
    ├── ARCHITECTURE.md                  # System design
    └── DEPLOYMENT.md                    # Deployment guide
```

---

## Contributing

We welcome contributions! This project is designed to be beginner-friendly and a great way to learn about AI integration, FastAPI, and Chrome extensions.

### How to Contribute

1. **Check Open Issues**
   - Visit our [GitHub Issues](https://github.com/Manishrdy/resume_tailoring_extension/issues)
   - Look for issues tagged `good first issue` or `help wanted`
   - Comment on the issue to claim it

2. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   git clone https://github.com/YOUR_USERNAME/resume_tailoring_extension.git
   cd resume_tailoring_extension
   ```

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

4. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

5. **Test Your Changes**
   ```bash
   cd backend
   pytest
   black src/
   flake8 src/
   ```

6. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add job scraper for Monster.com"
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Link related issues
   - Wait for review

### Contribution Ideas

Check our [Issues](https://github.com/Manishrdy/resume_tailoring_extension/issues) for:

- **Good First Issues**: Perfect for beginners
- **Feature Requests**: New functionality to add
- **Bug Fixes**: Issues that need fixing
- **Documentation**: Improve docs and guides
- **Testing**: Add more test coverage

### Code Style Guidelines

#### Python (Backend)
- Use Black for formatting (line length: 88)
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

#### JavaScript (Extension)
- Use ES6+ syntax
- Use meaningful variable names
- Add comments for complex logic
- Follow async/await patterns

#### TypeScript (PDF Service)
- Use strict mode
- Define proper types
- Avoid `any` type
- Use functional components

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new job scraper for Monster.com
fix: resolve PDF generation timeout issue
docs: update API documentation
test: add tests for tailor endpoint
refactor: simplify Gemini service logic
chore: update dependencies
```

---

## Troubleshooting

### Common Issues

#### Backend Won't Start

**Error: `ModuleNotFoundError: No module named 'app'`**

```bash
# Solution: Run from correct directory
cd backend/src
uvicorn app.main:app --reload
```

**Error: `Connection refused to Gemini API`**

```bash
# Solution: Check API key
echo $GEMINI_API_KEY  # Should show your key
# Or check backend/.env file
```

#### Extension Not Loading

**Error: `Manifest version 2 is deprecated`**

```bash
# Solution: Ensure manifest.json has "manifest_version": 3
# Reload extension in chrome://extensions
```

**Error: `Extension popup is blank`**

```bash
# Solution: Check console for errors (F12 on popup)
# Verify API URL in extension settings
# Check CORS configuration in backend
```

#### PDF Generation Fails

**Error: `Failed to generate PDF: Connection timeout`**

```bash
# Solution 1: Check Open Resume service is running
curl http://localhost:3000/api/health

# Solution 2: Increase timeout in .env
OPEN_RESUME_API_TIMEOUT=60

# Solution 3: Check logs
tail -f backend/logs/app.log
```

**Error: `PDF missing content`**

```bash
# Solution: Check data transformation in logs
# Verify resume data matches expected schema
# Review backend/logs/app.log for transformation errors
```

#### Job Scraping Doesn't Work

**Error: `Could not extract job description`**

```bash
# Solution 1: Use manual paste option
# Solution 2: Check if site structure changed (F12 → Inspect Element)
# Solution 3: Report issue with job posting URL
```

#### API Health Check Fails

```bash
# Check services
curl http://localhost:8000/api/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "fastapi": "running",
    "gemini": "available",
    "open_resume": "available"
  }
}

# If unhealthy, check logs
docker-compose logs backend
docker-compose logs open-resume
```

### Debug Mode

Enable verbose logging:

```ini
# backend/.env
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

Then check logs:

```bash
# Docker
docker-compose logs -f backend

# Manual
tail -f backend/logs/app.log
```

### Getting Help

If you're stuck:

1. **Check Logs**: Most issues show up in logs
   - Backend: `backend/logs/app.log`
   - Extension: F12 → Console
   - Docker: `docker-compose logs`

2. **Search Issues**: [GitHub Issues](https://github.com/Manishrdy/resume_tailoring_extension/issues)

3. **Open an Issue**: Include:
   - Operating system
   - Python/Node.js version
   - Error messages
   - Steps to reproduce
   - Logs (sanitize API keys!)

---

## Performance

### Benchmarks

- **Resume Tailoring**: 10-15 seconds (Gemini AI processing)
- **PDF Generation**: 2-5 seconds
- **Job Scraping**: <1 second (instant)
- **Extension Popup**: <100ms load time
- **API Response Time**: <50ms (excluding AI/PDF)

### Optimization Tips

1. **Reduce Tailoring Time**
   - Use `gemini-2.0-flash-exp` (fastest model)
   - Reduce `GEMINI_MAX_TOKENS` if responses are too long
   - Enable response caching (future feature)

2. **Improve PDF Speed**
   - Simplify resume template
   - Reduce font size
   - Minimize custom styling

3. **Extension Performance**
   - Limit number of stored profiles (<10 recommended)
   - Clear history periodically
   - Use pagination for large history

---

## Security

### Best Practices

- **API Keys**: Never commit `.env` files to Git
- **CORS**: Restrict to specific origins in production
- **Input Validation**: All inputs validated via Pydantic
- **Rate Limiting**: Consider adding rate limits in production
- **Data Privacy**: All data stored locally, not on external servers

### Security Checklist

- [ ] `.env` files in `.gitignore`
- [ ] CORS configured properly
- [ ] API keys stored securely
- [ ] No sensitive data in logs
- [ ] HTTPS in production
- [ ] Regular dependency updates
- [ ] Extension permissions minimized

---

## Roadmap

### Planned Features

- [ ] Support for more job sites (Monster, ZipRecruiter)
- [ ] Multiple PDF templates
- [ ] Cover letter generation
- [ ] LinkedIn profile optimization
- [ ] Resume comparison tool
- [ ] A/B testing for different resume versions
- [ ] Analytics dashboard
- [ ] Team collaboration features
- [ ] API key management UI
- [ ] Resume version history

### Community Wishlist

See our [GitHub Issues](https://github.com/Manishrdy/resume_tailoring_extension/issues) for feature requests and vote on your favorites!

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

You are free to:
- Use commercially
- Modify
- Distribute
- Use privately

---

## Acknowledgments

### Special Thanks

This project builds upon the excellent work of the open-source community:

#### Document Generation

This project uses industry-standard Python libraries for professional document generation:

**ReportLab** - Enterprise-grade PDF generation library trusted by major corporations worldwide
- Professional ATS-friendly PDF templates
- Precise control over layout and formatting
- Production-ready and battle-tested
- [ReportLab Website](https://www.reportlab.com/)

**python-docx** - Official Python library for creating Word documents
- Clean DOCX generation with full formatting support
- Wide compatibility with Microsoft Word and alternatives
- Active maintenance and excellent documentation
- [python-docx Documentation](https://python-docx.readthedocs.io/)

**Huge credit and thanks to the ReportLab and python-docx teams for their excellent open-source libraries!**

#### Other Acknowledgments

- **Google Gemini AI** - For providing the powerful AI engine that makes intelligent resume tailoring possible
- **FastAPI** - For the excellent Python web framework
- **ReportLab** - For the professional PDF generation library
- **python-docx** - For the robust DOCX generation capabilities
- **Loguru** - For beautiful logging
- **pytest** - For comprehensive testing capabilities
- **Chrome Extensions API** - For enabling browser integration
- **All Contributors** - Thanks to everyone who has contributed code, reported bugs, or suggested features!

### Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Google Gemini](https://ai.google.dev/) - AI-powered resume optimization
- [ReportLab](https://www.reportlab.com/) - PDF generation library
- [python-docx](https://python-docx.readthedocs.io/) - DOCX generation library
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Loguru](https://github.com/Delgan/loguru) - Python logging
- [pytest](https://pytest.org/) - Testing framework

---

## Support

### Getting Help

- **Documentation**: Check this README and `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/Manishrdy/resume_tailoring_extension/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Manishrdy/resume_tailoring_extension/discussions)

### Show Your Support

If you find Resume Tailor helpful:

- Star this repository on GitHub
- Share with friends and colleagues
- Contribute improvements
- Report bugs and suggest features
- Write a blog post or tutorial

---

## Project Statistics

- **Lines of Code**: 5,000+
- **Backend**: 1,927 lines of Python
- **Test Coverage**: 90%+
- **API Endpoints**: 5+
- **Supported Job Sites**: 5+
- **AI Model**: Gemini 2.0 Flash
- **Container Support**: Docker & Docker Compose
- **License**: MIT

---

**Made with ❤️ for job seekers everywhere**

*Building better careers, one tailored resume at a time.*

---

## Quick Links

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Contributing Guidelines](#contributing)
- [GitHub Repository](https://github.com/Manishrdy/resume_tailoring_extension)
- [Report a Bug](https://github.com/Manishrdy/resume_tailoring_extension/issues/new?template=bug_report.md)
- [Request a Feature](https://github.com/Manishrdy/resume_tailoring_extension/issues/new?template=feature_request.md)
- [Open Resume Project](https://github.com/xitanggg/open-resume)

---

**Last Updated**: January 2026
**Version**: 1.0.0
**Status**: Production Ready
