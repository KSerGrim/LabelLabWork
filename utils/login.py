from utils.database import actions
from utils.structures import LabelIntent, LabelStructure, CustomerStructure


class Login:
    def __init__(
            self,
            email: str,
            password: str
    ):
        self.email = email
        self.password = password

    def request_login(self):
        user_account = actions.fetch_user(self.email)
        if not user_account:
            return False
        if user_account[0][3] == self.password:
            return CustomerStructure(user_account[0][2], user_account[0][1], user_account[0][0])
        return False
