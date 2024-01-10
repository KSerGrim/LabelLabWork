from utils.structures import LabelIntent, LabelStructure, CustomerStructure
from utils.plugs import *
from utils.database import actions
import utils.plugs
import asyncio
import threading
from datetime import date
LabelPlug = globals()[actions.get_plug()]


class Core:
    def __init__(
            self,
            customer: CustomerStructure
    ):
        self.customer = customer

    async def order_labels(self, labels: LabelIntent):
        customers_balance = actions.fetch_user_bal(self.customer.customerEmail)
        number_of_labels = len(labels.labels)
        if number_of_labels * actions.get_price_per() >= customers_balance:
            return False
        actions.set_user_bal(self.customer.customerEmail, customers_balance-(number_of_labels * actions.get_price_per()))
        actions.add_sale_daily(len(labels.labels), str(date.today()))
        order_thread = threading.Thread(target=LabelPlug(labels).order)
        order_thread.start()
        return True

    async def check_credits(self):
        return actions.fetch_user_bal(self.customer.customerEmail)

    async def buy_credits(self, number_of_credits):
        customers_balance = actions.fetch_user_bal(self.customer.customerEmail)
        actions.add_to_user_overall(self.customer.customerEmail, number_of_credits)
        actions.set_user_bal(self.customer.customerEmail, customers_balance+number_of_credits)
        return True

    async def get_orders(self, specified_order=None):
        result = actions.fetch_user_orders(self.customer.customerEmail, orderid=specified_order)
        return result

    async def get_total_deposited(self):
        total = actions.fetch_user_overall(self.customer.customerEmail)
        return total if total else 0

    async def admin_get_price(self):
        if self.customer.customerEmail != 'adminemail':
            return
        current_price = actions.get_price_per()
        return current_price

    async def admin_set_price(self, price):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.set_price_per(price)

    async def admin_get_sales(self):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.get_all_sales()

    async def admin_get_plugs(self):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.get_all_plugs()

    async def admin_add_plug(self, plug):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.add_new_plug(plug)

    async def admin_get_current_plug(self):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.get_plug()

    async def admin_set_current_plug(self, plug):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.set_plug_type(plug)

    async def admin_fetch_all(self):
        if self.customer.customerEmail != 'adminemail':
            return
        return actions.fetch_all()

    async def admin_set_user_credits(self, user, bal):
        if self.customer.customerEmail != 'adminemail':
            return
        result = actions.set_user_bal(user, bal)
        return result

    async def admin_give_user_credits(self, user, amount):
        if self.customer.customerEmail != 'adminemail':
            return
        customers_balance = actions.fetch_user_bal(user)
        actions.add_to_user_overall(user, amount)
        actions.set_user_bal(user, customers_balance + amount)
        return True
