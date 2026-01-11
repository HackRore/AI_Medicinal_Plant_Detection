# API Reference - AI Medicinal Plant Detection System

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, most endpoints are public. Authentication endpoints are available for user-specific features.

---

## Prediction Endpoints

### POST /predict/

Upload a leaf image and get plant identification.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "prediction_id": 1,
  "predicted_plant": "Azadirachta_indica",
  "confidence": 0.95,
  "top_predictions": [
    {"class_name": "Azadirachta_indica", "confidence": 0.95},
    {"class_name": "Ocimum_sanctum", "confidence": 0.03}
  ],
  "processing_time_ms": 1250.5,
  "model_version": "demo-v1.0",
  "plant_details": {
    "id": 1,
    "species_name": "Azadirachta_indica",
    "common_name": "Neem",
    "description": "...",
    "image_url": null
  }
}
```

### POST /predict/batch

Batch prediction for multiple images (max 10).

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `files` (array of image files)

**Response:**
```json
{
  "total": 3,
  "successful": 3,
  "results": [
    {
      "filename": "leaf1.jpg",
      "predicted_plant": "Azadirachta_indica",
      "confidence": 0.95,
      "success": true
    }
  ]
}
```

### GET /predict/history

Get prediction history.

**Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (default: 20)

**Response:**
```json
{
  "total": 50,
  "skip": 0,
  "limit": 20,
  "predictions": [
    {
      "id": 1,
      "image_url": "./uploads/20241213_001234_leaf.jpg",
      "predicted_plant": "Azadirachta_indica",
      "common_name": "Neem",
      "confidence": 0.95,
      "created_at": "2024-12-13T00:12:34",
      "feedback_correct": null
    }
  ]
}
```

---

## Plant Information Endpoints

### GET /plants/

List all medicinal plants with pagination.

**Parameters:**
- `skip` (int): Records to skip (default: 0)
- `limit` (int): Max records (default: 50)
- `search` (string): Search query (optional)

**Response:**
```json
{
  "total": 6,
  "skip": 0,
  "limit": 50,
  "plants": [
    {
      "id": 1,
      "species_name": "Azadirachta_indica",
      "common_name": "Neem",
      "common_name_hi": "नीम",
      "description": "Neem is a tree in the mahogany family...",
      "image_url": null
    }
  ]
}
```

### GET /plants/{plant_id}

Get detailed information about a specific plant.

**Response:**
```json
{
  "id": 1,
  "species_name": "Azadirachta_indica",
  "common_names": {
    "en": "Neem",
    "hi": "नीम",
    "ta": "வேம்பு",
    "te": "వేప",
    "bn": "নিম"
  },
  "scientific_classification": {
    "kingdom": "Plantae",
    "family": "Meliaceae",
    "genus": "Azadirachta"
  },
  "description": "...",
  "medicinal_properties": [
    {
      "ailment": "Skin infections",
      "usage": "...",
      "preparation": "...",
      "dosage": "...",
      "precautions": "...",
      "efficacy_rating": 5
    }
  ]
}
```

### GET /plants/search/by-name

Search plants by name.

**Parameters:**
- `q` (string): Search query (min 2 characters)

---

## Explainability Endpoints

### POST /explain/gradcam

Generate Grad-CAM visualization.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "prediction": {
    "predicted_class": "Azadirachta_indica",
    "confidence": 0.95
  },
  "gradcam_overlay": "data:image/png;base64,...",
  "heatmap": "data:image/png;base64,...",
  "explanation": "The highlighted regions show...",
  "method": "Grad-CAM"
}
```

### POST /explain/lime

Generate LIME explanation.

**Response:**
```json
{
  "prediction": {...},
  "lime_visualization": "data:image/png;base64,...",
  "top_features": [
    {"feature": "Leaf shape", "importance": 0.42, "positive": true}
  ],
  "explanation": "LIME highlights image regions...",
  "method": "LIME"
}
```

---

## Recommendation Endpoints

### GET /recommend/similar/{plant_id}

Get similar plants based on medicinal properties.

**Parameters:**
- `limit` (int): Number of recommendations (default: 5)

**Response:**
```json
{
  "plant_id": 1,
  "count": 3,
  "recommendations": [
    {
      "id": 2,
      "species_name": "Ocimum_sanctum",
      "common_name": "Holy Basil",
      "similarity_score": 0.85,
      "reason": "Similar medicinal properties"
    }
  ]
}
```

### POST /recommend/ailment

Get plants for a specific ailment.

**Parameters:**
- `ailment` (string): Ailment or condition

---

## Gemini AI Endpoints

### POST /gemini/describe

Get AI-generated plant description.

**Request:**
```json
{
  "file": "<image>",
  "language": "en"
}
```

### POST /gemini/chat

Chat about a plant.

**Request:**
```json
{
  "plant_id": 1,
  "question": "What are the side effects?"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Default rate limit: 60 requests per minute per IP.

---

## Interactive Documentation

Visit `/docs` for interactive Swagger UI documentation.
Visit `/redoc` for ReDoc documentation.
