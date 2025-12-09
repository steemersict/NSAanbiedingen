"""PDF generation using fpdf2 (pure Python, no GTK dependencies)."""

import logging
from pathlib import Path
from typing import Optional

from fpdf import FPDF
from fpdf.enums import XPos, YPos

try:
    from .models import GeneratePDFRequest
except ImportError:
    from models import GeneratePDFRequest

logger = logging.getLogger(__name__)

# Euro symbol for non-unicode fonts
EURO = "EUR"


class FolderPDF(FPDF):
    """Custom PDF class for offer folders."""

    def __init__(self, orientation: str = "portrait"):
        super().__init__(orientation=orientation.upper()[0], unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Add page header."""
        pass  # Can be customized later

    def footer(self):
        """Add page footer with page numbers."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")


def generate_pdf(request: GeneratePDFRequest, output_path: Path) -> bool:
    """
    Generate PDF from folder data using fpdf2.

    Args:
        request: PDF generation request with folder data
        output_path: Path where the PDF should be saved

    Returns:
        bool: True if generation succeeded, False otherwise
    """
    try:
        # Create PDF with correct orientation
        pdf = FolderPDF(orientation=request.orientation)
        pdf.alias_nb_pages()

        for page in request.pages:
            pdf.add_page()

            # Set background color if specified
            if page.background_color and page.background_color != "#ffffff":
                _draw_background(pdf, page.background_color)

            # Page title
            if page.title:
                pdf.set_font("Helvetica", "B", 24)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 15, page.title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
                pdf.ln(5)

            # Render products based on layout
            if page.layout == "grid":
                _render_grid_layout(pdf, page.products)
            elif page.layout == "list":
                _render_list_layout(pdf, page.products)
            elif page.layout == "featured":
                _render_featured_layout(pdf, page.products)
            else:
                _render_grid_layout(pdf, page.products)

        # Save PDF
        pdf.output(str(output_path))
        logger.info(f"PDF generated successfully: {output_path}")
        return True

    except Exception as e:
        logger.error(f"PDF Generation Error: {e}", exc_info=True)
        return False


def _draw_background(pdf: FPDF, color: str):
    """Draw background color on current page."""
    try:
        # Parse hex color
        color = color.lstrip("#")
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        pdf.set_fill_color(r, g, b)
        pdf.rect(0, 0, pdf.w, pdf.h, "F")
    except Exception as e:
        logger.warning(f"Could not draw background: {e}")


def _render_grid_layout(pdf: FPDF, products):
    """Render products in a grid layout (2 columns)."""
    if not products:
        return

    cols = 2
    col_width = (pdf.w - 30) / cols  # 15mm margin each side
    row_height = 60

    start_x = 15
    start_y = pdf.get_y()

    for i, product in enumerate(products):
        col = i % cols
        row = i // cols

        x = start_x + (col * col_width)
        y = start_y + (row * row_height)

        # Check if we need a new page
        if y + row_height > pdf.h - 20:
            pdf.add_page()
            start_y = pdf.get_y()
            y = start_y + ((i // cols - (i // cols)) * row_height)

        _render_product_card(pdf, product, x, y, col_width - 5, row_height - 5)


def _render_list_layout(pdf: FPDF, products):
    """Render products in a list layout (full width)."""
    if not products:
        return

    card_width = pdf.w - 30
    card_height = 35

    for product in products:
        # Check if we need a new page
        if pdf.get_y() + card_height > pdf.h - 20:
            pdf.add_page()

        _render_product_card(pdf, product, 15, pdf.get_y(), card_width, card_height)
        pdf.ln(card_height + 5)


def _render_featured_layout(pdf: FPDF, products):
    """Render products in featured layout (first product large, rest in grid)."""
    if not products:
        return

    # First product - featured (large)
    if len(products) >= 1:
        featured = products[0]
        _render_product_card(pdf, featured, 15, pdf.get_y(), pdf.w - 30, 80)
        pdf.ln(85)

    # Rest in grid
    if len(products) > 1:
        _render_grid_layout(pdf, products[1:])


def _render_product_card(pdf: FPDF, product, x: float, y: float, width: float, height: float):
    """Render a single product card."""
    # Card border
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.3)
    pdf.rect(x, y, width, height)

    # Product name
    pdf.set_xy(x + 3, y + 3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)

    # Truncate name if too long
    name = product.name
    if len(name) > 30:
        name = name[:27] + "..."
    pdf.cell(width - 6, 8, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Product description
    if product.description:
        pdf.set_xy(x + 3, y + 12)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)

        # Truncate description
        desc = product.description
        if len(desc) > 60:
            desc = desc[:57] + "..."
        pdf.multi_cell(width - 6, 5, desc)

    # Price (use EUR instead of € for font compatibility)
    if product.price:
        pdf.set_xy(x + 3, y + height - 12)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(width - 6, 8, f"{EURO} {product.price:.2f}")

    # Quantity if > 1
    if product.quantity > 1:
        pdf.set_xy(x + width - 25, y + height - 12)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(22, 8, f"x{product.quantity}", align="R")
