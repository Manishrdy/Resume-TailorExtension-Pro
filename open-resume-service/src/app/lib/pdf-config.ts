/**
 * PDF Configuration from Environment Variables
 *
 * This module loads PDF generation settings from environment variables,
 * allowing configuration without code changes.
 *
 * Environment Variables:
 * - NEXT_PUBLIC_PDF_FONT_FAMILY: Font family for PDF ("Open Sans", "Roboto", "Lato")
 * - NEXT_PUBLIC_PDF_FONT_SIZE: Font size in points (10-12 recommended)
 * - NEXT_PUBLIC_PDF_THEME_COLOR: Theme color as hex code (e.g., "#38bdf8")
 * - NEXT_PUBLIC_PDF_DOCUMENT_SIZE: Document size ("A4", "LETTER", "LEGAL")
 */

import type { Settings } from "lib/redux/settingsSlice";

/**
 * Valid font families that have font files in public/fonts/
 */
const VALID_FONT_FAMILIES = ["Open Sans", "Roboto", "Lato"] as const;
type ValidFontFamily = (typeof VALID_FONT_FAMILIES)[number];

/**
 * Valid document sizes
 */
const VALID_DOCUMENT_SIZES = ["A4", "LETTER", "LEGAL"] as const;
type ValidDocumentSize = (typeof VALID_DOCUMENT_SIZES)[number];

/**
 * PDF Configuration Interface
 */
interface PDFConfig {
  fontFamily: ValidFontFamily;
  fontSize: number;
  themeColor: string;
  documentSize: ValidDocumentSize;
}

/**
 * Default PDF configuration
 */
const DEFAULT_CONFIG: PDFConfig = {
  fontFamily: "Open Sans",
  fontSize: 11,
  themeColor: "#000000",
  documentSize: "A4",
};

/**
 * Validate and parse font family from environment variable
 */
function parseFontFamily(value: string | undefined): ValidFontFamily {
  if (!value) return DEFAULT_CONFIG.fontFamily;

  const normalized = value.trim();
  if (VALID_FONT_FAMILIES.includes(normalized as ValidFontFamily)) {
    return normalized as ValidFontFamily;
  }

  console.warn(
    `Invalid NEXT_PUBLIC_PDF_FONT_FAMILY: "${value}". Must be one of: ${VALID_FONT_FAMILIES.join(", ")}. Using default: "${DEFAULT_CONFIG.fontFamily}"`
  );
  return DEFAULT_CONFIG.fontFamily;
}

/**
 * Validate and parse font size from environment variable
 */
function parseFontSize(value: string | undefined): number {
  if (!value) return DEFAULT_CONFIG.fontSize;

  const size = parseInt(value, 10);

  if (isNaN(size)) {
    console.warn(
      `Invalid NEXT_PUBLIC_PDF_FONT_SIZE: "${value}". Must be a number. Using default: ${DEFAULT_CONFIG.fontSize}`
    );
    return DEFAULT_CONFIG.fontSize;
  }

  if (size < 8 || size > 16) {
    console.warn(
      `NEXT_PUBLIC_PDF_FONT_SIZE out of recommended range: ${size}. Recommended: 10-12. Using value anyway.`
    );
  }

  return size;
}

/**
 * Validate and parse theme color from environment variable
 */
function parseThemeColor(value: string | undefined): string {
  if (!value) return DEFAULT_CONFIG.themeColor;

  const normalized = value.trim();

  // Validate hex color format
  const hexPattern = /^#[0-9A-Fa-f]{6}$/;
  if (!hexPattern.test(normalized)) {
    console.warn(
      `Invalid NEXT_PUBLIC_PDF_THEME_COLOR: "${value}". Must be a 6-digit hex color (e.g., #38bdf8). Using default: "${DEFAULT_CONFIG.themeColor}"`
    );
    return DEFAULT_CONFIG.themeColor;
  }

  return normalized;
}

/**
 * Validate and parse document size from environment variable
 */
function parseDocumentSize(value: string | undefined): ValidDocumentSize {
  if (!value) return DEFAULT_CONFIG.documentSize;

  const normalized = value.trim().toUpperCase();
  if (VALID_DOCUMENT_SIZES.includes(normalized as ValidDocumentSize)) {
    return normalized as ValidDocumentSize;
  }

  console.warn(
    `Invalid NEXT_PUBLIC_PDF_DOCUMENT_SIZE: "${value}". Must be one of: ${VALID_DOCUMENT_SIZES.join(", ")}. Using default: "${DEFAULT_CONFIG.documentSize}"`
  );
  return DEFAULT_CONFIG.documentSize;
}

/**
 * Load PDF configuration from environment variables
 */
function loadPDFConfig(): PDFConfig {
  return {
    fontFamily: parseFontFamily(process.env.NEXT_PUBLIC_PDF_FONT_FAMILY),
    fontSize: parseFontSize(process.env.NEXT_PUBLIC_PDF_FONT_SIZE),
    themeColor: parseThemeColor(process.env.NEXT_PUBLIC_PDF_THEME_COLOR),
    documentSize: parseDocumentSize(process.env.NEXT_PUBLIC_PDF_DOCUMENT_SIZE),
  };
}

/**
 * Global PDF configuration loaded from environment variables
 */
export const PDF_CONFIG = loadPDFConfig();

/**
 * Get default settings with environment variable overrides
 *
 * This merges the environment-based PDF config with the standard settings structure
 */
export function getDefaultPDFSettings(): Partial<Settings> {
  return {
    fontFamily: PDF_CONFIG.fontFamily,
    fontSize: PDF_CONFIG.fontSize,
    themeColor: PDF_CONFIG.themeColor === "#000000" ? "" : PDF_CONFIG.themeColor,
    documentSize: PDF_CONFIG.documentSize,
  };
}

/**
 * Log configuration on module load (only in development)
 */
if (process.env.NODE_ENV === "development") {
  console.log("PDF Configuration loaded from environment:");
  console.log({
    fontFamily: PDF_CONFIG.fontFamily,
    fontSize: PDF_CONFIG.fontSize,
    themeColor: PDF_CONFIG.themeColor,
    documentSize: PDF_CONFIG.documentSize,
  });
}
