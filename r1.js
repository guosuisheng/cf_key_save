// Predefined authentication password
const AUTH_PASSWORD = "your_secure_password_here";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // Only handle POST requests
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    // Route to appropriate handler
    if (path === "/receive") {
      return handleReceive(request, env);
    } else if (path === "/get") {
      return handleGet(request, env);
    } else if (path === "/list") {
      return handleList(request, env);
    } else {
      return new Response("Not Found", { status: 404 });
    }

  },
};

// Handler for /receive route
async function handleReceive(request, env) {
  try {
    // Parse the JSON body
    const body = await request.json();
    
    // Validate required fields
    if (!body.key || !body.value || !body.auth) {
      return new Response(
        JSON.stringify({ 
          error: "Missing required fields: key, value, auth" 
        }), 
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check authentication
    if (body.auth !== AUTH_PASSWORD) {
      return new Response(
        JSON.stringify({ 
          error: "Authentication failed" 
        }), 
        { 
          status: 401,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check if D1 database is bound
    if (!env.DB) {
      return new Response(
        JSON.stringify({ 
          error: "Database not configured. Please bind your D1 database to 'DB'" 
        }), 
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Insert into D1 database
    const stmt = env.DB.prepare(
      "INSERT INTO kv_message (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value"
    );
    
    const result = await stmt.bind(body.key, body.value).run();

    if (result.success) {
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: "Data saved successfully",
          key: body.key 
        }), 
        { 
          status: 200,
          headers: { "Content-Type": "application/json" }
        }
      );
    } else {
      return new Response(
        JSON.stringify({ 
          error: "Database operation failed" 
        }), 
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

  } catch (error) {
    // Handle JSON parsing errors or database errors
    return new Response(
      JSON.stringify({ 
        error: "Invalid request or server error",
        details: error.message 
      }), 
      { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}

// Handler for /list route
async function handleList(request, env) {
  try {
    // Parse the JSON body
    const body = await request.json();
    
    // Validate required fields
    if (!body.auth) {
      return new Response(
        JSON.stringify({ 
          error: "Missing required field: auth" 
        }), 
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check authentication
    if (body.auth !== AUTH_PASSWORD) {
      return new Response(
        JSON.stringify({ 
          error: "Authentication failed" 
        }), 
        { 
          status: 401,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check if D1 database is bound
    if (!env.DB) {
      return new Response(
        JSON.stringify({ 
          error: "Database not configured. Please bind your D1 database to 'DB'" 
        }), 
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Query all keys from the D1 database
    const stmt = env.DB.prepare("SELECT key FROM kv_message ORDER BY key");
    const result = await stmt.all();

    if (result.success) {
      // Extract just the keys into an array
      const keys = result.results.map(row => row.key);
      
      return new Response(
        JSON.stringify({ 
          success: true,
          keys: keys,
          count: keys.length
        }), 
        { 
          status: 200,
          headers: { "Content-Type": "application/json" }
        }
      );
    } else {
      return new Response(
        JSON.stringify({ 
          error: "Database query failed" 
        }), 
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

  } catch (error) {
    // Handle JSON parsing errors or database errors
    return new Response(
      JSON.stringify({ 
        error: "Invalid request or server error",
        details: error.message 
      }), 
      { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}

// Handler for /get route
async function handleGet(request, env) {
  try {
    // Parse the JSON body
    const body = await request.json();
    
    // Validate required fields
    if (!body.key || !body.auth) {
      return new Response(
        JSON.stringify({ 
          error: "Missing required fields: key, auth" 
        }), 
        { 
          status: 400,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check authentication
    if (body.auth !== AUTH_PASSWORD) {
      return new Response(
        JSON.stringify({ 
          error: "Authentication failed" 
        }), 
        { 
          status: 401,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Check if D1 database is bound
    if (!env.DB) {
      return new Response(
        JSON.stringify({ 
          error: "Database not configured. Please bind your D1 database to 'DB'" 
        }), 
        { 
          status: 500,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

    // Query the D1 database
    const stmt = env.DB.prepare("SELECT value FROM kv_message WHERE key = ?");
    const result = await stmt.bind(body.key).first();

    if (result) {
      return new Response(
        JSON.stringify({ 
          key: body.key,
          value: result.value,
          auth: body.auth
        }), 
        { 
          status: 200,
          headers: { "Content-Type": "application/json" }
        }
      );
    } else {
      return new Response(
        JSON.stringify({ 
          error: "Key not found" 
        }), 
        { 
          status: 404,
          headers: { "Content-Type": "application/json" }
        }
      );
    }

  } catch (error) {
    // Handle JSON parsing errors or database errors
    return new Response(
      JSON.stringify({ 
        error: "Invalid request or server error",
        details: error.message 
      }), 
      { 
        status: 400,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
};

// SQL to create the table (run this in D1 console first):
/*
CREATE TABLE IF NOT EXISTS kv_message (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS update_timestamp 
AFTER UPDATE ON kv_message
BEGIN
  UPDATE kv_message SET updated_at = CURRENT_TIMESTAMP WHERE key = NEW.key;
END;
*/
