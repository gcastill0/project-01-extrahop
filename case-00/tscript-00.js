// Define the webhook URL where the JSON data will be sent
const s1_path = "/services/collector/raw?sourcetype=extrahop"

// Check if the event is TIMER_30SEC send hello world
if (event === 'TIMER_30SEC') {

    var jsonData = {
        "message": "Hello Work!"                // Hello Work! 
    };

    // Convert the JSON object to a string
    var jsonString = JSON.stringify(jsonData);

    // Send the JSON data to the webhook URL using an HTTP POST request
    Remote.HTTP("s1_ODS_target").post({
        "path": s1_path,
        "payload": jsonString,
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        enbleResponseEvent: true
    });
}

// If there is a response to the Remote.HTTP via REMOTE_RESPONSE
if (event === 'REMOTE_RESPONSE') {
    var rsp_body;
    if (Remote.response.body) { rsp_body = Remote.response.body.toString() }
    debug("Status Code: " + Remote.response.statusCode.toString() + "\n" + rsp_body)
}