// s1_ODS_target is configured as a target for an Open Data Stream
const s1_path = "/services/collector/raw?sourcetype=extrahop"

// Check if the event is DNS_REQUEST to capture transaction data

if (event === "DNS_REQUEST") {
    // Create a JSON object with full record
    var jsonData = DNS.record;

    // Convert the JSON object to a string
    var jsonString = JSON.stringify(jsonData);

    // Send the JSON data to the webhook URL using an HTTP POST request
        Remote.HTTP('s1_ODS_target').post({
            'path': s1_path,
            'payload': jsonString
        });
}