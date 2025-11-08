import base64
import random
import time
import socket
import hashlib

# funs
def chebyshev_polynomial(n, x, p=14797):
    if n == 0:
        return 1 
    elif n == 1:
        return x  
    else:
        T_0 = 1
        T_1 = x 
        
        for i in range(2, n + 1):
            T_n = (2 * x * T_1 - T_0) % p  
            T_0 = T_1  
            T_1 = T_n  
        
        return T_1 


def rand_num():
	return random.randint(1_000_000, 9_000_000)

def sha256(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()

def xor_bytes(list_of_bytes):
    max_len = max(len(b) for b in list_of_bytes)

    result = bytearray(max_len)
    for i in range(len(result)):
        result[i] = list_of_bytes[0][i] if i < len(list_of_bytes[0]) else 0

    for b in list_of_bytes[1:]:
        for i in range(len(b)):
            result[i] ^= b[i]

    return bytes(result)

def from_b64(b64_str):
        return base64.b64decode(b64_str.encode('utf-8'))

def to_b64(bytes):
	return base64.b64encode(bytes).decode("ascii")


m3 = "AgQHD1AAAFYDAgcFVFJTDAAAB1ECVVIHAlNVClMACAVVBVBWBVQJAg8HA1QDU1MDAlJXVwQJAgFbXAxVAQpSWg==,1762060221,1762081821,bda7381ccff43d7e4d6a17d4cffb9a1374ca474457b5533b96ea0e2062c564d1,06116e3ebd4a8c26fe2ea955797c3338805f9aad042791317cc1f042089292da,Cg0HD1ZmZGMyZjU2NmJiNDEyZDdhN2Y0MmY0OTJiMWY0MmM1MmE4MDZkYWU0ZGVhM2YxYTE4ZmJiODk0ODllYw=="
print(f"[+] The adversary has eavesdropped on the channel between nodes and now has access to M3. M3={{Auth_AP_G_date, t1, t2, AT_a, AT_b, TID_G}} = {{{m3}}}")



K_ap_msc = 7529
print(f"[+] Additionally, the adversary has access to K_AP_MSC through a colluding AP node. K_AP_MSC: {K_ap_msc}")


m3 = m3.split(",")
Auth_ap_g_date = from_b64(m3[0])
t1 = int(m3[1])
t2 = int(m3[2])
AT_a = m3[3]
AT_b = m3[4] 
TID_g = from_b64(m3[5])


date = 1762071 # int(time.time()/1000) # related date to captured message
h_date_K_ap_msc = sha256(f"{date}{K_ap_msc}").encode('utf-8')
h_ID_i_K_de_MSC = xor_bytes([Auth_ap_g_date, h_date_K_ap_msc])

ID_g = xor_bytes([TID_g, h_ID_i_K_de_MSC]).decode()

print(f"[+] Consequently, the adversary can compute the following: \n\t h( date || K_AP_MSC): {h_date_K_ap_msc.decode()}\n\th( ID_i || K_DE_MSC): {h_ID_i_K_de_MSC.decode()}\n\tID_G: {ID_g}")