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


# establishing the connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = 'localhost'
port = 8911

try:
    sock.bind((host, port))
except socket.error as e:
    print(str(e))
    exit(0)

sock.listen()
ap_sock , ap_address = sock.accept()


# initial values 
x = 45567

p=14797

PK_ap = 14363

ID_j = 77889

# stored values
Auth_ap_g_date = "BAUBBQNRAwQOVVUCDAVWDQNfAloHUgEHVlEJCgNWUAVUAFtRUwsOVFAEVVtaAQsAA1ZbU1IIUVVSAAxRXgMDVQ=="
ID_g = 98765
h_date_kApMsc = "e495fd26834597f81f3867352f8245d629cf79953a1c823845bae0f339558057"
AT_a = 8732
AT_b = 8736


# generating M1
a = rand_num()

PK_de = chebyshev_polynomial(a,x) % p

K_de_ap = chebyshev_polynomial(a,PK_ap) % p

TID_j = ID_j ^ K_de_ap

V_de = sha256(f"{ID_g}{K_de_ap}")


m1 = f"{Auth_ap_g_date},{TID_j},{PK_de},{V_de}"
print(f"\033[96m[+] Sending M1={{Auth_AP_G_date, TID_j, PK_DE, V_DE}} : {{{m1}}}\033[0m")
ap_sock.send(m1.encode('utf-8'))


# receiving m2
m2 = ap_sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ]  M2={{Auth_AP_G_date, t1, t2, V_3, PK_AP}} has been received: {{{m2}}}\033[0m")
m2 = m2.split(",")
Auth_AP_G_date_rec = from_b64(m2[0])
t1 = int(m2[1])
t2 = int(m2[2])
V_3 = m2[3]
PK_ap = int(m2[4])


h_ID_i_K_de_msc = xor_bytes([from_b64(Auth_ap_g_date), h_date_kApMsc.encode()])


if V_3 != sha256(f"{h_ID_i_K_de_msc}{h_date_kApMsc}{ID_g}{PK_ap}"):
    print("[+] AP has been authenticated successfully.")
else:
    print("[-] V3s are not the same!")
    exit()

date = int(time.time()/1000) # almost current hour

print(f"{h_date_kApMsc},{chebyshev_polynomial(a,PK_ap)},{PK_de},{PK_ap}")
SK_de_ap = sha256(f"{h_date_kApMsc}{chebyshev_polynomial(a,PK_ap)}{PK_de}{PK_ap}")


_temp1 = sha256(f"{AT_a}")
_temp2 = sha256(f"{AT_b}")
V_4 = sha256(f"{SK_de_ap}{_temp1}{_temp2}")

m3 = f"{V_4}"
print(f"\033[96m[+] Sending M3={{V_4}} : {{{m3}}}\033[0m")
ap_sock.send(m3.encode('utf-8'))


print(f"[+] SK_AP-DE: {SK_de_ap}")