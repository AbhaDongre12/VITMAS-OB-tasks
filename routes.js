const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const User = require("../models/User");

const router = express.Router();

// Signup
router.post("/signup", async (req, res) => {
    console.log("Signup route hit");
  console.log("Request body:", req.body);
  const { fullname, regno, email, password, branch } = req.body;
  try {
    const existingUser = await User.findOne({ email });
    if (existingUser) {
        console.log("User already exists with email:", email);
        return res.status(400).json({ message: "User already exists" });
    }
  const hashedPassword = await bcrypt.hash(password, 10);

  const newUser = new User({ fullname, regno, email, password: hashedPassword, branch });
  await newUser.save();
  console.log("User created:", newUser);
  res.status(201).json({ message: "User created successfully" });
  } catch (err) {
    console.error("Signup error:", err);
    res.status(500).json({ message: "Server error during signup" });
  }
});

// Login
router.post("/login", async (req, res) => {
    console.log("Login route called");
    console.log("Request body:", req.body);
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ message: "Invalid email or password" });

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ message: "Invalid email or password" });

    const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "1d" });

    res.json({ token });
});

// Get user details
router.get("/me", async (req, res) => {
  const token = req.headers.authorization?.split(" ")[1];
  if (!token) return res.status(401).json({ message: "Token required" });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    const user = await User.findById(decoded.id).select("-password");
    res.json(user);
  } catch {
    res.status(401).json({ message: "Invalid token" });
  }
});

module.exports = router;
