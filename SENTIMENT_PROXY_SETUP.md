# Sentiment Analysis and Proxy API Setup

This document describes the sentiment analysis microservice and Django proxy API endpoints added to the project.

## Overview

The project now includes:
1. A Flask-based sentiment analysis microservice (placeholder returning "neutral")
2. Django proxy views that forward requests to external services
3. Docker Compose orchestration for local development

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Client    │─────▶│    Django    │─────▶│  Sentiment      │
│             │      │  Proxy Views │      │  Service (8080) │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            │
                            ▼
                     ┌──────────────┐
                     │   Express    │
                     │ Service:3000 │
                     └──────────────┘
```

## Files Added

### 1. Sentiment Microservice
- `server/djangoapp/microservices/sentiment/Dockerfile` - Docker build configuration
- `server/djangoapp/microservices/sentiment/requirements.txt` - Python dependencies (Flask 3.0.0, Gunicorn 22.0.0)
- `server/djangoapp/microservices/sentiment/app.py` - Flask application with sentiment endpoints

### 2. Django Proxy Views
- `server/djangoapp/microservices/dealerships/proxy_views.py` - Proxy endpoints for dealers and reviews
- `server/djangoapp/microservices/dealerships/__init__.py` - Package marker
- `server/djangoapp/microservices/urls.py` - URL routing configuration
- `server/djangoapp/microservices/__init__.py` - Package marker

### 3. Docker Configuration
- `docker-compose.yml` - Orchestration for sentiment and Django services

### 4. Updated Files
- `server/djangoapp/microservices/requirements.txt` - Updated to Django>=4.2.24, requests>=2.28, gunicorn>=22.0.0
- `server/djangoproj/urls.py` - Added include for microservices URLs

## API Endpoints

### Sentiment Analysis Service (Port 8080)
- `GET /analyze/<text>` - Analyze sentiment of URL-encoded text
- `POST /analyze` - Analyze sentiment of JSON payload `{"text": "..."}`

Response format: `{"sentiment": "neutral", "text": "..."}`

### Django Proxy API (Port 8000)
- `GET /api/dealers/` - Fetch all dealers
- `GET /api/dealer/<dealer_id>/` - Fetch specific dealer by ID
- `GET /api/reviews/dealer/<dealer_id>/` - Fetch reviews for dealer (with sentiment analysis)
- `POST /api/review/add/` - Insert new review

## Testing Instructions

### 1. Build and Start Services

```bash
docker compose up --build
```

This will:
- Build the sentiment microservice on port 8080
- Build the Django application on port 8000
- Connect them via Docker network

### 2. Test Sentiment Service

```bash
# Test GET endpoint
curl http://localhost:8080/analyze/hello%20world

# Test POST endpoint
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test"}'
```

Expected response:
```json
{
  "sentiment": "neutral",
  "text": "hello world"
}
```

### 3. Test Django Proxy Endpoints

Note: These endpoints require the Express dealerships service to be running. If not available, they will return server errors.

```bash
# Test dealers endpoint (requires express-service)
curl http://localhost:8000/api/dealers/

# Test dealer by ID (requires express-service)
curl http://localhost:8000/api/dealer/1/

# Test reviews with sentiment (requires express-service)
curl http://localhost:8000/api/reviews/dealer/1/
```

## Environment Variables

The Django service can be configured with these environment variables:

- `DEALERS_SERVICE_URL` - URL of the Express dealerships service (default: `http://express-service:3000`)
- `SENTIMENT_SERVICE_URL` - URL of the sentiment service (default: `http://sentiment:8080`)

## Security Notes

1. **Updated Dependencies**: All dependencies have been updated to patch known security vulnerabilities:
   - Django >= 4.2.24 (fixes SQL injection, DoS, and other vulnerabilities)
   - Gunicorn >= 22.0.0 (fixes HTTP request smuggling)
   - Flask 3.0.0 (latest stable)

2. **Stack Trace Protection**: Error handling logs exceptions internally but does not expose stack traces to external users, preventing information disclosure.

3. **CSRF Protection**: The review insertion endpoint has CSRF exemption as it's designed for API use. Ensure proper authentication is added in production.

## Warnings

⚠️ **Important**: Do not run `find_duplicates.sh --delete` without manual review, as it may remove necessary files.

⚠️ **Development Only**: The sentiment service currently returns "neutral" for all text. This is a placeholder for actual sentiment analysis implementation.

⚠️ **Express Service Required**: The proxy endpoints depend on an external Express service running on port 3000. Without it, these endpoints will return errors.

## Next Steps

1. Implement actual sentiment analysis logic (e.g., using VADER, TextBlob, or ML models)
2. Add authentication to proxy endpoints
3. Implement proper error handling and retry logic for external service calls
4. Add comprehensive tests for proxy views
5. Configure the Express dealerships service
6. Add monitoring and logging for production deployment
