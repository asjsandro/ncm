import configparser
import pyodbc
from zeep import Client
import pprint as pp
import time
from xml.etree import ElementTree
import re

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

def add_root_to_xml(xml_string):
    return f"<root>{xml_string}</root>"

def normalize_xml_tags(xml_string):
    # Função que transforma a tag em letras minúsculas
    def lowercase_tag(match):
        return match.group(1) + match.group(2).lower() + ">"
    # Substitui as tags encontradas pela versão em letras minúsculas
    return re.sub(r"(<\/*)([^>]+)>", lowercase_tag, xml_string)

def consulta_produto(codigo_produto, token):
    # Definindo o endereço WSDL
    wsdl = "http://sicbr.com/wsinfoproduto/wsInfoProduto1.asmx?WSDL"
    client = Client(wsdl)

    # Fazendo a consulta à API SOAP
    response = client.service.BuscaPorCodigo(Codigo=codigo_produto, Token=token)  # Altere "NomeDoMetodo" pelo método correto.

    # Normalizando a string XML
    response = normalize_xml_tags(response)
    response = add_root_to_xml(response)

    # Analisando a string XML
    response = ElementTree.fromstring(response)
    # Convertendo o XML para um objeto Python
    if response.text =='0' :
        produto = {'root':'0'}
    else:
        produto = {
            "codigo": response.find("codigo").text,
            "produto": response.find("produto").text,
            "fabricante": response.find("fabricante").text,
            "unidade": response.find("unidade").text,
            "codipi": response.find("codipi").text,
            "pesobruto": response.find("pesobruto").text or None,
            "pesoliq": response.find("pesoliq").text or None,
            "aprovado": response.find("aprovado").text or None,
            "datainc": response.find("datainc").text
        }
    return produto

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
	and t.codigo NOT LIKE ?
	and t.fabricante != 'SERVICOS'
	and t.codigo not like ?
ORDER BY
	t.codigo
'''
    cur = DBConnect()
    produtos = DBQuery(cur,query, ['200%','SR.%'])
    print('Total de registros retornado da consulta: ', len(produtos))
    for produto in produtos:
        print(80*'=')
        print('Pesquisando Produto:')
        print('Codigo: ',produto['codigo'])
        print('Descricao: ',produto['produto'])
        ean = produto['codigo']
        consulta = consulta_produto(ean, token)
        pp.pprint(consulta)
        print('Final da pesquisa!')
        print(80*'=')
        print('\n')
        time.sleep(2)