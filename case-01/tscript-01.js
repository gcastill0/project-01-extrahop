// Version
const version = "1.0.0";
// s1_ODS_target is configured as a target for an Open Data Stream
const SENTINELONE_ODS_TARGET = "s1_ODS_target";
const CONTEXT = "SentinelOne Test";
const SENTINELONE_PATH = "/services/collector/raw?sourcetype=extrahop";

// Check if the event is HTTP_REQUEST to capture transaction data
// Note: the HTTP_REQUEST uses HTTP.commitRecord to capture transaction

if ( event === 'HTTP_REQUEST' ) {
  // Create a JSON object with full record
  var jsonData = HTTP.commitRecord;

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