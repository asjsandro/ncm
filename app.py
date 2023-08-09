'''
import urllib3
import json

headers = {
    'X-Cosmos-Token': 'Hgm9hZI5iYtD43QHifSgiQ',
    'Content-Type': 'application/json',
    'User-Agent': 'asjsandro'
    }
req      = urllib3.request('https://api.cosmos.bluesoft.com.br/gtins/7891910000197.json', None, headers)

response = urllib3.response(req)
data     = json.loads(response.read())

print(json.dumps(data, indent=4))
'''

import urllib3
import json
# Create an HTTP connection pool
http = urllib3.PoolManager()
ean = '7891910000197'
# Set the custom headers
custom_headers = {
   'X-Cosmos-Token': 'Hgm9hZI5iYtD43QHifSgiQ',
    'Content-Type': 'application/json',
    'User-Agent': 'asjsandro'
 }

# Make a GET request to a URL with the custom headers
r = http.request('GET', f'https://api.cosmos.bluesoft.com.br/gtins/{ean}.json', None, headers=custom_headers)

# Check the status code of the response
if r.status == 200:
    # If the status code is 200, the request was successful
    # Do something with the response data
    response_data = r.data
    #print(response_data)
    data     = json.loads(response_data.decode('utf-8'))
    #print(json.dumps(data, indent=4))
    print('descricao: ', data['description'])
    print('ncm: ', data['ncm']['code'])
    print('cest: ', data['cest']['code'])
else:
    print('request error!')