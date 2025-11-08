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

PK_msc = 5151 #chebyshev_polynomial(K_s,x)


p=14797

ID_ap = 76450

z = int(time.time()) + (60 * 60 * 10) # 10 hours from now

m = 90801
n = 98760

ID_g = 98765
GK = 76019
ID_i = 77889 # has access after other attacks

print(f"[ ] Adversary has access to: ID_g:{ID_g}, GK:{GK}, ID_i:{ID_i}")

# establishing the connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = 'localhost'
port = 8910

try:
    sock.bind((host, port))
except socket.error as e:
    print(str(e))
    exit(0)

sock.listen()
de_sock, de_address = sock.accept()





# receiving m1
m1 = de_sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ] M1={{TID_i, ID_MSC, PK_DE, V_1}} has been received: {{{m1}}}\033[0m")
m1 = m1.split(",")
TID_i= int(m1[0])
ID_msc= int(m1[1])
PK_de=int(m1[2])
V_1 = m1[3]

# generating m2, m3
b = rand_num()

PK_ap = chebyshev_polynomial(b,x) % p

K_ap_msc = chebyshev_polynomial(b, PK_msc)

V_2 = sha256(f"{PK_ap}{ID_ap}{K_ap_msc}")


t1 = int(time.time()) - (60 * 60 * 3) # from 3 hours ago
t2 = t1 + (60 * 60 * 6) # 3 hours from now

date = int(time.time()/1000) # almost current hour


seed_1 = sha256(f"{GK}{ID_ap}{date}{t1}{t2}{m}")

seed_2 = sha256(f"{n}{GK}{ID_ap}{date}{t1}{t2}")


AT_a = sha256(seed_1)
AT_b = sha256(seed_2)

K_de_msc = ID_i ^ TID_i

TID_g = xor_bytes([f"{ID_g}".encode('utf-8'), sha256(f"{ID_i}{K_de_msc}").encode("utf-8")])


_temp1 = sha256(f"{date}{K_ap_msc}").encode('utf-8')
_temp2 = sha256(f"{ID_i}{K_de_msc}").encode('utf-8')
Auth_ap_g_date = xor_bytes([_temp1,_temp2])


# generating m4
if not (1 <= t1 <= int(time.time()) <= t2 <= z):
    print("[-] Time slots are not currect.")


date = int(time.time()/1000) # almost current hour
h_date_K_ap_msc = sha256(f"{date}{K_ap_msc}").encode('utf-8')
h_ID_i_K_de_msc = xor_bytes([h_date_K_ap_msc,Auth_ap_g_date])

ID_g = xor_bytes([TID_g, h_ID_i_K_de_msc])

V_3 = sha256(f"{h_ID_i_K_de_msc}{h_date_K_ap_msc}{ID_g}{PK_ap}")

m4 = f"{to_b64(Auth_ap_g_date)},{t1},{t2},{V_3},{PK_ap}"
print(f"\033[96m[+] Sending M4={{Auth_AP_G_date, t1, t2, V_3, PK_AP}} : {{{m4}}}\033[0m")
de_sock.send(m4.encode('utf-8'))


# receiving m5
m5 = de_sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ]  M5={{V_4}} has been received: {{{m5}}}\033[0m")
V_4 = m5

SK_de_ap = sha256(f"{h_date_K_ap_msc}{chebyshev_polynomial(b,PK_de)}{PK_de}{PK_ap}")


_temp1 = sha256(f"{AT_a}")
_temp2 = sha256(f"{AT_b}")

if V_4 != sha256(f"{SK_de_ap}{_temp1}{_temp2}"):
    print("[+] DE has been authenticated successfully.")
else:
    print("[-] V4s are not the same!")
    exit()


print(f"[+] SK_AP-DE: {SK_de_ap}")

