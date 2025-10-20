# Frontend-Backend Integration Guide

## Overview
This document describes how to use the frontend [ai_search.html](file:///C:/Users/MSI/Desktop/tchaller/frontend/ai_search.html) with the backend API at https://tchallerback.onrender.com.

## Frontend Files
1. **[ai_search.html](file:///C:/Users/MSI/Desktop/tchaller/frontend/ai_search.html)** - Main search interface
2. **[test_connection.html](file:///C:/Users/MSI/Desktop/tchaller/frontend/test_connection.html)** - Connection testing tool

## Backend API Endpoints
- **Health Check**: `https://tchallerback.onrender.com/health`
- **Search Endpoint**: `https://tchallerback.onrender.com/api/v1/search/`

## How to Use the Frontend

### 1. Open the Frontend
Simply open [ai_search.html](file:///C:/Users/MSI/Desktop/tchaller/frontend/ai_search.html) in a web browser.

### 2. Perform a Search
You can search in two ways:
- Type your query in the search box and press Enter or click "Envoyer"
- Click on one of the predefined tags (Pharmacies, Hôpitaux, Écoles, Garages, Banques)

### 3. View Results
Search results will be displayed below the search box with:
- Business name
- Address and distance
- Rating and price level
- Description
- Contact information (phone, WhatsApp, email, website)

## Search Request Format
The frontend sends POST requests to the search endpoint with the following JSON structure:

```json
{
  "query": "pharmacie",
  "latitude": -4.05,
  "longitude": 5.35,
  "radius": 10000,
  "limit": 5
}
```

## Search Response Format
The backend returns search results in the following format:

```json
{
  "query": "pharmacie",
  "processed_query": "pharmacie",
  "intent": "search_place",
  "entities": {
    "category": "sante"
  },
  "activities": [
    {
      "id": 19,
      "name": "Pharmacie Centrale",
      "description": "Pharmacie communautaire avec prix abordables.",
      "address": "Rue des Jardins, Cocody",
      "latitude": 5.352417584269034,
      "longitude": -4.056631447004233,
      "category_id": 1,
      "category_name": "Santé",
      "phone_number": "+2250794520607",
      "whatsapp_number": "+2250794520607",
      "email": "contact@pharmaciecentrale.ci",
      "website": "https://pharmaciecentrale.ci",
      "opening_hours": {
        "monday": "08:00-20:00",
        "tuesday": "08:00-20:00"
      },
      "price_level": 2,
      "rating": 4.6,
      "review_count": 163,
      "is_verified": true,
      "is_active": true,
      "distance": 780.89916627,
      "media": [],
      "reviews": []
    }
  ],
  "total_results": 4,
  "response_time": 2.1623148918151855,
  "suggestions": [
    "Voir plus de santé",
    "Activités près de moi",
    "Activités ouvertes maintenant"
  ],
  "filters_applied": {
    "radius": 5000
  }
}
```

## Troubleshooting

### No Results Found
If searches return no results:
1. Verify the backend is running by visiting https://tchallerback.onrender.com/health
2. Check that the coordinates are correct (latitude: -4.05, longitude: 5.35 for Abidjan)
3. Try a different search query

### Connection Errors
If you see connection errors:
1. Ensure you have internet connectivity
2. Check that the backend URL is correct
3. Verify that your browser is not blocking cross-origin requests

## Testing the Connection
Use the [test_connection.html](file:///C:/Users/MSI/Desktop/tchaller/frontend/test_connection.html) file to verify that:
1. The backend is accessible
2. The search endpoint is working correctly
3. Data can be retrieved and displayed properly