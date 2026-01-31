#!/bin/bash
# Quick Start Guide for Tax Compliance Automation Pipeline

echo "🚀 TAX COMPLIANCE AUTOMATION PIPELINE - QUICK START"
echo "=================================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python --version
if [ $? -ne 0 ]; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python OK"
echo ""

# Check dependencies
echo "2️⃣  Checking dependencies..."
pip list | grep -E "langgraph|langchain|pydantic|loguru|requests|taxjar" > /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip install -r requirements.txt
fi
echo "✅ Dependencies OK"
echo ""

# Check .env file
echo "3️⃣  Checking configuration..."
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Create .env with:"
    echo ""
    echo "OPENAI_API_KEY=your_key_or_skip"
    echo "GEMINI_API_KEY=your_key_or_skip"
    echo "TAX_API_BASE_URL=https://jsonplaceholder.typicode.com"
    echo "TAX_API_FAILOVER_URL=https://httpbin.org"
    echo "TAXJAR_API_KEY=your_sandbox_key"
    echo "TAXJAR_API_URL=https://api.sandbox.taxjar.com"
    echo "LLM_MODEL=gpt-4-turbo"
    echo "MAX_RETRIES=3"
    echo ""
else
    echo "✅ .env file found"
fi
echo ""

# Run the pipeline
echo "4️⃣  Running pipeline..."
echo "=================================="
python src/healing_pipeline/pipeline_runner.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ PIPELINE EXECUTION COMPLETED"
    echo ""
    echo "📋 Check these files:"
    echo "   - pipeline_execution.log  (detailed logs)"
    echo "   - PIPELINE_GUIDE.md        (full documentation)"
    echo "   - EXECUTION_RESULTS.md     (test results)"
    echo ""
else
    echo ""
    echo "⚠️  PIPELINE ENCOUNTERED ERRORS"
    echo "Check pipeline_execution.log for details"
    echo ""
fi
