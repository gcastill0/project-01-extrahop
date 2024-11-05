// s1_ODS_target is configured as a target for an Open Data Stream
const s1_path = "/services/collector/raw?sourcetype=extrahop"

// Check if the event is HTTP_RESPONSE to capture transaction data
// Note: the HTTP_RESPONSE uses HTTP.record to capture transaction

if ( event === 'HTTP_RESPONSE' ) {
    // Create a JSON object with all relevant transaction data fields
    var jsonData = {
        "protocol": HTTP.encryptionProtocol,                    // Determine the protocol
        "client_ip": HTTP.origin.toString(),                    // Client IP address
        "server_ip": HTTP.host.toString(),                      // Server IP address
        "method": HTTP.method,                                  // HTTP method (GET, POST, etc.)
        "uri": HTTP.uri,                                        // URI accessed
        "request_headers": HTTP.findHeaders("Request"),         // HTTP request headers
        "response_headers": HTTP.findHeaders("Response"),       // HTTP response headers
        "user_agent": HTTP.userAgent,                           // User agent string
        "content_type": HTTP.findHeaders("Content-"),           // Response content type
        "referrer": HTTP.referer,                               // Referer if specified
    };

    // HTTP.statusCode is not valid on HTTP_REQUEST
    if (HTTP.statusCode) {
        jsonData["response_code"] = HTTP.statusCode;            // HTTP response code
    }

    // HTTP.roundTripTime is not valid on HTTP_REQUEST
    if (HTTP.roundTripTime) {
        jsonData["duration"] = HTTP.roundTripTime;              // Transaction duration
    }

    if (HTTP.xss) {
        jsonData["xss"] = HTTP.xss;                             // An array of suspicious HTTP request fragments
    }

    // Convert the JSON object to a string
    var jsonString = JSON.stringify(jsonData);

  // Send the JSON data to the webhook URL using an HTTP POST request
  Remote.HTTP( SENTINELONE_ODS_TARGET ).post({
    'path': SENTINELONE_PATH,
    'headers': {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
    'payload': jsonString,
    'context': {
        'action': CONTEXT,
    },
    'enableResponseEvent': true,
  });

  debug(`version: ${version} | Sent test payload to SentinelOne`);

} else if ( event === 'REMOTE_RESPONSE' ) {
  var rsp = Remote.response,
      rspStatus = rsp.statusCode || null,
      rspBody = rsp.body ? rsp.body.toString() : null,
      rspContext = rsp.context || null;

  if ( rspContext instanceof Object && rspContext.action === CONTEXT ) {
    debug(`version: ${version} | statusCode: ${rspStatus} | responseContext: ${rspContext} | responseBody: ${rspBody}`);
  }
}