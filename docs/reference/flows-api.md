# WhatsApp Flows API Reference

Source: https://developers.facebook.com/docs/whatsapp/flows/reference/flowsapi

[WhatsApp Business Platform](https://developers.facebook.com/docs/whatsapp) > [WhatsApp Flows](https://developers.facebook.com/docs/whatsapp/flows)

# Flows API

The Flows API is a [Graph API](https://developers.facebook.com/docs/graph-api/) that enables you to perform a variety of operations with Flows.

## Postman Collection

You can use the [Flows API postman collection](https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.postman.com%2Fmeta%2Fworkspace%2Fwhatsapp-business-platform%2Fdocumentation%2F24926895-7bf51205-92ed-49d1-af4a-0130cf84b6f6&h=AT2x20YmCLQDJgeTkzRESGEk06CrESm6cg0qYYf8GS0nEwQIDoQzByrA-2jGAvDPNRfKPC-R99mdnocpLxdAXEJniwPM9KGeoqB0R4JdI0oHCoNETfxrDI1MVifrd9IBK_qUWfDOrwXYHaTZ) to make API requests and generate code in different languages.

## Troubleshooting

See the troubleshooting section for the help with debugging API issues.

## Variables Required for API Calls

The following variables are required in these API calls.

Key |  Value | BASE-URL | Base URL for Facebook Graph API Example: https://graph.facebook.com/v18.0  
---|---  
ACCESS-TOKEN | User access token for authentication. This can be retrieved by copying the _Temporary access token_ from your app which expires in 24 hours. Alternatively, you can generate a [System User Access Token](https://developers.facebook.com/docs/whatsapp/business-management-api/get-started#system-user-access-tokens).  
WABA-ID | This can be retrieved by copying the _WhatsApp Business Account ID_ from your app.  
FLOW-ID | ID of a Flow returned after calling Create a Flow.  
  
## API Requests

### Creating a Flow

New Flows are created in `DRAFT` status. You can then make changes to the Flow by uploading an updated JSON file.

**Sample Request**
[code] 
    curl -X POST '{BASE-URL}/{WABA-ID}/flows' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}' \
    --header "Content-Type: application/json" \
    --data '{
      "name": "My first flow",
      "categories": [ "APPOINTMENT_BOOKING" ]
    }'
[/code]

Parameter |  Description |  Optional | `name` _string_|  Flow name |   
---|---|---  
`categories` _array_|  A list of Flow categories. Multiple values are possible, but at least one is required. Choose the values which represent your business use case. The list of values:

  * `SIGN_UP`
  * `SIGN_IN`
  * `APPOINTMENT_BOOKING`
  * `LEAD_GENERATION`
  * `CONTACT_US`
  * `CUSTOMER_SUPPORT`
  * `SURVEY`
  * `OTHER`

|   
`clone_flow_id` _string_|  ID of source Flow to clone. You must have permission to access the specified Flow. | ✓  
`endpoint_uri` _string_|  The URL of the WA Flow Endpoint. Starting from Flow JSON version 3.0 this property should be specified only via API. Do not provide this field if you are cloning a Flow with Flow JSON version below 3.0. | ✓  
  
**Sample Response**
[code] 
    {
      "id": "<Flow-ID>"
    }
[/code]

### Updating Flow's Metadata

After you have created your Flow, you can update the name or categories using the update request.

**Sample Request**
[code] 
    curl -X POST '{BASE-URL}/{FLOW-ID}' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}' \
    --header "Content-Type: application/json" \
    --data '{
      "name": "New flow name"
    }'
[/code]

Parameter |  Description |  Optional | `name` _string_|  Flow name | ✓  
---|---|---  
`categories` _array_|  A list of Flow categories. Missing value will keep existing categories. If provided, at least one values is required. | ✓  
`endpoint_uri` _string_|  The URL of the WA Flow Endpoint. Starting from Flow JSON version 3.0 this property should be specified via API or via the Builder UI. Do not provide this field if you are updating a Flow with Flow JSON version below 3.0. | ✓  
`application_id` _string_|  The ID of the Meta application which will be connected to the Flow. All the flows with endpoints need to have an Application connected to them. | ✓  
  
**Sample Response**
[code] 
    {
      "success": true,
    }
[/code]

### Updating a Flow's Flow JSON

To update Flow JSON for a specified Flow, use this request. Note that the file must be attached as form-data.

**Sample Request**
[code] 
    curl -X POST '{BASE-URL}/{FLOW_ID}/assets' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}' \
    --form 'file=@"/path/to/file";type=application/json' \
    --form 'name="flow.json"' \
    --form 'asset_type="FLOW_JSON"' # file must be attached as form-data
[/code]

Parameter |  Description |  Optional | `name` _string_|  Flow asset name. The value must be `flow.json` |   
---|---|---  
`asset_type` _string_|  Asset type. The value must be `FLOW_JSON` |   
`file` _json_|  File with the JSON content. The size is limited to 10 MB |   
  
**Sample Response**

Every update request will return validation errors in the Flow JSON, if any.
[code] 
    {
      "success": true,
      "validation_errors": [
        {
          "error": "INVALID_PROPERTY",
          "error_type": "JSON_SCHEMA_ERROR",
          "message": "The property \"initial-text\" cannot be specified at \"$root/screens/0/layout/children/2/children/0\".",
          "line_start": 46,
          "line_end": 46,
          "column_start": 17,
          "column_end": 30
        }
      ]
    }
[/code]

### Visualizing and interacting with your Flow using the Web Preview

In order to visualize the Flows created, you can generate a web preview URL with this request. The preview URL is public and can be shared with different stakeholders to visualize the Flow. You can also interact with it in a similar way users will interact on their phones adding the URL parameters described in the table below.

The final screens will render slightly differently for the end user. We recommend you always to test on a mobile device before publishing a Flow.

**Sample Request**
[code] 
    curl '{BASE-URL}/{FLOW-ID}?fields=preview.invalidate(false)' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Sample Response**
[code] 
    {
      "preview": {
        "preview_url": "https://business.facebook.com/wa/manage/flows/550.../preview/?token=b9d6....",
        "expires_at": "2023-05-21T11:18:09+0000"
      },
      "id": "flow-1"
    }
[/code]

The `preview_url` can also be embedded as an iframe into an existing website using the following code \(replace url with the one returned by the API\):
[code] 
    <iframe src="https://business.facebook.com/wa/manage/flows/550.../preview/?token=b9d6...." width="430" height="800" ></iframe>
[/code]

Field |  Description | preview\_url | Link for the preview page. This link does not require login and can be shared with stakeholders, but the link will expire in 30 days, or if you call the API with `invalidate=true` which will generate a new link.  
---|---  
expires\_at | Time when the link will expire and the developer needs to call the API again to get a new link \(30 days from link creation\).  
  
The following parameters can be added to the generated URL to configure the interactive Web Preview:

URL Parameter |  Description | interactive _boolean_|  If `true`, the preview will run in interactive mode. Defaults to `false`.  
---|---  
flow\_token _string_|  It will be sent as part of each request. You should always verify that token on your server to block any other unexpected requests. Required for Flows with endpoint. See [Sending a Flow](https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow).  
flow\_action _navigate | data\_exchange_|  First action when Flow starts. `data_exchange` if it will make a request to the endpoint, or `navigate` if it won't \(this will also require `flow_action_payload` to be provided\). See [Sending a Flow](https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow).  
flow\_action\_payload _string_|  Initial screen data in JSON format, escaped using [encodeURIComponent](https://l.facebook.com/l.php?u=https%3A%2F%2Fdeveloper.mozilla.org%2Fen-US%2Fdocs%2FWeb%2FJavaScript%2FReference%2FGlobal_Objects%2FencodeURIComponent&h=AT2XNSpvL1hi4-l8sf2z2blwluajh9s0tkMbRRzp-Xeo4ZS4oQCIxLpqx2HtxoXPwGAgfnLUDMxkYwcX0BDa_HiuiiYXtaK1cfNqiRYcYhx0Bq8cihhUqWIhVYbxM3chOPYVhLWsXCzH76XP). Required if `flow_action` is `navigate`. Should be omitted otherwise. See [Sending a Flow](https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow).  
phone\_number _string_|  Phone number that will be used to send the Flow, from which the public key will be used to encrypt the request payload. Required for Flows with endpoint. See [Sending a Flow](https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow).  
debug _string_|  Show actions in a separate panel while interacting with the preview. It will be ignored if `interactive` is not `true`.  
  
**Sample URL**
[code] 
    https://business.facebook.com/wa/manage/flows/550.../preview/?token=b9d6...&interactive=true&flow_action=navigate&flow_action_payload=%7B%22screen%22%3A%22FIRST_SCREEN%22%2C%22data%22%3A%7B%22screen_heading%22%3A%22hello%20world%22%7D%7D&debug=true
[/code]

### Deleting a Flow

While a Flow is in `DRAFT` status, it can be deleted. Use this request for that purpose.

**Sample Request**
[code] 
    curl -X DELETE '{BASE-URL}/{FLOW-ID}' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Sample Response**
[code] 
    {
      "success": true,
    }
[/code]

### Retrieving a List of Flows

To retrieve a list of Flows under a WhatsApp Business Account \(WABA\), use the following request.

**Sample Request**
[code] 
    curl '{BASE-URL}/{WABA-ID}/flows' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Sample Response**
[code] 
    {
        "data": [
        {
            "id": "flow-1",
            "name": "flow 1",
            "status": "DRAFT",
            "categories": [ "CONTACT_US" ],
            "validation_errors": []
        },
        {
            "id": "flow-2",
            "name": "flow 2",
            "status": "PUBLISHED",
            "categories": [ "SURVEY" ],
            "validation_errors": []
        },
        {
            "id": "flow-3",
            "name": "flow 3",
            "status": "DRAFT",
            "categories": [ "LEAD_GENERATION" ],
            "validation_errors": []
        }
        ],
        "paging": {
            "cursors": {
                "before": "QVFI...",
                "after": "QVFI..."
            }
        }
    }
[/code]

### Retrieving Flow Details

This request will return a single Flow's details. By default it will return the fields `id`,`name`, `status`, `categories`, `validation_errors`. You can request other fields by using the `fields` param in the request. The request example below includes all possible fields.

**Sample Request**
[code] 
    curl '{BASE-URL}/{FLOW-ID}?fields=id,name,categories,preview,status,validation_errors,json_version,data_api_version,endpoint_uri,whatsapp_business_account,application,health_status' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

To check that a flow can be used with a specific phone number, you can use the optional `health_status.phone_number(PHONE_NUMBER_ID)` parameter.

**Sample Response**
[code] 
    {
      "id": "<Flow-ID>",
      "name": "<Flow-Name>",
      "status": "DRAFT",
      "categories": [ "LEAD_GENERATION" ],
      "validation_errors": [],
      "json_version": "3.0",
      "data_api_version": "3.0",
      "endpoint_uri": "https://example.com",
      "preview": {
        "preview_url": "https://business.facebook.com/wa/manage/flows/55000..../preview/?token=b9d6.....",
        "expires_at": "2023-05-21T11:18:09+0000"
      },
      "whatsapp_business_account": {
        ...
      },
      "application": {
        ...
      },
      "health_status": {
        "can_send_message": "BLOCKED",
        "entities": [
          {
            "entity_type": "FLOW",
            "id": "<Flow-ID>",
            "can_send_message": "BLOCKED",
            "errors": [
              {
                "error_code": 131000,
                "error_description": "endpoint_uri: You need to set the endpoint URI before you can send or publish a flow.",
                "possible_solution": "https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson#top-level-flow-json-properties"
              },
              {
                "error_code": 131000,
                "error_description": "app_check: You need to connect a Meta app to the flow before you can send or publish it.",
                "possible_solution": "https://developers.facebook.com/docs/development/create-an-app"
              }
            ]
          },
          {
            "entity_type": "WABA",
            "id": "<WABA-ID>",
            "can_send_message": "AVAILABLE"
          },
          {
            "entity_type": "BUSINESS",
            "id": "<Business-ID>",
            "can_send_message": "AVAILABLE"
          },
          {
            "entity_type": "APP",
            "id": "<App-ID>",
            "can_send_message": "LIMITED",
            "additional_info": [
              "Your app is not subscribed to the message webhook. This means you will not receive any messages sent to your phone number."
            ]
          }
        ]
      }
    }
[/code]

Field |  Description |  Returned by default | `id` _string_|  The unique ID of the Flow. | ✓  
---|---|---  
`name` _string_|  The user-defined name of the Flow which is not visible to users. | ✓  
`status` _string_| `DRAFT`: This is the initial status. The Flow is still under development. The Flow can only be sent with `"mode": "draft"` for testing. `PUBLISHED`: The Flow has been marked as published by the developer so now it can be sent to customers. This Flow cannot be deleted or updated afterwards. `DEPRECATED`: The developer has marked the Flow as deprecated \(since it cannot be deleted after publishing\). This prevents sending and opening the Flow, to allow the developer to retire their endpoint. Deprecated Flows cannot be deleted or undeprecated. `BLOCKED`: Monitoring detected that the endpoint is unhealthy and set the status to Blocked. The Flow cannot be sent or opened in this state; the developer needs to fix the endpoint to get it back to Published state \(more details in [Flows Health and Monitoring](https://developers.facebook.com/docs/whatsapp/flows/reference/healthmonitoring)\). `THROTTLED`: Monitoring detected that the endpoint is unhealthy and set the status to Throttled. Flows with throttled status can be opened, however only 10 messages of the Flow could be sent per hour. The developer needs to fix the endpoint to get it back to the `PUBLISHED` state \(more details in [Flows Health and Monitoring](https://developers.facebook.com/docs/whatsapp/flows/reference/healthmonitoring)\). | ✓  
`categories` _array_|  A list of flow categories. | ✓  
`validation_errors` _array_|  A list of errors in the Flow. **All errors must be fixed before the Flow can be published.** | ✓  
`json_version` _string_|  The version specified by the developer in the Flow JSON asset uploaded. |   
`data_api_version` _string_|  The version of the Data API specified by the developer in the Flow JSON asset uploaded. Only for Flows with an Endpoint. |   
`data_channel_uri` _string_| **\[DEPRECATED in API v19.0 \] Use`endpoint_uri` field instead.** The URL of the WA Flow Endpoint specified by the developer via API or in the Builder UI. |   
`endpoint_uri` _string_|  The URL of the WA Flow Endpoint specified by the developer via API or in the Builder UI. |   
`preview` _object_|  The URL to the web preview page to visualize the flow and its expiry time. |   
`whatsapp_business_account` _object_|  The WhatsApp Business Account which owns the Flow. |   
`application` _object_|  The Facebook developer application used to create the Flow initially. |   
`health_status` _object_|  A summary of the Flows health status. When you attempt to send a Flow, multiple nodes are involved, including the app, the business portfolio that owns or has claimed it, a WABA and Flow. Each of these nodes can have one of the following health statuses assigned to the `can_send_message` property:

  * `AVAILABLE`: Indicates that the node meets all requirements.
  * `LIMITED`: Indicates that the node meets requirements, but has some limitations. If a given node has this value, [additional info](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/cloud-api/health-status/#additional-info-property) will be included.
  * `BLOCKED`: Indicates that the node does not meet one or more messaging requirements. If a given node has this value, the [errors property](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/cloud-api/health-status/#errors-property) will be included which describes the error and a possible solution.

**Flow node** The Flow node will have the `can_send_message` property set to:

  * `LIMITED`: If published Flow is in [`THROTTLED` state](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring). 
  * `BLOCKED`: 
    * If unpublished Flow has one of the the [publishing checks](https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring#publishing-checks) failing.
    * If published Flow is in `BLOCKED` or `DEPRECATED` [state](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring).

For more details about other nodes and rest of the properties see [Messaging Health Status page](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/cloud-api/health-status/#messaging-health-status-2). |   
  
### Retrieving a Flow's List of Assets

Returns all assets attached to a specified Flow.

**Sample Request**
[code] 
    curl '{BASE-URL}/{FLOW-ID}/assets' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
    
[/code]

**Sample Response**
[code] 
    {
      "data": [
        {
          "name": "flow.json",
          "asset_type": "FLOW_JSON",
          "download_url": "https://scontent.xx.fbcdn.net/m1/v/t0.57323-24/An_Hq0jnfJ..."
        }
      ],
      "paging": {
        "cursors": {
          "before": "QVFIU...",
          "after": "QVFIU..."
        }
      }
    }
[/code]

### Publishing a Flow

This request updates the status of the Flow to "PUBLISHED". You can either edit this flow in the future and turn it back to the "DRAFT" state, or create a new flow by specifying the existing Flow ID as the `clone_flow_id` parameter. For more details, visit the [Lifecycle of a Flow](https://developers.facebook.com/docs/whatsapp/flows/reference/lifecycle) page.

You can publish your Flow once you have ensured that:

  * Your business is [verified](https://developers.facebook.com/docs/development/release/business-verification/) and maintains a [high message quality](https://developers.facebook.com/docs/whatsapp/messaging-limits#messaging-quality). 

  * All validation errors and [publishing checks](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/flows/guides/healthmonitoring#publishing-checks) have been resolved.
  * The Flow meets the [design principles](https://developers.facebook.com/docs/whatsapp/flows/guides/bestpractices) of WhatsApp Flows
  * The Flow complies with [WhatsApp Terms of Service](https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.whatsapp.com%2Flegal%2Fterms-of-service%2F%3Flang%3Den&h=AT3e31mknIOu7SYWUggh-_4bMx9g3c-jQL5jZu-h9lMdzQQpGm6sBluptB3ZsU2X55B-k1wl9_gqOiHH6RSZAKBNJQ0ewXtHyBocAT7rhOohtZ284VqUlFh3Zd16z_8_0MWwcsOlwhxumwUX), the [WhatsApp Business Messaging Policy](https://l.facebook.com/l.php?u=https%3A%2F%2Ffaq.whatsapp.com%2F933578044281252&h=AT0oZiSexq289B8NDPbSdiH99g9-PSW7QzE7iJFlowQBjbdA5SIi9U06k-uuxoZhKBIHvlPSEcmnKfA5Ng0HNsdW5AH4veWGb5nUEvwyLW3o7jlPaYAEl_1bM9E9RTiw2zhV9p8ErxfJHDMg) and, if applicable, the [WhatsApp Commerce Policy](https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.whatsapp.com%2Flegal%2Fcommerce-policy%2F%3Flang%3Den&h=AT3zm0MNsJHaQ3OiqxNcQ5nHvt5zphZrfmQ5-NhEOTnICadtCdhW5n603V9ZxUuXYv5_w_Syhr6aWpkbq2kUxRRo-23Emc0G3t0zHkxkM4wzo-NaZmJlvedQqoQr7sWPXi2JChbk-7UQKuNa)

**Sample Request**
[code] 
    curl -X POST '{BASE-URL}/{FLOW-ID}/publish' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Sample Response**
[code] 
    {
      "success": true
    }
[/code]

### Deprecating a Flow

Once a Flow is published, it cannot be modified or deleted, but can be marked as deprecated.

**Sample Request**
[code] 
    curl -X POST '{BASE-URL}/{FLOW-ID}/deprecate' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Sample Response**
[code] 
    {
      "success": true,
    }
[/code]

### Migrate Flows

Migrate Flows from one WhatsApp Business Account \(WABA\) to another. Migration doesn't move the source Flows, it creates copies of them with the same names in the destination WABA.

**Notes:**

  * You can specify specific Flow names to migrate, or choose to migrate all Flows in source WABA. 
  * Flows can only be migrated between WABAs owned by the same Meta business.
  * If a Flow exists with the same name in the destination WABA, it will be skipped and the API will return an error message for that Flow. Other Flows in the same request will be copied.
  * The migrated Flow will be published if the original Flow is published, otherwise it will be in draft state.
  * New Flows under destination WABA will have new Flow IDs.

#### Request syntax
[code] 
    curl -X POST '{BASE-URL}/<DESTINATION_WABA_ID>/migrate_flows?source_waba_id=<SOURCE_WABA_ID>
    &source_flow_names=<SOURCE_FLOW_NAMES>' \
    --header 'Authorization: Bearer {ACCESS-TOKEN}'
[/code]

**Parameters**

Placeholder| Description| Example Value| `<DESTINATION_WABA_ID>` _WhatsApp Business Account ID_ | **Required.** Destination WhatsApp Business Account ID. | `104996122399160`  
---|---|---  
`<SOURCE_WABA_ID>` _WhatsApp Business Account ID_ | **Required.** Source WhatsApp Business Account ID. | `102290129340398`  
`<SOURCE_FLOW_NAMES>`  
_Array_ | **Optional.** List of specific Flow names to migrate. If not specified, it will migrate all flows in source WABA. Only 100 Flows can be migrated in a request. | \[ "appointment-booking", "lead-gen" \]  
  
#### Response
[code] 
    {
      "migrated_flows": [
        {
          "source_name": "appointment-booking",
          "source_id": "1234",
          "migrated_id": "5678"
        }
      ],
      "failed_flows": [
        {
          "source_name": "lead-gen",
          "error_code": "4233041",
          "error_message": "Flows Migration Error: Flow with the same name exists in destination WABA."
        }
      ]
    }
[/code]

## Troubleshooting

Issue |  Potential cause |  Steps to resolve | Received a permission error while calling the API | Insufficient Permissions | You can check your permissions with the following link \(replace WA Business Account ID and Business ID with your values\)   
https://business.facebook.com/settings/whatsapp-business-accounts/\{waba-id\}?business\_id=\{business-id\}   
To use Flows API you need **Message templates \(view and manage\)** and **Phone Numbers \(view and manage\)** permissions.  
---|---|---  
| Incorrect Access Token | Use the Access Token Debugger tool to verify your token permissions   
<https://developers.facebook.com/tools/debug/accesstoken>   
In _Scopes_ field, you should have **whatsapp\_business\_management, whatsapp\_business\_messaging**. And under _Granular Scopes_ section you should see your WABA Id under both **whatsapp\_business\_management** and **whatsapp\_business\_messaging**   
After you verify access token, please try to make basic request with the the token, like `GET /waba-id` or `GET /flow-id`.  
| Invalid request syntax | Use the [Postman Collection](https://l.facebook.com/l.php?u=https%3A%2F%2Fwww.postman.com%2Fmeta%2Fworkspace%2Fwhatsapp-business-platform%2Fdocumentation%2F24926895-7bf51205-92ed-49d1-af4a-0130cf84b6f6&h=AT1eNJOzTpGWTLq2pgUN761XnBxLMXRoIcDiAMeX7qGk4b7jmVdulkwf-7qZ36M-5K7qyL04pTN2NlBpO4HgquoD8zI0HsJGGSSLmUnfHcGuGcMlR7bwJhHxeznTeTP9vzmm5zsZsygKv5ER) to make the same request.  
  
[←PreviousFlow JSON](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson)

[→NextError Codes](/web/20241209042535/https://developers.facebook.com/docs/whatsapp/flows/reference/error-codes)
