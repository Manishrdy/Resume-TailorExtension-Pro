import path from "path";

/**
 * Wrapper for PDF generation that ensures server-side execution
 * This delegates to pdf-generator-server which is marked with "use server"
 */
export const generatePDF = async (
  resume: any,
  template = "default",
  settings?: any
) => {
  // Dynamically import the server-side generator to avoid bundling @react-pdf/renderer on client
  const { generatePDFBuffer } = await import("./pdf-generator-server");
  return generatePDFBuffer(resume, template, settings);
};
