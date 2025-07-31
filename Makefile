# Makefile for Doctor Procedures Bedrock App

.PHONY: help setup activate build test test-local clean deploy start-api start-db populate-db

# Default target
help:
	@echo "Doctor Procedures Bedrock App - Available Commands:"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup          - Set up virtual environment and install dependencies"
	@echo "  make activate       - Show command to activate virtual environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build          - Build SAM application"
	@echo "  make test           - Run full test suite (requires Docker)"
	@echo "  make test-local     - Run local tests (no Docker required)"
	@echo "  make start-api      - Start local API server (requires Docker)"
	@echo "  make start-db       - Start local DynamoDB (requires Docker)"
	@echo "  make populate-db    - Populate DynamoDB with test data"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  make deploy         - Deploy to AWS"
	@echo "  make deploy-guided  - Deploy to AWS with guided setup"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Lint code with flake8"

# Setup virtual environment
setup:
	@echo "🚀 Setting up development environment..."
	./setup_env.sh

# Show activation command
activate:
	@echo "To activate the virtual environment, run:"
	@echo "  source venv/bin/activate"

# Build SAM application
build:
	@echo "🔨 Building SAM application..."
	sam build

# Run full test suite (requires Docker)
test: build
	@echo "🧪 Running full test suite..."
	./run_tests.sh

# Run local tests (no Docker required)
test-local:
	@echo "🧪 Running local tests..."
	python3 test_local.py

# Start local API server
start-api: build
	@echo "🌐 Starting local API server on port 3000..."
	@echo "Make sure Docker is running!"
	sam local start-api --port 3000

# Start local DynamoDB
start-db:
	@echo "🗄️ Starting local DynamoDB on port 8000..."
	@echo "Make sure Docker is running!"
	docker run -p 8000:8000 amazon/dynamodb-local

# Populate DynamoDB with test data
populate-db:
	@echo "📊 Populating DynamoDB with test data..."
	python3 populate_dummy_data.py

# Deploy to AWS
deploy: build
	@echo "🚀 Deploying to AWS..."
	sam deploy

# Deploy to AWS with guided setup
deploy-guided: build
	@echo "🚀 Deploying to AWS with guided setup..."
	sam deploy --guided

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf .aws-sam/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Format code
format:
	@echo "🎨 Formatting code with black..."
	black functions/

# Lint code
lint:
	@echo "🔍 Linting code with flake8..."
	flake8 functions/

# Validate SAM template
validate:
	@echo "✅ Validating SAM template..."
	sam validate
