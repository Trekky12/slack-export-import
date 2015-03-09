import json
import os
import re
import unicodecsv
import requests


home_dir = os.path.dirname(os.path.abspath(__file__))

user_file = open(os.path.join(home_dir, 'users.json'))
user_data = json.load(user_file)
user_file.close()

users = {}
for user in user_data:
    users.update({
        user['id']: user['name'],
    })


def replace_username(matchobj):
    return '@%s' % users[matchobj.group(1)]

with open('import.csv', 'wb') as csvfile:
    writer = unicodecsv.writer(csvfile)

    for (dirpath, dirnames, filenames) in os.walk(home_dir):
        for filename in filenames:
            base_name, extension = os.path.splitext(filename)
            if extension == '.json' and base_name != 'users':
                json_file = open(os.path.join(dirpath, filename))
                message_data = json.load(json_file)
                json_file.close()

                for message in message_data:
                    # ts
                    ts = message['ts'].split('.')[0]
                    # channel
                    channel = os.path.split(dirpath)[1]
                    # username
                    try:
                        user = users[message['user']]
                    except KeyError:
                        continue
                    if message.get('subtype', None):
                        #continue
                        if 'file' in message:
                            if 'url_download' in message['file']:
                                r = requests.get(message['file']['url_download'])
                                if (r.status_code == requests.codes.ok):
                                    with open(os.path.basename( os.path.realpath(message['file']['url_download']) ), "wb") as code:
                                        code.write(r.content)
                                print message['file']['url_download']
                        continue
                    # text
                    text = message['text']
                    text = re.sub(r'<@(?P<username>.{9})>', replace_username, text)
                    writer.writerow([ts, channel, user, text])
