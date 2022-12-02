# The startup of the code goes python chat.py for the server and python chat.py [ip_address] for a client
# Multiple clients on one machine will break the p2p functionality due to the port still being open and staying open indefinitely when trying to open
# This code was written by Dominic, Collin and Harry
# Somewhat inspired by NeuralNine and howCode on youtube
# 
import threading
from multiprocessing import Process
import time
import socket
import sys
import random
from random import randint
from cryptography.fernet import Fernet





def CreateServer():
    return Server()


#this is the server class it was made host the clients
class Server:
    #these are lists to hold the nicknames the clients and the 
    clients = []
    nicknames = []
    peers = []
    def __init__(self):
        print("Starting Server")  #runs when server tries to find connection
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 2345))
        server.listen()
        
        print("Server Running") #server started running
        while True:
            clients, address = server.accept()
            

            #Sends the client a keyword so user knows to send a nickname
            clients.send('NICK'.encode('utf-8'))
            message = clients.recv(1024)
            nickname = message.decode('utf-8') 
            nickname = nickname.rstrip()
            self.nicknames.append(nickname)
            self.clients.append(clients)
            self.peers.append(address[0])
            self.sendPeers()
            self.sendNames()
            time.sleep(.1)
            #Lets everyone know who joined the chat and the particular client it worked
            message = 'Connected to the server!'
            clients.send(connected.cipher.encrypt(bytes(message, 'utf-8')))
            message = f'{nickname} joined the chat'
            self.broadcast(connected.cipher.encrypt(bytes(message, 'utf-8')), clients)
            
            thread = threading.Thread(target=self.handle, args=(clients, address)) #new thread is created
            thread.start()

        
    def broadcast(self, message, client1): #broadcast peer
        for clients in self.clients:
            if clients != client1: #no two clients can be the same
                try:
                    clients.send(message)
                except:
                    pass
    def disconect(self, message):  #client disconnects
        for clients in self.clients:
            try:
                clients.send(message) # client sends message saying disconnected
            except:
                pass

    def handle(self, client, address): #handles the message the client sends
        while True:
            try:
                message = client.recv(1024)
                if message == b'': #clent dead end connection
                    index = self.clients.index(client)
                    self.clients.pop(index)
                    client.close()
                    nickname = self.nicknames[index]
                    self.disconect("!dead" + nickname) #displays the client is dead
                    self.disconect(connected.cipher.encrypt(bytes(f'{nickname} left the chat', 'utf-8')))
                    self.nicknames.remove(nickname)
                    self.peers.remove(address[0]) #removes dead player usernmame from list
                    self.sendPeers() #sends remaining peers
                    self.sendNames() #sends remaining nicknames
                    break
                elif message == b'\x20':
                    pass             
                else:
                    self.broadcast(message, client) #displays message from client to everyone
            except: #clent dead end connection
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.disconect("!dead" + nickname) #displays the client is dead
                self.disconect(connected.cipher.encrypt(bytes(f'{nickname} left the chat', 'utf-8')))
                self.nicknames.remove(nickname) #removes dead player username from list
                self.peers.remove(address[0])
                self.sendPeers() #sends remaining peers
                self.sendNames() #sends remaining nicknames
                break
    def sendPeers(self): #allows you to get all ip addresses
        p = ""
        for peer in self.peers:
            p = p + peer + ","
        for clients in self.clients:
            try:
                clients.send(b'\x11' + p.encode('utf-8'))
            except:
                pass
    def sendNames(self):  #allows you to get the nicknames
        n = ""
        for nickname in self.nicknames:
            n = n + nickname + ","
        for clients in self.clients:
            try:
                clients.send(b'\x13' + n.encode('utf-8'))
            except:
                pass

class Client:
    end = False
    client = None
    ip_address = ''
    def __init__(self, address): #client starting with ip address
        self.ip_address = address
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((address, 2345))
        if connected.nickname == "":
            connected.nickname = input("Choose a nickname ")
        Clientholder.client = self.client
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def receive(self): #recive message from server
        while True:
            try:
                message = self.client.recv(1024) #accept message
                if message[0:1] == b'': #The server has died and this is being recived
                    print("An error occurred!")
                    connected.connected = False
                    self.client.close()
                    break
                if str(message, 'utf-8') == 'NICK': #send the nickname back
                    self.client.send(connected.nickname.encode('utf-8'))
                elif message[0:1] == b'\x11': #take in the peers
                    self.updatePeers(message[1:])
                elif message[0:1] == b'\x13': #take in the nicknames
                    self.updateNicknames(message[1:])
                elif message[0:1] == b'\x16': #someone else has voted
                    game.otherVote(int.from_bytes(message[1:], "big"))
                elif message[0:1] == b'\x17': #mafia has killed
                    game.otherKill(int.from_bytes(message[1:], "big"))
                elif message[0:1] == b'\x18': #game has started initize the game
                    game.commands("start")
                    game.invest_player = int.from_bytes(message[1:], "big")
                    if game.invest_player == connected.nicknameNum:
                        print("You are the invest")
                elif message[0:1] == b'\x19': #game has started initize the game
                    game.mafia_player = int.from_bytes(message[1:], "big")
                    if game.mafia_player == connected.nicknameNum:
                        print("You are the Mafia")
                else:
                    msg = connected.cipher.decrypt(message) #decripts message
                    print(str(msg, 'utf-8')) #makes message readable
            except:
                print("An error occurred!")
                self.client.close()
                connected.connected = False
                self.end = True
                break
            if self.end == True:
                break

    def write(self): #send message to server
        while True:
            command = input("")
            if command[0:1] == '!':
                game.commands(command)
            elif not game.day:
                print("Its night")
            elif game.dead:
                print("Cannot speak you are dead")
            else:
                message = f'{connected.nickname}: {command}'
                try:
                    self.client.send(connected.cipher.encrypt(bytes(message, 'utf-8')))
                except:
                    self.client.send(b'\x20')
                
            if self.end == True:
                self.client.close()
                connected.connected = False
                break
            
    def updatePeers(self, peerData): #takes the peers from the server and puts them into the p2p peers list
        p2p.peers = str(peerData, 'utf-8'). split(",")[:-1]
        if p2p.knowIP == False: # gets your IP
            p2p.ipAddress = p2p.peers[len(p2p.peers)-1]
            p2p.knowIP = True
            print(p2p.ipAddress)
    def updateNicknames(self, peerData):
        p2p.nicknames = str(peerData, 'utf-8'). split(",")[:-1]
        i = 0
        for nickname in p2p.nicknames:
            if nickname == connected.nickname:
                connected.nicknameNum = i
            i += 1
            
class Clientholder: #holds the client for the game to access
    client = None

class p2p: # holds list of connected ip_Addresses, nicknames, your ip
    peers = []
    nicknames = []
    ipAddress = ''
    knowIP = False
    isServer = False
class connected: #checks connection and holds nickname
    connected = False
    nickname = ""
    nicknameNum = 0
    #the key for the encription
    key = b'q50ZCbQISUOyxJKIanr8KHC2LherjkESbwkBiSbOiBI='
    #make the encription
    cipher = Fernet(key)

class Game: #this is the inner class for the game
    #initalize game variables
    total_players = 0
    mafia_player = 0
    invest_player = 0
    deadList = []
    dead = False
    vote = {}
    voted = False
    day = True
    game = False
    check = False
    kill = False
    numberPlayerstoStart = 3 #update to 7
    
    def commands(self, command): #runs the game commands
        if command[:5] == "!vote": #run the vote command
            try:
                name = command[6:]
                number = 0
                for names in p2p.nicknames: #gets the position of the nickname from the list
                    if names == name:
                        break
                    number += 1
                self.Vote(number)
            except:
                print("Not a name")
        elif command[:5] == "dead": #run the dead command
            try:
                name = command[6:]
                number = 0
                for names in p2p.nicknames: #gets the position of the nickname from the list
                    if names == name:
                        break
                    number += 1
                self.voteKill(number)
            except:
                print("Not a name")
        elif command[:5] == "!kill": #run the kill command
            try:
                name = command[6:]
                number = 0
                for names in p2p.nicknames: #gets the position of the nickname from the list
                    if names == name:
                        break
                    number += 1
                self.mafia_kill(number)
            except:
                print("Not a name")
        elif command == "!start": #start the game command
            self.start(1)
        elif command == "start": #game has started
            self.start(0)
        elif command[:7] == "!invest": #run the invest command
            try:
                name = command[8:]
                number = 0
                for names in p2p.nicknames: #gets the position of the nickname from the list
                    if names == name:
                        break
                    number += 1
                self.investigation(number)
            except:
                print("Not a name")
        elif command == "!nicknames": #print list of nicknames
            print(p2p.nicknames)
            print(p2p.peers)
        elif command == "!help": #give help to others
            print("commands \n!start to start the game\n!vote [nickname] to vote a player\n!nicknames to get a list of nicknames")
            print("!kill [nickname] to chose a player to die\n!invest [nickname] to investigate a player")
            
        else: #command exception
            print("Not a command use !help for list of commands")
                    
      
    def start(self, other): #start the game
        num_players = len(p2p.nicknames)
        if other == 1 and not self.game: #you started the game
            if num_players >= self.numberPlayerstoStart: 
                self.total_players = num_players
                self.mafia_player = random.randint(0, num_players-1) #get the mafia player from list
                self.invest_player = random.randint(0, num_players-1) #get the invest player from list
                self.game = True
                timer_thread = threading.Thread(target=self.timer)
                timer_thread.start() #start the game timer
                if self.mafia_player == self.invest_player: #invest and mafia cannot be the same person
                    self.invest_player -= 1
                    if self.invest_player == -1:
                        self.invest_player = 1
                print("Game Start")
                v = self.invest_player
                if self.invest_player == connected.nicknameNum:
                    print("You are the Invest")
                Clientholder.client.send(b'\x18' + v.to_bytes(2, 'big')) #send invest player
                v = self.mafia_player
                if self.mafia_player == connected.nicknameNum:
                    print("You are the Mafia")
                Clientholder.client.send(b'\x19' + v.to_bytes(2, 'big')) #send mafia player
            else: #less than 7 players
                print("Not enough Players")
        elif not self.game: #different player started the game
            self.total_players = num_players
            self.game = True
            print("Game Start")
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.start() #start the game timer

    def mafia_kill(self, number): #mafia kills a player
        if not self.day and self.game: #cannot check if it is day or the game is not running
            if not self.kill: #cannot kill if you have already killed someone
                if number != self.mafia_player and connected.nicknameNum == self.mafia_player: #cannot kill self and if you are not mafia
                    self.deadList.append(number)
                    print(f"{p2p.nicknames[number]} has died")
                    self.total_players -= 1
                    self.kill = True
                    v = number
                    Clientholder.client.send(b'\x17' + v.to_bytes(2, 'big')) #send to others that maifa has killed
                    if self.total_players < 3: #reset the game there is a winner
                        self.game = False
                        self.dead = False
                        self.day = True
                        self.check = False
                        self.kill = False
                        self.voted = False
                        print("Game Over Mafia Wins")
                elif connected.nicknameNum != self.mafia_player:
                    print("You are not Mafia")
                else:
                    print("Mafia cannot kill Mafia")
            else:
                print("already killed tonight")

        else:
            print("it is day")

    def investigation(self, number): #check a player
        if not self.day and self.game: #cannot check if it is day or the game is not running
            if not self.check: #cannot check if you have already checked someone
                if connected.nicknameNum != self.invest_player: #cannot check if you are not invest
                    print("You are not invest")
                elif number == self.invest_player: #cannot check self
                    print("cannot invest self")
                elif number == self.mafia_player: #check if it is a mafia player
                    print ("Is mafia")
                    self.check = True
                else:
                    print ("Is not mafia")
                    self.check = True
            else:
                print("already checked tonight")
        elif self.day:
            print("it is day")
        else:
            print("not in game")
            
    def Vote(self, number): #you voted
        if self.day and self.game: #cannot vote if it is night or the game is not running
            if self.dead: #cannot vote if you are dead
                print("cant vote you are dead")
            elif not self.voted: #cannot vote if you voted already

                try:
                    self.vote[number] += 1 #add the vote to number of votes
                except:
                    self.vote[number] = self.vote.get(number, 0) + 1

                self.voted = True
                message = f'{connected.nickname}:Voted for {p2p.nicknames[number]}' #send that you have voted for who

                Clientholder.client.send(connected.cipher.encrypt(bytes(message, 'utf-8')))
                
                Clientholder.client.send(b'\x16' + number.to_bytes(2, 'big')) #send that you have voted for who
            elif self.voted:
                print("already voted today")
            else:
                print("Vote not counted")
        else:
            print("not in game")

    def otherVote(self, number): #someone else voted
        try:
            self.vote[number] += 1 #add their vote to number of votes
        except:
            self.vote[number] = self.vote.get(number, 0) + 1

    def voteKill(self, number): #there is a person dead or there is a disconnect
        if number == self.mafia_player: #reset the game there is a winner
            print(f"{p2p.nicknames[number]} has died")
            self.game = False
            self.dead = False
            self.day = True
            self.check = False
            self.kill = False
            self.voted = False
            print("Game Over Town Wins")
        else:
            self.deadList.append(number)
            print(f"{p2p.nicknames[number]} has died")
            if number == connected.nicknameNum: #did the running client die
                self.dead = True
            self.total_players -= 1
            if self.total_players < 3: #reset the game there is a winner
                self.game = False
                self.dead = False
                self.day = True
                self.check = False
                self.kill = False
                self.voted = False
                print("Game Over Mafia Wins")
            
    def otherKill(self, number): #mafia has killed and it goes to here for everyone else
        self.deadList.append(number)
        print(f"{p2p.nicknames[number]} has died")
        if number == connected.nicknameNum: #did the running client die
            self.dead = True
        self.total_players -= 1
        if self.total_players < 3:  #reset the game there is a winner
            self.game = False
            self.dead = False
            self.day = True
            self.check = False
            self.kill = False
            self.voted = False
            print("Game Over Mafia Wins")
    
    def timer(self): #this is the game timer
        t = 30 #day one number of seconds
        while True: 
            if not self.game: #break out of timer if there is no game
                break
            if t < 5: 
                print(t, end="\r") #prints countdown for last 5 seconds in dat
            if t == 0 and self.day: #turns day into night and counts votes
                print ("Its now night")
                self.day = False
                self.voted = False #reset if player voted
                t = 30 #reset t
                i = 0
                if self.total_players % 2 == 0: #if there is an even number of voters than the number of votes needed are half of the voters + 1
                    i = round(self.total_players/2) + 1
                else:  #if there is an even number of voters than the number of votes needed are half of the voters rounded up
                    i = round(self.total_players/2)
                for votes in self.vote: #check the votes
                    if self.vote[votes] >= i: #check if there is enough votes to kill
                        self.voteKill(votes)
                    self.vote[votes] = 0 #reset number of votes
            elif t == 0 and not self.day: #change night into day and reset night variables
                print ("Its now Day")
                self.check = False
                self.kill = False
                self.day = True
                t = 30
            time.sleep(1) #wait one second
            t -= 1

connected = connected()
game = Game() #set the game into a global variable
if __name__ == '__main__': #the program starts here
    if (len(sys.argv) == 1): #starts the program
        p2p.isServer = True
        server = Process(target=CreateServer, args=())
        server.start() #starts the server
        ## getting the hostname by socket.gethostname() method
        hostname = socket.gethostname()
        ## getting the IP address using socket.gethostbyname() method
        ip_address = socket.gethostbyname(hostname)
        connected.connected = True
        client = Client(ip_address) #starts the client
    if (len(sys.argv) > 1):  #starts the program client only
        connected.connected = True
        client = Client(sys.argv[1])

while True: #attempt at moving the server
    try:
        if connected.connected == False: #if connected it should not be running this
            print("Connecting") #tell users it is connecting
            time.sleep(1) #wait a 1 second connecting
            try:
                print(p2p.peers[1]) #try to connect to second peer in connections
                client = Client(p2p.peers[1])
                connected.connected = True
            except KeyboardInterrupt: #way to exit
                sys.exit(0)
            except:
                pass
            if p2p.peers[1] == p2p.ipAddress: #you are second peer in connections
                print("ReStarting Server")
                try:
                    if not p2p.isServer:
                        server = Process(target=CreateServer, args=())
                        p2p.isServer = True
                        server.start() #Start the server
                        client = Client(p2p.peers[1])
                        connected.connected = True
                except KeyboardInterrupt: #way to exit
                    sys.exit(0)
                except: #there was a bad falure
                    print('Error')
    except KeyboardInterrupt: #way to exit
        sys.exit(0)
    except:
        pass