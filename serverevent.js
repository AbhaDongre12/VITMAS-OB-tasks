const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
const mongoURI = 'mongodb://localhost:27017/eventdb';  // Replace if using cloud MongoDB
mongoose.connect(mongoURI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB'))
.catch((err) => console.error('MongoDB connection error:', err));

// Define registration schema
const registrationSchema = new mongoose.Schema({
  domainpref: { type: String, required: true },
  event: { type: String, required: true },
  registeredAt: { type: Date, default: Date.now }
});

// Create model
const Registration = mongoose.model('Registration', registrationSchema);
app.use(express.static(path.join(__dirname, 'public')));

// POST endpoint to save registration
app.post('/register', async (req, res) => {
  console.log('Received:', req.body);
  try {
    const { domainpref, event } = req.body;

    if (!domainpref || !event) {
      return res.status(400).json({ message: 'Please provide all required fields.' });
    }

    const newRegistration = new Registration({ domainpref, event });
    await newRegistration.save();

    res.status(201).json({ message: 'Registration successful!' });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error, please try again.' });
  }
});

// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
