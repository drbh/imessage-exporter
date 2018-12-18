#!/usr/bin/env python
import os, sys, sqlite3, datetime, json, math, boto3, config
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, LOCAL_FILE_NAME

USERNAME = os.popen('whoami').read().strip()

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class DataGrabber(object):
    """
    This class connects to the sqlite DB under iMessage, 
    it then exports all of the conversations to a tmp file 
    and uploads it to a s3 bucket
    """
    def __init__(self):
        # print '/Users/'+USERNAME+'/Library/Messages/chat.db'
        self.conn = sqlite3.connect('/Users/'+USERNAME+'/Library/Messages/chat.db', check_same_thread=False)
        self.OSX_EPOCH = 978307200

    def get_handles_like(self, search):
        c = self.conn.cursor()
        c.execute("SELECT * FROM `handle` WHERE ROWID ="+search)
        all_handles = c.fetchall()
        c.close()
        return all_handles

    def get_all_messages(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM `message`" )
        all_messages = c.fetchall()[::-1]
        payload = []
        for message in all_messages:
            # skip ones that are reactions
            if message[52] > 0:
                continue

            payload += [ { 
                "guid" :message[1], 
                "message": message[2], 
                "reaction": message[52],
                "time": str(datetime.datetime.fromtimestamp(message[15] + self.OSX_EPOCH)), 
                "sentby": message[21], 
                "from": message[5] 
            } ]

        c.close()
        return payload

client = DataGrabber()
start = datetime.datetime.now()
print datetime.datetime.now(), "Fetching Message from DB"
results = client.get_all_messages()

uni_sender = set()
for m in results:
    uni_sender.add(m['from'])

who_map = {}
for send in uni_sender:
    handles = client.get_handles_like(str(send))
    if len(handles) < 1:
        # print str(send), handles
        who_map[str(send)] = "NOT STORED"
        continue
    who_map[str(send)] = handles[0][1]
    # print handles[0][1]

for ms in results:
    ms['from'] = who_map[str(ms['from'])]

print datetime.datetime.now(), "Writing to tmp file"
with open(LOCAL_FILE_NAME, 'w') as outfile:
    json.dump(results, outfile, indent=4)
print datetime.datetime.now(), "Data extracted and saved"
print datetime.datetime.now(), "File size:", convert_size(os.path.getsize(LOCAL_FILE_NAME))

print datetime.datetime.now(), "Connecting to AWS"
s3 = boto3.resource('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
make_bucket = s3.create_bucket(Bucket=BUCKET_NAME)
print datetime.datetime.now(), "Saving file to cloud"
s3.Object(BUCKET_NAME, LOCAL_FILE_NAME).put(Body=open(LOCAL_FILE_NAME, 'rb'))
print datetime.datetime.now(), "Cloud upload complete"
print datetime.datetime.now(), "Proccess took:", datetime.datetime.now() - start


