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
        phone: "917559677000", // WhatsApp number (dummy)
        adhaar: "123456789012",
        passport: "P1234567",
        email: "pranav@example.com",
        address: "Delhi, India"
    },
    {
        name: "Aditya",
        phone: "918765432100", // WhatsApp number (dummy)
        adhaar: "987654321098",
        passport: "P7654321",
        email: "aditya@example.com",
        address: "Mumbai, India"
    }
];

let otpStore = {}; // { phone: {otp, adhaar, passport, timestamp} }
let activeSessions = []; // [{ phone, user, status, loginTime }]
let efirRecords = []; // [{ ref_id, phone, complaint, location, timestamp }]
let ratings = []; // [{ phone, rating, feedback, timestamp }]

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
    otpStore[user.phone] = {
        otp,
        adhaar: user.adhaar,
        passport: user.passport,
        timestamp: new Date().toISOString()
    };

    res.json({ 
        phone: user.phone, 
        otp, 
        name: user.name,
        message: "OTP generated successfully. It will be sent via WhatsApp shortly."
    });
});

// Validate OTP
app.post("/validate-otp", (req, res) => {
    const { phone, otp } = req.body;

    // Check if OTP is expired (5 minutes)
    if (otpStore[phone] && (new Date() - new Date(otpStore[phone].timestamp)) > 5 * 60 * 1000) {
        delete otpStore[phone];
        return res.json({ success: false, message: "OTP expired" });
    }

    if (otpStore[phone] && otpStore[phone].otp === otp) {
        const user = users.find(u => u.phone === phone);
        const { adhaar, passport } = otpStore[phone];
        delete otpStore[phone];

        // Add to active sessions if not already
        if (!activeSessions.some(s => s.phone === phone)) {
            activeSessions.push({ 
                phone, 
                user, 
                status: "Normal", 
                loginTime: new Date().toISOString() 
            });
        }

        return res.json({ 
            success: true, 
            message: "Login successful", 
            user,
            adhaar,
            passport
        });
    }

    res.json({ success: false, message: "Invalid OTP" });
});

// Dashboard list
app.get("/dashboard", (req, res) => {
    res.json({ success: true, users: activeSessions });
});

// Get pending OTP requests
app.get("/pending-otp", (req, res) => {
    const pending = [];
    for (const [phone, data] of Object.entries(otpStore)) {
        const user = users.find(u => u.phone === phone);
        if (user) {
            pending.push({
                phone,
                otp: data.otp,
                name: user.name,
                adhaar: data.adhaar,
                passport: data.passport,
                timestamp: data.timestamp
            });
        }
    }
    res.json({ success: true, pending });
});

// Mark OTP as sent
app.post("/mark-otp-sent", (req, res) => {
    const { phone } = req.body;
    
    if (otpStore[phone]) {
        otpStore[phone].sent = true;
        res.json({ success: true, message: "OTP marked as sent" });
    } else {
        res.json({ success: false, message: "OTP not found" });
    }
});

// SOS Trigger
app.post("/sos", (req, res) => {
    const { phone } = req.body;

    let index = activeSessions.findIndex(s => s.phone === phone);
    if (index !== -1) {
        activeSessions[index].status = "SOS";
        activeSessions[index].sosTime = new Date().toISOString();

        // Move to top of list
        const sosUser = activeSessions.splice(index, 1)[0];
        activeSessions.unshift(sosUser);

        return res.json({ success: true, message: "SOS Activated", users: activeSessions });
    }

    res.json({ success: false, message: "User not logged in" });
});

// e-FIR Filing
app.post("/efir", (req, res) => {
    const { phone, complaint, location } = req.body;
    
    const user = users.find(u => u.phone === phone);
    if (!user) {
        return res.json({ success: false, message: "User not found" });
    }
    
    const ref_id = crypto.randomBytes(8).toString('hex');
    const timestamp = new Date().toISOString();
    
    efirRecords.push({
        ref_id,
        phone,
        name: user.name,
        complaint,
        location,
        timestamp
    });
    
    res.json({ 
        success: true, 
        message: "e-FIR filed successfully",
        ref_id 
    });
});

// Submit Rating
app.post("/rating", (req, res) => {
    const { phone, rating, feedback } = req.body;
    
    const user = users.find(u => u.phone === phone);
    if (!user) {
        return res.json({ success: false, message: "User not found" });
    }
    
    const timestamp = new Date().toISOString();
    
    ratings.push({
        phone,
        name: user.name,
        rating,
        feedback,
        timestamp
    });
    
    res.json({ 
        success: true, 
        message: "Rating submitted successfully"
    });
});

// Get e-FIR records
app.get("/efir/:phone", (req, res) => {
    const { phone } = req.params;
    const userEfirs = efirRecords.filter(record => record.phone === phone);
    
    res.json({ success: true, records: userEfirs });
});

// Get all login logs
app.get("/logs", (req, res) => {
    const logs = activeSessions.map(session => ({
        name: session.user.name,
        phone: session.phone,
        status: session.status,
        loginTime: session.loginTime,
        sosTime: session.sosTime || "N/A"
    }));
    
    res.json({ success: true, logs });
});

// Remove user from active sessions (logout)
app.post("/logout", (req, res) => {
    const { phone } = req.body;
    const index = activeSessions.findIndex(s => s.phone === phone);
    
    if (index !== -1) {
        activeSessions.splice(index, 1);
        res.json({ success: true, message: "Logged out successfully" });
    } else {
        res.json({ success: false, message: "User not found in active sessions" });
    }
});

app.listen(5000, () => console.log("✅ Server running on port 5000"));
