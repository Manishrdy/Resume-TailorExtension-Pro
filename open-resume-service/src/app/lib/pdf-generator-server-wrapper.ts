/**
 * This file ensures @react-pdf/renderer is only imported server-side
 * Adding "use server" prevents this module from being bundled on the client
 */
"use server";

export { generatePDFBuffer } from "./pdf-generator-server";
