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


# establishing the connection
HOST = "localhost"
PORT = 8910
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# initial values
K_s = 34567

s_g = 11223

ID_g = 98765

x = 45567

p=14797

PK_msc = chebyshev_polynomial(K_s,x)

GK = 76019

m = 90801
n = 98760

# receiving m2
m2 = sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ] M2={{TID_i, ID_MSC, PK_DE, V_1, V_2, ID_AP, PK_AP}} has been received: {{{m2}}}\033[0m")
m2 = m2.split(",")
TID_i= int(m2[0])
ID_msc= int(m2[1])
PK_de= int(m2[2])
V_1= m2[3]
V_2= m2[4]
ID_ap= int(m2[5])
PK_ap= int(m2[6])


# generating m3
K_de_msc = chebyshev_polynomial(K_s, PK_de)

K_ap_msc = chebyshev_polynomial(K_s, PK_ap)

ID_i = TID_i ^ K_de_msc

SID_i = sha256(f"{ID_i ^ s_g}")

if V_1 == sha256(f"{PK_de}{ID_g}{K_de_msc}{SID_i}"):
    print("[+] DE has been authenticated successfully.")
else:
    print("[-] V1s are not the same!")
    exit()

if V_2 == sha256(f"{PK_ap}{ID_ap}{K_ap_msc}"):
    print("[+] AP has been authenticated successfully.")
else:
    print("[-] V2s are not the same!")
    exit()

t1 = int(time.time()) - (60 * 60 * 3) # from 3 hours ago
t2 = t1 + (60 * 60 * 6) # 3 hours from now

date = int(time.time()/1000) # almost current hour
_temp1 = sha256(f"{date}{K_ap_msc}").encode('utf-8')
_temp2 = sha256(f"{ID_i}{K_de_msc}").encode('utf-8')
Auth_ap_g_date = to_b64(xor_bytes([_temp1,_temp2]))

seed_1 = sha256(f"{GK}{ID_ap}{date}{t1}{t2}{m}")

seed_2 = sha256(f"{n}{GK}{ID_ap}{date}{t1}{t2}")

AT_a = sha256(seed_1)

AT_b = sha256(seed_2)

TID_g = to_b64(xor_bytes([f"{ID_g}".encode('utf-8'), sha256(f"{ID_i}{K_de_msc}").encode("utf-8")]))

m3 = f"{Auth_ap_g_date},{t1},{t2},{AT_a},{AT_b},{TID_g}"
print(f"\033[96m[+] Sending M3={{Auth_AP_G_date, t1, t2, AT_a, AT_b, TID_G}} : {{{m3}}}\033[0m")
sock.send(m3.encode('utf-8'))
