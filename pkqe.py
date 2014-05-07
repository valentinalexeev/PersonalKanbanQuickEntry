#!python
# Personal Kanban QuickEntry tool
#
# Author: Valentin Alexeev <valentin.alekseev@gmail.com>
# License: Apache License v2

# Usage:
# pkqe.py <text of the new task with tags>
#   Possible tags:
#       #<tag> - assign tag to the task
#       @<person> - assign task to a specific person (search by Initials)
#       %<topic> - set a specific topic on a task
#       $<column> - assign column directly
#       !! - set High priority (must precede the message)
#       ! - set Medium priority (must precede the message)

defaultColumn = 'Pending';
redisHostname = 'localhost';
redisPort = 6379;
redisDb = 0;

import uuid
import redis
import json
import string
import sys

def pkKeyDict(r, keyPattern, nameKey = 'Name'):
	idList = r.keys(keyPattern + '*');
	keys = map(lambda x: x.replace(keyPattern,'').replace('-', ''), idList);
	resultDict = dict(zip(map(lambda tag: json.loads(r.get(tag))[nameKey], idList), keys))
	return resultDict

taskUuid = str(uuid.uuid4())
defaultId = "00000000000000000000000000000000";

# 0. connect to redis
r = redis.StrictRedis(host=redisHostname, port=redisPort, db=redisDb)
# 1. load topics (dict topic name->id)
topicDict = pkKeyDict(r, "pk:urn:topic:");
# 2. load tags (dict tag->id)
tagDict = pkKeyDict(r, "pk:urn:tag:");
# 3. load columns (dict column->id)
columnDict = pkKeyDict(r, "pk:urn:column:");
# 4. load person (dict initials->id)
personDict = pkKeyDict(r, "pk:urn:person:", "Initials");

# x. Parse input string
sys.argv.pop(0)
task = " ".join(sys.argv)
taskTokens = task.split()
# find tags
tags = filter(lambda x: string.find(x, '#') == 0, taskTokens)
taskTokens = filter(lambda x: string.find(x, '#') != 0, taskTokens)
# find topic
topic = filter(lambda x: string.find(x, '%') == 0, taskTokens)
taskTokens = filter(lambda x: string.find(x, '%') != 0, taskTokens)
# find person
person = filter(lambda x: string.find(x, '@') == 0, taskTokens)
taskTokens = filter(lambda x: string.find(x, '@') != 0, taskTokens)
# find column
column = filter(lambda x: string.find(x, '$') == 0, taskTokens)
taskTokens = filter(lambda x: string.find(x, '$') != 0, taskTokens)

priority = 'Low'
if taskTokens[0] == "!":
	priority = 'Medium'
	taskTokens.pop(0)
elif taskTokens[0] == "!!":
	priority = 'High'
	taskTokens.pop(0)

task = ' '.join(taskTokens)

# 4. prepare task
taskDetails = dict()
taskDetails['Link'] = '';
taskDetails['Text'] = task
taskDetails['Id'] = taskUuid.replace('-', '');
taskDetails['Priority'] = priority;
taskDetails['Tags'] = map(lambda x: tagDict[x[1:]], tags);

taskDetails['TopicId'] = defaultId;
if topic:
	taskDetails['TopicId'] = topicDict[topic[0][1:]]; # xxx lookup

taskDetails['ColumnId'] = columnDict[defaultColumn]; # XXX default column ID
if column:
	taskDetails['ColumnId'] = columnDict[column[0][1:]];

taskDetails['PersonId'] = defaultId
if person:
	taskDetails['PersonId'] = personDict[person[0][1:]];

taskDetails['Canceled'] = False;
taskDetails['HasDeadline'] = False;
taskDetails['Points'] = 0;
taskDetails['Done'] = False;
taskDetails['Estimate'] = 0;
taskDetails['Subtasks'] = [];
# 5. submit to redis

print json.dumps(taskDetails);
r.set('pk:urn:task:' + taskUuid, json.dumps(taskDetails));
r.sadd('pk:ids:Task', taskUuid);
