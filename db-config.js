// config/db.js - Database configuration for MNC Delivery

const mongoose = require('mongoose');

// MongoDB connection URI
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/mnc_delivery';

// Connect to MongoDB
const connectDB = async () => {
  try {
    await mongoose.connect(MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB connected successfully');
  } catch (error) {
    console.error('MongoDB connection failed:', error.message);
    // Exit process with failure
    process.exit(1);
  }
};

// Disconnect from MongoDB
const disconnectDB = async () => {
  try {
    await mongoose.disconnect();
    console.log('MongoDB disconnected');
  } catch (error) {
    console.error('Error disconnecting from MongoDB:', error.message);
  }
};

module.exports = { connectDB, disconnectDB };
