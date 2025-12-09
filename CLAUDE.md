# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Identity

**NSAanbiedingen** is a hybrid desktop application for generating professional PDF offer folders (aanbiedingenfolders) with visual drag-and-drop editing and print-ready output.

- **Frontend:** Astro (Static Site Generator with React island for the editor), TypeScript, TailwindCSS, Nano Stores
- **Backend:** Python 3.9+, FastAPI, fpdf2 (PDF rendering), PyInstaller (compilation)
- **Core Runtime:** Rust (Tauri v2), acts as process orchestrator
- **Architecture:** Sidecar pattern (Python backend runs as external compiled executable)

## Architecture Overview

The application uses a **Sidecar Pattern with Localhost HTTP API**:

```
Astro Frontend (WebView)
    ↓ HTTP/JSON (fetch API)
Tauri v2 Core (Rust) - Process manager & security layer
    ↓ Process spawning
Python FastAPI Backend (Sidecar) - PDF generation engine
```

### Key Architectural Decisions

1. **Tauri v2 (NOT v1):** Uses ACL-based security model with capabilities, not deprecated allowlist
2. **Localhost HTTP API:** Python backend binds to ephemeral port (0), prints port to stdout, Rust reads and stores it
3. **Binary Naming:** Compiled Python executable must include target triple (e.g., `backend-x86_64-pc-windows-msvc.exe`)
4. **Island Architecture:** Only the editor component is interactive React; rest is static HTML
5. **Port Discovery:** Python prints `SERVER_PORT=<PORT>` to stdout with `flush=True` for real-time detection
6. **PDF via fpdf2:** Pure Python PDF library without GTK dependencies, supports grid/list/featured layouts

## Critical Constraints

### Tauri v2 Requirements

- **NO Tauri v1 patterns:** Never use deprecated `tauri.conf.json` allowlist
- **Use capabilities:** All permissions defined in `src-tauri/capabilities/sidecar.json`
- **Shell plugin:** Explicitly enable `"plugins": { "shell": { "active": true } }` in tauri.conf.json
- **External binaries:** Declared in `bundle.externalBin` as base name only (e.g., `"backend"`, not `"backend-x86_64..."`)
- **Runtime discovery:** Tauri automatically locates binaries with target triple suffix

### Python Sidecar Requirements

- **Dynamic port binding:** Always use `socket.bind(('127.0.0.1', 0))` for ephemeral port allocation
- **Port communication:** Print `SERVER_PORT=<PORT>` with `flush=True` after port assignment
- **Uvicorn async:** Use ASGI mode for concurrent requests
- **fpdf2:** Pure Python PDF library - no external dependencies required
- **CORS:** Enabled for localhost:4321 in dev mode
- **No hardcoded ports:** Port 8000 or fixed ports will cause conflicts

### Frontend Requirements

- **Astro config:** Use `output: 'static'` and `build.format: 'file'` for Tauri file-serving
- **Event listening:** Listen for `backend-ready` event emitted by Rust core
- **Nano Stores:** Use for shared state (port, auth token) outside React component tree
- **Fetch API:** All requests to `http://localhost:<DYNAMIC_PORT>/...`
- **File operations:** Use Tauri file dialog (`@tauri-apps/plugin-dialog`) and fs plugin for native file saving

## Development Workflow

### Quick Start (Browser Dev Mode)

```bash
# Install dependencies
npm install
pip3 install -r backend/requirements.txt

# Terminal 1: Start frontend
npm run dev

# Terminal 2: Start backend
cd backend/src && python3 server.py
# Note the SERVER_PORT=<PORT> output

# Open browser at: http://localhost:4321/?port=<PORT>
```

### Full Tauri Development

```bash
# Development mode (requires Rust toolchain + PyInstaller)
npm run tauri:dev

# Build for distribution
npm run tauri:build
```

### Testing Backend

```bash
cd backend/src
python3 server.py  # Prints SERVER_PORT=<PORT>

# Test health endpoint
curl http://127.0.0.1:<PORT>/health

# Test PDF generation
curl -X POST http://127.0.0.1:<PORT>/api/generate \
  -H "Content-Type: application/json" \
  -d '{"output_filename":"test.pdf","orientation":"portrait","color_mode":"RGB","pages":[{"page_number":1,"title":"Test","layout":"grid","products":[{"id":"1","name":"Product","price":9.99,"quantity":1}]}]}'
```

## Project Phases (Implementation Roadmap)

| Phase | Description | Status |
|-------|-------------|--------|
| 1. Backend Core | FastAPI server, fpdf2 PDF generation, port binding | ✅ Done |
| 2. Python Bundling | PyInstaller config, binary renaming | ✅ Done |
| 3. Rust Integration | Tauri sidecar, capabilities, port discovery | ✅ Done |
| 4. Frontend Integration | Astro editor, backend handshake, PDF export | ✅ Done |
| 5. Build Pipeline | CI/CD, cross-platform compilation | ✅ Done |
| 6. Distribution | Signing, installers, auto-updates | 🔄 Pending |
| 7. Optimization | Performance tuning, memory management | 🔄 Pending |

## Code Standards

### Python
- Type hints required (PEP 484)
- Pydantic models for request/response validation
- Black formatting (`black --line-length 100`)
- Async/await for I/O operations

### Rust
- Idiomatic Rust; follow Rust naming conventions
- Use `thiserror` for error handling
- Async tasks with Tokio (Tauri's runtime)
- CommandChild for process lifecycle management

### TypeScript/Frontend
- Strict mode enabled (`"strict": true` in tsconfig.json)
- Nano Stores for cross-component state
- React for editor island only; avoid unnecessary hydration

## Known Issues & Considerations

### PDF Library Choice
Originally planned for WeasyPrint, but switched to fpdf2 due to:
- WeasyPrint requires GTK3/Pango libraries (difficult on newer macOS)
- fpdf2 is pure Python with no external dependencies
- Trade-off: fpdf2 uses "EUR" instead of € symbol (font limitation)

### Zombie Processes
If Tauri app terminates unexpectedly, Python sidecar may remain running.
- **Solution:** Implement proper process group management in Rust; clean up CommandChild on app exit

### Port Discovery Race Condition
Tiny race window between detecting port and Uvicorn binding.
- **Workaround:** In practice negligible on localhost; use file descriptor inheritance if issues arise

### Cross-Platform Compilation
Building Windows binaries on Linux/macOS is complex for Python+GTK applications.
- **Recommendation:** Use native GitHub Actions runners (one per OS) for CI/CD

## Important References

- **Tauri v2 Docs:** https://v2.tauri.app/
- **Tauri Sidecar Guide:** https://v2.tauri.app/develop/sidecar/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **fpdf2 Docs:** https://py-pdf.github.io/fpdf2/
- **Astro Docs:** https://docs.astro.build/
- **PyInstaller Docs:** https://pyinstaller.org/

## Implementation Strategy for Claude Code

When implementing features or fixing bugs:

1. **Plan first:** Use `/init` or explicit planning for multi-step tasks
2. **Test independently:** Always test individual layers (backend, frontend, Rust) before integration
3. **Follow phases:** Don't implement Phase 4 (frontend) before completing Phase 2 (Python bundling)
4. **Reference the architecture doc:** Refer to `Tauri-Python App Ontwikkelplan.md` for deep technical details on IPC, lifecycle, and bundling strategies
5. **Avoid assumptions:** This is a Tauri v2 + Python hybrid; many blog posts/examples use outdated Tauri v1 or different IPC patterns

## Project Status

- **Current:** Werkend prototype (Fase 1-5 voltooid)
- **Next:** Distribution (Fase 6) - signing, installers
- **Browser dev mode:** Volledig functioneel op http://localhost:4321/?port=<PORT>
- **Tauri mode:** Vereist PyInstaller build voor sidecar binary
