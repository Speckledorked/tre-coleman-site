const https = require('https');

const BASE_ID = 'appk7mBGffiWhowPC';
const TABLE = encodeURIComponent('Listings');
const AIRTABLE_BASE_URL = `https://api.airtable.com/v0/${BASE_ID}/${TABLE}`;

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Content-Type': 'application/json'
};

function airtableRequest(method, urlStr, body) {
  return new Promise((resolve, reject) => {
    const token = process.env.AIRTABLE_TOKEN;
    if (!token) {
      return reject(new Error('AIRTABLE_TOKEN environment variable is not set'));
    }

    const url = new URL(urlStr);
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => resolve({ statusCode: res.statusCode, body: data }));
    });

    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

exports.handler = async (event) => {
  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: CORS_HEADERS, body: '' };
  }

  // GET — fetch approved listings (handles Airtable pagination)
  if (event.httpMethod === 'GET') {
    try {
      let records = [];
      let offset = null;

      do {
        const url = new URL(AIRTABLE_BASE_URL);
        url.searchParams.set('filterByFormula', '{Approved}=1');
        url.searchParams.set('pageSize', '100');
        if (offset) url.searchParams.set('offset', offset);

        const result = await airtableRequest('GET', url.toString(), null);
        const data = JSON.parse(result.body);

        if (result.statusCode !== 200) {
          return {
            statusCode: result.statusCode,
            headers: CORS_HEADERS,
            body: JSON.stringify({ error: data.error || 'Airtable error' })
          };
        }

        records = records.concat(data.records || []);
        offset = data.offset || null;
      } while (offset);

      return {
        statusCode: 200,
        headers: CORS_HEADERS,
        body: JSON.stringify({ records })
      };
    } catch (err) {
      return {
        statusCode: 500,
        headers: CORS_HEADERS,
        body: JSON.stringify({ error: err.message })
      };
    }
  }

  // POST — submit a new listing
  if (event.httpMethod === 'POST') {
    try {
      const result = await airtableRequest('POST', AIRTABLE_BASE_URL, event.body);
      return {
        statusCode: result.statusCode,
        headers: CORS_HEADERS,
        body: result.body
      };
    } catch (err) {
      return {
        statusCode: 500,
        headers: CORS_HEADERS,
        body: JSON.stringify({ error: err.message })
      };
    }
  }

  return {
    statusCode: 405,
    headers: CORS_HEADERS,
    body: JSON.stringify({ error: 'Method not allowed' })
  };
};
