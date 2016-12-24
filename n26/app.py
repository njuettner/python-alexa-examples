import logging
import requests
from flask import Flask, render_template
from flask_ask import Ask, statement

app = Flask(__name__)
ask = Ask(app, '/')

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

url = 'https://api.tech26.de'

def get_token():
    values_token = {'grant_type' : 'password',
	      'username' : '',
	      'password' : ''}
    headers_token = { 'Authorization' : 'Basic ' }

    response_token  = requests.post(url + '/oauth/token' , data=values_token, headers=headers_token)
    token_info = response_token.json()
    # TODO check if access_token is not nil
    return token_info['access_token']

@ask.intent('BankAccountIntent')
def get_balance():

    access_token = get_token()

    headers_balance= { 'Authorization' : 'bearer' + access_token }

    req_balance = requests.get(url + '/api/accounts' , headers=headers_balance)

    balance = req_balance.json()
    availableBalance  = balance['availableBalance']
    if availableBalance >= 0:
        speech_text = "Du hast momentan ein Guthaben von {} Euro".format(availableBalance)
        return statement(speech_text).simple_card('AccountBalance', speech_text)
    else:
        speech_text = "Du liegst aktuell im Dispo mit {} Euro".format(abs(availableBalance))
        return statement(speech_text).simple_card('AccountBalance', speech_text)


@ask.intent('TransactionsIntent')
def get_transactions(TRANSACTION_NUMBER):

    access_token = get_token()

    headers_balance= { 'Authorization' : 'bearer' + access_token }
    params = {
        "limit": TRANSACTION_NUMBER,
        "pending": "false",
    }
    res_transactions = requests.get(url + '/api/smrt/transactions' , headers=headers_balance, params=params)
    transactions = res_transactions.json()

    amounts = []
    for transaction in transactions:
        if transaction.get('partnerName'):
            amounts.append("{} mit {} {}".format(transaction['partnerName'], abs(transaction['amount']),transaction['currencyCode']))
        else:
            amounts.append("{} mit {} {}".format(transaction['merchantName'], abs(transaction['amount']),transaction['currencyCode']))

    speech_text = "Deine letzten Transaktionen waren von {}".format(", ".join(amounts))
    return statement(speech_text).simple_card('Transactions', speech_text)

@ask.intent('LastTransactionIntent')
def get_last_transaction():

    access_token = get_token()

    headers_balance= { 'Authorization' : 'bearer' + access_token }
    params = {
        "limit": 1,
        "pending": "false",
    }

    res_transaction = requests.get(url + '/api/smrt/transactions' , headers=headers_balance, params=params)
    transaction = res_transaction.json()
    if transaction[0].get('partnerName'):
        name = transaction[0]['partnerName']
    else:
        name = transaction[0]['merchantName']
    amount = transaction[0]['amount']
    currency_code = transaction[0]['currencyCode']
    speech_text = "Deine letzte Transaktion war von {} und es wurden {} {} abgebucht".format(name, abs(amount), currency_code)
    return statement(speech_text).simple_card('Transaction', speech_text)


if __name__ == '__main__':
    app.run(debug=True)
