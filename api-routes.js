// routes/api.js - API routes for MNC Delivery

const express = require('express');
const router = express.Router();
const deliveryController = require('../controllers/deliveryController');

// Order routes
router.post('/orders', deliveryController.createOrder);
router.get('/orders', deliveryController.getAllOrders);
router.get('/orders/:id', deliveryController.getOrderById);
router.put('/orders/:id', deliveryController.updateOrder);
router.delete('/orders/:id', deliveryController.deleteOrder);

// Courier routes
router.get('/couriers', deliveryController.getAllCouriers);
router.get('/couriers/available', deliveryController.getAvailableCouriers);
router.post('/couriers/:id/assign/:orderId', deliveryController.assignCourierToOrder);

// Tracking routes
router.get('/tracking/:orderId', deliveryController.trackOrder);
router.put('/tracking/:orderId/status', deliveryController.updateOrderStatus);

// Restaurant routes
router.get('/restaurants', deliveryController.getAllRestaurants);
router.get('/restaurants/:id/orders', deliveryController.getRestaurantOrders);

// Customer routes
router.get('/customers/:phone/orders', deliveryController.getCustomerOrders);

// Analytics routes
router.get('/analytics/performance', deliveryController.getDeliveryPerformance);

module.exports = router;
