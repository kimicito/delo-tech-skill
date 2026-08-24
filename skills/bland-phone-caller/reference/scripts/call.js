#!/usr/bin/env node
/**
 * Bland.ai Phone Call Script — Production Version
 * Usage: node call.js --to +79001234567 --task "Your task here" [--voice NAME] [--record]
 */

const https = require('https');

const API_BASE = 'api.bland.ai';
const API_KEY = process.env.BLAND_API_KEY;

if (!API_KEY) {
  console.error('Error: BLAND_API_KEY not set in .env');
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
  console.log('Usage: node call.js --to +79001234567 --task "Your task" [--voice NAME] [--record]');
  console.log('');
  console.log('Voices:');
  console.log('  2d8fd873-ea3c-4914-9b0f-84b3e1b75dd6  (Allie — рекомендуется)');
  console.log('  4c5db7cb-f097-4880-8634-139f2567033d  (Mitch)');
  console.log('  10a8fbe0-3d74-4bd4-9788-7f565c7e76a8  (Drew)');
  console.log('');
  console.log('Examples:');
  console.log('  node call.js --to +79001234567 --task "Запишите на приём"');
  console.log('  node call.js --to +79001234567 --task "Уточните заказ" --record true');
  process.exit(1);
}

const payload = JSON.stringify({
  phone_number: params.to,
  task: params.task,
  voice: params.voice || '2d8fd873-ea3c-4914-9b0f-84b3e1b75dd6', // Allie (лучший русский)
  language: 'ru',
  max_duration: parseInt(params.duration) || 600, // 10 минут max
  record: params.record === 'true' || params.record === true,
  wait_for_greeting: true, // Ждать приветствия на том конце
  answered_by_enabled: true, // Определять, кто взял трубку
  analysis_schema: {
    success: "boolean",
    summary: "string",
    details: "string"
  }
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
      if (result.status === 'success' || result.call_id) {
        console.log('✅ Звонок запущен!');
        console.log(`📞 Call ID: ${result.call_id || result.id}`);
        console.log(`⏱️  Макс. длительность: ${params.duration || 600} сек`);
        console.log(`🎙️  Голос: ${params.voice || 'Allie (ru)'}`);
        console.log(`📝 Задача: ${params.task}`);
        console.log('');
        console.log(`Проверить статус: curl -H "authorization: $BLAND_API_KEY" https://api.bland.ai/v1/calls/${result.call_id || result.id}`);
      } else {
        console.log('⚠️  Ответ:', JSON.stringify(result, null, 2));
      }
    } catch (e) {
      console.log('Response:', data);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Ошибка:', e.message);
});

req.write(payload);
req.end();
