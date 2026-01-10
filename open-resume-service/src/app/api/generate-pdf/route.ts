import { NextRequest, NextResponse } from "next/server";

/**
 * POST /api/generate-pdf
 * 
 * Generate a PDF from resume JSON using open-resume internals
 * 
 * Request body:
 * {
 *   "resume": { ... resume data ... },
 *   "template": "default",  // optional
 *   "settings": { ... pdf settings ... }  // optional
 * }
 * 
 * Response: PDF file or error JSON
 */
export async function POST(request: NextRequest) {
  let body: any = null;
  const startTime = Date.now();

  try {
    // Validate request
    const contentType = request.headers.get("content-type");
    if (!contentType?.includes("application/json")) {
      return NextResponse.json(
        { error: "Content-Type must be application/json" },
        { status: 400 }
      );
    }

    // Parse request body
    body = await request.json();
    const { resume, template = "default", settings } = body;

    // Validate resume data
    if (!resume || typeof resume !== "object") {
      return NextResponse.json(
        {
          error: "Invalid request",
          message: "Resume data is required and must be a valid object",
        },
        { status: 400 }
      );
    }

    // Validate template
    if (template !== "default") {
      return NextResponse.json(
        {
          error: "Unsupported template",
          message: `Template "${template}" is not supported. Use "default"`,
        },
        { status: 400 }
      );
    }

    // Import and call PDF generation
    // Using dynamic import to ensure it runs in server context
    const { generatePDF } = await import("../../lib/resume-pdf-generator");

    const pdfBuffer = await generatePDF(resume, template, settings);

    // Validate PDF buffer
    if (!Buffer.isBuffer(pdfBuffer) || pdfBuffer.length === 0) {
      throw new Error("PDF generation returned invalid data");
    }

    const generationTime = Date.now() - startTime;

    // Return PDF as binary response
    return new NextResponse(pdfBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": 'attachment; filename="resume.pdf"',
        "Content-Length": pdfBuffer.length.toString(),
        "X-Generation-Time-Ms": generationTime.toString(),
        "Cache-Control": "no-cache, no-store, must-revalidate",
      },
    });
  } catch (error) {
    const generationTime = Date.now() - startTime;

    // Enhanced error logging
    const errorMessage =
      error instanceof Error ? error.message : String(error);
    const errorStack = error instanceof Error ? error.stack : "No stack trace";

    console.error("PDF generation error:", {
      timestamp: new Date().toISOString(),
      message: errorMessage,
      stack: errorStack,
      generationTime,
      bodySummary: body
        ? {
            hasProfile: !!body.resume?.profile,
            hasWorkExperiences: Array.isArray(
              body.resume?.workExperiences
            ),
            hasEducations: Array.isArray(body.resume?.educations),
            hasProjects: Array.isArray(body.resume?.projects),
            hasSkills: !!body.resume?.skills,
          }
        : null,
    });

    // Return error response
    return NextResponse.json(
      {
        error: "PDF generation failed",
        message: errorMessage,
        ...(process.env.NODE_ENV === "development" && {
          stack: errorStack,
          cause: error instanceof Error && error.cause ? String(error.cause) : undefined,
        }),
      },
      { status: 500 }
    );
  }
}
