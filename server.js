// server.js
const express = require("express");
const bodyParser = require("body-parser");
const crypto = require("crypto");
const cors = require("cors");

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Fake DB
let users = [
    {
        name: "Pranav",
        phone: "919755967700",
        adhaar: "123456789012",
        passport: "P1234567",
        email: "pranav@example.com",
        address: "Delhi, India"
    },
    {
        name: "Aditya",
        phone: "919876543210",
        adhaar: "987654321098",
        passport: "P7654321",
        email: "aditya@example.com",
        address: "Mumbai, India"
    }
];

let otpStore = {}; // { phone: otp }
let activeSessions = []; // [{ phone, user, status }]

// Generate OTP
app.post("/generate-otp", (req, res) => {
    const { adhaar, passport } = req.body;
    let user = null;

    if (adhaar) user = users.find(u => u.adhaar === adhaar);
    else if (passport) user = users.find(u => u.passport === passport);

    if (!user) {
        return res.status(404).json({ error: "User not found" });
    }

    const otp = crypto.randomInt(100000, 999999).toString();
    otpStore[user.phone] = otp;

    res.json({ phone: user.phone, otp, name: user.name });
});

// Validate OTP
app.post("/validate-otp", (req, res) => {
    const { phone, otp } = req.body;

    if (otpStore[phone] && otpStore[phone] === otp) {
        const user = users.find(u => u.phone === phone);
        delete otpStore[phone];

        // Add to active sessions if not already
        if (!activeSessions.some(s => s.phone === phone)) {
            activeSessions.push({ phone, user, status: "Normal" });
        }

        return res.json({ success: true, message: "Welcome sir", user });
    }

    res.json({ success: false, message: "Invalid OTP" });
});

// Dashboard list
app.get("/dashboard", (req, res) => {
    res.json({ success: true, users: activeSessions });
});

// SOS Trigger
app.post("/sos", (req, res) => {
    const { phone } = req.body;

    let index = activeSessions.findIndex(s => s.phone === phone);
    if (index !== -1) {
        activeSessions[index].status = "SOS";

        // Move to top of list
        const sosUser = activeSessions.splice(index, 1)[0];
        activeSessions.unshift(sosUser);

        return res.json({ success: true, message: "SOS Activated", users: activeSessions });
    }

    res.json({ success: false, message: "User not logged in" });
});

app.listen(5000, () => console.log("✅ Server running on port 5000"));
