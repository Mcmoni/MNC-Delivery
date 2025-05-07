#!/usr/bin/env python3
# services/analytics_service.py - Analytics service for MNC Delivery

from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
# In production, use a database
delivery_data = []

# Data file paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DELIVERY_DATA_FILE = os.path.join(DATA_DIR, 'delivery_data.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load existing data if available
def load_data():
    global delivery_data
    try:
        if os.path.exists(DELIVERY_DATA_FILE):
            with open(DELIVERY_DATA_FILE, 'r') as f:
                delivery_data = json.load(f)
            logger.info(f"Loaded {len(delivery_data)} records from data file")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")

# Save data to file
def save_data():
    try:
        with open(DELIVERY_DATA_FILE, 'w') as f:
            json.dump(delivery_data, f)
        logger.info(f"Saved {len(delivery_data)} records to data file")
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")

# Load data on startup
load_data()

@app.route('/analytics', methods=['POST'])
def record_delivery_data():
    """
    Record delivery data for analytics
    """
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['orderId', 'deliveryTime', 'restaurantId', 'courierId']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()
        
        # Store data
        delivery_data.append(data)
        
        # Save to file
        save_data()
        
        logger.info(f"Recorded delivery data for order {data['orderId']}")
        return jsonify({'success': True}), 200
    
    except Exception as e:
        logger.error(f"Error recording delivery data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/performance', methods=['GET'])
def get_delivery_performance():
    """
    Calculate and return delivery performance metrics
    """
    try:
        # Get optional time range parameters
        days = request.args.get('days', default=30, type=int)
        
        # Create DataFrame for analysis
        if not delivery_data:
            return jsonify({
                'message': 'No delivery data available',
                'metrics': {}
            }), 200
        
        df = pd.DataFrame(delivery_data)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by date range if specified
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['timestamp'] >= cutoff_date]
        
        # Calculate metrics
        if len(df) == 0:
            return jsonify({
                'message': f'No delivery data available for the last {days} days',
                'metrics': {}
            }), 200
            
        # Convert deliveryTime to numeric if it's not already
        if not pd.api.types.is_numeric_dtype(df['deliveryTime']):
            df['deliveryTime'] = pd.to_numeric(df['deliveryTime'], errors='coerce')
        
        # Calculate key metrics
        metrics = {
            'total_deliveries': len(df),
            'average_delivery_time_ms': float(df['deliveryTime'].mean()),
            'average_delivery_time_minutes': float(df['deliveryTime'].mean() / (1000 * 60)),
            'fastest_delivery_ms': float(df['deliveryTime'].min()),
            'slowest_delivery_ms': float(df['deliveryTime'].max()),
            'deliveries_by_day': df.groupby(df['timestamp'].dt.date).size().to_dict()
        }
        
        # Calculate courier performance
        courier_performance = df.groupby('courierId')['deliveryTime'].agg(['mean', 'count']).reset_index()
        courier_performance['mean_minutes'] = courier_performance['mean'] / (1000 * 60)
        courier_performance = courier_performance.sort_values('mean')
        
        # Convert to serializable format
        metrics['courier_performance'] = courier_performance.to_dict(orient='records')
        
        # Calculate restaurant performance
        restaurant_performance = df.groupby('restaurantId')['deliveryTime'].agg(['mean', 'count']).reset_index()
        restaurant_performance['mean_minutes'] = restaurant_performance['mean'] / (1000 * 60)
        restaurant_performance = restaurant_performance.sort_values('mean')
        
        # Convert to serializable format
        metrics['restaurant_performance'] = restaurant_performance.to_dict(orient='records')
        
        logger.info("Calculated delivery performance metrics")
        return jsonify({
            'success': True,
            'data': metrics
        }), 200
    
    except Exception as e:
        logger.error(f"Error calculating delivery performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/trends', methods=['GET'])
def get_delivery_trends():
    """
    Analyze delivery trends over time
    """
    try:
        if not delivery_data:
            return jsonify({
                'message': 'No delivery data available',
                'trends': {}
            }), 200
            
        df = pd.DataFrame(delivery_data)
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Add date and hour columns for aggregation
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        
        # Delivery count by date
        daily_counts = df.groupby('date').size().reset_index()
        daily_counts.columns = ['date', 'count']
        
        # Average delivery time by date
        if not pd.api.types.is_numeric_dtype(df['deliveryTime']):
            df['deliveryTime'] = pd.to_numeric(df['deliveryTime'], errors='coerce')
            
        daily_avg_time = df.groupby('date')['deliveryTime'].mean().reset_index()
        daily_avg_time['deliveryTime_minutes'] = daily_avg_time['deliveryTime'] / (1000 * 60)
        
        # Busiest hours
        hourly_counts = df.groupby('hour').size().reset_index()
        hourly_counts.columns = ['hour', 'count']
        busiest_hours = hourly_counts.sort_values('count', ascending=False).head(5)
        
        # Format results
        trends = {
            'daily_counts': [
                {'date': str(row['date']), 'count': int(row['count'])} 
                for _, row in daily_counts.iterrows()
            ],
            'daily_avg_delivery_time': [
                {'date': str(row['date']), 'minutes': float(row['deliveryTime_minutes'])} 
                for _, row in daily_avg_time.iterrows()
            ],
            'busiest_hours': [
                {'hour': int(row['hour']), 'count': int(row['count'])} 
                for _, row in busiest_hours.iterrows()
            ]
        }
        
        return jsonify({
            'success': True,
            'data': trends
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating delivery trends: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analytics/reset', methods=['POST'])
def reset_analytics_data():
    """
    Reset all analytics data (for testing/development purposes)
    """
    try:
        global delivery_data
        delivery_data = []
        
        # Save empty data to file
        save_data()
        
        logger.info("Reset all analytics data")
        return jsonify({'success': True, 'message': 'All analytics data has been reset'}), 200
    
    except Exception as e:
        logger.error(f"Error resetting analytics data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)
