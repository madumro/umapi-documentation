# Copyright (c) 2023 Adobe Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy of this 
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# https://adobe-apiplatform.github.io/umapi-documentation/en/api/group.html
# GET /v2/usermanagement/groups/{orgId}/{page}

import json
import requests

# obtained via JWT or OAuth S2S workflow
ACCESS_TOKEN = ''
CLIENT_ID = ''
ORG_ID = ''
UMAPI_URL = 'https://usermanagement.adobe.io/v2/usermanagement/groups/'
# default call management settings
MAX_RETRIES = 4
TIMEOUT = 120.0
RANDOM_MAX = 5
FIRST_DELAY = 3


def get_groups_and_profiles():
    # returns list of dict objects, each one representing one group
    page_index = 0
    url = UMAPI_URL + ORG_ID + '/' + str(page_index)
    method = 'GET'
    done = False
    all_groups = []
    # resolve multiple page results
    while not done:
        r = make_call(method, url)
        last_page = r['lastPage']
        if last_page:
            all_groups.extend(r['groups'])
            done = True
        else:
            all_groups.extend(r['groups'])
            page_index += 1
    return all_groups

def make_call(method, url, body={}):
    # call manager function with retry mechanism
    # returns the API response
    retry_wait = 0
    h = {'Accept' : 'application/json',
         'x-api-key' : CLIENT_ID,
         'Authorization' : 'Bearer ' + ACCESS_TOKEN}
    if body:
        h['Content-type']  = 'application/json'
        body = json.dumps(body)
        method = 'POST'
    for num_attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f'Calling {method} {url}\n{body}' )
            r = requests.request(method, url, data=body, headers=h, timeout=TIMEOUT)
            if r.status_code == 200:
                return json.loads(r.text)
            elif r.status_code in [429, 502, 503, 504]:
                print(f'UMAPI timeout... (code {r.status_code} on try {num_attempt})')
                if retry_wait <= 0:
                    delay = randint(0, RANDOM_MAX)
                    retry_wait = (pow(2, num_attempt - 1) * FIRST_DELAY) + delay
                if 'Retry-After' in r.headers.keys():
                    retry_wait = int(r.headers['Retry-After']) + 1
            else:
                print(f'Unexpected HTTP Status: {r.status_code}: {r.text}')
                return
        except Exception as e:
            print(f'Exception encountered:\n {e}')
            return
        if num_attempt < MAX_RETRIES:
            if retry_wait > 0:
                print(f'Next retry in {retry_wait} seconds...')
                sleep(retry_wait)
    print(f'UMAPI timeout... giving up after {MAX_RETRIES} attempts.')
        
if __name__ == '__main__':
    groups = get_groups_and_profiles()
    if groups:
        for group in groups:
            print(group)

