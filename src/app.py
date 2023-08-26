import configparser
import pyodbc
from zeep import Client
import pprint as pp
import time
from lxml import objectify

#Get environment variavel
config = configparser.ConfigParser()
config.read('./src/config.ini')
host =  config['PRODUCAO']['host']
database = config['PRODUCAO']['database'] 
user = config['PRODUCAO']['user'] 
password = config['PRODUCAO']['password']
driver = config['PRODUCAO']['driver']
token = config['PRODUCAO']['token_sic']

def DBConnect():
    dbConn = pyodbc.connect(driver=driver, 
                             host=host, 
                             database=database,
                             user=user, 
                             password=password,
                            )
    
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

def find_ncm_sic(ean, token):
    '''
    creditos: https://webkul.com/blog/python-soap-clients-with-zeep/
    '''
    wsdl = 'http://sicbr.com/wsinfoproduto/wsInfoProduto1.asmx?WSDL'
    client = Client(wsdl=wsdl)
    result = client.service.BuscaPorCodigo(ean, token).lower()
    if result == '0':
        return
    else:
        objectxml = objectify.fromstring(result)
    return objectxml
if __name__ == '__main__':
    query = '''
  SELECT
	t.codigo,
	t.produto ,
	t.fabricante ,
	t.codipi ,
	t.cest
from
	TABEST1 t
where
	t.codipi is null
	and t.codigo NOT LIKE  '200%'
	and t.fabricante !='SERVICOS'
	and t.codigo not like 'SR.%'
ORDER BY t.fabricante 
            '''
    cur = DBConnect()
    produtos = DBQuery(cur,query, [''])
    print('Total de registros retornado da consulta: ', len(produtos))
    for produto in produtos:
        print('Pesquisando Produto:')
        print('Codigo: ',produto['codigo'])
        print('Descricao: ',produto['produto'])
        ean = produto['codigo']
        consulta = find_ncm_sic(ean, token)
        pp.pprint(consulta)
        # time.sleep(5)