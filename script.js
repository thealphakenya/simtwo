const https = require('https');

const TOKEN = process.argv[2];
const ENVIRONMENT_ID = "42d75714-c415-4a9f-ad1c-373141c3eac0"; // replace with your actual environment ID
const SERVICE_ID = "705a3574-eaee-44d8-9dac-187f7524a6ad"; // replace with your actual service ID

// GraphQL mutation to trigger redeploy
const data = JSON.stringify({
  query: `
    mutation ServiceInstanceRedeploy {
      serviceInstanceRedeploy(
        environmentId: "${ENVIRONMENT_ID}"
        serviceId: "${SERVICE_ID}"
      )
    }
  `
});

const options = {
  hostname: 'backboard.railway.app',
  path: '/graphql/v2',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length,
    'Authorization': `Bearer ${TOKEN}`
  }
};

const req = https.request(options, res => {
  let body = '';
  res.on('data', chunk => {
    body += chunk;
  });
  res.on('end', () => {
    try {
      const response = JSON.parse(body);
      if (response.errors) {
        console.error('❌ Deployment failed:', response.errors);
        process.exit(1); // exit with failure code
      } else {
        console.log('✅ Railway deployment triggered successfully:', response.data);
      }
    } catch (err) {
      console.error('❌ Failed to parse the response:', err);
      process.exit(1); // exit with failure code
    }
  });
});

req.on('error', error => {
  console.error('❌ Request error:', error);
  process.exit(1); // exit with failure code
});

req.write(data);
req.end();
