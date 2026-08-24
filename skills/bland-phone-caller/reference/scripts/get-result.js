#!/usr/bin/env node
/**
 * Bland.ai — Получение результата звонка
 * Usage: node get-result.js --call-id xxxxxx
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const API_BASE = 'api.bland.ai';
const API_KEY = process.env.BLAND_API_KEY;

if (!API_KEY) {
  console.error('❌ Error: BLAND_API_KEY not set in .env');
  process.exit(1);
}

// Parse arguments
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i += 2) {
  const key = args[i].replace(/^--/, '');
  params[key] = args[i + 1];
}

const callId = params['call-id'] || params.callId || params.id;

if (!callId) {
  console.log('Usage: node get-result.js --call-id xxxxxxx');
  console.log('');
  console.log('Examples:');
  console.log('  node get-result.js --call-id abc123');
  process.exit(1);
}

function apiRequest(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_BASE,
      path: path,
      method: 'GET',
      headers: {
        'authorization': API_KEY,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve({ raw: data });
        }
      });
    });

    req.on('error', reject);
    req.end();
  });
}

async function main() {
  console.log(`🔍 Получаем результат звонка: ${callId}\n`);

  try {
    // Получаем информацию о звонке
    const callInfo = await apiRequest(`/v1/calls/${callId}`);
    
    if (callInfo.status === 'error') {
      console.error('❌ Ошибка:', callInfo.message);
      process.exit(1);
    }

    // Формируем результат
    const result = {
      call_id: callId,
      timestamp: new Date().toISOString(),
      status: callInfo.status || 'unknown',
      phone_number: callInfo.phone_number,
      duration_seconds: callInfo.duration_seconds,
      cost_usd: callInfo.cost,
      
      // Транскрипт
      transcript: callInfo.transcript || callInfo.concatenated_transcript || null,
      
      // Анализ (если был включён)
      analysis: callInfo.analysis || null,
      
      // Запись
      recording_url: callInfo.recording_url || null,
      
      // Дополнительно
      call_ended_by: callInfo.call_ended_by,
      error_message: callInfo.error_message,
      
      // Полные данные (для отладки)
      _raw: callInfo
    };

    // Сохраняем в файл
    const resultsDir = path.join(__dirname, '..', '..', 'results');
    if (!fs.existsSync(resultsDir)) {
      fs.mkdirSync(resultsDir, { recursive: true });
    }

    const filename = `call_${callId}_${new Date().toISOString().split('T')[0]}.json`;
    const filepath = path.join(resultsDir, filename);
    
    fs.writeFileSync(filepath, JSON.stringify(result, null, 2), 'utf8');

    // Выводим краткое резюме
    console.log('✅ Результат получен и сохранён!\n');
    console.log('📁 Файл:', filepath);
    console.log('');
    console.log('📊 Резюме звонка:');
    console.log('  Статус:', result.status);
    console.log('  Номер:', result.phone_number);
    console.log('  Длительность:', result.duration_seconds ? `${result.duration_seconds} сек` : 'N/A');
    console.log('  Стоимость:', result.cost_usd ? `$${result.cost_usd}` : 'N/A');
    console.log('');

    if (result.transcript) {
      console.log('📝 Транскрипт:');
      console.log(result.transcript.substring(0, 500));
      if (result.transcript.length > 500) {
        console.log('... (сокращено, полный текст в файле)');
      }
      console.log('');
    }

    if (result.analysis) {
      console.log('📈 Анализ:');
      console.log(JSON.stringify(result.analysis, null, 2));
      console.log('');
    }

    if (result.recording_url) {
      console.log('🎙️  Запись:', result.recording_url);
      console.log('   Скачать: curl -o recording.mp3', result.recording_url);
    }

    console.log('\n📂 Все результаты сохранены в: skills/bland-phone-caller/results/');

  } catch (error) {
    console.error('❌ Ошибка:', error.message);
    process.exit(1);
  }
}

main();
