# Alexa Find Any Film
## Amazon Echo Alexa Integration with findanyfilm.com for UK 

to be deployed using AWS and Alexa Skills kit 

### AWS Lambda

edit keys.py with your alexa skill key  
deploy the aws lambda deployment package contents as a zip file  
  
**runtime:** python 2.7  
**handler:** lambda.lambda_handler  
**role:** choose existing role  
**eisting role:** lambda_basic_execution  
**trigger:** alexa skills kit  

### Alexa Skills Kit

**intents:** intents.js  
**custom slot type:** LOCATIONS values: locations.txt  
**samle utterances:** sample-utterances.txt      

### Usage

Alexa, ask films what's playing in {location} on the {date}
