from utils.structures import CustomerStructure, LabelStructure


class LabelIntent:
    def __init__(
            self,
            customer: CustomerStructure,
            labels: list[LabelStructure]
    ):
        self.customer = customer
        self.labels = labels
