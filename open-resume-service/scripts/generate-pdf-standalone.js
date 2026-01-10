#!/usr/bin/env node
/**
 * Standalone PDF generator script
 * This runs in a separate process to avoid Next.js webpack bundling issues
 */

const React = require('react');
const { renderToBuffer, Font } = require('@react-pdf/renderer');
const path = require('path');
const fs = require('fs');

// Read input from stdin or file
async function main() {
  try {
    const inputData = process.argv[2]
      ? JSON.parse(fs.readFileSync(process.argv[2], 'utf-8'))
      : JSON.parse(fs.readFileSync(0, 'utf-8')); // stdin

    const { resume, settings, template = 'default' } = inputData;

    if (!resume) {
      throw new Error('Resume data is required');
    }

    // Register fonts
    const FONT_FILES = {
      'Open Sans': {
        regular: 'OpenSans-Regular.ttf',
        bold: 'OpenSans-Bold.ttf',
      },
      Roboto: {
        regular: 'Roboto-Regular.ttf',
        bold: 'Roboto-Bold.ttf',
      },
      Lato: {
        regular: 'Lato-Regular.ttf',
        bold: 'Lato-Bold.ttf',
      },
    };

    const fontFamily = settings?.fontFamily || 'Open Sans';
    const files = FONT_FILES[fontFamily];

    if (files) {
      const fontsDir = path.join(process.cwd(), 'public', 'fonts');
      Font.register({
        family: fontFamily,
        fonts: [
          { src: path.join(fontsDir, files.regular), fontWeight: 'normal' },
          { src: path.join(fontsDir, files.bold), fontWeight: 'bold' },
        ],
      });
    }

    // Dynamically require the ResumePDF component
    // We can't use import here because this needs to run in Node.js context
    const modulePath = path.join(
      __dirname,
      '../dist/server/app/components/Resume/ResumePDF/index.js'
    );

    console.error('This standalone script approach requires building Next.js first');
    console.error('Using direct import approach instead...');
    process.exit(1);
  } catch (error) {
    console.error('PDF generation error:', error);
    process.exit(1);
  }
}

main();
