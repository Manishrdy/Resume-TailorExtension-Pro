import { NextRequest, NextResponse } from "next/server";

/**
 * GET /api/health
 * Health check endpoint for Open Resume service
 */
export async function GET(request: NextRequest) {
  try {
    return NextResponse.json(
      {
        status: "healthy",
        service: "open-resume",
        timestamp: new Date().toISOString(),
        version: "1.0.0",
      },
      { status: 200 }
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        service: "open-resume",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
