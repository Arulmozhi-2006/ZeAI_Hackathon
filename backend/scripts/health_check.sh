#!/usr/bin/env bash
set -e

echo "================================"
echo "Firewall Backend Health Check"
echo "================================"
echo ""

# Check if backend is running
echo "1. Checking if backend server is running on port 8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Backend server is running"
else
    echo "   ✗ Backend server is NOT running"
    echo "   Start it with: cd backend && bash scripts/dev.sh"
    exit 1
fi

echo ""
echo "2. Checking database connection..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "   ✓ API documentation is accessible"
else
    echo "   ✗ API is not responding"
    exit 1
fi

echo ""
echo "3. Testing registration endpoint..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123", "full_name": "Test User"}' \
  -w "\n%{http_code}")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "201" ] || [ "$http_code" = "409" ]; then
    echo "   ✓ Registration endpoint working (HTTP $http_code)"
else
    echo "   ✗ Registration failed (HTTP $http_code)"
    echo "   Response: $body"
    exit 1
fi

echo ""
echo "4. Testing login endpoint..."
response=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPassword123"}' \
  -w "\n%{http_code}")

http_code=$(echo "$response" | tail -n1)

if [ "$http_code" = "200" ]; then
    echo "   ✓ Login endpoint working (HTTP $http_code)"
else
    echo "   ✗ Login failed (HTTP $http_code)"
    exit 1
fi

echo ""
echo "================================"
echo "✓ All health checks passed!"
echo "================================"