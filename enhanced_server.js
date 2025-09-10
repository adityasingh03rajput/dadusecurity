const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST", "PUT", "DELETE"]
    },
    pingInterval: 10000,
    pingTimeout: 5000,
    maxHttpBufferSize: 1e8
});

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Create directories
const dirs = ['logs', 'data', 'uploads'];
dirs.forEach(dir => {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath);
    }
});

// Setup logging
const logStream = fs.createWriteStream(path.join(__dirname, 'logs', 'server.log'), { flags: 'a' });
function log(message, level = 'INFO') {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}\n`;
    logStream.write(logMessage);
    console.log(logMessage.trim());
}

// Multi-language support
const languages = {
    'en': {
        'sos_alert': 'Emergency SOS Alert',
        'help_coming': 'Help is on the way!',
        'geofence_alert': 'Geo-fence Alert',
        'danger_zone': 'You are entering a danger zone',
        'red_zone_alert': 'Red zone alert in your itinerary',
        'eta_update': 'ETA Update',
        'rating_thanks': 'Thank you for your rating',
        'feedback_received': 'Feedback received'
    },
    'hi': {
        'sos_alert': 'आपातकालीन SOS अलर्ट',
        'help_coming': 'मदद आ रही है!',
        'geofence_alert': 'जियो-फेंस अलर्ट',
        'danger_zone': 'आप खतरे के क्षेत्र में प्रवेश कर रहे हैं',
        'red_zone_alert': 'आपके यात्रा कार्यक्रम में रेड जोन अलर्ट',
        'eta_update': 'ETA अपडेट',
        'rating_thanks': 'आपकी रेटिंग के लिए धन्यवाद',
        'feedback_received': 'फीडबैक प्राप्त हुआ'
    },
    'es': {
        'sos_alert': 'Alerta de Emergencia SOS',
        'help_coming': '��La ayuda está en camino!',
        'geofence_alert': 'Alerta de Geo-cerca',
        'danger_zone': 'Estás entrando en una zona peligrosa',
        'red_zone_alert': 'Alerta de zona roja en tu itinerario',
        'eta_update': 'Actualización de ETA',
        'rating_thanks': 'Gracias por tu calificación',
        'feedback_received': 'Comentario recibido'
    },
    'fr': {
        'sos_alert': 'Alerte SOS d\'urgence',
        'help_coming': 'L\'aide arrive!',
        'geofence_alert': 'Alerte Géo-clôture',
        'danger_zone': 'Vous entrez dans une zone dangereuse',
        'red_zone_alert': 'Alerte zone rouge dans votre itinéraire',
        'eta_update': 'Mise à jour ETA',
        'rating_thanks': 'Merci pour votre évaluation',
        'feedback_received': 'Commentaire reçu'
    },
    'de': {
        'sos_alert': 'Notfall-SOS-Alarm',
        'help_coming': 'Hilfe ist unterwegs!',
        'geofence_alert': 'Geo-Zaun-Alarm',
        'danger_zone': 'Sie betreten eine Gefahrenzone',
        'red_zone_alert': 'Rote Zone Alarm in Ihrem Reiseplan',
        'eta_update': 'ETA-Update',
        'rating_thanks': 'Danke für Ihre Bewertung',
        'feedback_received': 'Feedback erhalten'
    },
    'ja': {
        'sos_alert': '緊急SOSアラート',
        'help_coming': '助けが向かっています！',
        'geofence_alert': 'ジオフェンスアラート',
        'danger_zone': '危険地帯に入っています',
        'red_zone_alert': '旅程にレッドゾーンアラート',
        'eta_update': 'ETA更新',
        'rating_thanks': '評価ありがとうございます',
        'feedback_received': 'フィードバックを受信しました'
    },
    'zh': {
        'sos_alert': '紧急SOS警报',
        'help_coming': '救援正在路上！',
        'geofence_alert': '地理围栏警报',
        'danger_zone': '您正在进入危险区域',
        'red_zone_alert': '您的行程中有红色区域警报',
        'eta_update': 'ETA更新',
        'rating_thanks': '感谢您的评分',
        'feedback_received': '已收到反馈'
    },
    'ar': {
        'sos_alert': 'تنبيه SOS طارئ',
        'help_coming': 'المساعدة في الطريق!',
        'geofence_alert': 'تنبيه السياج الجغرافي',
        'danger_zone': 'أنت تدخل منطقة خطر',
        'red_zone_alert': 'تنبيه المنطقة الحمراء في برنامجك',
        'eta_update': 'تحديث وقت الوصول المتوقع',
        'rating_thanks': 'شكرا لتقييمك',
        'feedback_received': 'تم استلام التعليق'
    },
    'pt': {
        'sos_alert': 'Alerta de Emergência SOS',
        'help_coming': 'A ajuda está a caminho!',
        'geofence_alert': 'Alerta de Geo-cerca',
        'danger_zone': 'Você está entrando em uma zona perigosa',
        'red_zone_alert': 'Alerta de zona vermelha no seu itinerário',
        'eta_update': 'Atualização de ETA',
        'rating_thanks': 'Obrigado pela sua avaliação',
        'feedback_received': 'Feedback recebido'
    },
    'ru': {
        'sos_alert': 'Экстренное SOS оповещение',
        'help_coming': 'Помощь уже в пути!',
        'geofence_alert': 'Геозона оповещение',
        'danger_zone': 'Вы входите в опасную зону',
        'red_zone_alert': 'Оповещение о красной зоне в вашем маршруте',
        'eta_update': 'Обновление ETA',
        'rating_thanks': 'Спасибо за вашу оценку',
        'feedback_received': 'Отзыв получен'
    }
};

// Enhanced user database with more fields
const users = {
    '123456789012': { 
        name: 'John Doe', 
        location: 'Mumbai, India', 
        phone: '+91-9876543210', 
        emergency_contact: '+91-9123456780',
        language: 'en',
        real_time_tracking: false,
        emergency_contacts: [
            { name: 'Wife', phone: '+91-9123456780', relation: 'spouse' },
            { name: 'Brother', phone: '+91-9123456781', relation: 'sibling' }
        ]
    },
    '987654321098': { 
        name: 'Jane Smith', 
        location: 'Delhi, India', 
        phone: '+91-9876543211', 
        emergency_contact: '+91-9123456781',
        language: 'en',
        real_time_tracking: true,
        emergency_contacts: [
            { name: 'Mother', phone: '+91-9123456781', relation: 'parent' }
        ]
    },
    '456789012345': { 
        name: 'Bob Wilson', 
        location: 'Bangalore, India', 
        phone: '+91-9876543212', 
        emergency_contact: '+91-9123456782',
        language: 'en',
        real_time_tracking: false,
        emergency_contacts: []
    }
};

// Emergency services database
const emergencyServices = {
    'police': { name: 'Police', phone: '100', priority: 1 },
    'ambulance': { name: 'Ambulance', phone: '108', priority: 1 },
    'fire': { name: 'Fire Brigade', phone: '101', priority: 1 },
    'women_helpline': { name: 'Women Helpline', phone: '1091', priority: 2 },
    'child_helpline': { name: 'Child Helpline', phone: '1098', priority: 2 },
    'tourist_helpline': { name: 'Tourist Helpline', phone: '1363', priority: 2 }
};

// Danger zones and red zones
let dangerZones = [
    { id: 1, name: 'High Crime Area', lat: 19.0760, lng: 72.8777, radius: 2, type: 'crime', severity: 'high' },
    { id: 2, name: 'Flood Zone', lat: 28.7041, lng: 77.1025, radius: 5, type: 'natural', severity: 'critical' }
];

let redZones = [
    { id: 1, name: 'Earthquake Zone', lat: 34.0522, lng: -118.2437, radius: 10, type: 'natural', severity: 'critical', active: true }
];

// Places database for ratings and feedback
let places = {};

// In-memory storage
let connectedUsers = new Map();
let sosSignals = [];
let activeHelp = new Map(); // Track active help requests
let connectionStats = {
    totalConnections: 0,
    activeConnections: 0,
    totalSOS: 0,
    startTime: new Date().toISOString()
};

// Heartbeat tracking
const heartbeats = new Map();

// Helper functions
function getCurrentTimestamp() {
    return new Date().toISOString();
}

function getTranslation(lang, key) {
    return languages[lang] && languages[lang][key] ? languages[lang][key] : languages['en'][key];
}

function calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function checkGeofencing(lat, lng, userId) {
    const user = users[userId];
    if (!user) return;

    // Check danger zones
    dangerZones.forEach(zone => {
        const distance = calculateDistance(lat, lng, zone.lat, zone.lng);
        if (distance <= zone.radius) {
            const socketId = findUserSocket(userId);
            if (socketId) {
                io.to(socketId).emit('geofence_alert', {
                    type: 'danger_zone',
                    zone: zone,
                    message: getTranslation(user.language, 'danger_zone'),
                    distance: distance
                });
            }
        }
    });

    // Check red zones
    redZones.forEach(zone => {
        if (zone.active) {
            const distance = calculateDistance(lat, lng, zone.lat, zone.lng);
            if (distance <= zone.radius) {
                const socketId = findUserSocket(userId);
                if (socketId) {
                    io.to(socketId).emit('red_zone_alert', {
                        type: 'red_zone',
                        zone: zone,
                        message: getTranslation(user.language, 'red_zone_alert'),
                        distance: distance
                    });
                }
            }
        }
    });
}

function findUserSocket(userId) {
    for (const [socketId, userData] of connectedUsers.entries()) {
        if (userData.aadhaar_id === userId) {
            return socketId;
        }
    }
    return null;
}

function broadcastToDashboards(event, data) {
    for (const [id, user] of connectedUsers.entries()) {
        if (user.client_type === 'dashboard') {
            io.to(id).emit(event, data);
        }
    }
}

function generateETA(helpType, userLocation) {
    // Simulate ETA calculation based on help type and location
    const baseTime = {
        'police': 8,
        'ambulance': 12,
        'fire': 10,
        'rescue': 15
    };
    
    const randomFactor = Math.random() * 5; // 0-5 minutes variation
    return Math.round((baseTime[helpType] || 10) + randomFactor);
}

// Socket.IO connection handling
io.on('connection', (socket) => {
    log(`New client connected: ${socket.id}`, 'INFO');
    connectionStats.totalConnections++;
    connectionStats.activeConnections++;
    
    heartbeats.set(socket.id, Date.now());
    
    // Handle heartbeat
    socket.on('heartbeat', (data) => {
        heartbeats.set(socket.id, Date.now());
        socket.emit('heartbeat_ack', { 
            timestamp: Date.now(),
            server_time: getCurrentTimestamp()
        });
    });

    // User connection
    socket.on('user_connect', (data) => {
        const { aadhaar_id, client_type, name, version, language } = data;
        const user = users[aadhaar_id];
        
        if (user || client_type === 'dashboard') {
            const userData = {
                socket_id: socket.id,
                aadhaar_id: aadhaar_id,
                name: user ? user.name : (name || 'Dashboard'),
                location: user ? user.location : 'Control Center',
                phone: user ? user.phone : 'N/A',
                client_type: client_type || 'user',
                connected_at: getCurrentTimestamp(),
                last_seen: getCurrentTimestamp(),
                version: version || '1.0',
                language: language || user?.language || 'en'
            };
            
            connectedUsers.set(socket.id, userData);
            
            socket.emit('connection_ack', { 
                status: 'connected', 
                name: userData.name,
                socket_id: socket.id,
                server_time: getCurrentTimestamp(),
                server_version: '3.0',
                emergency_services: emergencyServices,
                user_data: user
            });
            
            broadcastToDashboards('users_update', Array.from(connectedUsers.values()));
            broadcastToDashboards('stats_update', connectionStats);
            
            log(`User connected: ${userData.name} (${socket.id}, ${client_type})`, 'INFO');
        } else {
            socket.emit('connection_error', { 
                error: 'User not found',
                aadhaar_id: aadhaar_id
            });
        }
    });

    // SOS Signal
    socket.on('sos_signal', (data) => {
        const user = connectedUsers.get(socket.id);
        
        if (user) {
            const sosData = {
                ...user,
                sos_id: uuidv4(),
                sos_time: getCurrentTimestamp(),
                status: 'active',
                location: data.location || user.location,
                message: data.message || 'Emergency SOS activated',
                coordinates: data.coordinates || null,
                image: data.image || null,
                help_type: data.help_type || 'general'
            };
            
            sosSignals.unshift(sosData);
            connectionStats.totalSOS++;
            
            // Generate ETA for help
            const eta = generateETA(sosData.help_type, sosData.coordinates);
            sosData.eta = eta;
            
            // Start tracking help
            activeHelp.set(sosData.sos_id, {
                ...sosData,
                eta_minutes: eta,
                start_time: new Date(),
                status: 'dispatched'
            });
            
            log(`🚨 SOS received from ${user.name} at ${sosData.location}`, 'ALERT');
            
            // Broadcast to dashboards
            broadcastToDashboards('sos_update', sosSignals);
            broadcastToDashboards('stats_update', connectionStats);
            broadcastToDashboards('new_sos_alert', sosData);
            
            // Notify all users
            io.emit('sos_broadcast', {
                id: sosData.sos_id,
                name: sosData.name,
                location: sosData.location,
                time: sosData.sos_time
            });
            
            // Send ETA to user
            socket.emit('sos_ack', { 
                status: 'received', 
                sos_id: sosData.sos_id,
                timestamp: sosData.sos_time,
                message: getTranslation(user.language, 'help_coming'),
                eta_minutes: eta,
                help_type: sosData.help_type
            });
            
            // Start ETA updates
            startETAUpdates(socket.id, sosData.sos_id);
        }
    });

    // Location update with geofencing
    socket.on('location_update', (data) => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            user.location = data.location;
            user.last_seen = getCurrentTimestamp();
            if (data.coordinates) {
                user.coordinates = data.coordinates;
                // Check geofencing
                checkGeofencing(data.coordinates.lat, data.coordinates.lng, user.aadhaar_id);
            }
            connectedUsers.set(socket.id, user);
            
            broadcastToDashboards('users_update', Array.from(connectedUsers.values()));
        }
    });

    // E-FIR filing
    socket.on('file_efir', (data) => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            const efirData = {
                efir_id: uuidv4(),
                user_id: user.aadhaar_id,
                user_name: user.name,
                incident_type: data.incident_type,
                description: data.description,
                location: data.location || user.location,
                coordinates: data.coordinates,
                timestamp: getCurrentTimestamp(),
                status: 'filed',
                attachments: data.attachments || []
            };
            
            // Save E-FIR (in production, save to database)
            log(`E-FIR filed by ${user.name}: ${data.incident_type}`, 'INFO');
            
            socket.emit('efir_ack', {
                status: 'filed',
                efir_id: efirData.efir_id,
                message: 'E-FIR filed successfully',
                reference_number: `EFIR${Date.now()}`
            });
            
            broadcastToDashboards('new_efir', efirData);
        }
    });

    // Rating submission
    socket.on('submit_rating', (data) => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            const placeId = data.place_id || data.location;
            if (!places[placeId]) {
                places[placeId] = {
                    name: data.place_name || data.location,
                    ratings: [],
                    feedbacks: [],
                    average_rating: 0
                };
            }
            
            places[placeId].ratings.push({
                user_id: user.aadhaar_id,
                rating: data.rating,
                timestamp: getCurrentTimestamp()
            });
            
            // Calculate average rating
            const ratings = places[placeId].ratings;
            places[placeId].average_rating = ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length;
            
            socket.emit('rating_ack', {
                status: 'received',
                message: getTranslation(user.language, 'rating_thanks'),
                place: places[placeId].name,
                average_rating: places[placeId].average_rating
            });
            
            log(`Rating submitted by ${user.name} for ${places[placeId].name}: ${data.rating} stars`, 'INFO');
        }
    });

    // Feedback submission
    socket.on('submit_feedback', (data) => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            const placeId = data.place_id || data.location;
            if (!places[placeId]) {
                places[placeId] = {
                    name: data.place_name || data.location,
                    ratings: [],
                    feedbacks: [],
                    average_rating: 0
                };
            }
            
            places[placeId].feedbacks.push({
                user_id: user.aadhaar_id,
                feedback: data.feedback,
                sentiment: data.sentiment || 'neutral',
                timestamp: getCurrentTimestamp()
            });
            
            socket.emit('feedback_ack', {
                status: 'received',
                message: getTranslation(user.language, 'feedback_received')
            });
            
            log(`Feedback submitted by ${user.name} for ${places[placeId].name}`, 'INFO');
        }
    });

    // Real-time tracking toggle
    socket.on('toggle_tracking', (data) => {
        const user = connectedUsers.get(socket.id);
        if (user && users[user.aadhaar_id]) {
            users[user.aadhaar_id].real_time_tracking = data.enabled;
            socket.emit('tracking_ack', {
                status: 'updated',
                enabled: data.enabled
            });
            log(`Real-time tracking ${data.enabled ? 'enabled' : 'disabled'} for ${user.name}`, 'INFO');
        }
    });

    // Disconnect handling
    socket.on('disconnect', (reason) => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            connectedUsers.delete(socket.id);
            heartbeats.delete(socket.id);
            connectionStats.activeConnections--;
            
            log(`User disconnected: ${user.name} (Reason: ${reason})`, 'INFO');
            
            broadcastToDashboards('users_update', Array.from(connectedUsers.values()));
            broadcastToDashboards('stats_update', connectionStats);
        }
    });
});

// ETA update system
function startETAUpdates(socketId, sosId) {
    const helpData = activeHelp.get(sosId);
    if (!helpData) return;
    
    const updateInterval = setInterval(() => {
        const elapsed = Math.floor((new Date() - helpData.start_time) / 60000); // minutes
        const remainingETA = Math.max(0, helpData.eta_minutes - elapsed);
        
        if (remainingETA <= 0) {
            // Help has arrived
            io.to(socketId).emit('help_arrived', {
                sos_id: sosId,
                message: 'Help has arrived at your location'
            });
            activeHelp.delete(sosId);
            clearInterval(updateInterval);
        } else {
            // Send ETA update
            io.to(socketId).emit('eta_update', {
                sos_id: sosId,
                eta_minutes: remainingETA,
                status: 'en_route'
            });
        }
    }, 30000); // Update every 30 seconds
}

// Connection health monitoring
setInterval(() => {
    const now = Date.now();
    for (const [socketId, lastBeat] of heartbeats.entries()) {
        if (now - lastBeat > 30000) {
            const socket = io.sockets.sockets.get(socketId);
            if (socket) {
                const user = connectedUsers.get(socketId);
                if (user) {
                    log(`No heartbeat from ${user.name} (${socketId}), disconnecting`, 'WARN');
                } else {
                    log(`No heartbeat from ${socketId}, disconnecting`, 'WARN');
                }
                socket.disconnect(true);
            }
        }
    }
}, 10000);

// HTTP Routes
app.post('/connect', (req, res) => {
    const { aadhaar_id } = req.body;
    const user = users[aadhaar_id];
    
    if (user) {
        res.json({ 
            status: 'connected', 
            name: user.name,
            location: user.location,
            phone: user.phone,
            emergency_contact: user.emergency_contact,
            language: user.language,
            emergency_services: emergencyServices
        });
    } else {
        res.status(404).json({ error: 'User not found' });
    }
});

app.get('/places/:placeId/rating', (req, res) => {
    const place = places[req.params.placeId];
    if (place) {
        res.json({
            name: place.name,
            average_rating: place.average_rating,
            total_ratings: place.ratings.length
        });
    } else {
        res.status(404).json({ error: 'Place not found' });
    }
});

app.get('/danger-zones', (req, res) => {
    res.json(dangerZones);
});

app.get('/red-zones', (req, res) => {
    res.json(redZones.filter(zone => zone.active));
});

app.post('/update-red-zones', (req, res) => {
    const { zones } = req.body;
    redZones = zones;
    
    // Notify all connected users about red zone updates
    io.emit('red_zones_updated', redZones.filter(zone => zone.active));
    
    res.json({ status: 'updated', count: zones.length });
});

app.get('/status', (req, res) => {
    res.json({
        connected_users: Array.from(connectedUsers.values()),
        sos_signals: sosSignals,
        statistics: connectionStats,
        uptime: process.uptime(),
        server_time: getCurrentTimestamp(),
        active_help: Array.from(activeHelp.values()),
        places_count: Object.keys(places).length
    });
});

app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        timestamp: getCurrentTimestamp(),
        uptime: process.uptime(),
        connections: {
            total: connectionStats.totalConnections,
            active: connectionStats.activeConnections,
            sos: connectionStats.totalSOS
        },
        version: '3.0',
        features: [
            'multi_language',
            'geofencing',
            'efir',
            'rating_feedback',
            'real_time_tracking',
            'eta_tracking'
        ]
    });
});

// Serve static files
app.use(express.static('public'));

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    log(`🚀 Enhanced Tourist Safety Server running on port ${PORT}`, 'INFO');
    log('🌍 Multi-language support enabled (10+ languages)', 'INFO');
    log('📋 Available Aadhaar IDs for testing:', 'INFO');
    log(Object.keys(users).join(', '), 'INFO');
    log('💓 Heartbeat monitoring enabled', 'INFO');
    log('����️ Geofencing system active', 'INFO');
    log('📱 E-FIR system ready', 'INFO');
    log('⭐ Rating & Feedback system active', 'INFO');
    log('📍 Real-time tracking available', 'INFO');
    log('🚨 ETA tracking system ready', 'INFO');
    log(`🔗 Dashboard: http://localhost:${PORT}`, 'INFO');
    log(`📊 API Status: http://localhost:${PORT}/status`, 'INFO');
});

// Graceful shutdown
process.on('SIGINT', () => {
    log('\n🛑 Shutting down server gracefully...', 'INFO');
    io.disconnectSockets();
    server.close(() => {
        log('✅ Server stopped', 'INFO');
        logStream.end();
        process.exit(0);
    });
});

process.on('uncaughtException', (error) => {
    log(`Uncaught Exception: ${error}`, 'ERROR');
    logStream.end();
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    log(`Unhandled Rejection at: ${promise}, reason: ${reason}`, 'ERROR');
    logStream.end();
    process.exit(1);
});