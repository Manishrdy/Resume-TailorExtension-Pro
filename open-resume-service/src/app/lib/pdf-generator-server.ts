"use server";

import path from "path";
import React from "react";
import type { Settings } from "lib/redux/settingsSlice";
import type { Resume } from "lib/redux/types";

type GeneratePDFSettings = Partial<Settings>;

// Track registered fonts per process to avoid re-registering
const registeredFonts = new Set<string>();

const FONT_FILES: Record<string, { regular: string; bold: string }> = {
  "Open Sans": {
    regular: "OpenSans-Regular.ttf",
    bold: "OpenSans-Bold.ttf",
  },
  Roboto: {
    regular: "Roboto-Regular.ttf",
    bold: "Roboto-Bold.ttf",
  },
  Lato: {
    regular: "Lato-Regular.ttf",
    bold: "Lato-Bold.ttf",
  },
};

/**
 * Register font family with @react-pdf/renderer
 * Must be called before rendering any documents
 */
const registerFontFamily = async (fontFamily: string) => {
  // Avoid re-registering fonts
  if (registeredFonts.has(fontFamily)) {
    return;
  }

  const files = FONT_FILES[fontFamily];
  if (!files) {
    console.warn(`Font family ${fontFamily} not found in FONT_FILES`);
    return;
  }

  try {
    const { Font } = await import("@react-pdf/renderer");
    const fontsDir = path.join(process.cwd(), "public", "fonts");
    
    Font.register({
      family: fontFamily,
      fonts: [
        { src: path.join(fontsDir, files.regular), fontWeight: "normal" },
        { src: path.join(fontsDir, files.bold), fontWeight: "bold" },
      ],
    });
    registeredFonts.add(fontFamily);
  } catch (error) {
    console.error(`Failed to register font ${fontFamily}:`, error);
    // Continue without custom font - it will fall back to defaults
  }
};

/**
 * Generate PDF buffer from resume data
 * This function must be called server-side only
 */
export const generatePDFBuffer = async (
  resume: Resume,
  template = "default",
  settings?: GeneratePDFSettings
) => {
  if (!resume) {
    throw new Error("Resume data is required");
  }

  if (template !== "default") {
    throw new Error(`Unsupported template: ${template}`);
  }

  try {
    // Import here to ensure it runs in Node.js environment
    const { renderToBuffer } = await import("@react-pdf/renderer");
    const { initialSettings } = await import("lib/redux/settingsSlice");
    const { ResumePDF } = await import("components/Resume/ResumePDF");

    // Build final settings
    const mergedSettings = {
      ...initialSettings,
      ...settings,
    };

    // Register custom fonts
    await registerFontFamily(mergedSettings.fontFamily);

    // Create the PDF document element
    const pdfElement = React.createElement(ResumePDF, {
      resume,
      settings: mergedSettings,
      isPDF: true,
    });

    // Render to buffer - use type assertion since ResumePDF returns Document
    const pdfBuffer = await (renderToBuffer as any)(pdfElement);

    if (!Buffer.isBuffer(pdfBuffer)) {
      throw new Error("PDF generation failed: renderToBuffer did not return a Buffer");
    }

    return pdfBuffer;
  } catch (error) {
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Unknown error during PDF generation";
    const errorStack =
      error instanceof Error
        ? error.stack
        : "No stack trace available";

    console.error("PDF generation failed:", {
      message: errorMessage,
      stack: errorStack,
    });

    // Re-throw with additional context
    throw new Error(
      `PDF generation failed: ${errorMessage}`,
      { cause: error }
    );
  }
};
