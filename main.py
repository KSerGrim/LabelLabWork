from utils import Core, Login
from utils.structures import LabelIntent, LabelStructure, CustomerStructure
import asyncio
import requests

#headers = {
#    'X-Api-Auth' : '9b75349c-49a3-86d4-9568-906400cc56bd'
#}
#res = requests.get('https://cheaplabels.io/api/order/3a9a47c9-52e3-6bf6-60c0-621358961c09/file', headers=headers)
#with open('testpdf.pdf', "wb") as pdf_file:
#    pdf_file.write(bytes(res.content))

# Would get this AFTER logging in with email and password
#pretend_customer = CustomerStructure('poohead@d.com', 'poo D head', 'poohead@d.com')
login_attempt = Login('poohead@d.com', 'fakepassword').request_login()
##print(login_attempt)
pretend_label = LabelStructure('test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test','test',False,False,'test')
pretend_intent = LabelIntent(login_attempt, [pretend_label])
core = Core(login_attempt)
##asyncio.run(core.buy_credits(1000))
asyncio.run(core.order_labels(pretend_intent))
#print(asyncio.run(core.check_credits()))
#print(asyncio.run(core.admin_get_price()))
#print(asyncio.run(core.get_orders()))
#print(asyncio.run(core.order_labels(pretend_intent)))
##print(asyncio.run(core.get_orders()))
#print(asyncio.run(core.check_credits()))
#print(asyncio.run(core.get_total_deposited()))

#
admin_login = Login('adminemail', 'adminpassword').request_login()
core2 = Core(admin_login)
#print(asyncio.run(core_customer.admin_get_price()))
#print(asyncio.run(core2.admin_get_price()))





