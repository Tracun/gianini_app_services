import datetime
import schedule
import json
import time
import requests
import sys
import urllib.parse
import configparser
from firebase import firebase

class Services:

    def __init__(self):
        self.firebaseApp = firebase.FirebaseApplication(
            'https://gianini-manutencao.firebaseio.com/', None)
        self.whatsappURL = "https://api.callmebot.com/whatsapp.php?"
        self.gianiniPhone = ""
        self.gianiniToken = ""
        self.devPhone = ""
        self.devToken = ""
        self.readConfig()

    def readConfig(self):
        parser = configparser.ConfigParser()
        parser.read_file(open(r'config.txt'))
        self.gianiniPhone = parser.get('config', 'gianiniPhone')
        self.gianiniToken = parser.get('config', 'gianiniToken')
        self.devPhone = parser.get('config', 'devPhone')
        self.devToken = parser.get('config', 'devToken')

    def getAllSchedules(self):
        try:
            schedules = self.firebaseApp.get('Schedules/', '')
            return schedules
        except Exception as e:
            self.sendErrorMessage("Erro getAllSchedules: " + str(e))
        return None

    def getAllExpenses(self):
        try:
            expenses = self.firebaseApp.get('Expenses/', '')
            return expenses
        except Exception as e:
            self.sendErrorMessage("Erro getAllExpenses: " + str(e))
        return None

    def diffBetweenDates(self, date):
        date = self.convertStr2Date(str(date))
        return (date - datetime.datetime.now()).days

    def checkPreventivaSchedule(self):

        scheduleList = self.getAllSchedules()

        for key, schedules in scheduleList.items():
            diff = self.diffBetweenDates(schedules["date"])
            if diff > 0 and diff < 2:
                print("ENVIANDO EMAIL/SMS ...")

    def checkExpensesCloseToDueDate(self, to):

        expensesList = self.getAllExpenses()
        count = 0
        message = "*##### As despesas abaixo que estão com o status de 'Pendente', vencidas e/ou próximas do vencimento - {0}/{1}/{2} #####*\n\n".format(
            datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)

        for key, expense in expensesList.items():
            diff = self.diffBetweenDates(expense["dueDate"])
            status = expense["status"]

            if status != "Pago":
                if diff < 0:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} - *_(❌VENCIDO)_* - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])
                elif diff == 0:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} -  *_(⚠️HOJE)_* - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])
                elif diff < 2:
                    dueDate = self.convertStr2Date(expense["dueDate"])
                    count += 1
                    message += "{0} - *{1}({2})* com o valor de *R$ {3}* e vencimento em *{4}/{5}/{6}* - *{7}*\n\n".format(
                        count, expense["description"], expense["obs"], expense["value"], dueDate.day, dueDate.month, dueDate.year, expense["type"])

        if count == 0:
            message += "Nenhum despesa pendente para o dia de hoje - {0}/{1}/{2}".format(
                datetime.datetime.now().day, datetime.datetime.now().month, datetime.datetime.now().year)
        message = urllib.parse.quote(message)

        if to == None or to == 'dev':
            return self.sendWhatsappMessage(message, self.devPhone, self.devToken)
        elif to == "all":
            self.sendWhatsappMessage(message, self.devPhone, self.devToken)
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        elif to == "gianini":
            return self.sendWhatsappMessage(message, self.gianiniPhone, self.gianiniToken)
        return None

    def convertStr2Date(self, strDate):
        date_time_obj = datetime.datetime.strptime(
            strDate, '%Y-%m-%d %H:%M:%S.%f')
        return date_time_obj

    def sendSMS(self):
        print("TO BE DEF")

    # Using CallMeBot, a free tool
    def sendWhatsappMessage(self, message, phone, apiKey):
        endpoint = self.whatsappURL + \
            "phone={0}&text={1}&apikey={2}".format(phone, message, apiKey)
        self.log(endpoint)

        res = requests.get(url=endpoint)

        if res.status_code != 200:
            self.sendErrorMessage("Erro ao enviar Whatsapp: " + res.text)

        self.log(res.text)
        return res

    def log(self, message):
        print("{0} - {1}".format(datetime.datetime.now(), message))

    def sendErrorMessage(self, message):
        self.sendWhatsappMessage(
            "{0} - {1}".format(datetime.datetime.now(), message), self.devPhone, self.devToken)

def main():
    ("Executando serviço ...")
    services = Services()
    try:
        services.log("Executando serviço ...")

        # services.checkPreventivaSchedule()
        res = services.checkExpensesCloseToDueDate(to="dev")

        services.log("Execução finalizada ...")

    except Exception as e:
        # services.sendErrorMessage("Erro main: " + str(e))
        services.log("Erro main: " + str(e))


if __name__ == "__main__":
    try:
        print("Serviço iniciado ...")
        # schedule.every(10).seconds.do(main)
        main()

        # while True:
        #     schedule.run_pending()
        #     time.sleep(1)
    except Exception as e:
        print("Erro ao executar serviço: " + str(e))
        sys.exit()

def lambda_handler(event, context):
    print("Executando serviço ...")
    try:
        services = Services()
        services.log("Executando serviço ...")

        res = services.checkExpensesCloseToDueDate(event['to'])

        services.log("Execução finalizada ...")

        return {
            "statusCode": res.status_code,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "Text ": 'Em breve receberá um whatsapp com as informações requeridas'
            })
        }
    except Exception as e:
        services.sendErrorMessage("Erro main: " + str(e))
        services.log("Erro main: " + str(e))