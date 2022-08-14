import requests
from webhooks.conf import ICOUNT_COMPANY_ID, ICOUNT_USERNAME, ICOUNT_PASSWORD

class Client:
    def __init__(self, clientId, firstName, lastName, email, mobile, description, quantity, totalwithvat):
        self.clientId = clientId
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.mobile = mobile
        self.description = description
        self.quantity = quantity
        self.totalwithvat = totalwithvat


def getClientInfo(docData):

    URL = "https://api.icount.co.il/api/v3.php/client/info"

    PARAMS = {'cid': ICOUNT_COMPANY_ID,
              'user': ICOUNT_USERNAME,
              'pass': ICOUNT_PASSWORD,
              'client_id': docData["client_id"]}

    r = requests.get(url=URL, params=PARAMS)
    clientInfoData = r.json()


    if clientInfoData["client_info"]["mobile"] == '':     # add dummy numbers to mobile field in case it is empty
        clientInfoData["client_info"]["mobile"] = "12345678"

    if docData["items"][0]["quantity"] == '' or docData["items"][0]["quantity"] == '0':  # if the quantity is 0, make it 1
        docData["items"][0]["quantity"] = "1"


    client = Client(docData["client_id"],  # client object, having necessary fields that are to be used
                    clientInfoData["client_info"]["fname"],
                    clientInfoData["client_info"]["lname"],
                    docData["client"]["email"],
                    clientInfoData["client_info"]["mobile"],
                    docData["items"][0]["description"],
                    docData["items"][0]["quantity"],
                    docData["totalwithvat"])

    return client
