# Welcome to iMessage Exporter

[![Join the chat at https://gitter.im/imessage-exporter/community](https://badges.gitter.im/imessage-exporter/community.svg)](https://gitter.im/imessage-exporter/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Esstentailly this project takes a MacBook iMessage sqlite db, pulls all of your converstations, and pushes it to a JSON file into a secure S3 bucket.

This way a user can access a snapshot of thier chat data from a cloud location they control.

The next script pulls this data (not from the cloud but a local copy) and makes a frequency table of the emojies in the convo from a specified point in time.


You need to set AWS creds in as env vars with permissions to create a new bucket and write to S3

```
export AWS_ACCESS_KEY_ID=- - - YOUR KEY HERE - - -
export AWS_SECRET_ACCESS_KEY=- - - YOUR KEY HERE - - -  
```

clone the repo and navigate to the folder   
```
python run.py. 
```
