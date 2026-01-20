# Resume Tailor AI

> AI-powered resume optimization platform with ATS scoring, intelligent tailoring, and professional PDF/DOCX generation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.0_Flash-blue?logo=google)](https://ai.google.dev/)
[![WeasyPrint](https://img.shields.io/badge/WeasyPrint-61.0-green)](https://weasyprint.org/)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Resume Tailor AI** is a production-ready platform that helps job seekers optimize their resumes for specific job applications using AI. The system combines Google's Gemini AI with professional HTML-to-PDF generation to create ATS-friendly resumes that maximize your chances of passing automated screening systems.

### Why Resume Tailor AI?

- **🤖 AI-Powered Optimization** - Gemini 2.0 Flash analyzes and tailors your resume to match job descriptions
- **📊 ATS Scoring** - Get 0-100 compatibility scores with actionable improvement suggestions
- **📄 Professional PDF Generation** - WeasyPrint creates pixel-perfect ATS-optimized PDFs from HTML templates
- **🎨 Template-Based Design** - Jinja2 HTML templates for complete customization and consistency
- **🎯 Job Site Integration** - Auto-scrape job descriptions from LinkedIn, Indeed, Greenhouse, and more
- **🔒 Privacy-First** - All data stored locally, zero external tracking
- **⚡ Production-Ready** - Docker support, comprehensive testing, structured logging
- **✨ Modern Stack** - FastAPI + WeasyPrint + Jinja2 for enterprise-grade document generation

### System Components

```
┌─────────────────────┐
│  Chrome Extension   │  ← User Interface
│  (Popup + Scraper)  │
└──────────┬──────────┘
           │ REST API
           ▼
┌─────────────────────┐
│   FastAPI Backend   │  ← Core Orchestration
│                     │
│  ┌───────────────┐  │
│  │  Gemini AI    │  │  ← Resume Tailoring & ATS Analysis
│  │  Service      │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │  WeasyPrint   │  │  ← HTML → PDF Rendering
│  │  Generator    │  │     (ATS-Optimized)
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │  python-docx  │  │  ← DOCX Generation
│  │  Generator    │  │     (Editable Word Docs)
│  └───────────────┘  │
└─────────────────────┘
```

---

## Key Features

### 🎯 AI Resume Tailoring

- **Smart Keyword Matching** - Automatically identify and incorporate relevant keywords from job descriptions
- **Bullet Point Optimization** - Rewrite experience bullets to highlight relevant skills and achievements
- **Skills Gap Analysis** - Identify missing skills and get specific suggestions for improvement
- **Professional Summary Rewriting** - Tailor your summary to match job requirements
- **Contextual Understanding** - AI maintains factual accuracy while optimizing language
- **ATS Keyword Extraction** - Advanced parsing of job descriptions to identify critical terms

### 📊 ATS Compatibility

- **0-100 Scoring System** - Quantitative assessment of resume-job compatibility
- **Matched Keywords Analysis** - See exactly which keywords are present in your resume
- **Missing Keywords Identification** - Discover important terms you should add
- **Actionable Suggestions** - Specific, prioritized recommendations to improve your score
- **Industry Standards Compliance** - Follows ATS best practices for formatting and structure

### 📄 Professional Document Generation

#### WeasyPrint HTML-to-PDF (Current Standard)
- **Pixel-Perfect Rendering** - Professional-grade PDF output from HTML templates
- **CSS3 Support** - Modern styling with flexbox, custom fonts, and advanced layouts
- **ATS-Optimized Design** - Single-column layout, proper semantic structure, clean text extraction
- **Template-Based** - Jinja2 HTML templates for complete customization
- **Font Embedding** - Proper font handling for consistent rendering
- **Metadata Support** - PDF metadata for better searchability

#### Template Features
- **Professional Layout** - Clean, modern design with accent color bar
- **Customizable Styling** - Easy font, color, and spacing adjustments via template variables
- **Semantic HTML** - Proper heading hierarchy and structure for ATS parsing
- **Responsive Sections** - Dynamic layout based on content availability
- **Project Links** - Separate GitHub/portfolio links for better ATS extraction

#### Supported Formats
-** PDF** - ATS-optimized, professional layout via WeasyPrint
- **DOCX** - Fully editable Word documents with python-docx

### 🌐 Job Site Support

Built-in scrapers for major job platforms:

| Platform | Status | Features |
|----------|--------|----------|
| LinkedIn | ✅ Active | Title, company, description, location, requirements |
| Indeed | ✅ Active | Full job details and structured requirements |
| Greenhouse | ✅ Active | Complete job postings with company info |
| Glassdoor | ✅ Active | Job details and salary information |
| Ashby | ✅ Active | Technical role details and requirements |
| Manual Entry | ✅ Active | Paste any job description directly |

### 🔧 Chrome Extension Features

- **Profile Management** - Create and manage multiple resume versions for different job types
- **Auto-Save** - Never lose your work with automatic profile saving
- **History Tracking** - Review all previously tailored resumes with ATS scores
- **Real-time Validation** - Input validation with helpful error messages
- **Import/Export** - Backup and restore your resume profiles as JSON
- **Intuitive UI** - Clean, modern interface with smooth user experience

---

## Architecture

### Technology Stack

#### Backend (FastAPI)
```python
Framework:        FastAPI 0.109.0
Server:           Uvicorn (ASGI)
AI Engine:        Google Gemini 2.0 Flash (google-genai 0.2.0)
Validation:       Pydantic 2.5.3 + pydantic-settings 2.1.0
PDF Generation:   WeasyPrint 61.0 (HTML → PDF)
DOCX Generation:  python-docx 1.2.0
Template Engine:  Jinja2 3.1.3
Logging:          Loguru 0.7.2
Testing:          pytest 7.4.4 + pytest-asyncio + pytest-cov
```

#### Frontend (Chrome Extension)
```javascript
Language:     Vanilla JavaScript (ES6+)
UI:           HTML5/CSS3
Storage:      Chrome Storage API
Manifest:     V3 (modern Chrome extension standard)
Job Scrapers: Custom content scripts for each platform
```

#### Document Generation Pipeline
```
Resume Data (JSON)
        ↓
Jinja2 Template Rendering (HTML)
        ↓
WeasyPrint (HTML → PDF)
   - CSS3 styling
   - Font embedding
   - Semantic structure
        ↓
ATS-Optimized PDF Output
```

#### Infrastructure
```yaml
Containerization:   Docker + Docker Compose
Orchestration:      Make commands for simplified workflows
Logging:            File-based with rotation (logs/app.log, logs/gemini.log)
Environment:        python-dotenv for configuration management
Health Checks:      /api/health endpoint with service status
```

### Data Flow

```
1. User opens job posting on supported platform
   ↓
2. Extension auto-detects site and scrapes job description
   ↓
3. User selects resume profile and clicks "Tailor Resume"
   ↓
4. POST /api/tailor → FastAPI Backend
   ↓
5. Gemini AI analyzes job requirements vs. resume
   ↓
6. AI optimizes resume content and calculates ATS score
   ↓
7. Return tailored resume + ATS score + keyword analysis
   ↓
8. User reviews optimizations and clicks "Download PDF"
   ↓
9. POST /api/generate-pdf with tailored resume
   ↓
10. Jinja2 renders HTML template with resume data
   ↓
11. WeasyPrint converts HTML → PDF with proper styling
   ↓
12. Browser downloads ATS-optimized PDF resume
```

---

## Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Google Gemini API Key** ([Get Free Key](https://ai.google.dev/))
- **Chrome Browser** ([Download](https://www.google.com/chrome/))
- **GTK+ Runtime** (Windows) - Required for WeasyPrint ([Download](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases))

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/Manishrdy/resume_tailoring_extension.git
cd resume_tailoring_extension

# 2. Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_actual_key_here

# 4. Start backend
cd src
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Load Chrome Extension
# - Open chrome://extensions/
# - Enable "Developer mode" (top right)
# - Click "Load unpacked"
# - Select the extension/ folder

# 6. Verify installation
# Backend should be running at: http://localhost:8000
# API docs available at: http://localhost:8000/docs
```

### Windows WeasyPrint Setup

WeasyPrint requires GTK+ runtime on Windows:

1. Download GTK3 Runtime from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Install with default options
3. Restart your terminal/IDE
4. Install WeasyPrint: `pip install weasyprint==61.0`

Alternatively, WeasyPrint will fall back to DOCX→PDF conversion using `docx2pdf` (Windows only).

---

## Installation

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# Run backend
cd src
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Chrome Extension Setup

```bash
# No build step required

# Load in Chrome:
# 1. Open chrome://extensions/
# 2. Enable "Developer mode" (toggle top-right)
# 3. Click "Load unpacked"
# 4. Select the extension/ folder
# 5. Pin extension to toolbar
```

---

## Configuration

### Backend Environment Variables

Create `backend/.env`:

```ini
# =======================
# Environment
# =======================
ENVIRONMENT=production
DEBUG=false

# =======================
# API Configuration
# =======================
API_HOST=0.0.0.0
API_PORT=8000

# =======================
# CORS Settings
# =======================
CORS_ORIGINS=chrome-extension://*,http://localhost:*

# =======================
# Google Gemini AI
# =======================
GEMINI_API_KEY=your_actual_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.7

# =======================
# Resume Template Settings
# =======================
RESUME_ACCENT_COLOR=#1e3a5f
RESUME_FONT_FAMILY=Roboto
RESUME_FONT_SIZE=9

# =======================
# Document Generation
# =======================
DOCUMENT_GENERATION=weasyprint

# =======================
# Logging
# =======================
LOG_LEVEL=INFO
LOG_FORMAT=text
```

### Template Customization

Edit `backend/templates/resume_template_professional.html` to customize:

- **Colors**: Change `accentColor` variable or hardcode colors
- **Fonts**: Modify `font-family` declarations (ensure ATS compatibility)
- **Layout**: Adjust spacing, margins, section order
- **Sections**: Add/remove resume sections as needed

The template uses Jinja2 syntax for dynamic content:
```html
<h1>{{ personalInfo.name }}</h1>
<div style="color: {{ accentColor | default('#1e3a5f') }}">
    Section with customizable accent color
</div>
```

---

## Usage

### Creating Your Resume Profile

1. **Open Extension** - Click Resume Tailor AI icon in Chrome toolbar
2. **Create Profile** - Click "New Profile" and fill in:
   - **Personal Info**: Name, email, phone, location, LinkedIn, GitHub, portfolio
   - **Professional Summary**: 2-3 sentences highlighting your expertise
   - **Work Experience**: Companies, roles, dates, achievement bullets
   - **Education**: Institutions, degrees, dates, GPA (optional)
   - **Skills**: Technical and soft skills (comma-separated)
   - **Projects**: Portfolio projects with GitHub links (optional)
   - **Certifications**: Professional certifications (optional)
3. **Save** - Profile saves automatically and is ready for tailoring

### Tailoring for a Specific Job

1. **Navigate to Job** - Go to job posting on LinkedIn, Indeed, Greenhouse, Glassdoor, or Ashby
2. **Open Extension** - Click extension icon
3. **Scrape Job** - Click "Scrape Job Description" (or use "Manual Entry" to paste)
4. **Review** - Verify scraped content is accurate
5. **Tailor** - Click "Tailor Resume" and wait 10-20 seconds
6. **Analyze Results**:
   - **ATS Score**: 0-100 compatibility rating
   - **Matched Keywords**: Skills found in your resume
   - **Missing Keywords**: Important skills to add
   - **Suggestions**: Specific improvements to make
7. **Review** - Check optimized content for accuracy
8. **Download** - Click "Download PDF" or "Download DOCX"

### Understanding ATS Scores

- **90-100**: Excellent match - very high chance of passing ATS
- **75-89**: Good match - likely to pass with minor improvements
- **60-74**: Fair match - consider adding missing keywords
- **Below 60**: Poor match - significant gaps to address

### Managing Multiple Profiles

Create different profiles for different job types:
- "Backend Engineer - Python/FastAPI"
- "Full Stack - MERN Stack"
- "Data Engineer - AWS/Spark"

Switch between profiles using the dropdown menu. All changes auto-save.

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "fastapi": "running",
    "gemini": "available",
    "document_generator": "weasyprint"
  }
}
```

#### 2. Tailor Resume
```http
POST /api/tailor
Content-Type: application/json
```

**Request**: Resume object + job description string
**Response**: Tailored resume + ATS score + keywords + suggestions

#### 3. Generate PDF
```http
POST /api/generate-pdf
Content-Type: application/json
```

**Request**: Resume object
**Response**: PDF file (application/pdf)

#### 4. Generate DOCX
```http
POST /api/generate-docx
Content-Type: application/json
```

**Request**: Resume object
**Response**: DOCX file (application/vnd.openxmlformats-officedocument.wordprocessingml.document)

### Interactive Documentation

Visit when backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Development

### Running Tests

```bash
cd backend
pytest                     # Run all tests
pytest --cov              # Run with coverage
pytest -v                 # Verbose output
pytest tests/test_gemini.py  # Specific test file
```

### Code Quality

```bash
# Format code
black backend/src

# Lint code
flake8 backend/src

# Type checking
mypy backend/src
```

### Adding New Job Platform Scrapers

1. Create content script in `extension/content-scripts/[platform].js`
2. Add scraping logic following existing patterns
3. Update manifest.json with content_scripts entry
4. Test on actual job postings

---

## Project Structure

```
resume_tailoring_extension/
├── backend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── main.py              # FastAPI application
│   │   │   ├── config.py            # Configuration with pydantic-settings
│   │   │   └── routes/
│   │   │       ├── tailor.py        # Resume tailoring endpoints
│   │   │       └── documents.py     # PDF/DOCX generation endpoints
│   │   ├── models/
│   │   │   └── resume.py            # Pydantic models for resume data
│   │   └── services/
│   │       ├── gemini_service.py    # AI tailoring service
│   │       └── template_document_generator.py  # WeasyPrint + python-docx
│   ├── templates/
│   │   └── resume_template_professional.html   # Jinja2 HTML template
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template
│   └── tests/                       # Pytest test suite
├── extension/
│   ├── manifest.json                # Chrome extension manifest V3
│   ├── popup/
│   │   ├── popup.html              # Extension popup UI
│   │   ├── popup.js                # UI logic and API calls
│   │   └── popup.css               # Styling
│   ├── background.js                # Service worker
│   └── content-scripts/             # Job site scrapers
│       ├── linkedin.js
│       ├── indeed.js
│       ├── greenhouse.js
│       └── ...
├── test_pdf_gen.py                  # Standalone PDF generator test
└── README.md
```

---

## Troubleshooting

### WeasyPrint Issues (Windows)

**Problem**: `OSError: cannot load library 'gobject-2.0-0'`
**Solution**: Install GTK3 Runtime:
1. Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Run installer with default settings
3. Restart terminal/IDE
4. Reinstall: `pip install --force-reinstall weasyprint==61.0`

**Alternative**: System will fall back to docx2pdf if WeasyPrint fails

### No Colors or Wrong Fonts in PDF

**Problem**: Template variables not rendering
**Cause**: Auto-formatter broke Jinja2 syntax in template
**Solution**: 
1. Disable auto-format for HTML files in VS Code:
   ```json
   "[html]": {
     "editor.formatOnSave": false
   }
   ```
2. Ensure template variables are on single lines:
   ```html
   ✅ CORRECT: {{ fontFamily | default("Roboto") }}
   ❌ WRONG:   { { fontFamily | default("Roboto") } }
   ```

### Gemini API Errors

**Problem**: `401 Unauthorized`
**Solution**: Verify GEMINI_API_KEY in backend/.env is correct

**Problem**: `429 Too Many Requests`
**Solution**: Wait and retry, or upgrade to paid Gemini API tier

###Extension Not Loading

**Problem**: "Manifest version 2 is deprecated"
**Solution**: Extension is already Manifest V3, reload extension

**Problem**: Extension icon not showing
**Solution**: Pin extension from chrome://extensions/ → Details → Pin

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow existing code style (Black for Python, ESLint for JS)
- Add tests for new features
- Update documentation as needed
- Test on multiple job platforms before submitting

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Google Gemini** - AI-powered resume optimization
- **WeasyPrint** - Professional HTML-to-PDF rendering
- **FastAPI** - Modern, fast web framework
- **Job platforms** - LinkedIn, Indeed, Greenhouse, Glassdoor, Ashby

---

**Made with ❤️ by developers, for developers**

For questions, issues, or suggestions, please open an issue on GitHub.
