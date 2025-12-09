/**
 * Main Editor Component for NSAanbiedingen
 * Interactive drag-and-drop editor for creating offer folders
 */

import React, { useState, useEffect } from "react";

interface Product {
  id: string;
  name: string;
  price?: number;
  description?: string;
}

interface Page {
  page_number: number;
  title?: string;
  products: Product[];
  layout: "grid" | "list" | "featured";
}

interface PDFSettings {
  output_filename: string;
  color_mode: "RGB" | "CMYK";
  orientation: "portrait" | "landscape";
  dpi: number;
}

interface Job {
  job_id: string;
  status: "generating" | "completed" | "failed";
  size_kb?: number;
  error?: string;
}

export default function Editor() {
  const [pages, setPages] = useState<Page[]>([
    {
      page_number: 1,
      title: "Cover",
      products: [],
      layout: "grid",
    },
  ]);
  const [port, setPort] = useState<number | null>(null);
  const [backendStatus, setBackendStatus] = useState<
    "loading" | "connected" | "error"
  >("loading");
  const [selectedPageIndex, setSelectedPageIndex] = useState(0);
  const [showProductForm, setShowProductForm] = useState(false);
  const [job, setJob] = useState<Job | null>(null);
  const [productForm, setProductForm] = useState({
    id: "",
    name: "",
    price: "",
    description: "",
  });
  const [settings, setSettings] = useState<PDFSettings>({
    output_filename: "offer_folder.pdf",
    color_mode: "RGB",
    orientation: "portrait",
    dpi: 300,
  });

  useEffect(() => {
    // Listen for backend-ready event from Layout.astro
    const handleBackendReady = (event: CustomEvent<{ port: number }>) => {
      const backendPort = event.detail.port;
      setPort(backendPort);
      setBackendStatus("connected");
      localStorage.setItem("backend-port", backendPort.toString());
      console.log("[Editor] Backend connected on port:", backendPort);
    };

    window.addEventListener("backend-ready", handleBackendReady as EventListener);

    // Check for backend port from localStorage (fallback)
    const storedPort = localStorage.getItem("backend-port");
    if (storedPort) {
      const portNum = parseInt(storedPort);
      // Verify the stored port is still valid
      fetch(`http://127.0.0.1:${portNum}/health`)
        .then((res) => {
          if (res.ok) {
            setPort(portNum);
            setBackendStatus("connected");
            console.log("[Editor] Backend connected on port:", portNum);
          } else {
            throw new Error("Backend not responding");
          }
        })
        .catch(() => {
          localStorage.removeItem("backend-port");
          setBackendStatus("loading");
          console.log("[Editor] Stored port invalid, waiting for backend...");
        });
    } else {
      setBackendStatus("loading");
      console.log("[Editor] Waiting for backend initialization...");
    }

    return () => {
      window.removeEventListener("backend-ready", handleBackendReady as EventListener);
    };
  }, []);

  const handleAddProduct = () => {
    if (!productForm.name.trim()) {
      alert("Product name is required");
      return;
    }

    const newProduct: Product = {
      id: productForm.id || `prod-${Date.now()}`,
      name: productForm.name,
      price: productForm.price ? parseFloat(productForm.price) : undefined,
      description: productForm.description || undefined,
    };

    const updatedPages = [...pages];
    updatedPages[selectedPageIndex].products.push(newProduct);
    setPages(updatedPages);

    // Reset form
    setProductForm({ id: "", name: "", price: "", description: "" });
    setShowProductForm(false);
  };

  const handleRemoveProduct = (productId: string) => {
    const updatedPages = [...pages];
    updatedPages[selectedPageIndex].products = updatedPages[
      selectedPageIndex
    ].products.filter((p) => p.id !== productId);
    setPages(updatedPages);
  };

  const handleAddPage = () => {
    const newPageNumber = Math.max(...pages.map((p) => p.page_number)) + 1;
    const newPage: Page = {
      page_number: newPageNumber,
      title: `Page ${newPageNumber}`,
      products: [],
      layout: "grid",
    };
    setPages([...pages, newPage]);
    setSelectedPageIndex(pages.length);
  };

  const handleUpdatePageTitle = (title: string) => {
    const updatedPages = [...pages];
    updatedPages[selectedPageIndex].title = title;
    setPages(updatedPages);
  };

  const handleUpdatePageLayout = (
    layout: "grid" | "list" | "featured"
  ) => {
    const updatedPages = [...pages];
    updatedPages[selectedPageIndex].layout = layout;
    setPages(updatedPages);
  };

  const handleGeneratePDF = async () => {
    if (!port) {
      alert("Backend is not ready. Please refresh the page.");
      return;
    }

    if (pages.length === 0 || pages.every((p) => p.products.length === 0)) {
      alert("Please add at least one product before generating PDF.");
      return;
    }

    try {
      setJob({
        job_id: "generating...",
        status: "generating",
      });

      const response = await fetch(`http://127.0.0.1:${port}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pages: pages,
          output_filename: settings.output_filename,
          color_mode: settings.color_mode,
          dpi: settings.dpi,
          orientation: settings.orientation,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        setJob({
          job_id: result.job_id,
          status: "completed",
          size_kb: result.file_size_kb,
        });

        // Auto-download after 1 second
        setTimeout(() => {
          handleDownloadPDF(result.job_id);
        }, 1000);
      } else {
        throw new Error(result.message || "PDF generation failed");
      }
    } catch (error) {
      console.error("[Editor] PDF generation error:", error);
      alert(
        `Failed to generate PDF: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      setJob({
        job_id: "error",
        status: "failed",
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  };

  const handleDownloadPDF = async (jobId: string) => {
    if (!port) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:${port}/api/download/${jobId}`
      );
      if (!response.ok) {
        throw new Error("Download failed");
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = settings.output_filename;
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error("[Editor] Download error:", error);
      alert("Failed to download PDF");
    }
  };

  const currentPage = pages[selectedPageIndex];

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-80 bg-white shadow-lg overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Editor</h2>

          {/* Backend Status */}
          <div className="mb-6 p-3 bg-gray-100 rounded-lg text-sm">
            <p className="font-semibold text-gray-700">Backend Status:</p>
            <p
              className={`mt-1 ${
                backendStatus === "connected"
                  ? "text-green-600"
                  : backendStatus === "error"
                    ? "text-red-600"
                    : "text-yellow-600"
              }`}
            >
              {backendStatus === "connected"
                ? `✓ Connected (port ${port})`
                : backendStatus === "error"
                  ? "✗ Connection failed"
                  : "⏳ Loading..."}
            </p>
          </div>

          {/* Pages Section */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Pages</h3>
            <div className="space-y-2 mb-3">
              {pages.map((page, idx) => (
                <button
                  key={page.page_number}
                  onClick={() => setSelectedPageIndex(idx)}
                  className={`w-full text-left px-3 py-2 rounded transition-colors ${
                    idx === selectedPageIndex
                      ? "bg-blue-500 text-white"
                      : "bg-gray-100 text-gray-900 hover:bg-gray-200"
                  }`}
                >
                  <span className="font-semibold">
                    {page.title || `Page ${page.page_number}`}
                  </span>
                  <span className="text-sm opacity-75 ml-2">
                    ({page.products.length} products)
                  </span>
                </button>
              ))}
            </div>
            <button
              onClick={handleAddPage}
              className="w-full px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors text-sm font-medium"
            >
              + Add Page
            </button>
          </div>

          {/* Page Settings */}
          {currentPage && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Page Settings
              </h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Page Title
                  </label>
                  <input
                    type="text"
                    value={currentPage.title || ""}
                    onChange={(e) => handleUpdatePageTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Layout
                  </label>
                  <select
                    value={currentPage.layout}
                    onChange={(e) =>
                      handleUpdatePageLayout(
                        e.target.value as "grid" | "list" | "featured"
                      )
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  >
                    <option value="grid">Grid</option>
                    <option value="list">List</option>
                    <option value="featured">Featured</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* PDF Settings */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              PDF Settings
            </h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Color Mode
                </label>
                <select
                  value={settings.color_mode}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      color_mode: e.target.value as "RGB" | "CMYK",
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                >
                  <option value="RGB">RGB</option>
                  <option value="CMYK">CMYK (Print)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Orientation
                </label>
                <select
                  value={settings.orientation}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      orientation: e.target.value as
                        | "portrait"
                        | "landscape",
                    })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                >
                  <option value="portrait">Portrait</option>
                  <option value="landscape">Landscape</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  DPI Resolution
                </label>
                <input
                  type="number"
                  value={settings.dpi}
                  onChange={(e) =>
                    setSettings({ ...settings, dpi: parseInt(e.target.value) })
                  }
                  min="72"
                  max="600"
                  className="w-full px-3 py-2 border border-gray-300 rounded"
                />
              </div>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGeneratePDF}
            disabled={job?.status === "generating"}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {job?.status === "generating" ? "Generating PDF..." : "Generate PDF"}
          </button>

          {job && job.status === "completed" && (
            <div className="mt-4 p-4 bg-green-100 text-green-800 rounded">
              <p className="text-sm font-medium">
                ✓ PDF Generated ({job.size_kb} KB)
              </p>
              <button
                onClick={() => handleDownloadPDF(job.job_id)}
                className="w-full mt-2 px-3 py-2 bg-green-600 text-white rounded text-sm font-medium hover:bg-green-700"
              >
                Download PDF
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-md p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {currentPage?.title || `Page ${currentPage?.page_number}`}
              </h2>

              {/* Add Product Form */}
              {!showProductForm ? (
                <button
                  onClick={() => setShowProductForm(true)}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  + Add Product
                </button>
              ) : (
                <div className="bg-gray-50 p-6 rounded-lg mb-6">
                  <h3 className="text-lg font-semibold mb-4">Add Product</h3>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <input
                      type="text"
                      placeholder="Product Name *"
                      value={productForm.name}
                      onChange={(e) =>
                        setProductForm({
                          ...productForm,
                          name: e.target.value,
                        })
                      }
                      className="px-3 py-2 border border-gray-300 rounded"
                    />
                    <input
                      type="number"
                      placeholder="Price"
                      value={productForm.price}
                      onChange={(e) =>
                        setProductForm({
                          ...productForm,
                          price: e.target.value,
                        })
                      }
                      className="px-3 py-2 border border-gray-300 rounded"
                    />
                  </div>
                  <textarea
                    placeholder="Description"
                    value={productForm.description}
                    onChange={(e) =>
                      setProductForm({
                        ...productForm,
                        description: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded mb-4"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={handleAddProduct}
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                    >
                      Add
                    </button>
                    <button
                      onClick={() => setShowProductForm(false)}
                      className="px-4 py-2 bg-gray-400 text-white rounded hover:bg-gray-500"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}

              {/* Products List */}
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">
                  Products on this page
                </h3>
                {currentPage?.products && currentPage.products.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {currentPage.products.map((product) => (
                      <div
                        key={product.id}
                        className="p-4 border border-gray-300 rounded-lg bg-gray-50"
                      >
                        <h4 className="font-semibold text-gray-900">
                          {product.name}
                        </h4>
                        {product.price && (
                          <p className="text-blue-600 font-bold">
                            € {product.price.toFixed(2)}
                          </p>
                        )}
                        {product.description && (
                          <p className="text-sm text-gray-600 mt-2">
                            {product.description}
                          </p>
                        )}
                        <button
                          onClick={() => handleRemoveProduct(product.id)}
                          className="mt-3 px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No products added yet.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
