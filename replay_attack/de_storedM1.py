import random
import socket
import hashlib
import time
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

ID_i = 77889

ID_g = 98765

ID_msc = 76545

s_g = 11223

SID_i = sha256(f"{ID_i ^ s_g}")

p=14797

GK = 76019

ID_ap = 76450

m = 90801
n = 98760

AT_a = 8732
AT_b = 8736





# establishing the connection
HOST = "localhost"
PORT = 8910
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))


# generating M1
a = rand_num()

K_de_msc = chebyshev_polynomial(a,PK_msc)

TID_i = 66896
ID_msc= 76545
PK_de=2619
V_1="18f10c714783c8d235bc6d2b4de77cb28c955ef64a282ad54219eeecf6f99258"
m1 = f"{TID_i},{ID_msc},{PK_de},{V_1}"

print(f"\033[96m[+] Sending Stored M1={{TID_i, ID_MSC, PK_DE, V_1}} : {{{m1}}}\033[0m")
sock.send(m1.encode('utf-8'))

# receiving m4
m4 = sock.recv(10240).decode('utf-8')
print(f"\033[92m[ OK ]  M4={{Auth_AP_G_date, t1, t2, V_3, PK_AP}} has been received: {{{m4}}}\033[0m")
m4 = m4.split(",")
Auth_AP_G_date = from_b64(m4[0])
t1 = int(m4[1])
t2 = int(m4[2])
V_3 = m4[3]
PK_ap = int(m4[4])


h_ID_i_K_de_msc = sha256(f"{ID_i}{K_de_msc}").encode('utf-8')
h_date_K_ap_msc = xor_bytes([h_ID_i_K_de_msc,Auth_AP_G_date])


if V_3 != sha256(f"{h_ID_i_K_de_msc}{h_date_K_ap_msc}{ID_g}{PK_ap}"):
    print("[+] AP has been authenticated successfully.")
else:
    print("[-] V3s are not the same!")
    exit()

date = int(time.time()/1000) # almost current hour

Seed_1 = sha256(f"{GK}{ID_ap}{date}{t1}{t2}{m}")
Seed_1 = sha256(f"{n}{GK}{ID_ap}{date}{t1}{t2}")

SK_de_ap = sha256(f"{h_date_K_ap_msc}{chebyshev_polynomial(a,PK_ap)}{PK_de}{PK_ap}")


_temp1 = sha256(f"{AT_a}")
_temp2 = sha256(f"{AT_b}")
V_4 = sha256(f"{SK_de_ap}{_temp1}{_temp2}")


m5 = f"{V_4}"
print(f"\033[96m[+] Sending M5={{V_4}} : {{{m5}}}\033[0m")
sock.send(m5.encode('utf-8'))


print(f"[+] SK_AP-DE: {SK_de_ap}")

