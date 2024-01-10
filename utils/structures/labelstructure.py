class LabelStructure:
    def __init__(
            self,
            fromname: str,
            fromcompany: str,
            fromstreet: str,
            fromstreet2: str,
            fromzip: str,
            fromcity: str,
            fromstate: str,
            fromphone: str,
            toname: str,
            tocompany: str,
            tostreet: str,
            tostreet2: str,
            tozip: str,
            tocity: str,
            tostate: str,
            tophone: str,
            packageweight: str,
            length: str,
            width: str,
            height: str,
            description: str,
            reference1: str,
            reference2: str,
            signature: str,
            saturday: str,
            price: str

    ):
        self.fromname = fromname
        self.fromcompany = fromcompany
        self.fromstreet = fromstreet
        self.fromstreet2 = fromstreet2
        self.fromzip = fromzip
        self.fromcity = fromcity
        self.fromstate = fromstate
        self.fromphone = fromphone
        self.toname = toname
        self.tocompany = tocompany
        self.tostreet = tostreet
        self.tostreet2 = tostreet2
        self.tozip = tozip
        self.toCity = tocity
        self.toState = tostate
        self.toPhone = tophone
        self.packageWeight = packageweight
        self.Length = length
        self.Width = width
        self.Height = height
        self.description = description
        self.reference1 = reference1
        self.reference2 = reference2
        self.signature = signature
        self.saturday = saturday
        self.price = price
