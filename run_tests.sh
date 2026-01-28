#!/bin/bash

echo "Running RAG Chatbot Test Suite"
echo "=================================="

echo ""
echo "Running Unit Tests..."
pytest tests/unit/ -v --tb=short -W ignore::DeprecationWarning

echo ""
echo "Running Integration Tests..."
pytest tests/integration/ -v --tb=short -W ignore::DeprecationWarning

echo ""
echo "Test suite complete!"