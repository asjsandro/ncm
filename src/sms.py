import urllib3
import json
# Create an HTTP connection pool
# Set the custom headers
ENDPOINT = ''

def find_ncm(ean):
    http = urllib3.PoolManager()
    custom_headers = {
        'X-Cosmos-Token': 'Hgm9hZI5iYtD43QHifSgiQ',
        'Content-Type': 'application/json',
        'User-Agent': 'asjsandro'
        }

    # Make a GET request to a URL with the custom headers
    r = http.request('POST', f'https://api.cosmos.bluesoft.com.br/gtins/{ean}.json', None, headers=custom_headers)

    # Check the status code of the response
    if r.status == 200:
        # If the status code is 200, the request was successful
        # Do something with the response data
        response_data = r.data
        data     = json.loads(response_data.decode('utf-8'))
        value = {
            "description": data['description'],
            "ncm": data['ncm']['code'],
            "cest": data['cest']['code']
        }
        
        return(value)
    else:
        return('request error!')
    
if __name__ == '__main__':
    for i in range(20):
        pass
    
    ean = '7891910000197'
    consulta = find_ncm(ean)
    print('Descricao: ',consulta['description'])
    print('Ncm: ',consulta['ncm'])
    print('Cest: ',consulta['cest'])
        