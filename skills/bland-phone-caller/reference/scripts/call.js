#!/usr/bin/env node
/**
 * Bland.ai Phone Call Script
 * Usage: node call.js --to +79001234567 --task "Your task here" [--record] [--webhook URL]
 */

const https = require('https');

const API_BASE = 'api.bland.ai';
const API_KEY = process.env.BLAND_API_KEY;

if (!API_KEY) {
  console.error('Error: BLAND_API_KEY not set');
  process.exit(1);
}

// Parse arguments
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, '');
  params[key] = args[i + 1];
}

if (!params.to || !params.task) {
  console.log('Usage: node call.js --to +79001234567 --task "Your task" [--record] [--webhook URL]');
  process.exit(1);
}

const payload = JSON.stringify({
  phone_number: params.to,
  task: params.task,
  voice: params.voice || 'ru-RU-Standard-A',
  language: params.language || 'ru',
  max_duration: parseInt(params.duration) || 300,
  record: params.record === 'true' || params.record === true,
  webhook: params.webhook || undefined
});

const options = {
  hostname: API_BASE,
  path: '/v1/calls',
  method: 'POST',
  headers: {
    'authorization': API_KEY,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => data += chunk);
  res.on('end', () => {
    try {
      const result = JSON.parse(data);
      console.log('Call initiated:', JSON.stringify(result, null, 2));
      
      if (result.call_id) {
        console.log(`\nCall ID: ${result.call_id}`);
        console.log(`Status: ${result.status}`);
        console.log(`Check status: curl -H "authorization: $BLAND_API_KEY" https://api.bland.ai/v1/calls/${result.call_id}`);
      }
    } catch (e) {
      console.log('Response:', data);
    }
  });
});

req.on('error', (e) => {
  console.error('Error:', e.message);
});

req.write(payload);
req.end();
