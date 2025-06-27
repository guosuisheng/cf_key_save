# Replace YOUR_WORKER_URL with your actual Cloudflare Worker URL
# Replace "your_secure_password_here" with your actual auth password

# 1. Store a key-value pair using /receive endpoint
curl -X POST https://YOUR_WORKER_URL.workers.dev/receive \
  -H "Content-Type: application/json" \
  -d '{
    "key": "first",
    "value": "Hello",
    "auth": "your_secure_password_here"
  }'

# Expected response:
# {"success":true,"message":"Value stored successfully","key":"first"}

# 2. Retrieve a value using /get endpoint
curl -X POST https://YOUR_WORKER_URL.workers.dev/get \
  -H "Content-Type: application/json" \
  -d '{
    "key": "first",
    "auth": "your_secure_password_here"
  }'

# Expected response:
# {"key":"first","value":"Hello","auth":"your_secure_password_here"}

# 3. Store another key-value pair
curl -X POST https://YOUR_WORKER_URL.workers.dev/receive \
  -H "Content-Type: application/json" \
  -d '{
    "key": "greeting",
    "value": "Welcome to my API",
    "auth": "your_secure_password_here"
  }'

# 4. Retrieve the second value
curl -X POST https://YOUR_WORKER_URL.workers.dev/get \
  -H "Content-Type: application/json" \
  -d '{
    "key": "greeting",
    "auth": "your_secure_password_here"
  }'

# Error examples:

# 5. Invalid authentication (should return 401)
curl -X POST https://YOUR_WORKER_URL.workers.dev/receive \
  -H "Content-Type: application/json" \
  -d '{
    "key": "test",
    "value": "test",
    "auth": "wrong_password"
  }'

# Expected response:
# {"error":"Invalid authentication"}

# 6. Missing key in /get request (should return 400)
curl -X POST https://YOUR_WORKER_URL.workers.dev/get \
  -H "Content-Type: application/json" \
  -d '{
    "auth": "your_secure_password_here"
  }'

# Expected response:
# {"error":"Missing key"}

# 7. Try to get non-existent key (should return 404)
curl -X POST https://YOUR_WORKER_URL.workers.dev/get \
  -H "Content-Type: application/json" \
  -d '{
    "key": "nonexistent",
    "auth": "your_secure_password_here"
  }'

# Expected response:
# {"error":"Key not found"}

# 8. Wrong HTTP method (should return 405)
curl -X GET https://YOUR_WORKER_URL.workers.dev/receive

# Expected response:
# {"error":"Only POST requests are allowed"}

# Verbose output (add -v flag to see headers and status codes)
curl -v -X POST https://YOUR_WORKER_URL.workers.dev/receive \
  -H "Content-Type: application/json" \
  -d '{
    "key": "debug",
    "value": "debugging",
    "auth": "your_secure_password_here"
  }'
# list all key
curl -X POST https://your-worker-domain.workers.dev/list \
  -H "Content-Type: application/json" \
  -d '{"auth": "your_secure_password_here"}'
  
