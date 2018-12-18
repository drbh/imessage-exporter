# -*- coding: utf-8 -*-

import json, re, datetime, boto3
from pprint import pprint
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, \
LOCAL_FILE_NAME, EMOJI_FILE_NAME, HTML_FILE
from uniseg import graphemecluster as gc
import emoji

start = datetime.datetime.now()
print datetime.datetime.now(), "Fetching Messages from file"

with open(LOCAL_FILE_NAME) as f:
    data = json.load(f)

filt = filter(lambda x: x['time'] > "2018-12-09 00:00:00", data)


print datetime.datetime.now(), "Extracting Emojis"

results = []
for msg in filt:
	if msg['message'] == None:
		continue

	done = []
	emjs = [x.encode('utf-8') for x in gc.grapheme_clusters(msg['message'])]
	for aaa in emjs:
		if len(aaa) < 4:
			continue
		a = aaa
		m = json.dumps({"k": a})
		# print(len(a),json.loads(m)["k"])  # 
		done += [json.loads(m)["k"].encode("utf-8")]
	emjs=done
	results += [{"emojis": emjs, "time": msg['time'], "who": msg['from']}]


print datetime.datetime.now(), "People people frequencies"

people = {}
for t in results:
	# ADD PERSON IF NOT IN CACHE
	if t['who'] not in people:
		people[t['who']] = {}
	# ADD ALL EMOJIS PER MSG TO PEOPLE COUNT OBJ
	for e in t['emojis']:
		e_key = e#.encode('utf-16', 'surrogatepass').decode('utf-16')
		if e not in people[t['who']]:
			people[t['who']][e_key] = 0
		people[t['who']][e_key] += 1

print datetime.datetime.now(), "Save to file"

with open(EMOJI_FILE_NAME, 'w') as outfile:
    json.dump(people, outfile, indent=4)


print datetime.datetime.now(), "Building HTML"

htm = "<html>"

htm += """
<head>
	<style>
	.grid-container {
	  display: grid;
	  grid-template-columns: auto auto auto;
	  background-color: #f0f0f0;
	  padding: 10px;
	}
	.grid-item {
	  background-color: rgba(255, 255, 255, 0.8);
	  border: 1px solid rgba(0, 0, 0, 0.8);
	  padding: 20px;
	  margin: 5px 5px 5px 5px;
	  font-size: 30px;
	  text-align: center;
	}
	</style>
</head>
"""

for person, emjicount in people.iteritems():
	if len(emjicount) == 0:
		continue
	s = '<div class="grid-container">'
	s += '<div class="person">' +  str(person) + '</div>'
 	for emo, c in emjicount.iteritems():
 		# print emo.encode("utf-8")
		s += '<div class="grid-item">' +  emo + ' - ' + str(c) + '</div>'

	s += '</div>'
	htm += s

htm += "</html>"

print datetime.datetime.now(), "Write HTML file"

# Write HTML String to file.html
with open(HTML_FILE, "w") as file:
    file.write(htm)


print datetime.datetime.now(), "Connecting to AWS"
s3 = boto3.resource('s3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
make_bucket = s3.create_bucket(Bucket=BUCKET_NAME)
print datetime.datetime.now(), "Saving file to cloud"
s3.Object(BUCKET_NAME, EMOJI_FILE_NAME).put(Body=open(EMOJI_FILE_NAME, 'rb'))
print datetime.datetime.now(), "Cloud upload complete"
print datetime.datetime.now(), "Proccess took:", datetime.datetime.now() - start




