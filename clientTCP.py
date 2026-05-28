import socket
import hashlib
import time

#receive a message from the client and return it
def receiveMessage():
    full_msg = ""
    while True:
        msg = s.recv(4096)
        if len(msg) > 0:
            full_msg += msg.decode("utf-8")
            return full_msg

#display the login menu
def logExitMenu():
    while True:
        print("Please select one of the following by entering the keyword: ")
        print("1. LOGIN")
        print("2. EXIT")
        choice = input()
        if choice == "LOGIN" or choice == "EXIT":
            s.sendto(choice.encode(), server)
            return choice
        else:
            print("That is not a valid keyword. Please try again.")

#display the main menu of the bank after logging in
def actionMenu():
    while True:
        print("Please select one of the following by entering the keyword: ")
        print("LOCATE")
        print("DEPOSIT")
        print("WITHDRAW")
        print("EXIT")
        choice = input()
        if choice == "LOCATE" or choice == "DEPOSIT" or choice == "WITHDRAW" or choice == "EXIT":
            s.sendto(choice.encode(),server)
            match choice:
                case "LOCATE":
                    locate()
                case "DEPOSIT":
                    deposit()
                case "WITHDRAW":
                    withdraw()
                case "EXIT":
                    exitBank()
                    break
        else:
            print("That is not a valid keyword. Please try again.")

#login funtion controls the login process
def logIn():
    #client types in username
    msg = receiveMessage()
    print(msg)
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
    return msg

#search the bank for the requested data and send it to the client
def locate():
    msg = receiveMessage()
    print(msg)
    while True:
        print("Please enter the name of the pokemon you're searching for.")
        pokemon = input("Pokemon: ")
        pokemon = pokemon.lower()
        check = True
        if len(pokemon) < 1 or len(pokemon) > 20:
          check = False
            
        if check == False:
          print("Name cannot exceed 20 characters. Please try again")
        else: 
          s.sendto(pokemon.encode(),server)
          msg = receiveMessage()
          print(msg)
          if msg == "FOUND":
            pokemonDetail = receiveMessage()
            display(pokemonDetail)
            break
          else:
            print("Unable to find Pokemon")
            break

#deposit pokemon into the bank
def deposit():
  msg = receiveMessage()
  print(msg)
  duplicateFlag = False

  pokemonInformation = ""

  #user inputs pokemon name
  while True:
    print("What is the name of the Pokemon you'd like to deposit?")
    pokemon = input("Pokemon: ")
    pokemon = pokemon.lower()
    check = True
    if len(pokemon) < 1 or len(pokemon) > 20:
      check = False

    if check == False:
      print("Name cannot contain spaces or numbers. Please try again")
    else:
      s.sendto(pokemon.encode(),server)
      msg = receiveMessage()
      if (msg == "DUPE"):
        print(pokemon, " already exists in the bank. Cannot have duplicates")
        duplicateFlag = True
      pokemon = pokemon + ","
      pokemonInformation += pokemon
      #need to send name to ensure there are no duplicates

      break
      
  #user inputs pokemon level
  while duplicateFlag == False:
    print("What is the level of your pokemon?")
    level = input("Level: ")

    levelCheck = True
    if len(level) < 1 or len(level) > 20:
      check = False
    else:
      for char in level:
        if ord(char) < 48 or ord(char) > 57:
          levelCheck = False
          
      if int(level) < 1 or int(level) > 100:
        levelCheck = False

    if levelCheck == False:
      print("Level must be an integer number between 1-100 (inclusive). ",
      "Please try again.")
    else:
      level = level + ","
      pokemonInformation += level
      break
      
  #user inputs pokemon type
  while duplicateFlag == False:
    typeList = []
    print("What type is your Pokemon?")
    print("If a pokemon is multiple types, seperate them with a '/'")
    pokeType = input("Type: ")

    typeCheck = True
    if len(pokeType) < 1 or len(pokeType) > 20:
      typeCheck = False
    else:
      pokeType = pokeType.lower()
      typeList = pokeType.split('/')

      #possible type 
      validList = ["normal", "fire", "water", "grass", "flying", "fighting", "poison", 
                  "electric", "ground", "rock", "psychic", "ice", "bug", "ghost", "steel",
                  "dragon", "dark", "fairy"]

      found = False
      for item in typeList:
        for value in validList:
          if item == value:
            found = True

      if found == False:
        print("ERROR1")
        typeCheck = False
        
    #cannot have a type repeated multiple times for a singular pokemon
    #Example: cant do fighting/fire/fighting
    if len(typeList) < 1 or len(typeList) > 2:
        typeCheck = False
    if len(typeList) == 2:
        if typeList[0] == typeList[1]:
            typeCheck = False
    if typeCheck == False:
      print(pokeType, " is not a valid type. Please enter a valid type. ", 
            "Types cannot repeat.")
    else:
      pokeType = ""
      
      if len(typeList) == 2:
       pokeType += typeList[0] + "/" + typeList[1] + ","
      else:
       pokeType += typeList[0] + ","
        
      pokemonInformation += pokeType
      break

  #user inputs pokemon hp
  while duplicateFlag == False:
    print("What is the HP (Health Points) of your pokemon?")
    hp = input("HP: ")

    hpCheck = True
    if len(hp) < 1:
      hpCheck = False
    else:
      for char in hp:
        if ord(char) < 48 or ord(char) > 57:
          hpCheck = False
      if int(hp) < 1 or int(hp) > 255:
        hpCheck = False

    if hpCheck == False:
      print("HP must be an integer number between 1-255 (inclusive). ",
      "Please try again.")
    else:
      hp = hp + ","
      pokemonInformation += hp
      break

  #user inputs 4 pokemon moves
  while duplicateFlag == False:
    moveSet = ""
    i = 1

    while i < 5:
      print("Enter move ", i)
      move = input(f"move {i}:")
      move = move.lower()
      check = True
      if len(move) < 1 or len(move) > 20:
        check = False

      if check == False:
        print("Move cannot be less than 1 character or be greater than 20. Please try again.")
        i -= 1
      else:
        if i == 4:
          moveSet += move
        else:
          moveSet += move + ","
      i += 1
  
    pokemonInformation += moveSet
    break
  
  if duplicateFlag == False:
    print(pokemonInformation)
    s.sendto(pokemonInformation.encode(),server)
    msg = receiveMessage()
    print(msg)
        
#remove a pokemon from the bank
def withdraw():
  msg = receiveMessage()
  print(msg)
  while True:
      print("Please enter the name of the pokemon you want to withdraw.")
      pokemon = input("Pokemon: ")
      pokemon = pokemon.lower()
      check = True
      if len(pokemon) < 1 or len(pokemon) > 20:
        check = False

      if check == False:
        print("Name cannot exceed 20 characters. Please try again")
      else: 
        s.sendto(pokemon.encode(),server)
        msg = receiveMessage()
        print(msg)
        if msg == "FOUND":
          msg = receiveMessage()
          print(msg)
          break
        else:
          print("Unable to find Pokemon")
          break

#exit function exits the program
def exitBank():
  msg = receiveMessage()
  print(msg)
  s.close()

#displays the pokemons stats to the screen
def display(pokemonDetail):
  informationList = pokemonDetail.split(",", 8)
                                       
  name = informationList[0]
  level = informationList[1]
  pokeType = informationList[2]
  hp = informationList[3]
  move1 = informationList[4]
  move2 = informationList[5]
  move3 = informationList[6]
  move4 = informationList[7]

  print("Pokemon: " , name)
  print("Level: ", level)
  print("Type: ", pokeType)
  print("HP: ", hp)
  print("Move 1:", move1)
  print("Move 2:", move2)
  print("Move 3:", move3)
  print("Move 4:", move4)
  

#--------------------------------------------------------------------------------
#initialize the socket connection
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(input("Enter Port Number: "))
server = ('172.21.9.5', port)
timeout = 45

try:
    s.connect(server)
    s.settimeout(timeout)
    while True:
        #client waiting to receive log in prompt from server
        print("client has been activated")
        
        flag = True
        msg = ""
        while flag:
            option = logExitMenu()
            match option:
                case "LOGIN":
                    msg = logIn()
                    if msg == "DENIED":
                        print("Login failed. Please try again")
                    else:
                        print("Login Success!!!")
                        flag = False
                case "EXIT":
                    exitBank()
                    flag = False

        if option == "LOGIN":
            actionMenu()
        
        break

except s.timeout():
    print("No message from server, connection has timed out")
    s.close()