#!/usr/bin/env node

/**
 * Binary Renaming Script for Tauri Sidecar
 *
 * Renames PyInstaller-generated binaries to include target triple
 * for Tauri v2 sidecar pattern.
 *
 * Usage: node scripts/rename-sidecar.js
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

console.log("[Sidecar] Starting binary rename process...");

// Get Rust target triple
let targetTriple = "";
try {
  const rustcOutput = execSync("rustc -vV", { encoding: "utf-8" });
  const targetMatch = rustcOutput.match(/host: (.+)/);
  if (targetMatch) {
    targetTriple = targetMatch[1].trim();
    console.log(`[Sidecar] Detected target triple: ${targetTriple}`);
  } else {
    console.error("[Sidecar] Failed to parse rustc output");
    process.exit(1);
  }
} catch (error) {
  console.error("[Sidecar] Failed to run rustc:", error.message);
  process.exit(1);
}

// Platform-specific binary names
const platform = process.platform;
const binaryExt = platform === "win32" ? ".exe" : "";
const sourceName = `backend${binaryExt}`;
const targetName = `backend-${targetTriple}${binaryExt}`;

// Paths
const projectRoot = path.join(__dirname, "..");
const distPath = path.join(projectRoot, "backend", "dist", "backend", sourceName);
const targetDir = path.join(projectRoot, "src-tauri", "binaries");
const targetPath = path.join(targetDir, targetName);

console.log(`[Sidecar] Source: ${distPath}`);
console.log(`[Sidecar] Target: ${targetPath}`);

// Verify source exists
if (!fs.existsSync(distPath)) {
  console.error(`[Sidecar] ERROR: Source binary not found at: ${distPath}`);
  console.error("[Sidecar] Did you run 'npm run build:backend' first?");
  process.exit(1);
}

// Create target directory if needed
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
  console.log(`[Sidecar] Created directory: ${targetDir}`);
}

// Copy binary to target location with target triple in name
try {
  // Remove old binary if exists
  if (fs.existsSync(targetPath)) {
    fs.unlinkSync(targetPath);
    console.log(`[Sidecar] Removed old binary: ${targetName}`);
  }

  // Copy binary
  fs.copyFileSync(distPath, targetPath);

  // Make executable on Unix-like systems
  if (platform !== "win32") {
    fs.chmodSync(targetPath, 0o755);
  }

  const stats = fs.statSync(targetPath);
  const sizeMB = (stats.size / 1024 / 1024).toFixed(2);

  console.log(`[Sidecar] ✓ Successfully renamed sidecar binary`);
  console.log(`[Sidecar]   Binary: ${targetName}`);
  console.log(`[Sidecar]   Size: ${sizeMB} MB`);
  console.log(`[Sidecar]   Location: src-tauri/binaries/`);
} catch (error) {
  console.error(`[Sidecar] ERROR: Failed to copy binary:`, error.message);
  process.exit(1);
}

console.log("[Sidecar] ✓ Rename process completed successfully");
