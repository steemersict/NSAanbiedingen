/**
 * Nano Stores for backend connection state
 * Framework-agnostic state management for Tauri integration
 */

import { atom } from "nanostores";

// Backend connection state
export const backendPort = atom<number | null>(null);
export const backendStatus = atom<"loading" | "connected" | "error">(
  "loading"
);
export const backendError = atom<string | null>(null);

// Folder data state
export interface Product {
  id: string;
  name: string;
  price?: number;
  description?: string;
  image_url?: string;
  quantity?: number;
}

export interface FolderPage {
  page_number: number;
  title?: string;
  products: Product[];
  layout: "grid" | "list" | "featured";
  background_color?: string;
}

export interface PDFSettings {
  output_filename: string;
  color_mode: "RGB" | "CMYK";
  dpi: number;
  orientation: "portrait" | "landscape";
}

export const pages = atom<FolderPage[]>([
  {
    page_number: 1,
    title: "Featured Products",
    products: [],
    layout: "grid",
  },
]);

export const pdfSettings = atom<PDFSettings>({
  output_filename: "aanbieding.pdf",
  color_mode: "RGB",
  dpi: 300,
  orientation: "portrait",
});

// Current job status
export interface PDFJob {
  job_id: string;
  status: "generating" | "completed" | "failed";
  size_kb?: number;
  error?: string;
}

export const currentJob = atom<PDFJob | null>(null);
export const jobHistory = atom<PDFJob[]>([]);

// Helper functions
export function addProduct(
  pageNumber: number,
  product: Product
): void {
  pages.set(
    pages.get().map((page) =>
      page.page_number === pageNumber
        ? { ...page, products: [...page.products, product] }
        : page
    )
  );
}

export function removeProduct(pageNumber: number, productId: string): void {
  pages.set(
    pages.get().map((page) =>
      page.page_number === pageNumber
        ? {
            ...page,
            products: page.products.filter((p) => p.id !== productId),
          }
        : page
    )
  );
}

export function updatePage(
  pageNumber: number,
  updates: Partial<FolderPage>
): void {
  pages.set(
    pages.get().map((page) =>
      page.page_number === pageNumber ? { ...page, ...updates } : page
    )
  );
}

export function addPage(): void {
  const currentPages = pages.get();
  const newPageNumber = Math.max(...currentPages.map((p) => p.page_number)) + 1;
  pages.set([
    ...currentPages,
    {
      page_number: newPageNumber,
      title: `Page ${newPageNumber}`,
      products: [],
      layout: "grid",
    },
  ]);
}

export function removePage(pageNumber: number): void {
  const currentPages = pages.get();
  if (currentPages.length > 1) {
    pages.set(currentPages.filter((p) => p.page_number !== pageNumber));
  }
}
