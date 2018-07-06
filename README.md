# Python RabbitMQ demo for cloudfoundry
## Setup
The only setup required is to create a rabbitmq service in your org/space within cloudfoundry.

### Notes
- If the rabbitmq service is named something other than `p-rabbitmq` in the marketplace, you will need to update the manifest file with your marketplace service name.
- You will need to give the service the name `rmq-demo`; if you name it anything different, you will need to update your manifest.

## Walkthrough
### Deploying an app
- Take a look at the folder structure and the manifest
  - Notice that all connection info variables are environment variables
- Call out the services and the manifest variables
- Try the push
- Create the services for the apps
- Try the push
- Show healthchecks
- Hit api to generate message

### HA
- Simulate slow receiver, then scale!
- Show GUI
- Kill the GUI!
- That's not good, scale up?
- TADA! Highlander mode! We can kill one instance of the GUI but us as a customer don't see the site go down.

### Helpful stuff
#### Custom message call
`<URL>/test`
```JSON
{
    "message": "Some cool message!"
}
```