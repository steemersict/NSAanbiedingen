"""FastAPI server for NSAanbiedingen backend."""

import logging
import uuid
from pathlib import Path
from typing import Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from .models import ErrorResponse, GeneratePDFRequest, GeneratePDFResponse, HealthResponse
    from .pdf_generator import generate_pdf
    from .utils import announce_port, cleanup_temp_files, get_free_port, get_temp_pdf_dir
except ImportError:
    from models import ErrorResponse, GeneratePDFRequest, GeneratePDFResponse, HealthResponse
    from pdf_generator import generate_pdf
    from utils import announce_port, cleanup_temp_files, get_free_port, get_temp_pdf_dir

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NSAanbiedingen Backend",
    description="PDF generation service for offer folders",
    version="0.1.0",
)

# Add CORS middleware for browser dev mode
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321", "http://127.0.0.1:4321", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store PDF generation jobs in memory (in production, use a proper queue)
jobs: Dict[str, dict] = {}


@app.on_event("startup")
async def startup_event():
    """Called when server starts up."""
    logger.info("NSAanbiedingen backend starting up...")
    cleanup_temp_files()  # Clean up old PDFs on startup


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Rust to verify backend is ready."""
    return HealthResponse(
        status="ok",
        service="nsaanbiedingen-backend",
        version="0.1.0",
    )


@app.post("/api/generate", response_model=GeneratePDFResponse)
async def generate_pdf_endpoint(request: GeneratePDFRequest):
    """
    Start PDF generation job.

    Args:
        request: PDF generation request with folder data

    Returns:
        GeneratePDFResponse: Job status and ID
    """
    try:
        job_id = str(uuid.uuid4())
        temp_dir = get_temp_pdf_dir()
        output_path = temp_dir / f"{job_id}.pdf"

        logger.info(f"Starting PDF generation job {job_id}")

        # Generate PDF
        success = generate_pdf(request, output_path)

        # Store job info
        if success and output_path.exists():
            file_size_kb = output_path.stat().st_size // 1024
            jobs[job_id] = {
                "status": "completed",
                "path": output_path,
                "size_kb": file_size_kb,
            }
            logger.info(f"PDF job {job_id} completed ({file_size_kb} KB)")
            return GeneratePDFResponse(
                success=True,
                job_id=job_id,
                message="PDF generated successfully",
                file_size_kb=file_size_kb,
            )
        else:
            jobs[job_id] = {"status": "failed", "path": None}
            logger.error(f"PDF job {job_id} failed during generation")
            return GeneratePDFResponse(
                success=False,
                job_id=job_id,
                message="PDF generation failed",
            )

    except Exception as e:
        logger.error(f"Error in PDF generation: {e}", exc_info=True)
        return GeneratePDFResponse(
            success=False,
            job_id="unknown",
            message=f"Server error: {str(e)}",
        )


@app.get("/api/download/{job_id}")
async def download_pdf(job_id: str):
    """
    Download generated PDF.

    Args:
        job_id: The job ID from generation request

    Returns:
        FileResponse: The PDF file

    Raises:
        HTTPException: If job not found or not completed
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error="Job not found", job_id=job_id).dict(),
        )

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error="Job not completed",
                detail=f"Status: {job['status']}",
                job_id=job_id,
            ).dict(),
        )

    file_path = job["path"]
    if not file_path or not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(error="PDF file not found", job_id=job_id).dict(),
        )

    logger.info(f"Downloading PDF for job {job_id}")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="aanbieding.pdf",
    )


@app.get("/api/status/{job_id}")
async def job_status(job_id: str):
    """
    Check status of a PDF generation job.

    Args:
        job_id: The job ID

    Returns:
        dict: Job status information
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "size_kb": job.get("size_kb"),
    }


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs (for debugging only)."""
    return {
        "total": len(jobs),
        "jobs": [
            {
                "job_id": jid,
                "status": job["status"],
                "size_kb": job.get("size_kb"),
            }
            for jid, job in jobs.items()
        ],
    }


@app.delete("/api/cleanup")
async def cleanup_jobs():
    """Clean up completed jobs (for debugging/maintenance)."""
    before = len(jobs)
    # Keep only last 10 jobs
    if len(jobs) > 10:
        job_ids = list(jobs.keys())
        for job_id in job_ids[:-10]:
            if jobs[job_id]["status"] == "completed":
                try:
                    path = jobs[job_id].get("path")
                    if path and path.exists():
                        path.unlink()
                    del jobs[job_id]
                except Exception as e:
                    logger.error(f"Error cleaning up job {job_id}: {e}")
    return {"jobs_before": before, "jobs_after": len(jobs)}


def main():
    """Entry point for the backend server."""
    port = get_free_port()
    announce_port(port)

    logger.info(f"Starting Uvicorn server on http://127.0.0.1:{port}")

    # Uvicorn configuration for sidecar mode
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
