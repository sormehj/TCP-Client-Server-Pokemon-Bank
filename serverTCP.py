import socket
import hashlib
import random
import time
import os

#UMBC ID:CK58777

#holds the entire bank in memory
bank = {}

#delete bank data file if it exists
def deleteBankFile():
    if os.path.exists("bankaccount.data"):
        os.remove("bankaccount.data")

#populates the bank dictionary based on the data file saved local to the server        
def genBankDict():
    file = open("bankaccount.data", "rt")
    for row in file:
        #name, level, type, hp, move1, move2, move3, move4
        pokeDetails = row.rsplit(",")
        detailList = []
        for item in range(8):
            detailList.append(pokeDetails[item].rstrip("\n"))
            
        bank[pokeDetails[0]] = detailList
    file.close()

#save bank data to the bankaccount.data file
def saveBankData():
    deleteBankFile()
    file = open("bankaccount.data", "a")
    for pokemon in bank:
        fileRow = ""
        print(bank[pokemon])
        for i in range(8):
            fileRow += bank[pokemon][i]
            if i != 7:
                fileRow += ","
            else:
                fileRow += "\n"
        file.write(fileRow)
    file.close()

#receive a message from the client and return it
def receiveMessage():
    full_msg = ""
    while True:
        msg = client.recv(4096)
        if len(msg) > 0:
            full_msg += msg.decode("utf-8")
            return full_msg

#login funtion controls the login process
def login():
    #Receive username
    message = "LOGIN Started"
    client.send(bytes(message,"utf-8"))
    print("LOGIN Selected")
    print("Waiting for username...")
    full_msg = receiveMessage()
    print(f"Msg Received: {full_msg}")
    username = full_msg

    #Send challenge string
    if full_msg[:4] == "USER":
        print("removing USER from username")
        username = full_msg[4:]
        print(username)
    chal = str(random.randrange(100000000000000, 999999999999999))
    print(f"Sent challenge token: {chal}")
    client.send(bytes(chal,"utf-8"))

    #Receive password
    message = "Username Received \nPlease enter your password"
    client.send(bytes(message,"utf-8"))
    print("Waiting for password...")
    clientPswdHash = receiveMessage()
    print(f"Msg Received: {clientPswdHash}")

    #Server computes password hash
    correctPswdChal = chal + PASSWORD
    correctPswdHash = hashlib.md5(correctPswdChal.encode()).hexdigest()
    print(f"Correct Hash: {correctPswdHash}")
    if clientPswdHash == correctPswdHash and username == USERNAME:
        message = "ACCEPTED"
        client.send(bytes(message,"utf-8"))
        print("Client successfully logged in")
    else:
        message = "DENIED"
        client.send(bytes(message,"utf-8"))
        print("Client login denied")

#deposit pokemon into the bank
def deposit():
    message = "DEPOSIT Started"
    client.send(bytes(message,"utf-8"))
    print("DEPOSIT Selected")

    
    print("Waiting for pokemon name...")
    pokeName = receiveMessage()
    
    #verify pokemon does not exist in the bank
    if pokeName in bank.keys():
        message = "DUPE"
        client.send(bytes(message,"utf-8"))
        print("DUPE Pokemon detected")
        return
    else:
        message = "UNIQUE"
        client.send(bytes(message,"utf-8"))
        print("UNIQUE Pokemon name")
    
    #receive new pokemon stats from the client
    print("Waiting for pokemon details...")
    details = receiveMessage()
    print(details)
    pokeDetails = details.split(",")
    bank[pokeDetails[0]] = pokeDetails
    
    message = "Pokemon successfully deposited to the bank"
    client.send(bytes(message,"utf-8"))
    print(message)
    print("Bank contents:")
    print(bank)

#search the bank for the requested data and send it to the client
def locate():
    message = "LOCATE Started"
    client.send(bytes(message,"utf-8"))
    print("LOCATE Selected")
    print("Waiting for pokemon name...")
    name = receiveMessage()
    if name in bank:
        message = "FOUND"
        client.send(bytes(message,"utf-8"))
        
        details = ""
        for i in range(8):
            details += bank[name][i]
            if i != 7:
                details += ","

        client.send(bytes(details,"utf-8"))
    else:
        message = "NOT FOUND"
        client.send(bytes(message,"utf-8"))

#remove a pokemon from the bank
def withdraw():
    message = "WITHDRAW Started"
    client.send(bytes(message,"utf-8"))
    print("WITHDRAW Selected")
    print("Waiting for pokemon name...")
    name = receiveMessage()
    if name in bank:
        message = "FOUND"
        client.send(bytes(message,"utf-8"))
        
        bank.pop(name)
        message = f"{name} successfully withdrawn"
        client.send(bytes(message,"utf-8"))
    else:
        message = "NOT FOUND"
        client.send(bytes(message,"utf-8"))

#initialize variables
random.seed()
ip_addr = "172.21.9.5"
port = int(input("Enter Port Number: "))
timeout = 45
queueSize = 5
USERNAME = "newtrainer" #correct username to login
PASSWORD = "someonespc" #correct password to login

#populates the bank dictionary if the bank database file exists
if os.path.exists("bankaccount.data"):
    genBankDict()
    print(bank)

#setup server and listen for connections
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((ip_addr, port))
print("Server is waiting for connections...")
sock.listen(queueSize)

try:
    #accept a found connection
    client, address = sock.accept()
    client.settimeout(timeout)    
    print(f"Connection from {address} has been established.")
    
    #loop the availible commands the client can request
    while True:
        request = ""
        print("Waiting for client request...")
        request = receiveMessage()
        match request:
            case "LOGIN":
                login()
            case "LOCATE":
                locate()
            case "DEPOSIT":
                deposit()
            case "WITHDRAW":
                withdraw()
            case "EXIT":
                break
    
    #exit the program and save the bank to the bankaccount.data file
    print("Exit request received")
    saveBankData()
    message = "Server disconnecting. Thank you for using the Pokemon Bank!"
    client.send(bytes(message,"utf-8"))
    print("Closing connection...")
    client.close()
    sock.close()
        
except socket.timeout:
    print("Connection has timed out")
    client.close()
    sock.close()