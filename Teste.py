from openpyxl import load_workbook
import json

data = {}
data['key'] = 'value'

wb = load_workbook(filename='../PLANILHA DE PAGAMENTOS.xlsm')
count = 0
ws = wb['Maio - 21']
for cell in ws:
    descr = cell[0].value
    date = cell[1].value
    status = cell[2].value
    valor = cell[3].value
    obs = cell[4].value

    count += 1

    data["-manual{0}".format(count)] = {
        
            "categoryId": 12,
            "description": descr,
            "dueDate": date,
            "id": 2021519+count,
            "obs": obs,
            "status": status,
            "type": "Empresa",
            "value": valor
        }
    

    print(data)
