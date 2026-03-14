const https = require('https');

const BASE_ID = 'appk7mBGffiWhowPC';
const TABLE = encodeURIComponent('Listings');
const AIRTABLE_BASE_URL = `https://api.airtable.com/v0/${BASE_ID}/${TABLE}`;

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Methods': 'GET, POST, PATCH, OPTIONS',
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
      const VALID_CATEGORIES = [
        'Restaurant & Food', 'Food Truck', 'Catering', 'Contractor & Trades',
        'Retail', 'Marketing & Design', 'Real Estate', 'Landscaping',
        'Cleaning Services', 'Health & Wellness', 'Legal & Financial',
        'Auto & Transportation', 'Technology', 'Other'
      ];
      let payload;
      try { payload = JSON.parse(event.body); } catch { payload = {}; }
      if (payload.records && payload.records[0] && payload.records[0].fields) {
        const cat = payload.records[0].fields.Category;
        if (!VALID_CATEGORIES.includes(cat)) {
          payload.records[0].fields.Category = 'Other';
        }
      }
      const result = await airtableRequest('POST', AIRTABLE_BASE_URL, JSON.stringify(payload));
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

  // PATCH — increment a click counter on a listing record
  if (event.httpMethod === 'PATCH') {
    try {
      const CLICK_FIELDS = ['Phone Clicks', 'Email Clicks', 'Website Clicks'];
      let payload;
      try { payload = JSON.parse(event.body); } catch { payload = {}; }
      const { recordId, field } = payload;

      if (!recordId || !CLICK_FIELDS.includes(field)) {
        return { statusCode: 400, headers: CORS_HEADERS, body: JSON.stringify({ error: 'Invalid recordId or field' }) };
      }

      // Read current value, then write back incremented
      const getResult = await airtableRequest('GET', `${AIRTABLE_BASE_URL}/${recordId}`, null);
      const record = JSON.parse(getResult.body);
      const current = (record.fields && record.fields[field]) || 0;

      const patchResult = await airtableRequest('PATCH', `${AIRTABLE_BASE_URL}/${recordId}`,
        JSON.stringify({ fields: { [field]: current + 1 } })
      );
      return { statusCode: patchResult.statusCode, headers: CORS_HEADERS, body: patchResult.body };
    } catch (err) {
      return { statusCode: 500, headers: CORS_HEADERS, body: JSON.stringify({ error: err.message }) };
    }
  }

  return {
    statusCode: 405,
    headers: CORS_HEADERS,
    body: JSON.stringify({ error: 'Method not allowed' })
  };
};
