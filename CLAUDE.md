# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Identity

**NSAanbiedingen** is a hybrid desktop application for generating professional PDF offer folders (aanbiedingenfolders) with visual drag-and-drop editing and print-ready output.

- **Frontend:** Astro (Static Site Generator with React island for the editor), TypeScript, TailwindCSS, Nano Stores
- **Backend:** Python 3.11+, FastAPI, WeasyPrint (PDF rendering), PyInstaller (compilation)
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
6. **PDF via WeasyPrint:** Converts Astro-generated HTML/CSS to print-ready PDFs with CMYK/bleeds support

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
- **WeasyPrint dependencies:** GTK3 libraries must be bundled (via PyInstaller hooks) on Windows; system-provided on Linux/macOS
- **No hardcoded ports:** Port 8000 or fixed ports will cause conflicts

### Frontend Requirements

- **Astro config:** Use `output: 'static'` and `build.format: 'file'` for Tauri file-serving
- **Event listening:** Listen for `backend-ready` event emitted by Rust core
- **Nano Stores:** Use for shared state (port, auth token) outside React component tree
- **Fetch API:** All requests to `http://localhost:<DYNAMIC_PORT>/...`
- **File operations:** Use Tauri file dialog (`@tauri-apps/plugin-dialog`) and fs plugin for native file saving

## Development Workflow

### Setup Commands (Not yet implemented, planned for Phase 1-2)

```bash
# Initialize Tauri project (requires npm)
npm create tauri-app@latest

# Install dependencies
npm install && cd backend && pip install -r requirements.txt

# Development mode (watches frontend, rebuilds Python backend on changes)
npm run tauri dev

# Build for distribution (requires native build environment)
npm run tauri build

# Test Python backend independently
cd backend && python -m pytest

# Build Python executable with PyInstaller (manual)
pyinstaller backend.spec
```

### Typical Development Tasks

**Developing the editor UI:**
```bash
npm run dev  # Astro dev server (frontend only)
```

**Testing backend independently:**
```bash
cd backend
python server.py  # Prints SERVER_PORT=<PORT>
# In another terminal: curl http://localhost:<PORT>/health
```

**Full integration testing:**
```bash
npm run tauri dev  # Starts Astro + Rust + Python with hot reload
```

**Building for release:**
```bash
npm run tauri build  # Triggers PyInstaller, Tauri bundler, binary rename
```

## Project Phases (Implementation Roadmap)

The project is in **planning phase**. Planned implementation follows these phases:

1. **Phase 1: Backend Core** - Python FastAPI server with WeasyPrint, port binding, health checks
2. **Phase 2: Python Bundling** - PyInstaller configuration, GTK3 dependency hooks, binary renaming script
3. **Phase 3: Rust Integration** - Tauri sidecar lifecycle, capabilities, port discovery, event emission
4. **Phase 4: Frontend Integration** - Astro editor, backend handshake, PDF export workflow
5. **Phase 5: Build Pipeline** - CI/CD, cross-platform compilation
6. **Phase 6: Distribution** - Signing, installers, auto-updates
7. **Phase 7: Optimization** - Performance tuning, memory management

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

### Windows: GTK3 "DLL Hell"
WeasyPrint depends on GTK3 libraries (Pango, Cairo, GDK-Pixbuf). PyInstaller may miss dynamic imports.
- **Solution:** Create PyInstaller hook for weasyprint; bundle GTK3 DLLs in `_internal` directory
- **Fallback:** Document system GTK3 installation requirement in README

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
- **WeasyPrint Docs:** https://doc.courtbouillon.org/weasyprint/
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

- **Current:** Planning & specification phase (architecture documented)
- **Next:** Backend core implementation (Phase 1)
- **Constraint:** Tauri v2 is rapidly evolving; always verify against v2.tauri.app docs, not v1 or community tutorials
