import requests
import time

"""
    Customer creates account 
    logs in
    buys credits (admin account gives credits in test)
    checks balance
    orders a label
    gets label data
    checks balance 
    orders label    
    gets label data
"""
info = {
    "email": "test1email@.com",
    "name": "John Pork",
    "password": "test1password"
}
create_acc = requests.post('http://localhost:8000/create_account', json=info)
print("Account creation")
print(create_acc.json())

login_info = {
    "email": "test1email@.com",
    "password": "test1password"
}
login_result = requests.post('http://localhost:8000/login', json=login_info)
headers = {
    'Authorization': f'Bearer {login_result.json()["access_token"]}'
}

# Admin will grant credits to sim buy
admin_login = requests.post('http://localhost:8000/login', json={'email': 'adminemail', 'password': 'adminpassword'})
print("Login with creds")
print(admin_login.json())
admin_headers = {
    'Authorization': f'Bearer {admin_login.json()["access_token"]}'
}

give_info = {
    "amount": 3000,
    "user": "test1email@.com"
}

give_test = requests.post('http://localhost:8000/give_credits', headers=admin_headers, json=give_info)
print("Buying credits")
print(give_test.json())

get_balance = requests.get('http://localhost:8000/get_balance', headers=headers)
print("Checking balance")
print(get_balance.json())

get_orders = requests.get('http://localhost:8000/get_orders', headers=headers)
print("Checking my orders")
print(get_orders.json())

label_info = [
    {
        "fromname": "test",
        "fromcompany": "test",
        "fromstreet": "test",
        "fromstreet2": "test",
        "fromzip": "test",
        "fromcity": "test",
        "fromstate": "test",
        "fromphone": "test",
        "toname": "test",
        "tocompany": "test",
        "tostreet": "test",
        "tostreet2": "test",
        "tozip": "test",
        "tocity": "test",
        "tostate": "test",
        "tophone": "test",
        "packageweight": "test",
        "length": "test",
        "width": "test",
        "height": "test",
        "description": "test",
        "reference1": "test",
        "reference2": "test",
        "signature": "test",
        "saturday": 'False',
        "price": "test"
    },
    {
        "fromname": "test",
        "fromcompany": "test",
        "fromstreet": "test",
        "fromstreet2": "test",
        "fromzip": "test",
        "fromcity": "test",
        "fromstate": "test",
        "fromphone": "test",
        "toname": "test",
        "tocompany": "test",
        "tostreet": "test",
        "tostreet2": "test",
        "tozip": "test",
        "tocity": "test",
        "tostate": "test",
        "tophone": "test",
        "packageweight": "test",
        "length": "test",
        "width": "test",
        "height": "test",
        "description": "test",
        "reference1": "test",
        "reference2": "test",
        "signature": "test",
        "saturday": 'False',
        "price": "test"
    },
    {
        "fromname": "test",
        "fromcompany": "test",
        "fromstreet": "test",
        "fromstreet2": "test",
        "fromzip": "test",
        "fromcity": "test",
        "fromstate": "test",
        "fromphone": "test",
        "toname": "test",
        "tocompany": "test",
        "tostreet": "test",
        "tostreet2": "test",
        "tozip": "test",
        "tocity": "test",
        "tostate": "test",
        "tophone": "test",
        "packageweight": "test",
        "length": "test",
        "width": "test",
        "height": "test",
        "description": "test",
        "reference1": "test",
        "reference2": "test",
        "signature": "test",
        "saturday": "false",
        "price": "test"
    }
]

order_labels = requests.post('http://localhost:8000/order_labels', headers=headers, json=label_info)
print("Placing order")
print(order_labels.json())
time.sleep(5)

get_orders = requests.get('http://localhost:8000/get_orders', headers=headers)
print("Checking my orders")
print(get_orders.json())

get_balance = requests.get('http://localhost:8000/get_balance', headers=headers)
print("Checking balance")
print(get_balance.json())

order_labels = requests.post('http://localhost:8000/order_labels', headers=headers, json=label_info)
print("Placing order")
print(order_labels.json())
time.sleep(5)

get_orders = requests.get('http://localhost:8000/get_orders', headers=headers)
print("Checking my orders again")
print(get_orders.json())
