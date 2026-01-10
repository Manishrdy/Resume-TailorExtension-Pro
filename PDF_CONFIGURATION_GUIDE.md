# PDF Configuration Guide

## Overview

The PDF generation system supports environment variable configuration for styling and formatting, allowing you to customize PDFs without code changes.

## Architecture

### Two-Layer Configuration System

1. **Backend Configuration** (`backend/.env`)
   - Used when backend calls Open Resume API
   - Settings passed in API request payload

2. **Frontend Configuration** (`open-resume-service/.env.local`)
   - Used as defaults when frontend generates PDFs directly
   - Can override backend settings if provided

### Configuration Priority

Settings are merged with the following priority (highest to lowest):

1. **API Request Settings** - Explicitly passed in the request
2. **Environment Variables** - From `.env` or `.env.local`
3. **Default Settings** - Hardcoded defaults in the application

## Backend Configuration

### File: `backend/.env`

```bash
# Open Resume Service Configuration
OPEN_RESUME_URL=http://localhost:3000
OPEN_RESUME_API_TIMEOUT=30

# PDF Styling Configuration
OPEN_RESUME_FONT_FAMILY=Open Sans
OPEN_RESUME_FONT_SIZE=11
OPEN_RESUME_THEME_COLOR=#000000
OPEN_RESUME_DOCUMENT_SIZE=A4
```

### Environment Variables

#### OPEN_RESUME_FONT_FAMILY
- **Description**: Font family for PDF text
- **Type**: String
- **Options**:
  - `Open Sans` (default)
  - `Roboto`
  - `Lato`
- **Example**: `OPEN_RESUME_FONT_FAMILY=Roboto`
- **Note**: Font files must exist in `open-resume-service/public/fonts/`

#### OPEN_RESUME_FONT_SIZE
- **Description**: Font size in points
- **Type**: Integer
- **Range**: 8-16 (recommended: 10-12)
- **Default**: `11`
- **Example**: `OPEN_RESUME_FONT_SIZE=12`
- **Impact**: Larger = bigger text, more pages; Smaller = smaller text, fewer pages

#### OPEN_RESUME_THEME_COLOR
- **Description**: Accent color for headers and decorative elements
- **Type**: Hex color code
- **Format**: `#RRGGBB` (6 digits)
- **Default**: `#000000` (black - no color bar shown)
- **Examples**:
  - Blue: `#38bdf8`
  - Green: `#10b981`
  - Purple: `#8b5cf6`
  - Red: `#ef4444`
  - Black (no bar): `#000000`
- **Note**: Use `#000000` or `#010101` to disable the color bar

#### OPEN_RESUME_DOCUMENT_SIZE
- **Description**: PDF page size
- **Type**: String
- **Options**:
  - `A4` - 210mm × 297mm (default, international standard)
  - `LETTER` - 8.5in × 11in (US standard)
  - `LEGAL` - 8.5in × 14in (US legal)
- **Example**: `OPEN_RESUME_DOCUMENT_SIZE=LETTER`

---

## Frontend Configuration (Optional)

### File: `open-resume-service/.env.local`

Create this file from the example:

```bash
cp .env.local.example .env.local
```

### Environment Variables

```bash
# PDF Font Family
NEXT_PUBLIC_PDF_FONT_FAMILY="Open Sans"

# PDF Font Size (in points)
NEXT_PUBLIC_PDF_FONT_SIZE=11

# PDF Theme Color (hex code)
NEXT_PUBLIC_PDF_THEME_COLOR="#000000"

# PDF Document Size
NEXT_PUBLIC_PDF_DOCUMENT_SIZE="A4"
```

**Note**: These use the `NEXT_PUBLIC_` prefix because Next.js requires it for environment variables accessible in the application.

---

## Usage Examples

### Example 1: Professional Blue Theme

**Backend** (`backend/.env`):
```bash
OPEN_RESUME_FONT_FAMILY=Roboto
OPEN_RESUME_FONT_SIZE=11
OPEN_RESUME_THEME_COLOR=#2563eb
OPEN_RESUME_DOCUMENT_SIZE=LETTER
```

**Result**:
- Roboto font at 11pt
- Blue accent color
- US Letter size (8.5" × 11")

### Example 2: Minimal Black & White

**Backend** (`backend/.env`):
```bash
OPEN_RESUME_FONT_FAMILY=Open Sans
OPEN_RESUME_FONT_SIZE=10
OPEN_RESUME_THEME_COLOR=#000000
OPEN_RESUME_DOCUMENT_SIZE=A4
```

**Result**:
- Open Sans font at 10pt (more compact)
- No color bar (pure black & white)
- A4 size (international standard)

### Example 3: Modern Tech Resume

**Backend** (`backend/.env`):
```bash
OPEN_RESUME_FONT_FAMILY=Lato
OPEN_RESUME_FONT_SIZE=11
OPEN_RESUME_THEME_COLOR=#8b5cf6
OPEN_RESUME_DOCUMENT_SIZE=A4
```

**Result**:
- Lato font (modern, clean)
- Purple accent color
- A4 size

---

## How It Works

### Backend Flow

1. Backend reads configuration from `backend/.env`
2. When generating PDF, backend creates payload:
   ```python
   payload = {
       "resume": { ... },
       "settings": {
           "fontFamily": settings.OPEN_RESUME_FONT_FAMILY,
           "fontSize": settings.OPEN_RESUME_FONT_SIZE,
           "themeColor": settings.OPEN_RESUME_THEME_COLOR,
           "documentSize": settings.OPEN_RESUME_DOCUMENT_SIZE,
           # ... other settings
       }
   }
   ```
3. Backend sends request to `POST /api/generate-pdf`
4. Open Resume service receives settings and applies them
5. PDF is generated with the configured styling

### Frontend Flow (When settings not provided in request)

1. Frontend loads `open-resume-service/.env.local`
2. `pdf-config.ts` module parses and validates environment variables
3. Settings are merged:
   ```typescript
   const mergedSettings = {
       ...initialSettings,      // Defaults
       ...envSettings,           // From .env.local
       ...requestSettings,       // From API request (highest priority)
   };
   ```
4. PDF is generated with merged settings

---

## Validation & Error Handling

### Font Family Validation

```typescript
// Valid options
const VALID_FONT_FAMILIES = ["Open Sans", "Roboto", "Lato"];

// Invalid input
NEXT_PUBLIC_PDF_FONT_FAMILY="Comic Sans"
// Warning logged: "Invalid font family. Using default: Open Sans"
```

### Font Size Validation

```typescript
// Valid range: 8-16
NEXT_PUBLIC_PDF_FONT_SIZE=20
// Warning logged: "Font size out of recommended range: 20. Recommended: 10-12"
// Still uses 20 (allows override)
```

### Theme Color Validation

```typescript
// Must be 6-digit hex
NEXT_PUBLIC_PDF_THEME_COLOR="blue"
// Error: "Invalid hex color. Must be format: #RRGGBB"
// Falls back to default: #000000
```

### Document Size Validation

```typescript
// Valid options
const VALID_DOCUMENT_SIZES = ["A4", "LETTER", "LEGAL"];

// Invalid input
NEXT_PUBLIC_PDF_DOCUMENT_SIZE="TABLOID"
// Warning logged: "Invalid document size. Using default: A4"
```

---

## Testing Configuration

### 1. Test Backend Configuration

```bash
# Update backend/.env
OPEN_RESUME_THEME_COLOR=#38bdf8

# Restart backend
cd backend
uvicorn src.app.main:app --reload

# Run E2E test
python test_pdf_generation_e2e.py

# Check output PDF
# Should have blue accent color
```

### 2. Test Frontend Configuration

```bash
# Create .env.local in open-resume-service
echo 'NEXT_PUBLIC_PDF_THEME_COLOR="#ef4444"' > .env.local

# Restart Next.js
cd open-resume-service
npm run dev

# Check console output
# Should show: "PDF Configuration loaded: { themeColor: '#ef4444', ... }"
```

### 3. Verify Priority

```bash
# Set different values
# Backend: OPEN_RESUME_THEME_COLOR=#38bdf8
# Frontend: NEXT_PUBLIC_PDF_THEME_COLOR=#ef4444

# Request with explicit setting
curl -X POST http://localhost:3000/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "resume": { ... },
    "settings": { "themeColor": "#10b981" }
  }'

# Result: Uses #10b981 (request setting wins)
```

---

## Troubleshooting

### Issue: Settings not applied

**Check 1**: Environment variables loaded
```bash
# In backend
python -c "from src.app.config import settings; print(settings.OPEN_RESUME_THEME_COLOR)"

# In frontend (check browser console)
# Should see: "PDF Configuration loaded: { ... }"
```

**Check 2**: Server restarted after .env changes
- Backend: Restart uvicorn
- Frontend: Restart Next.js dev server

**Check 3**: Correct file names
- Backend: `.env` (not `.env.example`)
- Frontend: `.env.local` (not `.env` or `.env.local.example`)

### Issue: Invalid color format

**Problem**: Color not a hex code
```bash
OPEN_RESUME_THEME_COLOR=blue  # ❌ Invalid
```

**Solution**: Use hex format
```bash
OPEN_RESUME_THEME_COLOR=#0000ff  # ✅ Valid
```

### Issue: Font not rendering

**Problem**: Font family doesn't exist
```bash
OPEN_RESUME_FONT_FAMILY=Arial  # ❌ Font files don't exist
```

**Solution**: Use available fonts
```bash
OPEN_RESUME_FONT_FAMILY=Roboto  # ✅ Font files exist
```

**Check font files**:
```bash
ls open-resume-service/public/fonts/
# Should show: Roboto-Regular.ttf, Roboto-Bold.ttf, etc.
```

---

## Advanced: Adding Custom Fonts

### 1. Add font files

```bash
# Add to open-resume-service/public/fonts/
cp MyFont-Regular.ttf open-resume-service/public/fonts/
cp MyFont-Bold.ttf open-resume-service/public/fonts/
```

### 2. Update font configuration

**File**: `open-resume-service/src/app/lib/pdf-generator-server.ts`

```typescript
const FONT_FILES: Record<string, { regular: string; bold: string }> = {
  "Open Sans": { regular: "OpenSans-Regular.ttf", bold: "OpenSans-Bold.ttf" },
  "Roboto": { regular: "Roboto-Regular.ttf", bold: "Roboto-Bold.ttf" },
  "Lato": { regular: "Lato-Regular.ttf", bold: "Lato-Bold.ttf" },
  "My Font": { regular: "MyFont-Regular.ttf", bold: "MyFont-Bold.ttf" }, // Add this
};
```

### 3. Update validation

**File**: `open-resume-service/src/app/lib/pdf-config.ts`

```typescript
const VALID_FONT_FAMILIES = ["Open Sans", "Roboto", "Lato", "My Font"] as const;
```

### 4. Use the font

```bash
OPEN_RESUME_FONT_FAMILY=My Font
```

---

## Best Practices

### 1. Use Version Control for Defaults

- Commit `.env.example` with recommended defaults
- Don't commit actual `.env` or `.env.local` files
- Document any custom configurations in README

### 2. Test Configuration Changes

```bash
# Always test after changing configuration
cd backend
python test_pdf_generation_e2e.py
```

### 3. Consistent Styling

- Use the same settings across environments (dev/staging/prod)
- Document your chosen configuration

### 4. Performance Considerations

- **Larger fonts** = More pages = Larger file size
- **Smaller fonts** = Fewer pages but may be hard to read
- **Recommended**: 11pt for optimal readability and compactness

### 5. Color Accessibility

- Use high-contrast colors for professional appearance
- Avoid very light colors that don't print well
- Test PDFs in both screen and print preview

---

## Summary

✅ **Backend Configuration**: `backend/.env` controls PDF styling when backend generates PDFs
✅ **Frontend Configuration**: `open-resume-service/.env.local` provides defaults for frontend
✅ **Priority**: Request settings > Environment variables > Defaults
✅ **Validation**: All settings are validated with helpful error messages
✅ **Production Ready**: Environment-based configuration, no code changes needed

Configure once, generate thousands of styled PDFs! 🎨📄
