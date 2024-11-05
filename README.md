# Configure an HTTP target for an Open Data Stream

### 1. Log in to the Administration settings.

Log on the ExtraHop system through `https://<extrahop-hostname-or-IP-address>/admin`.

### 2. Add an **HTTPS** Target

In the System Configuration section,  click **Open Data Streams**. Fill in the following:

|     |     |
| --- | --- |
| Host  | ingest.us1.sentinelone.net |
| Extra Headers | Authorization : Bearer 0abc1dAeB2CfghDiEFj5klmG_JKnopq6Hr7sIMNOtPv8== |
| Options |{ <br> &nbsp;&nbsp;&nbsp;&nbsp; "path": "/services/collector/raw?sourcetype=extrahop",<br> &nbsp;&nbsp;&nbsp;&nbsp; "headers" : { <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "Content-Type" : ["application/json"], <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "Authorization" : ["Bearer  authToken"] <br> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; }, <br> &nbsp;&nbsp;&nbsp;&nbsp; "Payload": "Validation test" <br> }  |
|     |     |

### 3. Options field

The documentation indicates that you must specify headers as an array, even if you specify only one header. For example: 

> `"headers": {"content-type":["application/json"]}`

Your validation test should look somewhat as follows:

```json
{
    "path": "/services/collector/raw?sourcetype=extrahop",
    "headers": {
        "Content-Type" : ["application/json"],
        "Authorization" : ["Bearer 0abc1dAeB2CfghDiEFj5klmG_JKnopq6Hr7sIMNOtPv8=="]
    },
    "Payload": "Validation test"
}
```

### 4. Configure Extra Headers

Place the `Authorization` header in the Additional Headers section. Use the following syntax:

```
Authorization : Bearer 0abc1dAeB2CfghDiEFj5klmG_JKnopq6Hr7sIMNOtPv8==
```