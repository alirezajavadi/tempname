import time
import random
import socket
import hashlib
import base64

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
	return random.randint(1_000_0, 9_000_0)

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


# initial values
x = 45567

K_ap = 2359


p=14797

# stored values
Auth_ap_g_date = "BAUBBQNRAwQOVVUCDAVWDQNfAloHUgEHVlEJCgNWUAVUAFtRUwsOVFAEVVtaAQsAA1ZbU1IIUVVSAAxRXgMDVQ=="
ID_g = 98765
h_date_kApMsc = "e495fd26834597f81f3867352f8245d629cf79953a1c823845bae0f339558057"
AT_a = 8732
AT_b = 8736


# establishing the connection
HOST = "localhost"
PORT = 8911
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))



# receiving m1
m1 = sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ] M1={{Auth_AP_G_date, TID_j, PK_DE, V_DE}} has been received: {{{m1}}}\033[0m")
m1 = m1.split(",")
Auth_ap_g_date_rec = m1[0]
TID_j = int(m1[1])
PK_de = int(m1[2])
V_de = m1[3]


# generating m2
if Auth_ap_g_date != Auth_ap_g_date_rec:
     print("[!] Auth_AP_G_dates are not the same!")
     exit()

K_de_ap = chebyshev_polynomial(K_ap, PK_de) % p

if V_de != sha256(f"{ID_g}{K_de_ap}"):
     print("[!] V_DEs are not the same!")
     exit()

ID_j = TID_j ^ K_de_ap

b = rand_num()

PK_ap = chebyshev_polynomial(b,x) % p


h_idi_kDeMsc = to_b64(xor_bytes([h_date_kApMsc.encode("utf-8"), from_b64(Auth_ap_g_date)]))
V_3 = sha256(f"{h_idi_kDeMsc}{h_date_kApMsc}{ID_g}{PK_ap}")

t1 = int(time.time()) - (60 * 60 * 3) # from 3 hours ago
t2 = t1 + (60 * 60 * 6) # 3 hours from now

m2 = f"{Auth_ap_g_date},{t1},{t2},{V_3},{PK_ap}"
print(f"\033[96m[+] Sending M2={{Auth_AP_G_date, t1, t2, V_3, PK_AP}} : {{{m2}}}\033[0m")
sock.send(m2.encode('utf-8'))


# receiving m3
m3 = sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ]  M3={{V_4}} has been received: {{{m3}}}\033[0m")
V_4 = m3

print(f"{h_date_kApMsc},{chebyshev_polynomial(b,PK_de)},{PK_de},{PK_ap}")
SK_de_ap = sha256(f"{h_date_kApMsc}{chebyshev_polynomial(b,PK_de)}{PK_de}{PK_ap}")


_temp1 = sha256(f"{AT_a}")
_temp2 = sha256(f"{AT_b}")

if V_4 == sha256(f"{SK_de_ap}{_temp1}{_temp2}"):
    print("[+] DE has been authenticated successfully.")
else:
    print("[-] V4s are not the same!")
    exit()


print(f"[+] SK_AP-DE: {SK_de_ap}")
