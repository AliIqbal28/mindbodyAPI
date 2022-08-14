def is_docType(dType):
    if dType == "invrec" or dType == "receipt":
        return True
    return False


def is_supportedItem(itemName):
    supportedItemsList = ['שיעור ניסיון', 'חודש הכרות', 'חופשי אונליין', 'שיעור', 'שיעור אונליין', 'חופשי חודשי',
                          'כרטיסיה 5', 'כרטיסיה 10', 'כרטיסיה 30', 'כרטיסיה 50', 'חופשי מתחדש', 'קורס מורים חופשי חודשי', 'תשלום יחסי חופשי מתחדש']
    if itemName in supportedItemsList:
        return True
    return False
