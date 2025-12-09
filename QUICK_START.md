# NSAanbiedingen - Quick Start Guide

**Setup Status:** In Progress 🔄

## What Was Done

✅ **npm dependencies** installed (408 packages)
✅ **Python 3.11 virtual environment** created
✅ **Python dependencies** installed (FastAPI, WeasyPrint, Uvicorn, pytest, etc.)
✅ **Rust toolchain** verified (1.91.1)

## Current Step: Installing GTK3

WeasyPrint requires GTK3 system libraries. This is being installed now:
```bash
brew install gtk+3
```

This will take a few minutes. ☕

## Next Steps (When GTK3 Installation Completes)

### 1. Run Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

Expected: All 12 tests should pass ✓

### 2. Test Backend Independently
```bash
# Terminal 1: Start backend
cd backend
source venv/bin/activate
python src/server.py

# Terminal 2: Test API
curl http://127.0.0.1:$(lsof -ti:5000 | head -1)/health
```

### 3. Build Python Sidecar Binary
```bash
npm run build:sidecar
# This will:
# 1. Compile Python with PyInstaller
# 2. Rename binary with target triple
```

### 4. Start Full Development Environment
```bash
npm run tauri:dev
```

This launches:
- ✅ Astro dev server (http://localhost:4321)
- ✅ Tauri application with hot-reload
- ✅ Python backend sidecar
- ✅ Event-based connection between frontend and backend

## Project Structure

```
NSAanbiedingen/
├── backend/              # Python FastAPI backend
│   ├── src/              # Main code
│   ├── tests/            # Pytest test suite
│   ├── venv/             # Virtual environment (active)
│   └── requirements.txt   # Dependencies (installed)
│
├── src/                  # Astro frontend + React
│   ├── components/       # Editor.tsx - interactive UI
│   ├── layouts/          # Layout.astro
│   ├── pages/            # index.astro - main page
│   └── stores/           # Nano Stores state management
│
├── src-tauri/            # Rust core + Tauri v2
│   ├── src/              # Rust source (lib.rs, main.rs)
│   ├── capabilities/     # sidecar.json (ACL permissions)
│   ├── binaries/         # Compiled Python exe (when built)
│   └── tauri.conf.json   # Configuration
│
├── scripts/              # Build helpers
│   └── rename-sidecar.js # Binary naming script
│
└── Documentation/
    ├── CLAUDE.md         # AI development guide
    ├── SETUP.md          # Complete setup walkthrough
    ├── README.md         # User documentation
    └── IMPLEMENTATION_SUMMARY.md
```

## Available Commands

### Development
```bash
npm run tauri:dev          # Full app development
npm run dev                # Astro frontend only
cd backend && python src/server.py  # Backend only
```

### Testing
```bash
cd backend && pytest tests/ -v  # Backend tests
cd backend && pytest tests/test_pdf_generation.py::test_health_check  # Single test
```

### Building
```bash
npm run build:backend      # Compile Python
npm run build:sidecar      # Build sidecar binary
npm run tauri:build        # Full application build
```

## Architecture Overview

```
┌──────────────────────────────────────┐
│  Frontend (Astro + React)            │
│  - Editor UI                         │
│  - Product management                │
│  - PDF preview                       │
└──────────────────────────────────────┘
         ↓↑ HTTP/JSON API
┌──────────────────────────────────────┐
│  Core (Tauri v2 + Rust)              │
│  - Process orchestrator              │
│  - Port discovery                    │
│  - Event emission                    │
│  - Security (ACL)                    │
└──────────────────────────────────────┘
         ↓↑ Process Management
┌──────────────────────────────────────┐
│  Backend (Python + FastAPI)          │
│  - PDF generation                    │
│  - WeasyPrint rendering              │
│  - Job management                    │
└──────────────────────────────────────┘
```

## Key Features

✅ **Backend Core**
- REST API with FastAPI
- PDF generation with WeasyPrint
- Dynamic port binding
- Job queue management
- Comprehensive error handling

✅ **Frontend**
- Interactive editor for product management
- Multi-page folder creation
- PDF settings customization
- Native file dialogs
- Real-time status updates

✅ **Deployment Ready**
- Cross-platform builds (macOS, Windows)
- CI/CD pipelines (GitHub Actions)
- Sidecar pattern for stability
- Minimal binary size (~80-100MB)

## Troubleshooting

### "cannot load library 'libgobject-2.0-0'"
WeasyPrint needs GTK3. Wait for brew install to complete, then:
```bash
pip install --upgrade weasyprint
pytest tests/ -v
```

### "Backend not ready" in Tauri
1. Check backend is running: `curl http://127.0.0.1:PORT/health`
2. Check port discovery works:
   ```bash
   python -c "import socket; s = socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1])"
   ```
3. Check Python path: `which python` (should be in venv)

### macOS: "Permission denied" for shell profile
This is normal during Rust install. Ignore it - Rust is still installed.

## Configuration Files

### npm
- `package.json` - Project metadata and build scripts
- `tsconfig.json` - TypeScript configuration
- `astro.config.mjs` - Astro static site generation
- `tailwind.config.cjs` - TailwindCSS theming

### Python
- `backend/requirements.txt` - Python packages
- `backend/backend.spec` - PyInstaller configuration
- `backend/hooks/hook-weasyprint.py` - GTK3 bundling

### Rust/Tauri
- `src-tauri/Cargo.toml` - Rust dependencies
- `src-tauri/tauri.conf.json` - Tauri configuration
- `src-tauri/capabilities/sidecar.json` - ACL permissions

### CI/CD
- `.github/workflows/build.yml` - GitHub Actions pipeline
- `.gitignore` - Git exclusions

## Next Phase: Running the App

Once GTK3 is installed and tests pass:

```bash
# Start the full development environment
npm run tauri:dev
```

This will:
1. Build the Astro frontend
2. Compile Python with PyInstaller
3. Start the Tauri app window
4. Connect frontend ↔ backend via HTTP
5. Auto-reload on code changes

**Expected app flow:**
- Window opens with loading screen
- "Initializing..." message appears
- After ~5 seconds: "Ready (port XXXXX)"
- Editor UI loads
- You can now create PDF offers!

## Documentation

Read these in order:

1. **QUICK_START.md** (this file) - Get running quickly
2. **SETUP.md** - Detailed setup walkthrough
3. **CLAUDE.md** - Development guidelines
4. **README.md** - API documentation
5. **IMPLEMENTATION_SUMMARY.md** - What was built

## Support

For issues, check:
1. SETUP.md troubleshooting section
2. Backend logs: `npm run tauri:dev` console output
3. GitHub issues (future)

---

**Status:** Setup in progress
**Next:** Install GTK3 and run tests
**Estimated time:** 5-10 minutes

