# NSAanbiedingen - Complete Setup Guide

This guide walks you through setting up the NSAanbiedingen development environment from scratch.

## Step 1: System Prerequisites

### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install rustup nodejs python@3.11 gtk+3 cairo pango gdk-pixbuf libffi

# Verify installations
rustup default stable
node --version  # Should be v18+
npm --version   # Should be v9+
python3.11 --version
rustc --version
```

### Windows

1. **Download and install Node.js** from https://nodejs.org/ (v18+)
2. **Download and install Python 3.11** from https://www.python.org/downloads/
   - ⚠️ **Important:** Check "Add Python to PATH" during installation
3. **Install Rust** from https://rustup.rs/
4. **GTK3 Runtime** will be bundled automatically during build

Verify in PowerShell:
```powershell
node --version
npm --version
python --version
rustc --version
```

## Step 2: Clone and Initialize Project

```bash
cd /Volumes/NST1/code/NSAanbiedingen

# Verify files were created
ls -la | grep "CLAUDE\|package.json\|README"
```

## Step 3: Install npm Dependencies

```bash
npm install
```

This will install:
- Tauri CLI and plugins
- Astro and integrations (React, TailwindCSS)
- TypeScript, testing libraries
- Nano Stores for state management

## Step 4: Set Up Python Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify FastAPI works
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} OK')"
python -c "import weasyprint; print(f'WeasyPrint OK')"

cd ..
```

## Step 5: Run Backend Tests

```bash
cd backend
pytest tests/ -v
cd ..
```

Expected output: All tests should pass ✓

## Step 6: Test Backend Independently

**Terminal 1: Start the backend**
```bash
cd backend
source venv/bin/activate
python src/server.py
```

You should see output like:
```
[2025-12-09 12:34:56] INFO     Uvicorn running on http://127.0.0.1:51234
SERVER_PORT=51234
```

**Terminal 2: Test the API**
```bash
# Health check
curl http://127.0.0.1:51234/health

# Generate a test PDF
curl -X POST http://127.0.0.1:51234/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "pages": [{
      "page_number": 1,
      "title": "Test",
      "products": [{"id": "1", "name": "Test Product", "price": 99.99}]
    }]
  }'
```

## Step 7: Build Python Sidecar (Phase 2)

```bash
# Install PyInstaller
pip install pyinstaller

# Build the backend binary
npm run build:backend

# Rename binary for Tauri
npm run build:rename

# Verify binary was created
ls -la src-tauri/binaries/
```

Should show: `backend-<target-triple>` (e.g., `backend-x86_64-apple-darwin`)

## Step 8: Verify Rust/Tauri Setup

```bash
cd src-tauri

# Check Rust toolchain
cargo --version

# Verify Tauri configuration
cat tauri.conf.json | grep -A 5 "externalBin"

# Compile Rust code (just a check, doesn't run app)
cargo build

cd ..
```

## Step 9: Run in Development Mode

```bash
npm run tauri:dev
```

This command:
1. ✅ Builds and bundles the Astro frontend
2. ✅ Compiles Python backend with PyInstaller
3. ✅ Renames sidecar binary
4. ✅ Starts Astro dev server (http://localhost:4321)
5. ✅ Launches Tauri app with hot-reload
6. ✅ Connects to Python backend via localhost

Expected flow:
- Tauri window opens
- Status shows "Initializing..."
- After ~5 seconds: Status shows "Ready (port XXXXX)"
- Editor interface appears

## Step 10: Create Your First Offer Folder

1. In the Editor sidebar, click "+ Add Page"
2. In the main area, click "+ Add Product"
3. Fill in:
   - Product Name: "Laptop Computer"
   - Price: "999.99"
   - Description: "Professional laptop with 16GB RAM"
4. Click "Add"
5. Adjust PDF Settings if needed
6. Click "Generate PDF"
7. PDF downloads automatically

## Troubleshooting

### "Backend not ready" after 10 seconds

**Check:**
1. Are you on Python 3.11+?
   ```bash
   python3.11 --version
   ```
2. Is the virtual environment activated?
3. Do you have GTK3 development files?
   - macOS: `brew list gtk+3 | head`
   - Windows: Check PyInstaller build logs
   - Linux: `pkg-config --exists gtk+-3.0`

**Solution:**
```bash
# Rebuild Python sidecar
npm run build:backend
npm run build:rename

# Check for errors
tail -f src-tauri/target/release/build.log
```

### "PyInstaller: command not found"

```bash
cd backend
source venv/bin/activate
pip install pyinstaller
cd ..
npm run build:backend
```

### "Port discovery timeout"

The backend sidecar process didn't start. Check:
1. Console/terminal output for Python errors
2. System logs for missing libraries
3. Disk space (PDF generation needs temp space)

### macOS: "No backends available" from GTK

This means WeasyPrint can't find GTK3. Install it:
```bash
brew install gtk+3
# Or reinstall
brew reinstall gtk+3
```

Then rebuild:
```bash
rm -rf backend/venv
python3.11 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
npm run build:backend
```

## Development Workflow

### Make code changes

1. **Backend changes:** Edit files in `backend/src/`
   - Changes auto-reload in `tauri:dev`
   - If adding dependencies: `pip install <package>`, then rebuild sidecar

2. **Frontend changes:** Edit files in `src/`
   - Hot-reload works automatically

3. **Rust changes:** Edit files in `src-tauri/src/`
   - Must rebuild; run `npm run tauri:dev` again

### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend (manual)
# Use the UI to test features
```

### Building for Distribution

```bash
npm run tauri:build
```

This creates native installers in `src-tauri/target/release/bundle/`:
- **macOS:** `.dmg` file
- **Windows:** `.msi` installer
- **Linux:** `.AppImage` and `.deb` files (when Linux support is added)

## Next Steps

1. ✅ Setup complete!
2. 📖 Read `CLAUDE.md` for development guidelines
3. 🎨 Customize the editor UI
4. 📄 Add more PDF layout templates
5. 🚀 Deploy to production

## Getting Help

- Check `README.md` for API documentation
- Review `CLAUDE.md` for architecture overview
- Check `Tauri-Python App Ontwikkelplan.md` for detailed technical decisions

## Useful Commands Reference

```bash
# Development
npm run tauri:dev          # Full development mode
npm run dev                # Astro dev only
cd backend && python src/server.py  # Backend only

# Testing
cd backend && pytest       # Run all tests
cd backend && pytest tests/test_pdf_generation.py::test_health_check  # Single test

# Building
npm run build:backend      # Compile Python with PyInstaller
npm run build:rename       # Rename binary for Tauri
npm run build:sidecar      # Both of above
npm run tauri:build        # Full application build

# Cleaning
rm -rf node_modules        # Clean npm cache
rm -rf backend/venv        # Reset Python env
rm -rf backend/dist        # Clean Python build
rm -rf backend/build       # Clean PyInstaller
rm -rf src-tauri/target    # Clean Rust build
```

---

**Setup complete!** You're ready to start developing NSAanbiedingen. 🚀

