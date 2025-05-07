// controllers/deliveryController.js - Controller for MNC Delivery

const Order = require('../models/Order');
const axios = require('axios');

// Python service endpoints
const NOTIFICATION_SERVICE = 'http://localhost:5001/notify';
const ANALYTICS_SERVICE = 'http://localhost:5002/analytics';

// Order Controllers
exports.createOrder = async (req, res) => {
  try {
    const newOrder = new Order(req.body);
    const savedOrder = await newOrder.save();

    // Notify restaurant and nearby couriers about new order
    await axios.post(NOTIFICATION_SERVICE, {
      type: 'new_order',
      orderId: savedOrder._id,
      restaurantId: savedOrder.restaurant.id
    });

    res.status(201).json({
      success: true,
      data: savedOrder
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message
    });
  }
};

exports.getAllOrders = async (req, res) => {
  try {
    const orders = await Order.find().sort({ createdAt: -1 });
    res.status(200).json({
      success: true,
      count: orders.length,
      data: orders
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

exports.getOrderById = async (req, res) => {
  try {
    const order = await Order.findById(req.params.id);
    
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

exports.updateOrder = async (req, res) => {
  try {
    const order = await Order.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: order
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message
    });
  }
};

exports.deleteOrder = async (req, res) => {
  try {
    const order = await Order.findByIdAndDelete(req.params.id);
    
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: {}
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

// Courier Controllers
exports.getAllCouriers = async (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Get all couriers - Function to be implemented'
  });
};

exports.getAvailableCouriers = async (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Get available couriers - Function to be implemented'
  });
};

exports.assignCourierToOrder = async (req, res) => {
  try {
    const { id: courierId, orderId } = req.params;
    
    const order = await Order.findById(orderId);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    // Update order with courier info (simplified for example)
    order.courier = {
      id: courierId,
      name: req.body.courierName || 'Delivery Courier'
    };
    order.status = 'confirmed';
    
    await order.save();
    
    // Notify customer about order confirmation
    await axios.post(NOTIFICATION_SERVICE, {
      type: 'order_assigned',
      orderId: orderId,
      courierId: courierId,
      customerPhone: order.customer.phone
    });
    
    res.status(200).json({
      success: true,
      data: order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

// Tracking Controllers
exports.trackOrder = async (req, res) => {
  try {
    const { orderId } = req.params;
    const order = await Order.findById(orderId);
    
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    res.status(200).json({
      success: true,
      data: {
        orderId: order._id,
        status: order.status,
        estimatedDeliveryTime: order.estimatedDeliveryTime,
        currentLocation: 'Location tracking feature to be implemented'
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

exports.updateOrderStatus = async (req, res) => {
  try {
    const { orderId } = req.params;
    const { status } = req.body;
    
    const order = await Order.findById(orderId);
    if (!order) {
      return res.status(404).json({
        success: false,
        message: 'Order not found'
      });
    }
    
    // Validate status transition
    const validStatuses = ['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'];
    if (!validStatuses.includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid order status'
      });
    }
    
    order.status = status;
    
    // If status is delivered, set actual delivery time
    if (status === 'delivered') {
      order.actualDeliveryTime = new Date();
      
      // Send order data to analytics service
      await axios.post(ANALYTICS_SERVICE, {
        orderId: orderId,
        deliveryTime: order.actualDeliveryTime - order.createdAt,
        restaurantId: order.restaurant.id,
        courierId: order.courier.id
      });
    }
    
    await order.save();
    
    // Notify customer about status update
    await axios.post(NOTIFICATION_SERVICE, {
      type: 'status_update',
      orderId: orderId,
      status: status,
      customerPhone: order.customer.phone
    });
    
    res.status(200).json({
      success: true,
      data: order
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: error.message
    });
  }
};

// Restaurant Controllers
exports.getAllRestaurants = async (req, res) => {
  res.status(200).json({
    success: true,
    message: 'Get all restaurants - Function to be implemented'
  });
};

exports.getRestaurantOrders = async (req, res) => {
  try {
    const { id: restaurantId } = req.params;
    
    const orders = await Order.find({
      'restaurant.id': restaurantId
    }).sort({ createdAt: -1 });
    
    res.status(200).json({
      success: true,
      count: orders.length,
      data: orders
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

// Customer Controllers
exports.getCustomerOrders = async (req, res) => {
  try {
    const { phone } = req.params;
    
    const orders = await Order.find({
      'customer.phone': phone
    }).sort({ createdAt: -1 });
    
    res.status(200).json({
      success: true,
      count: orders.length,
      data: orders
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Server Error'
    });
  }
};

// Analytics Controllers
exports.getDeliveryPerformance = async (req, res) => {
  try {
    // Call Python analytics service
    const response = await axios.get(ANALYTICS_SERVICE + '/performance');
    
    res.status(200).json({
      success: true,
      data: response.data
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      message: 'Analytics service unavailable'
    });
  }
};
