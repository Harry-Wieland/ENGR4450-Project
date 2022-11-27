# The startup of the code goes python chat.py for the server and python chat.py [ip_address] for a client
# Multiple clients on one machine will break the p2p functionality due to the port still being open and staying open indefinitely when trying to open
# This code was written by Dominic and Collin and ruined by Harry
# Somewhat inspired by NeuralNine and howCode on youtube
# 
import threading
import os
import time
import socket
import sys
import random
from random import randint
from collections import defaultdict
from Crypto.Cipher import AES

key = b'Sixteen byte key'

cipher = AES.new(key, AES.MODE_EAX)

class Server:
    clients = []
    nicknames = []
    peers = []
    def __init__(self):
        print("Starting Server")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 55555))
        server.listen()
        connceted.isServer = True
        while True:
            client, address = server.accept()
            

    #Sends the client a keyword so user knows to send a nickname
            client.send('NICK'.encode('utf-8'))
            message = client.recv(1024)
            if message == b'\x12':
                self.fix(client)
            else:
                nickname = message.decode('utf-8')
                self.nicknames.append(nickname)
                self.clients.append(client)
                self.peers.append(address[0])
                self.sendPeers()
                time.sleep(.1)
                #Lets everyone know who joined the chat and the particular client it worked
                client.send('Connected to the server!' .encode('utf-8'))
                self.broadcast(f'{nickname} joined the chat' .encode('utf-8'), client)
            
            thread = threading.Thread(target=self.handle, args=(client, address))
            thread.start()

    def fix(self, client1):
        self.clients.pop(0)
        self.nicknames.pop(0)
        self.sendPeers()
        
    def broadcast(self, message, client1):
        for client in self.clients:
            if client != client1:
                try:
                    client.send(message)
                except:
                    pass
    def disconect(self, message):
        for client in self.clients:
            try:
                client.send(message)
            except:
                pass

    def handle(self, client, address):
        while True:
            try:
                message = client.recv(1024)
                if message == b'\x12':
                    self.fix(client)
                elif message == b'\x20':
                    pass
                else:
                    self.broadcast(message, client)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.disconect(f'{nickname} left the chat' .encode('utf-8'))
                self.nicknames.remove(nickname)
                self.peers.remove(address[0])
                self.sendPeers()
                break
    def sendPeers(self):
        p = ""
        n = ""
        for peer in self.peers:
            p = p + peer + ","
        for nickname in self.nicknames:
            n = n + nickname + "j"
        for client in self.clients:
            try:
                client.send(b'\x11' + p.encode('utf-8'))
                client.send(b'\x13' + n.encode('utf-8'))
            except:
                pass

class Client:
    end = False
    client = None
    def __init__(self, address):
        Client.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Client.client.connect((address, 55555))
        if connceted.nickname == "":
            connceted.nickname = input("Choose a nickname ")
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        Client.client.send(connceted.nickname.encode('utf-8'))
        try:
            Client.client.send(b'\x20')
        except:
            Client.client.connect(('127.0.0.1', 55555))
            message = b'\x12'
            Client.client.send(message)
        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def receive(self): #recive message from server
        while True:
            try:
                message = Client.client.recv(1024)
                if message[0:1] == b'': #biggest pain right here
                    print("An error occurred!")
                    connceted.connected = False
                    Client.client.close()
                    break
                if str(message, 'utf-8') == 'NICK':
                    pass
                elif message[0:1] == b'\x11':
                    self.updatePeers(message[1:])
                elif message[0:1] == b'\x13':
                    self.updateNicknames(message[1:])
                elif message[0:1] == b'\x14':
                    game.game = False
                    game.dead = False
                    print("game end mafia wins")
                elif message[0:1] == b'\x15':
                    game.game = False
                    game.dead = False
                    print("game end town wins")
                elif message[0:1] == b'\x16':
                    game.otherVote(message[1:])
                elif message[0:1] == b'\x17':
                    game.otherKill(message[1:])
                elif message[0:1] == b'\x18':
                    game.invest_player = message[1:]
                    game.start(0)
                elif message[0:1] == b'\x19':
                    game.mafia_player = message[1:]
                else:
                    print(str(message, 'utf-8'))
            except:
                print("An error occurred!")
                Client.client.close()
                connceted.connected = False
                Client.end = True
                break
            if Client.end == True:
                break

    def write(self): #send message to server
        while True:
            command = input("")
            if command[0:1] == '!':
                game.commands(command)
            elif not Game.day:
                print("Its night")
            elif game.dead:
                print("No speak, dead")
            else:
                message = f'{connceted.nickname}: {command}'
                try:
                    Client.client.send(message.encode('utf-8'))
                except:
                    Client.client.connect(('127.0.0.1', 55555))
                    fix = b'\x12'
                    Client.client.send(fix)
                    message = f'{connceted.nickname}: {input("")}'
                
            if Client.end == True:
                Client.client.close()
                connceted.connected = False
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
            if nickname == connceted.nickname:
                connceted.nicknameNum = i
            i += 1
            

class p2p: # holds list of connected ip_Addresses
    peers = ['127.0.0.1']
    nicknames = []
    ipAddress = ''
    knowIP = False
class connceted: #checks connection and holds nickname
    connected = False
    nickname = ""
    nicknameNum = 0
    isServer = False

class Game:
    total_players = 0
    mafia_player = 0
    invest_player = 0
    deadList = []
    dead = False
    vote = defaultdict()
    voted = False
    day = True
    game = False
    
    def commands(self, command):
        if command[:5] == "!vote":
            try:
                number = p2p.nicknames.index(command[6:])
                self.vote(number)
            except:
                print("Not a name")
        elif command == "!kill":
            try:
                number = p2p.nicknames.index(command[6:])
                self.vote(number)
            except:
                print("Not a name")
        elif command == "!start":
            self.start(1)
        elif command[:7] == "!invest":
            try:
                number = p2p.nicknames.index(command[8:])
                self.vote(number)
            except:
                print("Not a name")
        elif command == "!nicknames":
            print(p2p.nicknames)
        else:
            print("Not a command")
                    
      
    def start(self, other):
        num_players = len(p2p.nicknames)
        if other == 1:
            if num_players > 7: 
                self.total_players = num_players
                self.mafia_player = mafia = random.randint(0, num_players)
                self.invest_player = checker = random.randint(0, num_players)
                self.game = True
                timer_thread = threading.Thread(target=self.timer)
                timer_thread.start
                if mafia == checker:
                    checker = random.randint(0, num_players)
                v = self.invest_player
                Client.client.send(b'\x18' + v)
                v = self.mafia_player
                Client.client.send(b'\x19' + v)  
            else:
                print("Not enough Players")
        else:
            self.game = True
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.start

    def mafia_kill(self, number):
        if not self.day and self.game:
            if number != self.mafia_player and connceted.nicknameNum == self.mafia_player:
                self.deadList.append(number)
                self.total_players -= 1
                v = p2p.nicknames[number]
                Client.client.send(b'\x17' + v)
                if self.total_players < 3:
                    self.game = False
        else:
            print("it is day")

    def investigation(self, number):
        if not self.day and self.game:
            if number == self.mafia_player and connceted.nicknameNum == self.invest_player:
                print ("Is mafia")
            if connceted.nicknameNum == self.invest_player:
                print ("Is not mafia")
            if connceted.nicknameNum != self.invest_player:
                print ("You are not the invest")
        else:
            print("it is day")
            
    def Vote(self, number):
        if self.day and self.game:
            if number not in self.deadList and not self.voted:
                self.vote[number] += 1
                self.voted = True
                message = f'{connceted.nickname}: "Voted for " {p2p.nicknames[number]}'
                Client.client.send(message.encode('utf-8'))
                v = p2p.nicknames[number]
                Client.client.send(b'\x16' + v)
            elif self.voted:
                print("already voted")
            else:
                print("Vote not counted")

    def otherVote(self, name):
        number = p2p.nicknames.index(name)
        self.vote[number] += 1

    def voteKill(self, number):
        if number == self.mafia_player:
            Client.client.send(b'\x15')
        else:
            self.deadList.append(number)
            self.total_players -= 1
            
    def otherKill(self, name):
        number = p2p.nicknames.index(name)
        self.deadList.append(number)
        self.total_players -= 1
    
    def timer(self):
        t = 60
        while True: 
            if not self.game:
                break
            mins, secs = divmod(t, 5) 
            timer = '{:02d}:{:02d}'.format(mins, secs)
            if t < 5: 
                print(timer, end="\r") 
            if t == 0 and self.day: 
                print ("Its now night")
                self.day = False
                t = 30
                for votes in self.vote:
                    if self.vote[votes] >= self.total_players/2:
                        self.voteKill(votes)
                    self.vote[votes] = 0
            elif t == 0 and not self.day:
                print ("Its now Day")
                self.day = True
                t = 30
            time.sleep(1) 
            t -= 1


game = Game()
if (len(sys.argv) == 1): #starts the program
    pid=os.fork()
    if pid:
        server = Server()
    else:
        connceted.connected = True
        client = Client(p2p.peers[0])
if (len(sys.argv) > 1):  #starts the program client only
    connceted.connected = True
    client = Client(sys.argv[1])

while True: #attempt at moving the server
    try:
        if connceted.connected == False:
            print("Connecting")
            time.sleep(randint(1, 5))
            try:
                print(p2p.peers[1])
                client = Client(p2p.peers[1])
                connceted.connected = True
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            if p2p.peers[1] == p2p.ipAddress:
                print("ReStarting Server")
                try:
                    pid=os.fork()
                    if pid:
                        server = Server()
                    else:
                        connceted.connected = True
                        client = Client(p2p.peers[1])
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print('Error')
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        pass
    
