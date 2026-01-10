/**
 * This file ensures @react-pdf/renderer is only imported server-side
 * Re-exports the PDF generation function for use in API routes
 */
export { generatePDFBuffer } from "./pdf-generator-server";
