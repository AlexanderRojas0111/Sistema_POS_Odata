#!/bin/bash

# Pre-commit hook script for POS O'data
# This script runs before each commit to ensure code quality

set -e

echo "🔍 Running pre-commit checks..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Not in a virtual environment. Consider activating one."
fi

# 1. Check Python syntax
echo "📝 Checking Python syntax..."
python -m py_compile app/main.py
print_status "Python syntax check passed"

# 2. Run Black formatting check
echo "🎨 Checking code formatting with Black..."
if black --check --diff app/ tests/ 2>/dev/null; then
    print_status "Code formatting check passed"
else
    print_error "Code formatting issues found. Run 'black app/ tests/' to fix."
    exit 1
fi

# 3. Run Flake8 linting
echo "🔍 Running Flake8 linting..."
if flake8 app/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    print_status "Flake8 critical issues check passed"
else
    print_error "Flake8 critical issues found."
    exit 1
fi

# 4. Run basic tests
echo "🧪 Running basic tests..."
if python -m pytest tests/test_api.py tests/test_users.py -v --tb=short; then
    print_status "Basic tests passed"
else
    print_error "Basic tests failed."
    exit 1
fi

# 5. Check for security issues
echo "🔒 Checking for security issues..."
if command -v safety &> /dev/null; then
    if safety check --json --output /dev/null 2>/dev/null; then
        print_status "Security check passed"
    else
        print_warning "Security issues found. Check with 'safety check' for details."
    fi
else
    print_warning "Safety not installed. Install with 'pip install safety'"
fi

# 6. Check for TODO/FIXME comments
echo "📋 Checking for TODO/FIXME comments..."
TODO_COUNT=$(grep -r "TODO\|FIXME" app/ tests/ --exclude-dir=__pycache__ | wc -l)
if [ "$TODO_COUNT" -eq 0 ]; then
    print_status "No TODO/FIXME comments found"
else
    print_warning "Found $TODO_COUNT TODO/FIXME comments:"
    grep -r "TODO\|FIXME" app/ tests/ --exclude-dir=__pycache__ | head -5
fi

# 7. Check file sizes
echo "📏 Checking file sizes..."
LARGE_FILES=$(find app/ tests/ -name "*.py" -size +100k 2>/dev/null | wc -l)
if [ "$LARGE_FILES" -eq 0 ]; then
    print_status "No excessively large files found"
else
    print_warning "Found $LARGE_FILES files larger than 100KB"
fi

# 8. Check for hardcoded secrets
echo "🔐 Checking for potential hardcoded secrets..."
SECRET_PATTERNS=("password.*=.*['\"]" "secret.*=.*['\"]" "key.*=.*['\"]" "token.*=.*['\"]")
FOUND_SECRETS=0

for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r "$pattern" app/ --exclude-dir=__pycache__ | grep -v "example\|test\|mock" > /dev/null; then
        FOUND_SECRETS=$((FOUND_SECRETS + 1))
    fi
done

if [ "$FOUND_SECRETS" -eq 0 ]; then
    print_status "No obvious hardcoded secrets found"
else
    print_warning "Found potential hardcoded secrets. Review the code."
fi

echo ""
print_status "All pre-commit checks completed successfully!"
echo "🚀 Ready to commit!"

exit 0 