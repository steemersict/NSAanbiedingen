# NSAanbiedingen

**NSAanbiedingen** is a modern desktop application for generating professional PDF offer folders (aanbiedingenfolders) with an intuitive drag-and-drop interface.

## Technology Stack

- **Frontend:** Astro + React (editor component) + TailwindCSS
- **Backend:** Python 3.11+ with FastAPI and WeasyPrint
- **Core Runtime:** Rust with Tauri v2
- **Architecture:** Sidecar pattern for backend process management

## Features

- 🎨 Intuitive drag-and-drop interface for creating offer folders
- 📄 Professional PDF generation with WeasyPrint
- 🖼️ Support for multiple page layouts (grid, list, featured)
- 🎨 Customizable color modes (RGB and CMYK for print)
- ⚡ Fast startup and responsive UI
- 🔒 Secure localhost-based architecture

## Quick Start

### Prerequisites

- **Node.js** v18+ and npm v9+
- **Python** 3.11+
- **Rust** 1.70+ (via rustup)
- **System dependencies:**
  - **macOS:** `brew install gtk+3 cairo pango gdk-pixbuf libffi`
  - **Windows:** GTK3 runtime (bundled during build)
  - **Linux:** `sudo apt install libgtk-3-dev libcairo2-dev libpango1.0-dev`

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd nsaanbiedingen
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Set up Python backend:**
   ```bash
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```

### Development

#### Development Mode

Start the full development environment with hot-reload:

```bash
npm run tauri:dev
```

This command:
1. Builds the Python backend
2. Renames the sidecar binary
3. Starts Astro dev server
4. Launches Tauri with auto-reload

#### Backend Only

To develop the backend independently:

```bash
cd backend
source venv/bin/activate
python src/server.py
# Backend will print: SERVER_PORT=<random_port>
```

Test the API in another terminal:

```bash
curl http://127.0.0.1:<port>/health
```

#### Frontend Only

To develop the Astro frontend without Tauri:

```bash
npm run dev
# Opens at http://localhost:4321
```

#### Running Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Building for Distribution

```bash
npm run tauri:build
```

This will:
1. Optimize the Astro frontend
2. Compile the Python backend with PyInstaller
3. Build native installers for your platform

Generated binaries will be in `src-tauri/target/release/bundle/`

## Project Structure

```
nsaanbiedingen/
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── server.py       # Main FastAPI application
│   │   ├── models.py       # Pydantic schemas
│   │   ├── pdf_generator.py # PDF generation logic
│   │   └── utils.py        # Utilities (port discovery, cleanup)
│   ├── tests/              # pytest test suite
│   ├── requirements.txt    # Python dependencies
│   └── backend.spec        # PyInstaller configuration
│
├── src/                    # Astro frontend
│   ├── components/         # React components
│   ├── layouts/            # Astro layouts
│   ├── pages/              # Astro pages/routes
│   ├── stores/             # Nano Stores state management
│   └── styles/             # Global CSS
│
├── src-tauri/             # Rust/Tauri core
│   ├── src/
│   │   ├── main.rs        # Entry point
│   │   └── lib.rs         # Sidecar lifecycle management
│   ├── capabilities/      # Tauri v2 ACL permissions
│   ├── binaries/          # Compiled Python executables
│   ├── Cargo.toml         # Rust dependencies
│   └── tauri.conf.json    # Tauri configuration
│
├── scripts/               # Build scripts
│   └── rename-sidecar.js # Binary naming helper
│
├── .github/workflows/     # CI/CD pipelines
├── CLAUDE.md             # AI development guide
└── CLAUDE-implementation.md  # Implementation details
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Astro Frontend (HTML/CSS/JS)       │  ← User Interface
│  (Hosted in WebView)                │
└─────────────────────────────────────┘
              ↓ HTTP/JSON
┌─────────────────────────────────────┐
│  Rust Core (Tauri v2)               │  ← Process Orchestrator
│  - Manages sidecar lifecycle        │
│  - Port discovery                   │
│  - Security (ACL permissions)       │
└─────────────────────────────────────┘
              ↓ Process Management
┌─────────────────────────────────────┐
│  Python Backend (FastAPI Sidecar)   │  ← PDF Generation Engine
│  - FastAPI HTTP server              │
│  - WeasyPrint PDF rendering         │
│  - Dynamic port binding             │
└─────────────────────────────────────┘
```

## API Endpoints

### Health Check
```
GET /health
```

### Generate PDF
```
POST /api/generate
Content-Type: application/json

{
  "pages": [
    {
      "page_number": 1,
      "title": "Featured Products",
      "products": [
        {
          "id": "prod-001",
          "name": "Product Name",
          "price": 99.99,
          "description": "Optional description"
        }
      ],
      "layout": "grid"
    }
  ],
  "output_filename": "aanbieding.pdf",
  "color_mode": "RGB",
  "dpi": 300,
  "orientation": "portrait"
}

Response:
{
  "success": true,
  "job_id": "uuid-string",
  "message": "PDF generated successfully",
  "file_size_kb": 1024
}
```

### Download PDF
```
GET /api/download/{job_id}
→ Returns binary PDF file
```

### Check Job Status
```
GET /api/status/{job_id}

Response:
{
  "job_id": "uuid-string",
  "status": "completed",
  "size_kb": 1024
}
```

## Troubleshooting

### Backend fails to start
- Check that port 0 binding is working: `python -c "import socket; s = socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname())"`
- Verify Python 3.11+ is installed
- Ensure GTK3 development files are installed

### PDF generation is slow
- Reduce DPI setting (default 300)
- Reduce image sizes before adding to products
- Check available disk space for temporary files

### Tauri build fails
- Run `cargo clean` in `src-tauri/`
- Ensure Rust toolchain is up to date: `rustup update`
- Check that all prerequisites are installed

## Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** and test locally

3. **Run tests:**
   ```bash
   npm run test  # (if configured)
   cd backend && pytest
   ```

4. **Commit your changes:**
   ```bash
   git commit -am "feat: add my feature"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/my-feature
   ```

## Implementation Phases

The project follows a phased implementation approach:

1. ✅ **Phase 1: Backend Core** - FastAPI + WeasyPrint
2. ✅ **Phase 2: Python Bundling** - PyInstaller configuration
3. ✅ **Phase 3: Rust Integration** - Tauri sidecar management
4. ✅ **Phase 4: Frontend** - Astro + React editor
5. ⏳ **Phase 5: CI/CD** - GitHub Actions workflows
6. ⏳ **Phase 6: Distribution** - Code signing, installers, auto-updates
7. ⏳ **Phase 7: Optimization** - Performance tuning

See `CLAUDE-implementation.md` for detailed implementation guidance.

## Contributing

Contributions are welcome! Please:

1. Read `CLAUDE.md` for development guidelines
2. Follow the existing code style
3. Add tests for new features
4. Update documentation

## License

[Add your license here]

## Support

For issues, questions, or feature requests, please open a GitHub issue.

---

**Last Updated:** December 2025
**Built with ❤️ using Tauri, Astro, Python, and Rust**
