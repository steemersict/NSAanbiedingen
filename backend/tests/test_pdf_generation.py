"""Tests for PDF generation functionality."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.server import app
from src.models import FolderPage, GeneratePDFRequest, Product


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "nsaanbiedingen-backend"


def test_generate_pdf_basic(client):
    """Test basic PDF generation with one product."""
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "title": "Featured Products",
                "products": [
                    {
                        "id": "prod-001",
                        "name": "Test Product",
                        "price": 99.99,
                        "description": "A test product",
                    }
                ],
                "layout": "grid",
            }
        ],
        "output_filename": "test.pdf",
        "color_mode": "RGB",
        "dpi": 150,
    }

    response = client.post("/api/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "job_id" in data
    assert data["file_size_kb"] is not None
    assert data["file_size_kb"] > 0


def test_generate_pdf_multi_page(client):
    """Test PDF generation with multiple pages."""
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "title": "Page 1 - Featured",
                "products": [
                    {
                        "id": "prod-001",
                        "name": "Product 1",
                        "price": 50.00,
                    },
                    {
                        "id": "prod-002",
                        "name": "Product 2",
                        "price": 75.00,
                    },
                ],
                "layout": "grid",
            },
            {
                "page_number": 2,
                "title": "Page 2 - Additional Offers",
                "products": [
                    {
                        "id": "prod-003",
                        "name": "Product 3",
                        "price": 150.00,
                        "description": "Premium product",
                    }
                ],
                "layout": "list",
            },
        ],
        "output_filename": "multi_page.pdf",
    }

    response = client.post("/api/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_size_kb"] > 0


def test_generate_pdf_cmyk(client):
    """Test PDF generation with CMYK color mode."""
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "title": "CMYK Test",
                "products": [
                    {
                        "id": "prod-001",
                        "name": "CMYK Product",
                        "price": 199.99,
                    }
                ],
                "layout": "featured",
            }
        ],
        "output_filename": "cmyk_test.pdf",
        "color_mode": "CMYK",
    }

    response = client.post("/api/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_generate_pdf_landscape(client):
    """Test PDF generation with landscape orientation."""
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "title": "Landscape Page",
                "products": [
                    {"id": "prod-001", "name": "Landscape Product", "price": 299.99}
                ],
                "layout": "grid",
            }
        ],
        "orientation": "landscape",
    }

    response = client.post("/api/generate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_download_pdf_success(client):
    """Test successful PDF download after generation."""
    # First generate a PDF
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "products": [{"id": "prod-001", "name": "Download Test", "price": 49.99}],
            }
        ],
    }

    gen_response = client.post("/api/generate", json=request_data)
    assert gen_response.status_code == 200
    job_id = gen_response.json()["job_id"]

    # Now try to download it
    download_response = client.get(f"/api/download/{job_id}")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"
    assert len(download_response.content) > 0


def test_download_pdf_not_found(client):
    """Test downloading non-existent PDF."""
    response = client.get("/api/download/nonexistent-job-id")
    assert response.status_code == 404


def test_job_status(client):
    """Test checking job status."""
    # Generate a PDF
    request_data = {
        "pages": [
            {
                "page_number": 1,
                "products": [{"id": "prod-001", "name": "Status Test", "price": 79.99}],
            }
        ],
    }

    gen_response = client.post("/api/generate", json=request_data)
    job_id = gen_response.json()["job_id"]

    # Check status
    status_response = client.get(f"/api/status/{job_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "completed"
    assert data["size_kb"] > 0


def test_invalid_request(client):
    """Test with invalid request data."""
    # Empty pages list
    request_data = {
        "pages": [],
    }

    response = client.post("/api/generate", json=request_data)
    # The endpoint should still accept empty pages but generate a minimal PDF
    assert response.status_code in [200, 422]


def test_list_jobs(client):
    """Test listing all jobs."""
    # Generate a few PDFs
    for i in range(3):
        request_data = {
            "pages": [
                {
                    "page_number": 1,
                    "products": [{"id": f"prod-{i}", "name": f"Product {i}", "price": 99.99}],
                }
            ],
        }
        client.post("/api/generate", json=request_data)

    # List jobs
    response = client.get("/api/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3


def test_port_discovery():
    """Test that port discovery utilities work."""
    from src.utils import get_free_port

    port1 = get_free_port()
    port2 = get_free_port()

    assert isinstance(port1, int)
    assert isinstance(port2, int)
    assert port1 > 1024
    assert port2 > 1024
