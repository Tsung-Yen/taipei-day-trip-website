import hashlib
#Verify User
currentUser = {}  #storage current signin user
class Verify:
    def encryption(data):
        key = hashlib.sha256((data[1]).encode("utf-8")).hexdigest()
        currentUser[key] = {
            "id":data[0],
            "name":data[1],
            "email":data[2]
        }
        return key
    def verifyuser(data):
        if data in currentUser:
            return {
                "id":currentUser[data]["id"],
                "name":currentUser[data]["name"],
                "email":currentUser[data]["email"]
            }
        else:
            return False