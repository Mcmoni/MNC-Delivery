# MNC Delivery App

## Project Structure

```
mnc-delivery/
├── backend/
│   ├── server.js            # Node.js Express server entry point
│   ├── routes/              
│   │   └── api.js           # API routes for the application
│   ├── controllers/         
│   │   └── deliveryController.js  # Business logic
│   ├── models/              
│   │   └── Order.js         # Data models
│   └── config/              
│       └── db.js            # Database configuration
├── services/
│   ├── notification_service.py  # Python service for push notifications
│   └── analytics_service.py     # Python service for delivery analytics
├── frontend/
│   ├── public/              
│   │   ├── index.html       # Main HTML file
│   │   └── styles.css       # Stylesheet
│   └── scripts/             
│       └── app.js           # Frontend JavaScript
└── package.json             # Node.js dependencies and scripts
```

This structure organizes our application into backend (Node.js), services (Python), and frontend components.
