from flask_restful import Api
from flask import Flask, render_template
from services import Services

app = Flask(__name__)
api = Api(app) 

@app.route('/verifDespesasProxVenc')
@app.route('/verifDespesasProxVenc/<string:to>')
def checkeExpenses(to=None):
    service = Services()

    res = service.checkExpensesCloseToDueDate(to)
    
    if res != None and res.status_code == 200:
        return {'message': 'Em breve receberá um whatsapp com as informações requeridas', 'response': {}, 'status code':'{0}'.format(res.status_code)}
    elif res == None:
        return {'message': 'Endpoint inválido, era esperado um dos abaixos: /all ou /dev ou /gianini', 'response': {}, 'status code':'{0}'.format('400')}

@app.route('/verifPreventivasProxVenc')
@app.route('/verifPreventivasProxVenc/<string:to>')
def checkePreventivasSchedule(to=None):
    service = Services()

    res = service.checkPreventivaScheduleCloseToDueDate(to)
    
    if res != None and res.status_code == 200:
        return {'message': 'Em breve receberá um whatsapp com as informações requeridas', 'response': {}, 'status code':'{0}'.format(res.status_code)}
    elif res == None:
        return {'message': 'Endpoint inválido, era esperado um dos abaixos: /all ou /dev ou /gianini', 'response': {}, 'status code':'{0}'.format('400')}


@app.route('/')
@app.route('/home')
def index():
    return render_template(
        'index.html',
        title='Home Page'
    )

if __name__ == '__main__':
    #app.run(debug=True)
    app.run()