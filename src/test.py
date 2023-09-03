import pyodbc
import requests
import configparser
import xml.etree.ElementTree as ET
import pprint as pp

# Configurações de conexão com o SQL Server
config = configparser.ConfigParser()
config.read('./src/config.ini')
server =  config['PRODUCAO']['host']
database = config['PRODUCAO']['database'] 
username = config['PRODUCAO']['user'] 
password = config['PRODUCAO']['password']
driver = config['PRODUCAO']['driver']
token = config['PRODUCAO']['token_sic']
cnxn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_element_text(root, path):
    """Retorna o texto de um elemento XML ou None se o elemento não for encontrado."""
    element = root.find(path)
    return element.text if element is not None else None

# Endpoint da API SOAP
api_url = 'http://sicbr.com/wsinfoproduto/wsInfoProduto1.asmx'
headers = {
    'content-type': 'text/xml'
}

def get_product_data(codigo):
    """Consulta a API SOAP para obter os dados do produto pelo código"""
    body = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
   <soapenv:Header/>
   <soapenv:Body>
      <tem:BuscaPorCodigo>
         <!--Optional:-->
         <tem:Codigo>{codigo}</tem:Codigo>
         <!--Optional:-->
         <tem:Token>{token}</tem:Token>
      </tem:BuscaPorCodigo>
   </soapenv:Body>
</soapenv:Envelope>
    """
    
    response = requests.post(api_url, data=body, headers=headers)
    # pp.pprint(response.text)
    root = ET.fromstring(response.content)
    # pp.pprint(root.text)
    # Adapte a extração dos dados conforme o XML retornado
    print(get_element_text(root, './/CodIPI'))
    print(get_element_text(root, './/PesoLiq'))
    print(get_element_text(root, './/PesoBruto'))
    print(get_element_text(root, './/Fabricante'))
    product_data = {
        'CodIPI': get_element_text(root, './/CodIPI'),
        'PesoLiq': get_element_text(root, './/PesoLiq'),
        'PesoBruto': get_element_text(root,'..//PesoBruto'),
        'Fabricante': get_element_text(root, './/Fabricante'),
        'codigo': codigo
    }
    
    return product_data

def get_products_with_empty_codipi():
    """Obtém a lista de códigos de produtos com CODIPI vazio ou nulo"""
    with pyodbc.connect(cnxn_str) as cnxn:
        cursor = cnxn.cursor()
        cursor.execute("SELECT top 30 codigo FROM tabest1 t WHERE t.codipi IS NULL or t.codipi = ''")
        return [row.codigo for row in cursor.fetchall()]

def update_product_in_database(product_data):
    """Atualiza os dados do produto no SQL Server"""
    with pyodbc.connect(cnxn_str) as cnxn:
        cursor = cnxn.cursor()
        
        update_sql = """
        UPDATE TABEST1 SET
            CODIPI = ?
        WHERE codigo = ?
        """
        
        cursor.execute(update_sql,
                       product_data['CodIPI'],
                       product_data['codigo'])
        cnxn.commit()

def main():
    product_codes = get_products_with_empty_codipi()
    for codigo in product_codes:
        product_data = get_product_data(codigo)
        if 'root' in product_data and product_data['root'] == '0':
            print(f"Produto com código {codigo} não encontrado na API.")
        else:
            # update_product_in_database(product_data)
            print(f"Produto com código {codigo} atualizado com NCM: {product_data['CodIPI']} sucesso!")

if __name__ == "__main__":
    main()
