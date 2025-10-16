#!/usr/bin/env node

const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws');

ws.on('open', function open() {
  console.log('WebSocket connected');
  
  // Тестируем команду get_status
  ws.send(JSON.stringify({command: 'get_status'}));
});

ws.on('message', function message(data) {
  console.log('Received:', data.toString());
  
  // Тестируем команду connect
  setTimeout(() => {
    ws.send(JSON.stringify({command: 'connect'}));
  }, 1000);
  
  // Тестируем команду move_motor
  setTimeout(() => {
    ws.send(JSON.stringify({
      command: 'move_motor',
      motor: 0,
      direction: 'forward',
      speed: 200
    }));
  }, 2000);
  
  // Закрываем соединение
  setTimeout(() => {
    ws.close();
  }, 3000);
});

ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});

ws.on('close', function close() {
  console.log('WebSocket disconnected');
});



