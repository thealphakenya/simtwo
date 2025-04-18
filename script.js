const { exec } = require('child_process');

// Hardcoded Fly.io authentication token
const FLY_API_TOKEN = "FlyV1 fm2_lJPECAAAAAAACHpaxBBcchQS7yEaY7NMcoQliSfOwrVodHRwczovL2FwaS5mbHkuaW8vdjGUAJLOAA8mqh8Lk7lodHRwczovL2FwaS5mbHkuaW8vYWFhL3YxxDzQLtGON4z3Xd3jxYoqxbCWk2fPgyKWunKIeAGcCXoWBu/DQvtD4a2mISPhB1RJd1JHNkOs2sdO/obyONXETgTklMsNKT3+1tL3Ct44iKa9hD7nTH2UY8G9b2GWN1+/UxloqeBB5z9u7Od19dUS5sGsV7cWkB0HrthTlLI8hi6+bO0KwDNxNXEjqa9KB8QgVlMtfyb+TvQ53sMHzc6GdENR55yQghOvmB0yT2btiHo=";

// Function to authenticate to Fly.io using the Fly API token
function authenticateFly() {
  return new Promise((resolve, reject) => {
    const command = `flyctl auth login --access-token "${FLY_API_TOKEN}"`;
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(`Authentication failed: ${stderr || error}`);
      } else {
        resolve(stdout);
      }
    });
  });
}

// Function to trigger Fly deployment
function deployFly() {
  return new Promise((resolve, reject) => {
    const command = 'flyctl deploy --remote-only'; // Uses fly.toml
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(`Deployment failed: ${stderr || error}`);
      } else {
        resolve(stdout);
      }
    });
  });
}

// Execute the deployment
async function deploy() {
  try {
    console.log('Authenticating with Fly.io...');
    await authenticateFly();
    console.log('✅ Authentication successful!');
    
    console.log('🚀 Deploying to Fly.io...');
    const deployOutput = await deployFly();
    console.log('✅ Deployment successful:\n', deployOutput);
  } catch (error) {
    console.error('❌ Deployment failed:', error);
    process.exit(1);
  }
}

// Run the deployment process
deploy();
