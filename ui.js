// http://localhost:4343/

const port = parseInt(process.env.O2R_UI_PORT || '4343');

const baseUrl = process.env.BASE_URL || '/';
const serverUrl = baseUrl + 'o2r-ui';

const express = require('express');
const server = express();

server.use('/', express.static(__dirname));
server.listen(port);

console.log('[o2r-ui] running on port ', port);
