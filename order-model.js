// models/Order.js - Order model for MNC Delivery

const mongoose = require('mongoose');

const OrderSchema = new mongoose.Schema({
  customer: {
    name: {
      type: String,
      required: true
    },
    phone: {
      type: String,
      required: true
    },
    address: {
      street: {
        type: String,
        required: true
      },
      city: {
        type: String,
        required: true
      },
      postalCode: {
        type: String,
        required: true
      }
    }
  },
  items: [{
    name: {
      type: String,
      required: true
    },
    quantity: {
      type: Number,
      required: true,
      min: 1
    },
    price: {
      type: Number,
      required: true
    }
  }],
  restaurant: {
    id: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Restaurant',
      required: true
    },
    name: {
      type: String,
      required: true
    }
  },
  courier: {
    id: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Courier',
      default: null
    },
    name: String
  },
  status: {
    type: String,
    enum: ['pending', 'confirmed', 'preparing', 'out_for_delivery', 'delivered', 'cancelled'],
    default: 'pending'
  },
  totalPrice: {
    type: Number,
    required: true
  },
  paymentMethod: {
    type: String,
    enum: ['cash', 'credit_card', 'digital_wallet'],
    required: true
  },
  estimatedDeliveryTime: {
    type: Date
  },
  actualDeliveryTime: {
    type: Date
  },
  createdAt: {
    type: Date,
    default: Date.now
  },
  updatedAt: {
    type: Date,
    default: Date.now
  }
});

// Update the 'updatedAt' field on save
OrderSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

module.exports = mongoose.model('Order', OrderSchema);
