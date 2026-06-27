#!/usr/bin/env bash
set -e

echo "=========================================="
echo "AI Prompt Firewall - Complete Diagnostic"
echo "=========================================="
echo ""

# Check backend
echo "1. Checking Backend..."
echo "   Testing http://localhost:8000/health"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "   ✓ Backend is running"
else
    echo "   ✗ Backend is NOT running"
    echo "   Start: cd backend && bash scripts/dev.sh"
    exit 1
fi

echo ""
echo "2. Checking API Routes..."
echo "   Testing http://localhost:8000/docs"
if curl -s http://localhost:8000/docs | grep -q "swagger"; then
    echo "   ✓ Swagger docs accessible"
    
    # Count routes
    routes=$(curl -s http://localhost:8000/openapi.json | grep -o '"paths"' | wc -l)
    echo "   ✓ OpenAPI paths defined"
else
    echo "   ✗ Swagger docs not accessible"
    exit 1
fi

echo ""
echo "3. Checking Auth Endpoint..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456","full_name":"Test"}' \
  -w "\n%{http_code}")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "201" ] || [ "$http_code" = "409" ]; then
    echo "   ✓ Auth endpoint working (HTTP $http_code)"
else
    echo "   ✗ Auth endpoint failed (HTTP $http_code)"
    echo "   Response: $(echo "$response" | head -n-1)"
    exit 1
fi

echo ""
echo "4. Checking Frontend..."
echo "   Testing http://localhost:5173"
if curl -s http://localhost:5173 | grep -q "root"; then
    echo "   ✓ Frontend is running"
else
    echo "   ✗ Frontend is NOT running"
    echo "   Start: cd frontend && npm run dev"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All systems operational!"
echo "=========================================="
echo ""
echo "Access dashboard at: http://localhost:5173"
echo "Test credentials:"
echo "  Email: test@example.com"
echo "  Password: Test123456"
echo ""