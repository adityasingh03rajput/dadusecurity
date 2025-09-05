/**
 * DaduSecurity Server
 * Node.js server that connects HTML frontend with Python backend
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
    res.sendFile(path.join(__dirname, 'dadusecurity.html'));
});

// Function to call Python backend
function callPythonBackend(endpoint, data) {
    return new Promise((resolve, reject) => {
        const python = spawn('python', ['-c', `
import sys
import json
sys.path.append('${__dirname}')
from auth_backend import handle_request

try:
    endpoint = '${endpoint}'
    data = json.loads('${JSON.stringify(data).replace(/'/g, "\\'")}')
    result = handle_request(endpoint, data)
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"success": false, "message": str(e)}))
        `]);

        let result = '';
        let error = '';

        python.stdout.on('data', (data) => {
            result += data.toString();
        });

        python.stderr.on('data', (data) => {
            error += data.toString();
        });

        python.on('close', (code) => {
            if (code === 0) {
                try {
                    // Extract JSON from the result (last line usually contains the JSON)
                    const lines = result.trim().split('\n');
                    const jsonLine = lines[lines.length - 1];
                    const parsedResult = JSON.parse(jsonLine);
                    resolve(parsedResult);
                } catch (e) {
                    console.error('Error parsing Python output:', e);
                    console.error('Python output:', result);
                    resolve({ success: false, message: 'Error parsing response' });
                }
            } else {
                console.error('Python script error:', error);
                reject(new Error(`Python script failed with code ${code}: ${error}`));
            }
        });
    });
}

// API Routes

// Verify identity (Aadhaar or Passport)
app.post('/api/verify-identity', async (req, res) => {
    try {
        console.log('🔍 Identity verification request:', req.body);
        const result = await callPythonBackend('/api/verify-identity', req.body);
        console.log('✅ Identity verification result:', result);
        res.json(result);
    } catch (error) {
        console.error('❌ Identity verification error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during identity verification' 
        });
    }
});

// Verify OTP
app.post('/api/verify-otp', async (req, res) => {
    try {
        console.log('🔍 OTP verification request:', req.body);
        const result = await callPythonBackend('/api/verify-otp', req.body);
        console.log('✅ OTP verification result:', result);
        res.json(result);
    } catch (error) {
        console.error('❌ OTP verification error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during OTP verification' 
        });
    }
});

// Resend OTP
app.post('/api/resend-otp', async (req, res) => {
    try {
        console.log('🔍 OTP resend request:', req.body);
        const result = await callPythonBackend('/api/resend-otp', req.body);
        console.log('✅ OTP resend result:', result);
        res.json(result);
    } catch (error) {
        console.error('❌ OTP resend error:', error);
        res.status(500).json({ 
            success: false, 
            message: 'Server error during OTP resend' 
        });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        success: true, 
        message: 'DaduSecurity server is running',
        timestamp: new Date().toISOString()
    });
});

// Test Python backend connection
app.get('/api/test-backend', async (req, res) => {
    try {
        const testData = {
            auth_method: 'aadhaar',
            aadhaar: '123456789012'
        };
        
        const result = await callPythonBackend('/api/verify-identity', testData);
        res.json({
            success: true,
            message: 'Backend connection successful',
            test_result: result
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Backend connection failed',
            error: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
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
    console.log('\n' + '='.repeat(60));
    console.log('🚀 DaduSecurity Server Started');
    console.log('='.repeat(60));
    console.log(`📡 Server running on: http://localhost:${PORT}`);
    console.log(`🌐 Access the portal: http://localhost:${PORT}`);
    console.log(`🔧 Health check: http://localhost:${PORT}/api/health`);
    console.log(`🧪 Test backend: http://localhost:${PORT}/api/test-backend`);
    console.log('='.repeat(60));
    console.log('📋 Available Test Credentials:');
    console.log('   Aadhaar: 123456789012, 234567890123, 345678901234');
    console.log('   Passport: A1234567 (DOB: 1990-05-15), B2345678 (DOB: 1985-08-22)');
    console.log('='.repeat(60));
    console.log('📱 WhatsApp OTP will be displayed in console');
    console.log('='.repeat(60) + '\n');
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
