# Contributing to Resume Tailor

Thank you for your interest in contributing to Resume Tailor! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Personal or political attacks
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

Before contributing, make sure you have:

- **Python 3.11+** installed
- **Node.js 18+** installed
- **Git** for version control
- **Google Gemini API Key** (for testing AI features)
- A **GitHub account**
- Familiarity with FastAPI, React, or Chrome Extensions (depending on contribution area)

### Setting Up Your Development Environment

1. **Fork the Repository**
   ```bash
   # Visit https://github.com/Manishrdy/resume_tailoring_extension
   # Click "Fork" button
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/resume_tailoring_extension.git
   cd resume_tailoring_extension
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/Manishrdy/resume_tailoring_extension.git
   ```

4. **Install Dependencies**

   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Open Resume Service:**
   ```bash
   cd open-resume-service
   npm install
   ```

   **Extension:**
   ```bash
   cd extension
   # No build step required for basic development
   # Or run: npm install && npm run build (if using build tools)
   ```

5. **Configure Environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

6. **Verify Setup**
   ```bash
   # Start backend
   cd backend/src
   uvicorn app.main:app --reload

   # Start PDF service (in another terminal)
   cd open-resume-service
   npm run dev

   # Load extension
   # Open chrome://extensions, enable Developer Mode, load extension folder
   ```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Code Contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Code refactoring

2. **Documentation**
   - Improving README
   - Adding code comments
   - Writing tutorials
   - Creating diagrams

3. **Testing**
   - Writing unit tests
   - Integration testing
   - Reporting bugs
   - Verifying fixes

4. **Design**
   - UI/UX improvements
   - Icon design
   - Template creation

### Finding Work

- **Good First Issues**: Look for issues labeled `good first issue`
- **Help Wanted**: Check issues labeled `help wanted`
- **Feature Requests**: Browse issues labeled `enhancement`
- **Bugs**: Fix issues labeled `bug`

## Development Workflow

### Branch Strategy

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number-description
   ```

2. **Branch Naming Conventions**
   - `feature/` - New features (e.g., `feature/add-monster-scraper`)
   - `fix/` - Bug fixes (e.g., `fix/pdf-generation-timeout`)
   - `docs/` - Documentation (e.g., `docs/update-api-guide`)
   - `test/` - Testing (e.g., `test/add-tailor-tests`)
   - `refactor/` - Code refactoring (e.g., `refactor/simplify-gemini-service`)

### Making Changes

1. **Keep Changes Focused**
   - One feature/fix per PR
   - Don't mix refactoring with feature additions
   - Keep commits atomic and logical

2. **Write Clear Commit Messages**
   ```
   feat: add Monster.com job scraper

   - Implement scrapeMonster() function
   - Add Monster to PRIMARY_SOURCES
   - Add routing logic for Monster.com
   - Test on 5 different Monster job postings

   Closes #6
   ```

3. **Commit Message Format** (Conventional Commits)
   ```
   <type>(<scope>): <subject>

   <body>

   <footer>
   ```

   **Types:**
   - `feat`: New feature
   - `fix`: Bug fix
   - `docs`: Documentation changes
   - `style`: Code style changes (formatting, no logic change)
   - `refactor`: Code refactoring
   - `test`: Adding or updating tests
   - `chore`: Maintenance tasks

   **Examples:**
   ```
   feat(extension): add form validation for email field
   fix(backend): resolve Gemini API timeout issue
   docs(readme): update installation instructions
   test(backend): add tests for resume model validation
   ```

## Coding Standards

### Python (Backend)

**Style Guide:** Follow PEP 8

**Tools:**
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type check
mypy src/
```

**Best Practices:**
- Use type hints for all function signatures
- Write docstrings for all public functions
- Keep functions small and focused (< 50 lines)
- Use meaningful variable names
- Avoid global variables
- Handle exceptions appropriately

**Example:**
```python
from typing import List, Optional
from models.resume import Resume

async def tailor_resume(
    resume: Resume,
    job_description: str,
    temperature: float = 0.7
) -> dict:
    """
    Tailor resume content to match job description.

    Args:
        resume: The resume to tailor
        job_description: Target job description
        temperature: AI creativity level (0.0-1.0)

    Returns:
        Dict containing tailored resume and ATS score

    Raises:
        ValidationError: If resume data is invalid
        TimeoutError: If AI processing times out
    """
    # Implementation
    pass
```

### JavaScript/TypeScript (Extension & PDF Service)

**Style Guide:** Airbnb JavaScript Style Guide

**Tools:**
```bash
# Lint (if configured)
npm run lint

# Format (if using Prettier)
npm run format
```

**Best Practices:**
- Use `const` and `let`, never `var`
- Use arrow functions for callbacks
- Use async/await instead of callbacks
- Add JSDoc comments for complex functions
- Handle promises properly (always catch)
- Use meaningful variable names

**Example:**
```javascript
/**
 * Scrapes job description from the current page.
 *
 * @returns {Promise<Object>} Job data with title, company, and description
 * @throws {Error} If scraping fails or page is unsupported
 */
async function scrapeJobDescription() {
    try {
        const hostname = window.location.hostname;

        if (hostname.includes('linkedin.com')) {
            return await scrapeLinkedIn();
        }

        throw new Error('Unsupported job site');
    } catch (error) {
        console.error('Scraping failed:', error);
        throw error;
    }
}
```

### File Organization

- Keep files focused on a single responsibility
- Group related functions together
- Use clear file names that describe purpose
- Avoid files longer than 500 lines

## Testing Guidelines

### Backend Testing

**Framework:** pytest

**Running Tests:**
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test
pytest tests/test_tailor.py -v

# Run with debugging
pytest -s
```

**Writing Tests:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tailor_endpoint_success():
    """Test successful resume tailoring"""
    # Arrange
    request_data = {
        "resume": {...},
        "job_description": "..."
    }

    # Act
    response = client.post("/api/tailor", json=request_data)

    # Assert
    assert response.status_code == 200
    assert "tailored_resume" in response.json()
    assert "ats_score" in response.json()

def test_tailor_endpoint_invalid_input():
    """Test tailoring with invalid input"""
    response = client.post("/api/tailor", json={})
    assert response.status_code == 422  # Validation error
```

**Test Coverage Requirements:**
- New features must include tests
- Bug fixes should include regression tests
- Aim for 80%+ coverage on new code

### Extension Testing

**Framework:** Jest (when configured)

**Manual Testing Checklist:**
- [ ] Extension loads without errors
- [ ] Forms validate input correctly
- [ ] Job scraping works on test sites
- [ ] API calls succeed
- [ ] Error handling works
- [ ] UI updates correctly

## Submitting Changes

### Pre-Submission Checklist

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
- [ ] No sensitive data (API keys, passwords) in code
- [ ] Code is properly formatted (black/prettier)
- [ ] No linting errors

### Pull Request Process

1. **Update Your Branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template

4. **PR Title Format**
   ```
   feat: add Monster.com job scraper
   fix: resolve PDF generation timeout
   docs: update API documentation
   ```

5. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Related Issue
   Closes #123

   ## Changes Made
   - Added Monster.com scraper
   - Updated routing logic
   - Added tests

   ## Testing
   - Tested on 5 Monster job postings
   - All tests pass
   - Manual testing completed

   ## Screenshots (if UI changes)
   [Add screenshots]

   ## Checklist
   - [x] Tests pass
   - [x] Code follows style guide
   - [x] Documentation updated
   - [x] Ready for review
   ```

6. **Respond to Feedback**
   - Address reviewer comments
   - Make requested changes
   - Push updates to the same branch

7. **After Approval**
   - Maintainer will merge your PR
   - Delete your feature branch
   - Pull latest changes from upstream

## Issue Guidelines

### Creating Issues

**Before creating an issue:**
- Search existing issues to avoid duplicates
- Check if it's already fixed in the latest version
- Gather relevant information (logs, screenshots, environment)

**Issue Templates:**
- Bug Report: For reporting bugs
- Feature Request: For suggesting new features
- Good First Issue: For beginner-friendly tasks

### Claiming Issues

1. Comment on the issue: "I'd like to work on this"
2. Wait for maintainer confirmation
3. Start working within 1 week
4. Ask questions if you get stuck

## Pull Request Process

### Review Process

1. **Automated Checks** (when configured)
   - Tests must pass
   - Code quality checks must pass
   - Coverage thresholds must be met

2. **Code Review**
   - At least one maintainer review required
   - Address all comments
   - Make requested changes

3. **Approval**
   - Reviewer approves PR
   - Maintainer merges

### After Your PR is Merged

1. **Delete your branch**
   ```bash
   git branch -d feature/your-feature-name
   git push origin --delete feature/your-feature-name
   ```

2. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

3. **Celebrate!** You've contributed to open source! 🎉

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community chat
- **Pull Requests**: Code review and collaboration

### Getting Help

If you need help:

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Tag maintainers in your issue/PR

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project website (if applicable)

## Additional Resources

### Learning Resources

**FastAPI:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

**Chrome Extensions:**
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)

**Testing:**
- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)

**Git:**
- [Git Basics](https://git-scm.com/book/en/v2/Getting-Started-Git-Basics)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Project Documentation

- [README.md](README.md) - Project overview
- [OPEN_SOURCE_ISSUES.md](OPEN_SOURCE_ISSUES.md) - Detailed issue descriptions
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture (coming soon)

## Thank You!

Thank you for contributing to Resume Tailor! Your contributions help job seekers worldwide create better resumes and land their dream jobs.

**Happy coding!** 🚀

---

**Questions?** Open a discussion or ask in your issue/PR.

**Found a bug in these guidelines?** Submit a PR to improve them!
