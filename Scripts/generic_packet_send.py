from socket import *
import time, sys

if len(sys.argv) < 7:
    print("Requires at least six arguments.")
    print("Usage: generic_packet_send.py hex <connection-type> <remote/bind-ip> <port> <send-rate-sec> <filename(s)>")
    print("Usage: generic_packet_send.py string <connection-type> <remote/bind-ip> <port> <send-rate-sec> <filename(s)>")
    print("connection-type must be UDP, TCP-Server, or TCP-Client")
    exit()

if sys.argv[1] == "hex":
    hex_mode = True
elif sys.argv[1] == "string":
    hex_mode = False
else:
    print(sys.argv[1] + " is not valid. Must be hex or string")
    exit()
    
addr = (sys.argv[3], int(sys.argv[4]))
if sys.argv[2] == "UDP": 
    udp = True
    client = socket(AF_INET, SOCK_DGRAM)
elif sys.argv[2] == "TCP-Server": 
    udp = False
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(addr)
    s.listen(1)
    client, a = s.accept()
    print("Client connected from " + str(a))
elif sys.argv[2] == "TCP-Client":
    udp = False
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(addr)
    print("Connected to server at " + str(addr))
else:
    print(sys.argv[2] + " is not a valid socket type (TCP-Server, TCP-Client, or UDP)")
    exit()
    
fileset = []
for x in range(6, len(sys.argv)):
    one = open(sys.argv[x], "r")
    fileset.append(one.readlines())
    one.close()
    
idx = 0
rate = float(sys.argv[5])
m = max(fileset, key=len)
print("Preparing to send " + str(len(m)) + " packets")
for line in m:
    message = ""
    if hex_mode:    
        newLine = ""
        for set in fileset: newLine += set[idx%len(set)].strip()
        message = bytearray.fromhex(newLine)
    else:
        for set in fileset: message += set[idx%len(set)]
        message = message.encode()
    
    if udp: client.sendto(message, addr)
    else: client.send(message)
    idx += 1
    time.sleep(rate)
    
client.close()