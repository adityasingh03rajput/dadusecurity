const express = require("express");
const bodyParser = require("body-parser");
const crypto = require("crypto");
const cors = require("cors");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(bodyParser.json());
app.use(cors());

// Blockchain simulation for Digital ID
class Block {
    constructor(index, timestamp, data, previousHash = '') {
        this.index = index;
        this.timestamp = timestamp;
        this.data = data;
        this.previousHash = previousHash;
        this.hash = this.calculateHash();
        this.nonce = 0;
    }

    calculateHash() {
        return crypto.createHash('sha256')
            .update(this.index + this.timestamp + JSON.stringify(this.data) + this.previousHash + this.nonce)
            .digest('hex');
    }

    mineBlock(difficulty) {
        while (this.hash.substring(0, difficulty) !== Array(difficulty + 1).join("0")) {
            this.nonce++;
            this.hash = this.calculateHash();
        }
        console.log("Block mined: " + this.hash);
    }
}

class Blockchain {
    constructor() {
        this.chain = [this.createGenesisBlock()];
        this.difficulty = 2;
    }

    createGenesisBlock() {
        return new Block(0, new Date().toISOString(), { message: "Genesis Block" }, "0");
    }

    getLatestBlock() {
        return this.chain[this.chain.length - 1];
    }

    addBlock(newBlock) {
        newBlock.previousHash = this.getLatestBlock().hash;
        newBlock.mineBlock(this.difficulty);
        this.chain.push(newBlock);
    }

    isChainValid() {
        for (let i = 1; i < this.chain.length; i++) {
            const currentBlock = this.chain[i];
            const previousBlock = this.chain[i - 1];

            if (currentBlock.hash !== currentBlock.calculateHash()) {
                return false;
            }

            if (currentBlock.previousHash !== previousBlock.hash) {
                return false;
            }
        }
        return true;
    }
}

// Initialize blockchain
const touristIDChain = new Blockchain();

// Evidence logging system
class EvidenceLog {
    constructor() {
        this.logs = [];
        this.logFile = path.join(__dirname, 'evidence_logs.json');
        this.loadLogs();
    }

    loadLogs() {
        try {
            if (fs.existsSync(this.logFile)) {
                const data = fs.readFileSync(this.logFile, 'utf8');
                this.logs = JSON.parse(data);
            }
        } catch (err) {
            console.error('Error loading evidence logs:', err);
            this.logs = [];
        }
    }

    saveLogs() {
        try {
            fs.writeFileSync(this.logFile, JSON.stringify(this.logs, null, 2));
        } catch (err) {
            console.error('Error saving evidence logs:', err);
        }
    }

    addLog(userId, eventType, data) {
        const logEntry = {
            id: crypto.randomBytes(16).toString('hex'),
            userId,
            eventType,
            data,
            timestamp: new Date().toISOString(),
            hash: ''
        };

        // Create hash of the log entry (for tamper-proofing)
        logEntry.hash = crypto.createHash('sha256')
            .update(JSON.stringify({
                id: logEntry.id,
                userId: logEntry.userId,
                eventType: logEntry.eventType,
                data: logEntry.data,
                timestamp: logEntry.timestamp
            }))
            .digest('hex');

        this.logs.push(logEntry);
        this.saveLogs();
        return logEntry;
    }

    getUserLogs(userId) {
        return this.logs.filter(log => log.userId === userId);
    }

    verifyLogIntegrity() {
        for (let i = 0; i < this.logs.length; i++) {
            const log = this.logs[i];
            const calculatedHash = crypto.createHash('sha256')
                .update(JSON.stringify({
                    id: log.id,
                    userId: log.userId,
                    eventType: log.eventType,
                    data: log.data,
                    timestamp: log.timestamp
                }))
                .digest('hex');

            if (calculatedHash !== log.hash) {
                return { valid: false, tampered: log };
            }
        }
        return { valid: true };
    }
}

const evidenceLogger = new EvidenceLog();

// Fake DB
let users = [
    {
        id: "1",
        name: "Pranav Sharma",
        phone: "917559677000", // WhatsApp number
        adhaar: "123456789012",
        passport: "P1234567",
        email: "pranav@example.com",
        address: "Delhi, India",
        emergencyContacts: [
            { name: "Amit Sharma", relation: "Father", phone: "919876543210" },
            { name: "Priya Sharma", relation: "Mother", phone: "919876543211" }
        ],
        digitalId: null,
        preferences: {
            language: "en",
            voiceAssistance: false,
            realTimeTracking: false
        }
    },
    {
        id: "2",
        name: "Aditya Patel",
        phone: "918765432100", // WhatsApp number
        adhaar: "987654321098",
        passport: "P7654321",
        email: "aditya@example.com",
        address: "Mumbai, India",
        emergencyContacts: [
            { name: "Rajesh Patel", relation: "Father", phone: "919876543212" }
        ],
        digitalId: null,
        preferences: {
            language: "hi",
            voiceAssistance: false,
            realTimeTracking: false
        }
    }
];

// Danger zones (for geo-fencing alerts)
let dangerZones = [
    {
        id: "1",
        name: "Flood Area",
        coordinates: { lat: 28.6139, lng: 77.2090 },
        radius: 5, // km
        type: "natural_disaster",
        active: true,
        createdAt: new Date().toISOString()
    },
    {
        id: "2",
        name: "High Crime Area",
        coordinates: { lat: 19.0760, lng: 72.8777 },
        radius: 3, // km
        type: "crime",
        active: true,
        createdAt: new Date().toISOString()
    }
];

// Trip itineraries
let tripItineraries = [];

// Tourist locations with ratings
let touristLocations = [
    {
        id: "1",
        name: "Taj Mahal",
        city: "Agra",
        coordinates: { lat: 27.1751, lng: 78.0421 },
        description: "One of the seven wonders of the world",
        rating: 4.8,
        reviews: [],
        images: ["taj_mahal.jpg"],
        category: ["historical", "monument"]
    },
    {
        id: "2",
        name: "Gateway of India",
        city: "Mumbai",
        coordinates: { lat: 18.9217, lng: 72.8347 },
        description: "Historic arch monument built during the 20th century",
        rating: 4.5,
        reviews: [],
        images: ["gateway.jpg"],
        category: ["historical", "monument"]
    },
    {
        id: "3",
        name: "Jaipur City Palace",
        city: "Jaipur",
        coordinates: { lat: 26.9255, lng: 75.8236 },
        description: "A palace complex in Jaipur, the capital of Rajasthan",
        rating: 4.6,
        reviews: [],
        images: ["jaipur_palace.jpg"],
        category: ["historical", "palace"]
    }
];

let otpStore = {}; // { phone: {otp, adhaar, passport, timestamp} }
let activeSessions = []; // [{ phone, user, status, loginTime, location }]
let efirRecords = []; // [{ ref_id, phone, complaint, location, timestamp }]
let ratings = []; // [{ phone, rating, feedback, timestamp }]
let sosAlerts = []; // [{ id, userId, location, status, timestamp, responderId }]
let responders = []; // [{ id, type, name, location, status }]

// Languages supported
const supportedLanguages = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "te": "Telugu",
    "mr": "Marathi",
    "ta": "Tamil",
    "ur": "Urdu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
};

// Translations (simplified example)
const translations = {
    "welcome": {
        "en": "Welcome to Tourist Safety App",
        "hi": "पर्यटक सुरक्षा ऐप में आपका स्वागत है",
        "bn": "পর্যটক সুরক্ষা অ্যাপে স্বাগতম"
        // Add more languages as needed
    },
    "sos_sent": {
        "en": "SOS alert sent! Help is on the way.",
        "hi": "SOS अलर्ट भेजा गया! सहायता आ रही है।",
        "bn": "SOS সতর্কতা পাঠানো হয়েছে! সাহায্য আসছে।"
        // Add more languages as needed
    }
    // Add more translation keys as needed
};

// Helper function to get translation
function getTranslation(key, lang = "en") {
    if (!translations[key]) return "Translation missing";
    return translations[key][lang] || translations[key]["en"];
}

// Generate Digital ID
function generateDigitalId(user) {
    const digitalIdData = {
        userId: user.id,
        name: user.name,
        idType: user.adhaar ? "adhaar" : "passport",
        idNumber: user.adhaar || user.passport,
        issuedAt: new Date().toISOString(),
        validUntil: new Date(new Date().setFullYear(new Date().getFullYear() + 5)).toISOString(),
        biometricHash: crypto.randomBytes(32).toString('hex') // Simulated biometric hash
    };

    // Add to blockchain
    const newBlock = new Block(
        touristIDChain.chain.length,
        new Date().toISOString(),
        digitalIdData
    );
    touristIDChain.addBlock(newBlock);

    // Log the event
    evidenceLogger.addLog(user.id, "DIGITAL_ID_CREATED", {
        digitalIdHash: newBlock.hash,
        timestamp: newBlock.timestamp
    });

    return {
        id: newBlock.hash.substring(0, 16),
        blockchainRef: newBlock.hash,
        issuedAt: digitalIdData.issuedAt,
        validUntil: digitalIdData.validUntil
    };
}

// E-KYC Verification (simulated)
function verifyEKYC(idType, idNumber, userData) {
    // In a real implementation, this would call an external E-KYC API
    return new Promise((resolve) => {
        setTimeout(() => {
            // Simulate verification
            const isVerified = true;
            const verificationData = {
                verified: isVerified,
                verificationId: crypto.randomBytes(8).toString('hex'),
                timestamp: new Date().toISOString()
            };

            if (isVerified && userData.id) {
                evidenceLogger.addLog(userData.id, "E_KYC_VERIFIED", {
                    idType,
                    verificationId: verificationData.verificationId,
                    timestamp: verificationData.timestamp
                });
            }

            resolve(verificationData);
        }, 1500); // Simulate API delay
    });
}

// Calculate distance between two coordinates (in km)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a = 
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
        Math.sin(dLon/2) * Math.sin(dLon/2); 
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    const d = R * c; // Distance in km
    return d;
}

function deg2rad(deg) {
    return deg * (Math.PI/180);
}

// Check if user is in danger zone
function checkDangerZones(userLocation) {
    const alerts = [];
    
    dangerZones.forEach(zone => {
        if (!zone.active) return;
        
        const distance = calculateDistance(
            userLocation.lat, userLocation.lng,
            zone.coordinates.lat, zone.coordinates.lng
        );
        
        if (distance <= zone.radius) {
            alerts.push({
                zoneId: zone.id,
                zoneName: zone.name,
                zoneType: zone.type,
                distance: distance.toFixed(2)
            });
        }
    });
    
    return alerts;
}

// Generate OTP
app.post("/generate-otp", (req, res) => {
    const { adhaar, passport, language = "en" } = req.body;
    let user = null;

    if (adhaar) user = users.find(u => u.adhaar === adhaar);
    else if (passport) user = users.find(u => u.passport === passport);

    if (!user) {
        return res.status(404).json({ error: "User not found" });
    }

    const otp = crypto.randomInt(100000, 999999).toString();
    const timestamp = new Date().toISOString();
    
    otpStore[user.phone] = {
        otp,
        adhaar: user.adhaar,
        passport: user.passport,
        timestamp
    };

    // Log the OTP generation event
    evidenceLogger.addLog(user.id, "OTP_GENERATED", {
        timestamp,
        method: adhaar ? "adhaar" : "passport"
    });

    res.json({ 
        phone: user.phone, 
        otp, 
        name: user.name,
        message: getTranslation("otp_generated", language)
    });
});

// Validate OTP
app.post("/validate-otp", (req, res) => {
    const { phone, otp, location, language = "en" } = req.body;

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
                loginTime: new Date().toISOString(),
                location: location || null
            });
        }

        // Log the login event
        evidenceLogger.addLog(user.id, "USER_LOGIN", {
            timestamp: new Date().toISOString(),
            location: location || "unknown"
        });

        // Check if user has a digital ID, if not create one
        if (!user.digitalId) {
            user.digitalId = generateDigitalId(user);
        }

        return res.json({ 
            success: true, 
            message: getTranslation("login_successful", language), 
            user: {
                id: user.id,
                name: user.name,
                phone: user.phone,
                email: user.email,
                digitalId: user.digitalId,
                preferences: user.preferences
            },
            adhaar,
            passport
        });
    }

    res.json({ success: false, message: getTranslation("invalid_otp", language) });
});

// Update user preferences
app.post("/update-preferences", (req, res) => {
    const { userId, preferences, language = "en" } = req.body;
    
    const userIndex = users.findIndex(u => u.id === userId);
    if (userIndex === -1) {
        return res.status(404).json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    // Update preferences
    users[userIndex].preferences = {
        ...users[userIndex].preferences,
        ...preferences
    };
    
    // Log the preference update
    evidenceLogger.addLog(userId, "PREFERENCES_UPDATED", {
        timestamp: new Date().toISOString(),
        newPreferences: preferences
    });
    
    res.json({
        success: true,
        message: getTranslation("preferences_updated", language),
        preferences: users[userIndex].preferences
    });
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
                timestamp: data.timestamp || new Date().toISOString()
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
        
        // Find user and log the event
        const user = users.find(u => u.phone === phone);
        if (user) {
            evidenceLogger.addLog(user.id, "OTP_SENT", {
                timestamp: new Date().toISOString(),
                method: "whatsapp"
            });
        }
        
        res.json({ success: true, message: "OTP marked as sent" });
    } else {
        res.json({ success: false, message: "OTP not found" });
    }
});

// SOS Trigger
app.post("/sos", (req, res) => {
    const { userId, location, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.status(404).json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }

    // Create SOS alert
    const sosId = crypto.randomBytes(8).toString('hex');
    const timestamp = new Date().toISOString();
    
    const sosAlert = {
        id: sosId,
        userId: user.id,
        userName: user.name,
        userPhone: user.phone,
        location,
        status: "active",
        timestamp,
        responderId: null,
        responderEta: null
    };
    
    sosAlerts.push(sosAlert);
    
    // Update user status in active sessions
    let index = activeSessions.findIndex(s => s.phone === user.phone);
    if (index !== -1) {
        activeSessions[index].status = "SOS";
        activeSessions[index].sosTime = timestamp;

        // Move to top of list
        const sosUser = activeSessions.splice(index, 1)[0];
        activeSessions.unshift(sosUser);
    }
    
    // Log the SOS event
    evidenceLogger.addLog(user.id, "SOS_TRIGGERED", {
        sosId,
        timestamp,
        location
    });
    
    // Find nearest responder (simplified)
    let nearestResponder = null;
    let shortestDistance = Infinity;
    
    responders.forEach(responder => {
        if (responder.status === "available" && responder.location) {
            const distance = calculateDistance(
                location.lat, location.lng,
                responder.location.lat, responder.location.lng
            );
            
            if (distance < shortestDistance) {
                shortestDistance = distance;
                nearestResponder = responder;
            }
        }
    });
    
    // Assign responder if found
    if (nearestResponder) {
        sosAlert.responderId = nearestResponder.id;
        sosAlert.responderEta = Math.round(shortestDistance * 2); // Simple ETA calculation (2 min per km)
        
        // Update responder status
        const responderIndex = responders.findIndex(r => r.id === nearestResponder.id);
        if (responderIndex !== -1) {
            responders[responderIndex].status = "responding";
        }
    }

    return res.json({ 
        success: true, 
        message: getTranslation("sos_sent", language),
        sosId,
        responderAssigned: !!nearestResponder,
        eta: sosAlert.responderEta
    });
});

// Get SOS status
app.get("/sos/:sosId", (req, res) => {
    const { sosId } = req.params;
    const { language = "en" } = req.query;
    
    const sosAlert = sosAlerts.find(alert => alert.id === sosId);
    if (!sosAlert) {
        return res.status(404).json({
            success: false,
            message: getTranslation("sos_not_found", language)
        });
    }
    
    res.json({
        success: true,
        sos: sosAlert
    });
});

// e-FIR Filing
app.post("/efir", (req, res) => {
    const { userId, complaint, location, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const ref_id = crypto.randomBytes(8).toString('hex');
    const timestamp = new Date().toISOString();
    
    const efirRecord = {
        ref_id,
        userId: user.id,
        userName: user.name,
        userPhone: user.phone,
        complaint,
        location,
        status: "filed",
        timestamp
    };
    
    efirRecords.push(efirRecord);
    
    // Log the e-FIR filing
    evidenceLogger.addLog(user.id, "EFIR_FILED", {
        ref_id,
        timestamp,
        complaint: complaint.substring(0, 100) + (complaint.length > 100 ? '...' : ''),
        location
    });
    
    res.json({ 
        success: true, 
        message: getTranslation("efir_filed", language),
        ref_id 
    });
});

// Submit Rating
app.post("/rating", (req, res) => {
    const { userId, locationId, rating, feedback, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const location = touristLocations.find(loc => loc.id === locationId);
    if (!location) {
        return res.json({ 
            success: false, 
            message: getTranslation("location_not_found", language) 
        });
    }
    
    const timestamp = new Date().toISOString();
    
    const ratingRecord = {
        id: crypto.randomBytes(8).toString('hex'),
        userId: user.id,
        userName: user.name,
        locationId,
        locationName: location.name,
        rating,
        feedback,
        timestamp
    };
    
    ratings.push(ratingRecord);
    
    // Add to location reviews
    location.reviews.push({
        userId: user.id,
        rating,
        feedback,
        timestamp
    });
    
    // Update location rating
    const locationRatings = location.reviews.map(review => review.rating);
    const avgRating = locationRatings.reduce((sum, r) => sum + r, 0) / locationRatings.length;
    location.rating = parseFloat(avgRating.toFixed(1));
    
    // Log the rating submission
    evidenceLogger.addLog(user.id, "RATING_SUBMITTED", {
        locationId,
        locationName: location.name,
        rating,
        timestamp
    });
    
    res.json({ 
        success: true, 
        message: getTranslation("rating_submitted", language)
    });
});

// Create Trip Itinerary
app.post("/itinerary", (req, res) => {
    const { userId, startDate, endDate, locations, planType, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const itineraryId = crypto.randomBytes(8).toString('hex');
    const timestamp = new Date().toISOString();
    
    // Validate locations
    const validLocations = [];
    for (const locId of locations) {
        const location = touristLocations.find(loc => loc.id === locId);
        if (location) {
            validLocations.push({
                id: location.id,
                name: location.name,
                coordinates: location.coordinates
            });
        }
    }
    
    if (validLocations.length === 0) {
        return res.json({ 
            success: false, 
            message: getTranslation("no_valid_locations", language) 
        });
    }
    
    // Create itinerary
    const itinerary = {
        id: itineraryId,
        userId: user.id,
        userName: user.name,
        startDate,
        endDate,
        planType, // "full" or "daily"
        locations: validLocations,
        status: "active",
        createdAt: timestamp
    };
    
    tripItineraries.push(itinerary);
    
    // Log the itinerary creation
    evidenceLogger.addLog(user.id, "ITINERARY_CREATED", {
        itineraryId,
        startDate,
        endDate,
        locationCount: validLocations.length,
        timestamp
    });
    
    res.json({ 
        success: true, 
        message: getTranslation("itinerary_created", language),
        itinerary 
    });
});

// Get user's itineraries
app.get("/itinerary/:userId", (req, res) => {
    const { userId } = req.params;
    const { language = "en" } = req.query;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const userItineraries = tripItineraries.filter(itin => itin.userId === userId);
    
    res.json({ 
        success: true, 
        itineraries: userItineraries 
    });
});

// Get e-FIR records
app.get("/efir/:userId", (req, res) => {
    const { userId } = req.params;
    const { language = "en" } = req.query;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const userEfirs = efirRecords.filter(record => record.userId === userId);
    
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

// Get user evidence logs (for police/admin only)
app.get("/evidence-logs/:userId", (req, res) => {
    const { userId } = req.params;
    const { adminKey } = req.query;
    
    // Simple admin authentication
    if (adminKey !== "admin-secret-key") {
        return res.status(403).json({ 
            success: false, 
            message: "Unauthorized access" 
        });
    }
    
    const userLogs = evidenceLogger.getUserLogs(userId);
    
    res.json({ 
        success: true, 
        logs: userLogs,
        integrity: evidenceLogger.verifyLogIntegrity()
    });
});

// Update user location
app.post("/update-location", (req, res) => {
    const { userId, location, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    // Update location in active session
    const sessionIndex = activeSessions.findIndex(s => s.phone === user.phone);
    if (sessionIndex !== -1) {
        activeSessions[sessionIndex].location = location;
    }
    
    // Log the location update
    evidenceLogger.addLog(user.id, "LOCATION_UPDATED", {
        timestamp: new Date().toISOString(),
        location
    });
    
    // Check for danger zones
    const dangerAlerts = checkDangerZones(location);
    
    // Check for itinerary deviation
    let deviationAlert = null;
    const userItineraries = tripItineraries.filter(
        itin => itin.userId === userId && itin.status === "active"
    );
    
    if (userItineraries.length > 0) {
        // Simple check - are they near any planned location?
        const currentItinerary = userItineraries[0];
        let isNearPlannedLocation = false;
        
        for (const loc of currentItinerary.locations) {
            const distance = calculateDistance(
                location.lat, location.lng,
                loc.coordinates.lat, loc.coordinates.lng
            );
            
            if (distance <= 5) { // Within 5km of planned location
                isNearPlannedLocation = true;
                break;
            }
        }
        
        if (!isNearPlannedLocation) {
            deviationAlert = {
                type: "itinerary_deviation",
                message: getTranslation("itinerary_deviation", language),
                itineraryId: currentItinerary.id
            };
        }
    }
    
    res.json({ 
        success: true, 
        dangerAlerts: dangerAlerts.length > 0 ? dangerAlerts : null,
        deviationAlert
    });
});

// Remove user from active sessions (logout)
app.post("/logout", (req, res) => {
    const { userId, language = "en" } = req.body;
    
    const user = users.find(u => u.id === userId);
    if (!user) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_not_found", language) 
        });
    }
    
    const index = activeSessions.findIndex(s => s.phone === user.phone);
    
    if (index !== -1) {
        activeSessions.splice(index, 1);
        
        // Log the logout event
        evidenceLogger.addLog(user.id, "USER_LOGOUT", {
            timestamp: new Date().toISOString()
        });
        
        res.json({ 
            success: true, 
            message: getTranslation("logout_successful", language) 
        });
    } else {
        res.json({ 
            success: false, 
            message: getTranslation("not_logged_in", language) 
        });
    }
});

// Register new user
app.post("/register", async (req, res) => {
    const { 
        name, phone, email, address, 
        idType, idNumber, dateOfBirth,
        emergencyContacts, language = "en" 
    } = req.body;
    
    // Check if user already exists
    if (users.some(u => u.phone === phone)) {
        return res.json({ 
            success: false, 
            message: getTranslation("user_exists", language) 
        });
    }
    
    // Validate ID
    if (idType !== "adhaar" && idType !== "passport") {
        return res.json({ 
            success: false, 
            message: getTranslation("invalid_id_type", language) 
        });
    }
    
    // Verify E-KYC
    try {
        const userId = crypto.randomBytes(8).toString('hex');
        const newUser = {
            id: userId,
            name,
            phone,
            email,
            address,
            dateOfBirth,
            emergencyContacts: emergencyContacts || [],
            preferences: {
                language: language || "en",
                voiceAssistance: false,
                realTimeTracking: false
            },
            digitalId: null
        };
        
        if (idType === "adhaar") {
            newUser.adhaar = idNumber;
        } else {
            newUser.passport = idNumber;
        }
        
        // Perform E-KYC verification
        const ekycResult = await verifyEKYC(idType, idNumber, newUser);
        
        if (!ekycResult.verified) {
            return res.json({ 
                success: false, 
                message: getTranslation("ekyc_failed", language) 
            });
        }
        
        // Generate Digital ID
        newUser.digitalId = generateDigitalId(newUser);
        
        // Add user
        users.push(newUser);
        
        res.json({ 
            success: true, 
            message: getTranslation("registration_successful", language),
            userId: newUser.id,
            digitalId: newUser.digitalId
        });
    } catch (error) {
        console.error("Registration error:", error);
        res.json({ 
            success: false, 
            message: getTranslation("registration_error", language) 
        });
    }
});

// Get tourist locations
app.get("/locations", (req, res) => {
    const { language = "en" } = req.query;
    
    res.json({ 
        success: true, 
        locations: touristLocations.map(loc => ({
            id: loc.id,
            name: loc.name,
            city: loc.city,
            coordinates: loc.coordinates,
            description: loc.description,
            rating: loc.rating,
            reviewCount: loc.reviews.length,
            images: loc.images,
            category: loc.category
        }))
    });
});

// Get danger zones
app.get("/danger-zones", (req, res) => {
    const { language = "en" } = req.query;
    
    res.json({ 
        success: true, 
        zones: dangerZones.filter(zone => zone.active)
    });
});

// Get supported languages
app.get("/languages", (req, res) => {
    res.json({ 
        success: true, 
        languages: supportedLanguages 
    });
});

app.listen(5000, () => console.log("✅ Server running on port 5000"));
