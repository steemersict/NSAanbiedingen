#!/bin/bash

# NSAanbiedingen Setup Verification Script

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          NSAanbiedingen Setup Verification                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Function to check command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT found"
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 NOT found"
        return 1
    fi
}

echo "📦 System Prerequisites"
echo "────────────────────────"
check_command node || FAILED=1
check_command npm || FAILED=1
check_command python3.11 || FAILED=1
check_command rustc || FAILED=1
check_command cargo || FAILED=1
echo ""

echo "📁 Project Structure"
echo "────────────────────"
check_dir node_modules || FAILED=1
check_file package.json || FAILED=1
check_dir backend || FAILED=1
check_dir backend/venv || FAILED=1
check_dir backend/src || FAILED=1
check_dir backend/tests || FAILED=1
check_dir src || FAILED=1
check_dir src-tauri || FAILED=1
check_file tsconfig.json || FAILED=1
echo ""

echo "🐍 Python Environment"
echo "────────────────────"
PYTHON_BIN="backend/venv/bin/python3.11"
if [ -f "$PYTHON_BIN" ]; then
    echo -e "${GREEN}✓${NC} Python venv exists at $PYTHON_BIN"
    PYTHON_VERSION=$($PYTHON_BIN --version 2>&1)
    echo "  Version: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python venv not found"
    FAILED=1
fi

echo ""
echo "📦 Python Packages"
echo "────────────────────"
$PYTHON_BIN -c "import fastapi; print('✓ fastapi installed')" 2>/dev/null || echo "✗ fastapi NOT installed"
$PYTHON_BIN -c "import uvicorn; print('✓ uvicorn installed')" 2>/dev/null || echo "✗ uvicorn NOT installed"
$PYTHON_BIN -c "import weasyprint; print('✓ weasyprint installed')" 2>/dev/null || { echo -e "${YELLOW}⚠${NC} weasyprint - GTK3 may be missing"; FAILED=1; }
$PYTHON_BIN -c "import pytest; print('✓ pytest installed')" 2>/dev/null || echo "✗ pytest NOT installed"
$PYTHON_BIN -c "import pydantic; print('✓ pydantic installed')" 2>/dev/null || echo "✗ pydantic NOT installed"

echo ""
echo "🔧 Build System"
echo "────────────────────"
check_file scripts/rename-sidecar.js || FAILED=1
check_file backend/backend.spec || FAILED=1
check_file backend/hooks/hook-weasyprint.py || FAILED=1
echo ""

echo "📚 Documentation"
echo "────────────────────"
check_file CLAUDE.md || FAILED=1
check_file SETUP.md || FAILED=1
check_file README.md || FAILED=1
check_file QUICK_START.md || FAILED=1
echo ""

echo "📋 Configuration Files"
echo "────────────────────"
check_file package.json || FAILED=1
check_file tsconfig.json || FAILED=1
check_file astro.config.mjs || FAILED=1
check_file tailwind.config.cjs || FAILED=1
check_file src-tauri/tauri.conf.json || FAILED=1
check_file src-tauri/Cargo.toml || FAILED=1
echo ""

echo "🧪 Testing Backend"
echo "────────────────────"
if [ $FAILED -eq 0 ]; then
    echo "Running pytest..."
    cd backend
    source venv/bin/activate
    if pytest tests/ -v --tb=short 2>/dev/null; then
        echo -e "${GREEN}✓${NC} All tests passed!"
    else
        echo -e "${YELLOW}⚠${NC} Some tests failed - may need GTK3"
        FAILED=1
    fi
    cd ..
else
    echo -e "${YELLOW}⚠${NC} Skipping tests - prerequisites missing"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
if [ $FAILED -eq 0 ]; then
    echo -e "║${GREEN}                    ✓ SETUP SUCCESSFUL${NC}                    ║"
    echo "║  You can now run: npm run tauri:dev                    ║"
else
    echo -e "║${RED}              ✗ SETUP INCOMPLETE - SEE ERRORS${NC}             ║"
    echo "║  Check SETUP.md for troubleshooting                   ║"
fi
echo "╚════════════════════════════════════════════════════════════╝"

exit $FAILED
