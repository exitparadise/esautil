#!/usr/bin/env python
#
# https://github.com/exitparadise/esautil.git
# tim talpas github.festive812@passfwd.com
# 

import requests, sys
from requests.exceptions import HTTPError

def api_request(METHOD,KEY,HOST,VERIFY,LOC,PAYLOAD=None):
    url = f'https://{HOST}/{LOC}'
    headers = {
        'kbn-xsrf': 'reporting',
        'Content-Type': 'application/json',
        'Authorization': f'ApiKey {KEY}',
        'Elastic-Api-Version': '2023-10-31'
    }
    if METHOD == 'GET':
        response = requests.get(url, headers=headers, verify=VERIFY)
    elif METHOD == 'POST':
        response = requests.post(url, headers=headers, json=PAYLOAD, verify=VERIFY)
    elif METHOD == 'PUT':
        response = requests.put(url, headers=headers, json=PAYLOAD, verify=VERIFY)
    else:
       sys.exit(f"method {METHOD} not recognized")

    if response.status_code == 200:
        content = response.json()
        return content
    else:
        e = response.json()
        sys.exit(f"ERROR: {e['error']['reason']}")
