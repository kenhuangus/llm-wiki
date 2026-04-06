#!/bin/bash
# Configure LM Studio for Maximum Context Length
# For Mac Mini with 64GB RAM

echo "=========================================="
echo "  LM Studio Context Length Configuration"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if lms command exists
if ! command -v lms &> /dev/null; then
    echo -e "${YELLOW}⚠️  'lms' command not found in PATH${NC}"
    echo "Trying full path..."
    LMS_CMD="/Applications/LM Studio.app/Contents/MacOS/lms"
    
    if [ ! -f "$LMS_CMD" ]; then
        echo -e "${RED}❌ LM Studio not found at: $LMS_CMD${NC}"
        echo ""
        echo "Please install LM Studio or update the path in this script."
        exit 1
    fi
else
    LMS_CMD="lms"
fi

echo -e "${GREEN}✅ Found LM Studio: $LMS_CMD${NC}"
echo ""

# Stop current server
echo "🛑 Stopping current server..."
$LMS_CMD server stop 2>/dev/null || true
sleep 3

# Ask user for context length
echo "Select context length:"
echo "  1) 8K tokens  (Conservative, ~18GB RAM)"
echo "  2) 16K tokens (Balanced, ~22GB RAM) [Recommended]"
echo "  3) 32K tokens (Maximum, ~30GB RAM)"
echo "  4) 64K tokens (Extreme, ~46GB RAM, may be unstable)"
echo ""
read -p "Enter choice [1-4] (default: 2): " choice
choice=${choice:-2}

case $choice in
    1)
        CONTEXT_LENGTH=8192
        echo -e "${GREEN}Selected: 8K tokens${NC}"
        ;;
    2)
        CONTEXT_LENGTH=16384
        echo -e "${GREEN}Selected: 16K tokens (Recommended)${NC}"
        ;;
    3)
        CONTEXT_LENGTH=32768
        echo -e "${GREEN}Selected: 32K tokens${NC}"
        ;;
    4)
        CONTEXT_LENGTH=65536
        echo -e "${YELLOW}Selected: 64K tokens (Warning: May use all RAM)${NC}"
        ;;
    *)
        CONTEXT_LENGTH=16384
        echo -e "${GREEN}Invalid choice, using default: 16K tokens${NC}"
        ;;
esac

echo ""
echo "🚀 Starting LM Studio server..."
echo "   Model: google/gemma-4-26b-a4b:3"
echo "   Context Length: $CONTEXT_LENGTH tokens"
echo "   GPU Layers: All (-1)"
echo "   Port: 1234"
echo ""

# Start server with selected context length
$LMS_CMD server start google/gemma-4-26b-a4b:3 \
  --context-length $CONTEXT_LENGTH \
  --gpu-layers -1 \
  --threads 8 \
  --port 1234 \
  --host 0.0.0.0 &

SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 10

# Test if server is responding
echo "🔍 Testing server..."
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Server is running successfully!${NC}"
    echo ""
    echo "Server details:"
    echo "  URL: http://localhost:1234"
    echo "  Context Length: $CONTEXT_LENGTH tokens"
    echo "  Process ID: $SERVER_PID"
    echo ""
    echo "Test with:"
    echo "  curl http://localhost:1234/v1/models"
    echo ""
    echo "Generate paper:"
    echo "  python tools/paper_agent.py --focus agentic_ai_security"
    echo ""
    echo "To stop server:"
    echo "  $LMS_CMD server stop"
    echo "  or: kill $SERVER_PID"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    echo "Check LM Studio logs for errors"
    exit 1
fi

echo ""
echo "=========================================="
echo "  Configuration Complete!"
echo "=========================================="
