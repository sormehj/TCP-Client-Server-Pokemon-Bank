import socket
import hashlib
import time

def receiveMessage():
    full_msg = ""
    while True:
        msg = s.recv(4096)
        if len(msg) > 0:
            full_msg += msg.decode("utf-8")
            return full_msg
            
def sendMessage(msg):
    s.sendto(msg.encode(), server)
    ack = receiveMessage()
    print(ack)

def login():
    sendMessage("LOGIN")
    
    #client types in username
    user = input("User: ")
    userFlag = True
    if len(user) > 20 or ' ' in user:
        userFlag = False
        while(userFlag == False):
            print("Username cannot exceed 20 characters or contain ' '")
            user = input("User: ")
            if len(user) > 0 and len(user) <= 20 and ' ' not in user:
                userFlag = True
    
    #client sends username to server
    user = "USER" + user
    s.sendto(user.encode(), server)

    
    #Client receives challenge
    chal = receiveMessage()
    print(f"Challenge String: {chal}")
    
    msg = receiveMessage()
    print(msg)
    
    #client types in password
    pswd = input("Pass: ")
    userFlag = True
    if len(pswd) > 20 or ' ' in pswd:
        userFlag = False
        while(userFlag == False):
            print("Password cannot exceed 20 characters or contain ' '")
            pswd = input("Pass: ")
            if len(pswd) > 0 and len(pswd) <= 20 and ' ' not in pswd:
                userFlag = True
    
    #client generates hash and sends to server
    chalStr = chal + pswd
    chalHash = hashlib.md5(chalStr.encode()).hexdigest()
    s.sendto(chalHash.encode(), server)
    msg = receiveMessage()
    print(msg)
    if msg == "ACCEPTED":
        return True
    else:
        return False

def deposit():
    sendMessage("DEPOSIT")
    
    name = input("Enter the name of the pokemon you would like to deposit: ")
    s.sendto(name.encode(), server)
    ack = receiveMessage()
    print(ack)
    
    while ack != "UNIQUE":
        print("Enter name of pokemon to deposit: ")
        name = input()
        s.sendto(name.encode(), server)
        ack = receiveMessage()
        if ack != "UNIQUE":
            print("That Pokemon already exists in the bank! Try again")
    
    print("New pokemon detected!")
    print("Enter the details of the pokemon:")
    details = input()
    sendMessage(details)

def locate():
    # msg = receiveMessage()
    # print(msg)
    while True:
        print("Please enter the name of the pokemon you're searching for.")
        pokemon = input("Pokemon: ")
        pokemon = pokemon.lower()
        check = True
        for letter in pokemon:
          if ord(letter) < 97 or ord(letter) > 122:
            check = False

        if check == False:
          print("Name cannot contain spaces or numbers. Please try again")
        else: 
          s.sendto(pokemon.encode(),server)
          msg = receiveMessage()
          print(msg)
          if msg == "FOUND":
            pokemonDetail = receiveMessage()
            print(pokemonDetail)
            break
          else:
            print("Unable to find Pokemon")
            break
            
def withdraw():
    # msg = receiveMessage()
    # print(msg)
    while True:
        print("Please enter the name of the pokemon you're withdrawing.")
        pokemon = input("Pokemon: ")
        pokemon = pokemon.lower()
        check = True
        for letter in pokemon:
          if ord(letter) < 97 or ord(letter) > 122:
            check = False

        if check == False:
          print("Name cannot contain spaces or numbers. Please try again")
        else: 
          s.sendto(pokemon.encode(),server)
          msg = receiveMessage()
          print(msg)
          if msg == "FOUND":
            pokemonDetail = receiveMessage()
            print(pokemonDetail)
            break
          else:
            print("Unable to find Pokemon")
            break
            
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = 4444#int(input("Enter Port Number: "))
#server = ('172.21.9.5', port)
server = ('127.0.0.1', port)
timeout = 45
print("Connecting to server...")
s.connect(server)
s.settimeout(timeout)
print("Successfully connected to server")

#client waiting to receive log in prompt from server
# msg = receiveMessage()
# print(msg)
userInput = ""
try:
    while userInput != "2":
        print("Welcome to the Pokemon Bank!")
        print("1. Login")
        print("2. Exit")
        print("3. Deposit")
        print("4. Dump Bank Contents")
        print("5. Locate")
        print("6. Withdraw")
        userInput = input("Selection: ")
        match userInput:
            case "1":
                if login():
                    print("Login Successful")
                else:
                    print("Login Failed")
            case "2":
                msg = "EXIT"
                s.sendto(msg.encode(), server)
                break
            case "3":
                deposit()
            case "4":
                sendMessage("DUMP")
            case "5":
                sendMessage("LOCATE")
                locate()
            case "6":
                sendMessage("WITHDRAW")
                withdraw()
        
    print("Thanks for using the Pokemon Bank")	
    s.close()
    
except socket.timeout:
    print("Connection has timed out")
    s.close()