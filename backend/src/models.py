"""Pydantic models for API request/response validation."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    """Represents a product in a folder page."""

    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    price: Optional[float] = Field(None, description="Product price")
    description: Optional[str] = Field(None, description="Product description")
    image_url: Optional[str] = Field(None, description="URL or path to product image")
    quantity: int = Field(1, ge=1, description="Product quantity")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-001",
                "name": "Laptop Computer",
                "price": 999.99,
                "description": "Professional laptop with 16GB RAM",
                "image_url": "/images/laptop.jpg",
                "quantity": 1,
            }
        }


class FolderPage(BaseModel):
    """Represents a page in the offer folder."""

    page_number: int = Field(..., ge=1, description="Page number (1-based)")
    title: Optional[str] = Field(None, description="Page title")
    products: List[Product] = Field(default_factory=list, description="Products on this page")
    layout: str = Field(
        default="grid",
        description="Layout type (grid, list, or featured)",
        pattern="^(grid|list|featured)$",
    )
    background_color: Optional[str] = Field(
        default="white", description="Page background color (hex or color name)"
    )


class GeneratePDFRequest(BaseModel):
    """Request to generate a PDF from folder data."""

    pages: List[FolderPage] = Field(..., description="List of pages to include in PDF")
    output_filename: str = Field(
        default="aanbieding.pdf", description="Output PDF filename"
    )
    color_mode: str = Field(
        default="RGB",
        description="Color mode (RGB or CMYK)",
        pattern="^(RGB|CMYK)$",
    )
    dpi: int = Field(default=300, ge=72, le=600, description="DPI for PDF rendering")
    orientation: str = Field(
        default="portrait",
        description="Page orientation (portrait or landscape)",
        pattern="^(portrait|landscape)$",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pages": [
                    {
                        "page_number": 1,
                        "title": "Featured Products",
                        "products": [
                            {
                                "id": "prod-001",
                                "name": "Product A",
                                "price": 99.99,
                            }
                        ],
                        "layout": "grid",
                    }
                ],
                "output_filename": "Q4_Offering.pdf",
                "color_mode": "RGB",
                "dpi": 300,
                "orientation": "portrait",
            }
        }


class GeneratePDFResponse(BaseModel):
    """Response from PDF generation request."""

    success: bool = Field(..., description="Whether generation was successful")
    job_id: str = Field(..., description="Unique job identifier")
    message: str = Field(..., description="Status message")
    file_size_kb: Optional[int] = Field(None, description="Size of generated PDF in KB")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")


class ErrorResponse(BaseModel):
    """Error response format."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    job_id: Optional[str] = Field(None, description="Related job ID if applicable")
