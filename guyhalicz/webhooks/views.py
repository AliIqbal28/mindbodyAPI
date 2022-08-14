import json


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from webhooks.flags import is_docType, is_supportedItem
from webhooks.icount import getClientInfo
from webhooks.mindbodyAPI import getClient, updateShoppingCart, getService, addClient, getUserToken, PurchaseAccountCredit

@csrf_exempt
@require_POST
def webhook(request):
    data = json.loads(request.body)
    if not is_docType(data["doctype"]):         # check if document type is supported
        return HttpResponse("incorrect doctype")
    if not is_supportedItem(data["items"][0]["description"]):       # check if Item name/description is supported
        return HttpResponse("item not supported")

    client = getClientInfo(data)    # client object, having necessary fields that are to be used

    if not mindbody(client):
        return HttpResponse("task failed!!!")
    return HttpResponse("completed successfully!!!")


def mindbody(client):

    AUTHORIZATION = getUserToken() #user token
    if not AUTHORIZATION:
        print("unable to get UserToken")
        return False
    if client.description in ['חופשי מתחדש', 'קורס מורים חופשי חודשי', 'תשלום יחסי חופשי מתחדש']:
        if not PurchaseAccountCredit(client, AUTHORIZATION):
            return False
        return True
    if not getService(client, AUTHORIZATION):   # check if the service is available in mindbody
        print("service not available")
        return False
    serviceId, servicePrice = getService(client, AUTHORIZATION)

    mindbodyClientId = getClient(client, AUTHORIZATION)            # get existing client id
    if mindbodyClientId == False:
        mindbodyClientId = addClient(client, AUTHORIZATION)       # if a client does not exists, create a new one and get its ID
        if mindbodyClientId == False:
            print("unable to get an existing client or create a new client")    # some issue preventing to get an existing client, or create a new one!
            return False

    checkout = updateShoppingCart(mindbodyClientId, client.quantity, serviceId, servicePrice, client, AUTHORIZATION)
    if not checkout:
        return False
    return True




