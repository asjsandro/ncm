from zeep import Client
from pprint import pprint

wsdl = 'http://sicbr.com/wsinfoproduto/wsInfoProduto1.asmx?WSDL'
client = Client(wsdl)


def parseElements(elements):
    all_elements = {}
    for name, element in elements:
        all_elements[name] = {}
        all_elements[name]['optional'] = element.is_optional
        if hasattr(element.type, 'elements'):
            all_elements[name]['type'] = parseElements(
                element.type.elements)
        else:
            all_elements[name]['type'] = str(element.type)

    return all_elements


interface = {}
for service in client.wsdl.services.values():
    interface[service.name] = {}
    for port in service.ports.values():
        interface[service.name][port.name] = {}
        operations = {}
        for operation in port.binding._operations.values():
            operations[operation.name] = {}
            operations[operation.name]['input'] = {}
            elements = operation.input.body.type.elements
            operations[operation.name]['input'] = parseElements(elements)
        interface[service.name][port.name]['operations'] = operations


pprint(interface)