# 38274725-3a8f-4c2d-98c2-b3ea6ac5f35f
import asyncio
import threading
import time
import requests
import random
from ..database import actions
from ..structures import LabelIntent, LabelStructure, CustomerStructure


class Shipd:
    def __init__(
            self,
            labelintent: LabelIntent
    ):
        self.labelIntent = labelintent
        self.headers = {
            "Auth": "38274725-3a8f-4c2d-98c2-b3ea6ac5f35f"
        }

    def order(self):
        resulting_labels = {"orders": []}
        refund_amount = 0
        for label in self.labelIntent.labels:
            missing_keys = {
                "Length": label.Length,
                "Width": label.Width,
                "Height": label.Height,
                "Provider": "",
                "Description": label.description,
                "Reference1": label.reference1,
                "Reference2": label.reference2,
                "Signature": label.signature,
                "Saturday": label.saturday,
                "FromCompany": label.fromcompany,
                "FromZip": label.fromzip,
                "ToCompany": label.tocompany,
                "type": '54c0b387-b5d5-42c4-a55c-9d71ea8c13c0'
            }
            key_mapping = {
                "weight": "Weight",
                "from_name": "FromName",
                "from_phone": "FromPhone",
                "from_address1": "FromStreet",
                "from_address2": "FromStreet2",
                "from_city": "FromCity",
                "from_state": "FromState",
                "from_postcode": "FromZip",
                "from_country": "FromCountry",
                "to_name": "ToName",
                "to_phone": "ToPhone",
                "to_address1": "ToStreet",
                "to_address2": "ToStreet2",
                "to_city": "ToCity",
                "to_state": "ToState",
                "to_postcode": "ToZip",
                "to_country": "ToCountry"
            }
            pay = {
                "provider_code": "usps",
                "class": "usps_first_class",
                "weight": label.packageWeight,
                "from_name": label.fromname,
                "from_phone": label.fromphone,
                "from_address1": label.fromstreet,
                "from_address2": label.fromstreet2,
                "from_city": label.fromcity,
                "from_state": label.fromstate,
                "from_postcode": label.fromzip,
                "from_country": "US",
                "to_name": label.toname,
                "to_phone": label.toPhone,
                "to_address1": label.tostreet,
                "to_address2": label.tostreet2,
                "to_city": label.toCity,
                "to_state": label.toState,
                "to_postcode": label.toZip,
                "to_country": "US"
            }
            submit_label = requests.post('https://shipd.bz/api/v1/orders', headers=self.headers, json=pay)
            new_order_id = str(random.randint(100000, 900000))
            for k in missing_keys:
                pay[k] = missing_keys[k]
            for j in key_mapping:
                val = pay[j]
                del pay[j]
                pay[key_mapping[j]] = val
            del pay['provider_code']
            del pay['class']
            pay['LabelID'] = new_order_id
            if not submit_label.json()['success']:
                print('test remove this print')
                pay['Success'] = 'False'
                pay['TrackLink'] = ''
                refund_amount += actions.get_price_per()
            else:
                # fetch PDF from shipd
                pay['Success'] = 'True'
                id_to_search = submit_label.json()['order']['id']
                attempt = None
                for _ in range(5):
                    attempt = requests.get(f'https://shipd.bz/api/v1/orders/{id_to_search}')
                    print(attempt.json()['success'], 'another test print')
                    if attempt.json()['success']:
                        if attempt.json()['order']['downloadable']:
                            break
                    time.sleep(1)
                if not attempt:
                    pay['Success'] = 'False'
                    pay['TrackLink'] = ''
                else:
                    pay['TrackLink'] = attempt.json()['order']['tracking']
                    pdf_data = requests.get(f'https://shipd.bz/api/v1/orders/{attempt.json()["order"]["id"]}.pdf', headers=self.headers)
                    with open(rf"PDFs\{new_order_id}.pdf", "wb") as pdf_file:
                        pdf_file.write(bytes(pdf_data.content))
            resulting_labels['orders'].append(pay)
        if refund_amount:
            actions.set_user_bal(self.labelIntent.customer.customerEmail, actions.fetch_user_bal(self.labelIntent.customer.customerEmail) + refund_amount)
        actions.add_user_order(resulting_labels, str(random.randint(100000,900000)), self.labelIntent.customer.customerEmail)
