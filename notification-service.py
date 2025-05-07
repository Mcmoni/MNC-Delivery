#!/usr/bin/env python3
# services/notification_service.py - Notification service for MNC Delivery

from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SMS API configuration (example service)
SMS_API_KEY = os.environ.get('SMS_API_KEY', 'sms_api_key_placeholder')
SMS_API_URL = os.environ.get('SMS_API_URL', 'https://api.smsservice.com/send')

# Push notification service configuration
PUSH_API_KEY = os.environ.get('PUSH_API_KEY', 'push_api_key_placeholder')
PUSH_API_URL = os.environ.get('PUSH_API_URL', 'https://api.pushservice.com/send')

# In-memory notification storage for demo purposes
# In production, use a database
notifications = []

@app.route('/notify', methods=['POST'])
def send_notification():
    """
    Send notifications to various stakeholders based on the notification type.
    """
    try:
        data = request.json
        notification_type = data.get('type')
        
        if not notification_type:
            return jsonify({'error': 'Notification type is required'}), 400
        
        # Store notification
        notification = {
            'id': len(notifications) + 1,
            'type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        notifications.append(notification)
        
        # Process notification based on type
        if notification_type == 'new_order':
            # Notify restaurant
            restaurant_message = f"New order received (ID: {data.get('orderId')}). Please confirm."
            _send_sms_to_restaurant(data.get('restaurantId'), restaurant_message)
            
            # Find nearby couriers (simplified)
            _notify_nearby_couriers(data.get('orderId'), data.get('restaurantId'))
            
        elif notification_type == 'order_assigned':
            # Notify customer
            customer_message = f"Your order has been confirmed and assigned to a courier."
            _send_sms_to_customer(data.get('customerPhone'), customer_message)
            
        elif notification_type == 'status_update':
            # Notify customer about status change
            status = data.get('status')
            customer_message = f"Your order status has been updated to: {status}"
            _send_sms_to_customer(data.get('customerPhone'), customer_message)
            
            # Additional notifications based on status
            if status == 'out_for_delivery':
                push_message = f"Your delivery is on the way! Track it in the app."
                _send_push_notification(data.get('customerPhone'), push_message)
            
            elif status == 'delivered':
                thank_you_message = f"Thank you for using MNC Delivery! Please rate your experience."
                _send_push_notification(data.get('customerPhone'), thank_you_message)
        
        logger.info(f"Notification processed: {notification_type}")
        return jsonify({'success': True, 'notification_id': notification['id']}), 200
    
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Retrieve notifications with optional filtering
    """
    notification_type = request.args.get('type')
    
    if notification_type:
        filtered_notifications = [n for n in notifications if n['type'] == notification_type]
        return jsonify(filtered_notifications), 200
    
    return jsonify(notifications), 200

def _send_sms_to_restaurant(restaurant_id, message):
    """
    Send SMS to restaurant (mock implementation)
    """
    logger.info(f"SMS to Restaurant {restaurant_id}: {message}")
    # In a real implementation, call the SMS API
    # requests.post(SMS_API_URL, json={
    #     'apiKey': SMS_API_KEY,
    #     'to': _get_restaurant_phone(restaurant_id),
    #     'message': message
    # })

def _send_sms_to_customer(phone, message):
    """
    Send SMS to customer (mock implementation)
    """
    logger.info(f"SMS to Customer {phone}: {message}")
    # In a real implementation, call the SMS API
    # requests.post(SMS_API_URL, json={
    #     'apiKey': SMS_API_KEY,
    #     'to': phone,
    #     'message': message
    # })

def _send_push_notification(user_id, message):
    """
    Send push notification to user (mock implementation)
    """
    logger.info(f"Push to User {user_id}: {message}")
    # In a real implementation, call the Push Notification API
    # requests.post(PUSH_API_URL, json={
    #     'apiKey': PUSH_API_KEY,
    #     'userId': user_id,
    #     'message': message
    # })

def _notify_nearby_couriers(order_id, restaurant_id):
    """
    Notify nearby couriers about a new order (mock implementation)
    """
    logger.info(f"Notifying couriers about order {order_id} from restaurant {restaurant_id}")
    # In a real implementation, this would query for nearby couriers
    # and send them push notifications

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
