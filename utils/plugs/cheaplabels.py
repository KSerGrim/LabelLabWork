# 9b75349c-49a3-86d4-9568-906400cc56bd
import asyncio
import threading
import time
import requests
import random
from ..database import actions
from ..structures import LabelIntent, LabelStructure, CustomerStructure


class Cheaplabels:
    def __init__(
            self,
            labelintent: LabelIntent
    ):
        self.labelIntent = labelintent
        self.headers = {
            "X-Api-Auth": "9b75349c-49a3-86d4-9568-906400cc56bd"
        }

    def order(self):
        resulting_labels = {"orders": []}
        refund_amount = 0
        for label in self.labelIntent.labels:
            pay = {
                'type': '54c0b387-b5d5-42c4-a55c-9d71ea8c13c0',
                'Weight': (label.packageWeight),
                'Length	': (label.Length),
                'Width	': (label.Width),
                'Height	': (label.Height),
                'Provider': '',
                'Description': label.description,
                'Reference1': label.reference1,
                'Reference2': label.reference2,
                'Signature': label.signature,
                'Saturday': label.saturday,
                'FromCountry': 'US',
                'FromName': label.fromname,
                'FromCompany': label.fromcompany,
                'FromPhone': label.fromphone,
                'FromStreet': label.fromstreet,
                'FromStreet2': label.fromstreet2,
                'FromCity': label.fromcity,
                'FromState': label.fromstate,
                'FromZip': label.fromzip,
                'ToCountry': 'US',
                'ToName': label.toname,
                'ToCompany': label.tocompany,
                'ToPhone': label.toPhone,
                'ToStreet': label.tostreet,
                'ToStreet2': label.tostreet2,
                'ToCity': label.toCity,
                'ToState': label.toState,
                'ToZip': label.tozip
            }
            submit_label = requests.post('https://cheaplabels.io/api/order', headers=self.headers, json=pay).json()
            if submit_label['Success']:
                pay['Success'] = 'True'
                pay['TrackLink'] = submit_label['Data']['Order']['TrackLink']
                pay['LabelID'] = submit_label['Data']['Order']['ID']
                resulting_labels['orders'].append(pay)
                pdf_data = requests.get(f"https://cheaplabels.io/api/order/{submit_label['Data']['Order']['ID']}/file", headers=self.headers)
                with open(rf"PDFs\{submit_label['Data']['Order']['ID']}.pdf", "wb") as pdf_file:
                    pdf_file.write(bytes(pdf_data.content))
            else:
                pay['Success'] = 'False'
                pay['TrackLink'] = ''
                pay['LabelID'] = ''
                resulting_labels['orders'].append(pay)
                refund_amount += actions.get_price_per()

        if refund_amount:
            actions.set_user_bal(self.labelIntent.customer.customerEmail, actions.fetch_user_bal(self.labelIntent.customer.customerEmail) + refund_amount)
        actions.add_user_order(resulting_labels, str(random.randint(100000,900000)), self.labelIntent.customer.customerEmail)
