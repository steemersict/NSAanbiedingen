"""PDF generation using WeasyPrint."""

import logging
from pathlib import Path
from typing import Optional

from weasyprint import HTML, CSS

from .models import GeneratePDFRequest

logger = logging.getLogger(__name__)


def generate_pdf(request: GeneratePDFRequest, output_path: Path) -> bool:
    """
    Generate PDF from folder data using WeasyPrint.

    Args:
        request: PDF generation request with folder data
        output_path: Path where the PDF should be saved

    Returns:
        bool: True if generation succeeded, False otherwise
    """
    try:
        html_content = _build_html_from_request(request)
        css_content = _build_css_for_pdf(request)

        # Create HTML document and apply CSS
        document = HTML(string=html_content)

        # Generate PDF
        document.write_pdf(
            target=str(output_path),
            stylesheets=[CSS(string=css_content)],
        )

        logger.info(f"PDF generated successfully: {output_path}")
        return True

    except Exception as e:
        logger.error(f"PDF Generation Error: {e}", exc_info=True)
        return False


def _build_html_from_request(request: GeneratePDFRequest) -> str:
    """
    Build HTML structure from folder data.

    Args:
        request: PDF generation request

    Returns:
        str: HTML content as string
    """
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='UTF-8'>",
        f"<title>{request.output_filename}</title>",
        "</head>",
        "<body>",
    ]

    for page in request.pages:
        # Page wrapper
        page_class = f"page {page.layout}"
        bg_style = f"background-color: {page.background_color};" if page.background_color else ""
        html_parts.append(f'<div class="{page_class}" style="{bg_style}">')

        # Page title
        if page.title:
            html_parts.append(f"<h1 class='page-title'>{page.title}</h1>")

        # Products container
        html_parts.append(f'<div class="products {page.layout}-layout">')

        for product in page.products:
            html_parts.append(_build_product_html(product))

        html_parts.append("</div>")  # Close products container
        html_parts.append("</div>")  # Close page

    html_parts.extend(["</body>", "</html>"])

    return "\n".join(html_parts)


def _build_product_html(product) -> str:
    """Build HTML for a single product."""
    html = '<div class="product-card">'

    # Product image
    if product.image_url:
        html += f'<img src="{product.image_url}" alt="{product.name}" class="product-image">'

    # Product info
    html += '<div class="product-info">'
    html += f"<h2 class='product-name'>{product.name}</h2>"

    if product.description:
        html += f"<p class='product-description'>{product.description}</p>"

    if product.price:
        html += f"<p class='product-price'>€ {product.price:.2f}</p>"

    if product.quantity > 1:
        html += f"<p class='product-quantity'>Qty: {product.quantity}</p>"

    html += "</div>"  # Close product-info
    html += "</div>"  # Close product-card

    return html


def _build_css_for_pdf(request: GeneratePDFRequest) -> str:
    """
    Build CSS for PDF styling.

    Args:
        request: PDF generation request (contains layout and sizing info)

    Returns:
        str: CSS content as string
    """
    # Orientation settings
    page_width = "210mm" if request.orientation == "portrait" else "297mm"
    page_height = "297mm" if request.orientation == "portrait" else "210mm"

    css = f"""
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    @page {{
        size: {page_width} {page_height};
        margin: 20mm;
        @bottom-center {{
            content: "Page " counter(page) " of " counter(pages);
            font-size: 10pt;
            color: #666;
        }}
    }}

    html, body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
        color: #333;
        background: white;
    }}

    .page {{
        page-break-after: always;
        padding: 20px;
        min-height: 100vh;
    }}

    .page-title {{
        font-size: 28pt;
        font-weight: bold;
        margin-bottom: 20px;
        color: #000;
    }}

    .products {{
        display: flex;
        gap: 20px;
    }}

    .grid-layout {{
        flex-wrap: wrap;
    }}

    .list-layout {{
        flex-direction: column;
    }}

    .featured-layout {{
        flex-direction: column;
    }}

    .product-card {{
        flex: 1;
        min-width: 150px;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 4px;
        break-inside: avoid;
    }}

    .product-image {{
        width: 100%;
        max-height: 200px;
        object-fit: contain;
        margin-bottom: 10px;
    }}

    .product-info {{
        padding: 5px;
    }}

    .product-name {{
        font-size: 14pt;
        font-weight: 600;
        margin-bottom: 5px;
    }}

    .product-description {{
        font-size: 10pt;
        color: #666;
        margin-bottom: 8px;
        line-height: 1.4;
    }}

    .product-price {{
        font-size: 12pt;
        font-weight: bold;
        color: #0066cc;
        margin-bottom: 5px;
    }}

    .product-quantity {{
        font-size: 10pt;
        color: #999;
    }}

    /* Print-specific styles */
    @media print {{
        body {{
            background: white;
        }}
    }}
    """

    return css
