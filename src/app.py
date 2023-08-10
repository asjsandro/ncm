import urllib3
import json
# Create an HTTP connection pool
# Set the custom headers
import configparser
import pyodbc

#Get environment variavel
config = configparser.ConfigParser()
config.read('./config.ini')
host =  config['VM']['host']
database = config['VM']['database'] 
user = config['VM']['user'] 
password = config['VM']['password'] 
driver = 'ODBC Driver 18 for SQL Server '
#driver = config['PRODUCAO']['driver']


def DBConnect():
    dbConn = pyodbc.connect(driver=driver, 
                             host=host, 
                             database=database,
                             user=user, 
                             password=password)
    # dbConn = pyodbc.connect(DSN='SICNET',UID=user,PWD=password)
    return dbConn.cursor()

def DBQuery(cur, query, params = []):
    # Run a DB Query and return the results as a list of dicts
    cur.execute(query, params)
    headers = [item[0] for item in cur.description] 
    returndata = []
    for x in cur:
        thisrow = {}
        for i, y in enumerate(x):
            thisrow[headers[i]] = y
        returndata.append(thisrow)
    return returndata



def find_ncm(ean):
    http = urllib3.PoolManager()
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
    query = '''
SELECT TOP 15
	t.codigo,
	t.produto ,
	t.fabricante ,
	t.codipi ,
	t.cest
from 
	TABEST1 t 
where 
	t.codipi is null
'''

    cur = DBConnect()
    produtos = DBQuery(cur,query, [])
    for produto in produtos:

        ean = produto['codigo']#'7891910000197'
        consulta = find_ncm(ean)
        print('Descricao: ',consulta['description'])
        print('Ncm: ',consulta['ncm'])
        print('Cest: ',consulta['cest'])
            
        