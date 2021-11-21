from typing import Union

import configcatclient

configcat_client = configcatclient.create_client(
    'FI3ZCHuHAkqAlIMJBnqJ2A/ObuUUsViJkiuX3mIDtCiHg')

var = configcat_client.get_value("g_meaeaain", None)
print(var)




"""
class STAFF_ID:

    ID_DICT = {
        # *** Guilds ***
        "g_staff": 891521033700540457,

        # *** Channels ***
        "ch_verificationLogs": 894241199433580614
    }

def get_value(classType, value: str, datatype: Union[str, int, bool]) -> Union[str, int, bool]:
    if configcat_client.get_value(value) is None:
        raise ValueError(f"Cannot find {value} within ConfigCat!")

    if value in classType.ID_DICT:
        return datatype(configcat_client.get_value(value, classType.STAFF_IDL[value]))
    else:
        return datatype(configcat_client.get_value(value, None))



var = STAFF_ID()
value = var.get_value("g_main", int)
print(value, type(value))

"""



