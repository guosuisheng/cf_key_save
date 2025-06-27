// Predefined authentication password
const AUTH_PASSWORD = "your_secure_password_here";

export default {
  async fetch(request, env, ctx) {
    // Only handle POST requests
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Only POST requests are allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // Parse JSON body
      const body = await request.json();
      
      // Validate auth
      if (!body.auth || body.auth !== AUTH_PASSWORD) {
        return new Response(JSON.stringify({ error: 'Invalid authentication' }), {
          status: 401,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      // Handle /receive endpoint
      if (path === '/receive') {
        return await handleReceive(body, env);
      }
      
      // Handle /get endpoint
      if (path === '/get') {
        return await handleGet(body, env);
      }

      // Handle /list endpoint
      if (path === '/list') {
        return await handleList(body, env);
      }
      
      // Unknown endpoint
      return new Response(JSON.stringify({ error: 'Endpoint not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      return new Response(JSON.stringify({ error: 'Invalid JSON or server error' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};

async function handleReceive(body, env) {
  // Validate required fields
  if (!body.key || !body.value) {
    return new Response(JSON.stringify({ error: 'Missing key or value' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    // Store in KV
    await env.MY_KV_NAMESPACE.put(body.key, body.value);
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'Value stored successfully',
      key: body.key
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to store value' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function handleGet(body, env) {
  // Validate required fields
  if (!body.key) {
    return new Response(JSON.stringify({ error: 'Missing key' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    // Fetch from KV
    const value = await env.MY_KV_NAMESPACE.get(body.key);
    
    if (value === null) {
      return new Response(JSON.stringify({ error: 'Key not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({
      key: body.key,
      value: value,
      auth: body.auth
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to retrieve value' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function handleList(body, env) {
  try {
    // Get list of keys from KV
    const listResult = await env.MY_KV_NAMESPACE.list();
    
    // Extract just the key names
    const keys = listResult.keys.map(keyObj => keyObj.name);
    
    return new Response(JSON.stringify({
      success: true,
      keys: keys,
      count: keys.length,
      list_complete: listResult.list_complete
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to list keys' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
