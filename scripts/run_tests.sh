#!/bin/bash

# HRM Demo - Run Tests Script
# This script runs the unit test suite

set -e

echo "========================================"
echo "HRM Demo - Unit Tests"
echo "========================================"

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "Error: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Parse command line arguments
TEST_PATTERN=${1:-"contacts"}
VERBOSE=${2:-"-v 2"}

echo "Running tests for: $TEST_PATTERN"
echo "Verbosity: $VERBOSE"
echo ""

# Start timing
start_time=$(date +%s)

# Run tests
python manage.py test $TEST_PATTERN $VERBOSE

test_result=$?

# Calculate duration
end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "========================================"

if [ $test_result -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "⏱️  Time taken: ${duration} seconds"
    echo ""
    echo "Test coverage includes:"
    echo "- Basic API functionality"
    echo "- Dynamic property filtering"
    echo "- Display parameter functionality"
    echo "- Search functionality"
    echo "- Pagination and edge cases"
    echo "- Rate limiting integration"
else
    echo "❌ Some tests failed"
    echo "⏱️  Time taken: ${duration} seconds"
    exit 1
fi