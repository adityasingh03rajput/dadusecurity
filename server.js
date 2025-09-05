/**
 * DaduSecurity Server
 * Node.js server connecting HTML frontend with Python backend
 */

const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Function to call Python authentication handler
function callPythonAuth(endpoint, data) {
    return new Promise((resolve, reject) => {
        const pythonScript = `
import sys
import json
import os
sys.path.append('${__dirname.replace(/\\/g, '\\\\')}')

try:
    from auth_handler import auth_handler
    
    endpoint = '${endpoint}'
    data = json.loads('${JSON.stringify(data).replace(/'/g, "\\'")}')
    
    result = auth_handler.handle_request(endpoint, data)
    print("RESULT_START")
    print(json.dumps(result))
    print("RESULT_END")
    
except Exception as e:
    print("RESULT_START")
    print(json.dumps({"success": false, "message": str(e)}))
    print("RESULT_END")
`;

        const python = spawn('python', ['-c', pythonScript]);
        
        let result = '';
        let error = '';
        let capturing = false;
        
        python.stdout.on('data', (data) => {
            const output = data.toString();
            const lines = output.split('\n');
            
            for (const line of lines) {
                if (line.trim() === 'RESULT_START') {
                    capturing = true;
                    result = '';
                } else if (line.trim() === 'RESULT_END') {
                    capturing = false;
                } else if (capturing) {
                    result += line + '\n';
                } else {
                    // This is console output from Python (OTP messages, etc.)
                    if (line.trim()) {
                        console.log('🐍 Python:', line);
                    }
                }
            }
        });

        python.stderr.on('data', (data) => {
            error += data.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const parsedResult = JSON.parse(result.trim());
                    resolve(parsedResult);
                } catch (e) {
                    console.error('❌ Error parsing Python output:', e);
                    console.error('Raw output:', result);
                    resolve({ success: false, message: 'Error parsing response' });
                }
            } else {
                console.error('❌ Python script error:', error);
                reject(new Error(`Python script failed with code ${code}: ${error}`));
            }
        });
    });
}

// API Routes

// Health check
app.get('/api/health', (req, res) => {
    res.json({ 
        success: true, 
        message: 'DaduSecurity server is running',
        timestamp: new Date().toISOString(),
        server: 'Node.js + Python Backend'
    });
});

// Verify identity (Aadhaar or Passport)
app.post('/api/verify-identity', async (req, res) => {
    try {
        console.log('🔍 Identity verification request:', req.body);
        const result = await callPythonAuth('/api/verify-identity', req.body);
        console.log('✅ Identity verification result:', result.success ? 'Success' : 'Failed');
        res.json(result);
    } catch (error) {
        console.error('❌ Identity verification error:', error.message);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during identity verification' 
        });
    }
});

// Verify OTP
app.post('/api/verify-otp', async (req, res) => {
    try {
        console.log('🔍 OTP verification request for:', req.body.identifier);
        const result = await callPythonAuth('/api/verify-otp', req.body);
        console.log('✅ OTP verification result:', result.success ? 'Success' : 'Failed');
        res.json(result);
    } catch (error) {
        console.error('❌ OTP verification error:', error.message);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during OTP verification' 
        });
    }
});

// Resend OTP
app.post('/api/resend-otp', async (req, res) => {
    try {
        console.log('🔍 OTP resend request for:', req.body.identifier);
        const result = await callPythonAuth('/api/resend-otp', req.body);
        console.log('✅ OTP resend result:', result.success ? 'Success' : 'Failed');
        res.json(result);
    } catch (error) {
        console.error('❌ OTP resend error:', error.message);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during OTP resend' 
        });
    }
});

// Test Python backend connection
app.get('/api/test-backend', async (req, res) => {
    try {
        const testData = {
            auth_method: 'aadhaar',
            aadhaar: '123456789012'
        };
        
        const result = await callPythonAuth('/api/verify-identity', testData);
        res.json({
            success: true,
            message: 'Python backend connection successful',
            test_result: result
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Python backend connection failed',
            error: error.message
        });
    }
});

// Get database users (for testing)
app.get('/api/users', async (req, res) => {
    try {
        const python = spawn('python', ['-c', `
import sys
sys.path.append('${__dirname.replace(/\\/g, '\\\\')}')
from database import DaduSecurityDB
import json

db = DaduSecurityDB()
users = db.get_all_users()
result = []
for user in users:
    result.append({
        'name': user[0],
        'mobile': user[1],
        'aadhaar': user[2],
        'passport': user[3]
    })

print(json.dumps(result))
        `]);

        let result = '';
        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const users = JSON.parse(result.trim());
                    res.json({
                        success: true,
                        users: users
                    });
                } catch (e) {
                    res.status(500).json({
                        success: false,
                        message: 'Error parsing users data'
                    });
                }
            } else {
                res.status(500).json({
                    success: false,
                    message: 'Error fetching users'
                });
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Server error fetching users'
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('❌ Server error:', err);
    res.status(500).json({
        success: false,
        message: 'Internal server error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: 'Endpoint not found'
    });
});

// Start server
app.listen(PORT, () => {
    console.log('\n' + '='.repeat(70));
    console.log('🚀 DaduSecurity Server Started');
    console.log('='.repeat(70));
    console.log(`📡 Server running on: http://localhost:${PORT}`);
    console.log(`🌐 Access the portal: http://localhost:${PORT}`);
    console.log(`🔧 Health check: http://localhost:${PORT}/api/health`);
    console.log(`👥 View users: http://localhost:${PORT}/api/users`);
    console.log(`🧪 Test backend: http://localhost:${PORT}/api/test-backend`);
    console.log('='.repeat(70));
    console.log('📋 Registered Users:');
    console.log('   Archie - +91 93996 41235 - Aadhaar: 123456789012');
    console.log('   Pranav Namdeo - +91 97559 67700 - Aadhaar: 234567890123');
    console.log('   Aksh - +91 93997 65924 - Aadhaar: 345678901234');
    console.log('   Ayushi Vishwakarma - +91 93438 60485 - Aadhaar: 456789012345');
    console.log('   Ananya Samaiya - +91 73895 33745 - Aadhaar: 567890123456');
    console.log('   Anudhriti Mahanta - +91 93873 45518 - Aadhaar: 678901234567');
    console.log('='.repeat(70));
    console.log('📱 OTP will be displayed in this terminal');
    console.log('🔗 Connected to: https://dadusecurity-1.onrender.com');
    console.log('='.repeat(70) + '\n');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down DaduSecurity server...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down DaduSecurity server...');
    process.exit(0);
});
