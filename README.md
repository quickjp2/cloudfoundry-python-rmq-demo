# Python RabbitMQ demo for cloudfoundry
## Setup
The only setup required is to create a rabbitmq service in your org/space within cloudfoundry.

### Notes
- If the rabbitmq service is named something other than `p-rabbitmq` in the marketplace, you will need to update the manifest file with your marketplace service name.
- You will need to give the service the name `rmq-demo`; if you name it anything different, you will need to update your manifest.

