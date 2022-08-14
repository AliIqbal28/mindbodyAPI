import http.client
import json
from webhooks.errorMail import sendMail
from webhooks.conf import API_KEY, SITE_ID, TEST, MINDBODY_USERNAME, MINDBODY_PASSWORD

conn = http.client.HTTPSConnection("api.mindbodyonline.com")


def getClient(client, AUTHORIZATION):
    headers = {
        'Api-Key': API_KEY,
        'SiteId': SITE_ID,
        'Authorization': AUTHORIZATION
    }
    conn.request("GET", f"/public/v6/client/clients?SearchText={client.email}&IncludeInactive=true",headers=headers)  # for both active and inactive clients

    res = conn.getresponse()
    data = res.read()
    clientData = json.loads(data.decode("utf-8"))

    if clientData["PaginationResponse"]["TotalResults"] != 0:
        return clientData["Clients"][0]["UniqueId"]

    errorMessage = "Something went wrong while fetching the existing client UniqueID.\n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
    print(errorMessage)
    sendMail(errorMessage)
    return False


def addClient(client, AUTHORIZATION):
    payload = {"FirstName": client.firstName,
               "LastName": client.lastName,
               "Email": client.email,
               "Test": TEST,
               "AddressLine1": "street",
               "City": "TLV",
               "MobilePhone": client.mobile,
               }

    headers = {
        'Content-Type': "application/json",
        'Api-Key': API_KEY,
        'SiteId': SITE_ID
    }

    conn.request("POST", "/public/v6/client/addclient", str(payload).encode('utf-8'), headers)

    res = conn.getresponse()
    data = res.read()

    responseData = json.loads(data.decode("utf-8"))

    if "Error" not in responseData:  # if its not a duplicate client, send a password reset email
          return responseData["Client"]["UniqueId"]

    errorMessage = "something went wrong while creating a new client. \n Error message: " + responseData["Error"]["Message"] + ". \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
    print(errorMessage)
    sendMail(errorMessage)
    return False


def updateShoppingCart(minbodyClientId, quantity, serviceID, servicePrice, iCountClient, AUTHORIZATION):
    payload = {"ClientId": minbodyClientId,
               "Test": TEST,
               "Items": [
                   {
                       "Item": {
                           "Type": "Service",
                           "Metadata": {"Id": serviceID}
                       },
                       "Quantity": quantity
                   }
               ],
               "InStore": "true",
               "Payments": [
                   {
                       "Type": "Cash",
                       "Metadata": {"Amount": servicePrice}
                   }
               ]
               }

    headers = {
        'Content-Type': "application/json",
        'Api-Key': API_KEY,
        'SiteId': SITE_ID,
        'Authorization': AUTHORIZATION
    }
    conn.request("POST", "/public/v6/sale/checkoutshoppingcart", str(payload).encode('utf-8'), headers)
    res = conn.getresponse()
    data = res.read()
    responseData = json.loads(data.decode("utf-8"))

    if "Error" in responseData:
        errorMessage = "something went wrong during checkout operation \n Error message: " + responseData["Error"]["Message"] + ". \n Client iCount details: \n client firstName: " + iCountClient.firstName + " \n client lastName: " + iCountClient.lastName + " \n client email: " + iCountClient.email
        print(errorMessage)
        sendMail(errorMessage)
        return False

    return True

def getService(client, AUTHORIZATION):
    headers = {
        'Api-Key': API_KEY,
        'SiteId': SITE_ID,
        'authorization': AUTHORIZATION
    }

    conn.request("GET", "/public/v6/sale/services", headers=headers)

    res = conn.getresponse()
    data = res.read()

    allServices = json.loads(data)

    if "Error" in allServices:
        errorMessage = "something went wrong while fetching the required service \n Error message: " + allServices["Error"]["Message"] + ". \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
        print(errorMessage)
        sendMail(errorMessage)
        return False

    if allServices["PaginationResponse"]["TotalResults"] == 0:
        errorMessage = "something went wrong while fetching the required service.\n Error: no Services exist to search from. \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
        print(errorMessage)
        sendMail(errorMessage)
        return False

    for index in allServices["Services"]:
        if index["Name"] == client.description:
            return index["ProductId"], index["Price"]

    errorMessage = "something went wrong while fetching the required service.\n Service Name: " + client.description + " \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
    print(errorMessage)
    sendMail(errorMessage)
    return False
def CustomPaymentMethods(methodName):
    import http.client
    conn = http.client.HTTPSConnection("api.mindbodyonline.com")

    headers = {
        'Api-Key': API_KEY,
        'SiteId': SITE_ID
    }

    conn.request("GET", "/public/v6/sale/custompaymentmethods", headers=headers)

    res = conn.getresponse()
    data = res.read()
    responseData = json.loads(data.decode("utf-8"))

    if "Error" in responseData:
        errorMessage = "something went wrong while getting the custom payment method. \n Error message: " + responseData["Error"]["Message"]
        sendMail(errorMessage)
        return False


    for index in responseData["PaymentMethods"]:
        if index["Name"] == methodName:
            return index["Id"]


    return False


def PurchaseAccountCredit(client, AUTHORIZATION):

    mindbodyClientId = getClient(client, AUTHORIZATION)  # get existing client id
    if mindbodyClientId == False:
        errorMessage = "something went wrong while fetching the existing client for PurchaseAccountCredit. \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
        print(errorMessage)
        sendMail(errorMessage)
        return False

    customPaymentId = CustomPaymentMethods("Api payment")
    if not customPaymentId:
        return False

    payload = {
        "Test": TEST,
        "LocationId": 1,
        "ClientId": mindbodyClientId,
        "PaymentInfo": {
            "Type": "Custom",
            "Metadata": {"Amount": client.totalwithvat,
                "Id": customPaymentId}
  }
}
    headers = {
        'Content-Type': 'application/json',
        'API-Key': API_KEY,
        'SiteId': SITE_ID,
        'Authorization': AUTHORIZATION
    }
    conn.request("POST", "/public/v6/sale/purchaseaccountcredit", str(payload).encode('utf-8'), headers)
    res = conn.getresponse()
    data = res.read()
    responseData = json.loads(data.decode("utf-8"))

    print(responseData)

    if "Error" in responseData:
        errorMessage = "something went wrong during purchase account credit. \n Error message: " + responseData["Error"]["Message"] + ". \n Client iCount details: \n client firstName: " + client.firstName + " \n client lastName: " + client.lastName + " \n client email: " + client.email
        print(errorMessage)
        sendMail(errorMessage)
        return False
    return True

def getUserToken():
    payload = {
                "Username": MINDBODY_USERNAME,
                "Password": MINDBODY_PASSWORD
            }
    headers = {
        'Content-Type': "application/json",
        'Api-Key': API_KEY,
        'SiteId': SITE_ID
    }

    conn.request("POST", "/public/v6/usertoken/issue", str(payload).encode('utf-8'), headers)

    res = conn.getresponse()
    data = res.read()

    responseData = json.loads(data.decode("utf-8"))

    if "Error" in responseData:
        errorMessage = "something went wrong while getting the user token. \n Error message: " + responseData["Error"]["Message"]
        print(errorMessage)
        sendMail(errorMessage)
        return False

    AUTHORIZATION = responseData["AccessToken"]
    return AUTHORIZATION