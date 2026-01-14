# Testing Guide: DOCX Download Feature

## Quick Start

### 1. Start the Backend

```bash
cd C:\Users\manis\.claude-worktrees\resume_tailoring_extension\quizzical-cori\backend\src
uvicorn app.main:app --reload --port 8000
```

You should see:
```
🔧 GEMINI_API_KEY: ✅ SET
🔧 GEMINI_MODEL: gemini-2.5-flash-exp
🔧 DOCUMENT_GENERATION: Self-contained Python module (ReportLab + python-docx)
```

### 2. Load Extension in Chrome

1. Open Chrome and navigate to: `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **"Load unpacked"**
4. Navigate to: `C:\Users\manis\.claude-worktrees\resume_tailoring_extension\quizzical-cori\extension`
5. Click **"Select Folder"**

### 3. Test the Complete Flow

#### Step 1: Open Extension
- Click the extension icon in Chrome toolbar
- Extension popup should open

#### Step 2: Navigate to Tailor Tab
- Click on "Tailor" tab (should be default)
- You should see the job description input area

#### Step 3: Paste Job Description
Example job description to use:
```
Senior Software Engineer - AI/ML

We are seeking an experienced Senior Software Engineer to join our AI team.

Requirements:
- 5+ years of Python development
- Experience with FastAPI, Django, or Flask
- Strong understanding of machine learning concepts
- Experience with LLMs and RAG systems
- Knowledge of Docker and Kubernetes
- AWS or GCP cloud experience
- Excellent problem-solving skills

Responsibilities:
- Build scalable AI-powered applications
- Integrate LLMs into production systems
- Design and implement RESTful APIs
- Collaborate with cross-functional teams
- Mentor junior engineers

Nice to have:
- Experience with Google Gemini or OpenAI APIs
- Knowledge of LangChain or similar frameworks
- PostgreSQL and MongoDB experience
```

#### Step 4: Click "Tailor Resume with AI"
- Button should show loading state
- Wait 5-10 seconds for Gemini to process
- Results should appear with ATS score

#### Step 5: Test PDF Download
- Click **"Download PDF"** button (left button with 📄 icon)
- Button should show "⏳ Generating PDF..."
- PDF should download to Chrome downloads
- Check `C:\Users\manis\Downloads\tailored-resumes\` folder
- Open PDF and verify it looks professional

#### Step 6: Test DOCX Download
- Click **"Download DOCX"** button (right button with 📝 icon)
- Button should show "⏳ Generating DOCX..."
- DOCX should download to Chrome downloads
- Check `C:\Users\manis\Downloads\tailored-resumes\` folder
- Open DOCX in Microsoft Word and verify:
  - ✅ Formatting is clean
  - ✅ Content is editable
  - ✅ All sections are present
  - ✅ Bullet points work correctly

---

## Verification Checklist

### Backend
- [ ] Backend starts without errors
- [ ] Shows "Self-contained Python module" in startup logs
- [ ] PDF endpoint works: `http://localhost:8000/api/generate-pdf`
- [ ] DOCX endpoint works: `http://localhost:8000/api/generate-docx`
- [ ] Status endpoint shows both formats: `http://localhost:8000/api/document/status`

### Extension UI
- [ ] Two download buttons visible side-by-side
- [ ] PDF button shows 📄 icon and "Download PDF"
- [ ] DOCX button shows 📝 icon and "Download DOCX"
- [ ] Buttons are properly styled and equal width

### PDF Download
- [ ] Button shows loading state during generation
- [ ] PDF downloads successfully
- [ ] Filename format: `ResumeID_YYYY-MM-DDTHH-MM-SS.pdf`
- [ ] File saved to `tailored-resumes/` folder
- [ ] Success message displays
- [ ] Entry added to History tab
- [ ] PDF opens correctly
- [ ] All sections present
- [ ] Formatting is professional

### DOCX Download
- [ ] Button shows loading state during generation
- [ ] DOCX downloads successfully
- [ ] Filename format: `ResumeID_YYYY-MM-DDTHH-MM-SS.docx`
- [ ] File saved to `tailored-resumes/` folder
- [ ] Success message displays
- [ ] Entry added to History tab
- [ ] DOCX opens in Word/LibreOffice
- [ ] Content is editable
- [ ] Formatting preserved
- [ ] All sections present

### Error Handling
- [ ] Clicking download before tailoring shows error
- [ ] Network errors show appropriate message
- [ ] Backend down shows connection error
- [ ] Buttons re-enable after error

---

## Expected File Output

### PDF Output
**File**: `tailored-resumes/Your_Resume_Name_2026-01-12T15-30-45.pdf`

**Structure**:
```
┌─────────────────────────────────────┐
│         Your Name                    │
│  email@example.com • +1-555-1234    │
│  linkedin.com/in/you • github.com   │
├─────────────────────────────────────┤
│  PROFESSIONAL SUMMARY                │
│  Your summary text...                │
│                                      │
│  PROFESSIONAL EXPERIENCE             │
│  ■ Senior Software Engineer          │
│    Company Name - Location           │
│    Jan 2020 - Present               │
│    • Achievement bullet 1            │
│    • Achievement bullet 2            │
│                                      │
│  EDUCATION                           │
│  ■ Bachelor of Science              │
│    University Name                   │
│    2016 - 2020 • GPA: 3.8           │
│                                      │
│  TECHNICAL SKILLS                    │
│  Python • FastAPI • Docker • AWS    │
│                                      │
│  PROJECTS                            │
│  ■ Project Name                      │
│    Description...                    │
│    • Highlight 1                     │
└─────────────────────────────────────┘
```

### DOCX Output
**File**: `tailored-resumes/Your_Resume_Name_2026-01-12T15-30-45.docx`

**Features**:
- Editable text (can modify in Word)
- Proper heading styles
- Bullet points formatted correctly
- Consistent fonts (Arial, 11pt)
- Professional spacing
- Single-column layout

---

## Testing Scenarios

### Scenario 1: First-Time User
1. Open extension (never used before)
2. Go to "Create" tab
3. Fill in resume form
4. Save resume
5. Switch to "Tailor" tab
6. Paste job description
7. Click "Tailor Resume with AI"
8. Download both PDF and DOCX
9. Verify both files

### Scenario 2: Existing User
1. Open extension (already has resume)
2. Select resume from dropdown
3. Paste new job description
4. Tailor resume
5. Download PDF
6. Download DOCX
7. Check History tab for entries

### Scenario 3: Multiple Downloads
1. Tailor resume
2. Download PDF
3. Wait for success
4. Download DOCX
5. Wait for success
6. Verify both files exist
7. Check History shows 2 entries

### Scenario 4: Error Recovery
1. Stop backend server
2. Try to download PDF
3. Verify error message
4. Start backend
5. Try again
6. Verify success

---

## Debugging

### Enable Console Logs

**Chrome DevTools**:
1. Right-click extension popup
2. Select "Inspect"
3. Go to Console tab
4. Perform actions
5. Look for errors

**Backend Logs**:
- Terminal shows real-time logs
- Look for "Generating PDF/DOCX" messages
- Check for error stack traces

### Common Debug Commands

**Check backend health**:
```bash
curl http://localhost:8000/api/health
```

**Check document service status**:
```bash
curl http://localhost:8000/api/document/status
```

**View backend logs in real-time**:
- Just watch the terminal where you ran `uvicorn`

### Log Locations

**Backend Logs**: Terminal output
**Extension Logs**: Chrome DevTools Console
**Downloads**: `C:\Users\manis\Downloads\tailored-resumes\`

---

## Performance Testing

### Measure Generation Time

**PDF**:
- Expected: < 1 second
- Measure: Watch console logs for timing

**DOCX**:
- Expected: < 1 second
- Measure: Watch console logs for timing

### File Size Expectations

**PDF**: ~5-10 KB (typical resume)
**DOCX**: ~30-50 KB (typical resume)

*Sizes vary based on resume content*

---

## Advanced Testing

### Test with Different Resume Lengths

1. **Short Resume** (1 page):
   - 1-2 experiences
   - 1 education
   - Few skills
   - Expected: Fast generation, small files

2. **Medium Resume** (2 pages):
   - 3-5 experiences
   - 2 educations
   - Many skills
   - Expected: Normal generation, medium files

3. **Long Resume** (3+ pages):
   - 6+ experiences
   - Multiple educations
   - Many projects
   - Many certifications
   - Expected: Slightly longer, larger files

### Test Special Characters

Resume with:
- Accented characters (é, ñ, ü)
- Symbols (&, @, #, %)
- Quotes and apostrophes
- Em dashes and ellipses

Verify:
- PDF renders correctly
- DOCX preserves characters
- No encoding errors

---

## Success Indicators

### You'll Know It Works When:

1. ✅ Both buttons appear in the UI
2. ✅ PDF downloads to correct folder
3. ✅ DOCX downloads to correct folder
4. ✅ PDF opens without errors
5. ✅ DOCX is editable in Word
6. ✅ Formatting looks professional
7. ✅ All resume sections present
8. ✅ History tracks both downloads
9. ✅ Success messages display
10. ✅ No console errors

---

## Screenshots to Take

For verification, take screenshots of:

1. Extension popup with both download buttons
2. Loading state during generation
3. Success message after download
4. Chrome downloads showing both files
5. PDF opened in viewer
6. DOCX opened in Word
7. History tab showing entries

---

## Rollback If Needed

If something doesn't work:

```bash
# Go back to previous commit
cd C:\Users\manis\.claude-worktrees\resume_tailoring_extension\quizzical-cori
git status
git log --oneline -5

# If needed, rollback
git checkout HEAD~1 backend/src/app/api/pdf.py
git checkout HEAD~1 extension/popup/popup.html
git checkout HEAD~1 extension/popup/popup.js
git checkout HEAD~1 extension/assets/js/api.js
```

---

## Questions to Answer During Testing

- [ ] Does PDF generation work?
- [ ] Does DOCX generation work?
- [ ] Are files downloadable?
- [ ] Do files open correctly?
- [ ] Is formatting professional?
- [ ] Are buttons user-friendly?
- [ ] Are error messages clear?
- [ ] Is performance acceptable?
- [ ] Does history tracking work?
- [ ] Can you edit DOCX in Word?

---

## Next Steps After Testing

If all tests pass:
1. ✅ Mark testing as complete
2. ✅ Optional: Delete `open-resume-service/` folder
3. ✅ Optional: Commit changes to git
4. ✅ Start using the new system!

If tests fail:
1. Check error messages in console
2. Review backend logs
3. Verify dependencies installed
4. Check file permissions
5. Try rollback if needed

---

## Support

If you encounter issues:
1. Check `IMPLEMENTATION_SUMMARY.md` for details
2. Review `MIGRATION_GUIDE.md` for troubleshooting
3. Check backend logs for errors
4. Verify all dependencies installed
5. Ensure Python 3.11+ is being used

---

**Happy Testing! 🎉**
