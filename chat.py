# The startup of the code goes python chat.py for the server and python chat.py [ip_address] for a client
# Multiple clients on one machine will break the p2p functionality due to the port still being open and staying open indefinitely when trying to open
# This code was written by Dominic and Collin and ruined by Harry
# Somewhat inspired by NeuralNine and howCode on youtube
# 
import threading
from multiprocessing import Process
import os
import time
import socket
import sys
import random
from random import randint
from collections import defaultdict
from cryptography.fernet import Fernet

key = b'q50ZCbQISUOyxJKIanr8KHC2LherjkESbwkBiSbOiBI='

cipher = Fernet(key)

client = None

class Server:
    clients = []
    nicknames = []
    peers = []
    def __init__(self):
        print("Starting Server")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 2345))
        server.listen()
        connceted.isServer = True
        print("Server Running")
        while True:
            clients, address = server.accept()
            

    #Sends the client a keyword so user knows to send a nickname
            clients.send('NICK'.encode('utf-8'))
            message = clients.recv(1024)
            if message == b'\x12':
                self.fix(clients)
            else:
                nickname = message.decode('utf-8')
                nickname = nickname.rstrip()
                print(f"'{nickname}'")
                self.nicknames.append(nickname)
                self.clients.append(clients)
                self.peers.append(address[0])
                self.sendPeers()
                self.sendNames()
                time.sleep(.1)
                #Lets everyone know who joined the chat and the particular client it worked
                message = 'Connected to the server!'
                clients.send(cipher.encrypt(bytes(message, 'utf-8')))
                message = f'{nickname} joined the chat'
                self.broadcast(cipher.encrypt(bytes(message, 'utf-8')), clients)
            
            thread = threading.Thread(target=self.handle, args=(clients, address))
            thread.start()

    def fix(self, client1):
        self.clients.pop(0)
        self.nicknames.pop(0)
        self.sendPeers()
        
    def broadcast(self, message, client1):
        for clients in self.clients:
            if clients != client1:
                try:
                    clients.send(message)
                except:
                    pass
    def disconect(self, message):
        for clients in self.clients:
            try:
                clients.send(message)
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
                elif message == b'':
                    index = self.clients.index(client)
                    self.clients.pop(index)
                    client.close()
                    nickname = self.nicknames[index]
                    self.disconect("!dead" + nickname)
                    self.disconect(cipher.encrypt(bytes(f'{nickname} left the chat', 'utf-8')))
                    self.nicknames.remove(nickname)
                    self.peers.remove(address[0])
                    self.sendPeers()
                    self.sendNames()
                    break                
                else:
                    self.broadcast(message, client)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.disconect("!dead" + nickname)
                self.disconect(cipher.encrypt(bytes(f'{nickname} left the chat', 'utf-8')))
                self.nicknames.remove(nickname)
                self.peers.remove(address[0])
                self.sendPeers()
                self.sendNames()
                break
    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","
        for clients in self.clients:
            try:
                clients.send(b'\x11' + p.encode('utf-8'))
            except:
                pass
    def sendNames(self):
        n = ""
        print(self.nicknames)
        for nickname in self.nicknames:
            n = n + nickname + ","
        print(n)
        for clients in self.clients:
            try:
                clients.send(b'\x13' + n.encode('utf-8'))
            except:
                pass

class Client:
    end = False
    client = None
    ip_address = ''
    def __init__(self, address):
        self.ip_address = address
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((address, 2345))
        if connceted.nickname == "":
            connceted.nickname = input("Choose a nickname ")
            print(f"'{connceted.nickname}'")
        message = self.client.recv(1024)
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        self.client.send(connceted.nickname.encode('utf-8'))
        try:
            self.client.send(b'\x20')
        except:
            self.client.connect(('127.0.0.1', 2345))
            message = b'\x12'
            self.client.send(message)
        write_thread = threading.Thread(target=self.write)
        write_thread.start()

    def receive(self): #recive message from server
        while True:
            try:
                message = self.client.recv(1024)
                if message[0:1] == b'': #biggest pain right here
                    print("An error occurred!")
                    connceted.connected = False
                    self.client.close()
                    break
                if str(message, 'utf-8') == 'NICK':
                    pass
                elif message[0:1] == b'\x11':
                    self.updatePeers(message[1:])
                elif message[0:1] == b'\x13':
                    self.updateNicknames(message[1:])

                elif message[0:1] == b'\x16':
                    game.otherVote(int(message[1:]))
                elif message[0:1] == b'\x17':
                    game.otherKill(int(message[1:]))
                elif message[0:1] == b'\x18':
                    game.invest_player = int(message[1:])
                    if game.invest_player == connceted.nickname:
                        print("You are the invest")
                    game.start(0)
                elif message[0:1] == b'\x19':
                    game.mafia_player = int(message[1:])
                    if game.invest_player == connceted.nickname:
                        print("You are the Mafia")
                else:
                    msg = cipher.decrypt(message)
                    print(str(msg, 'utf-8'))
            except:
                print("An error occurred!")
                self.client.close()
                connceted.connected = False
                self.end = True
                break
            if self.end == True:
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
                    self.client.send(cipher.encrypt(bytes(message, 'utf-8')))
                except:
                    self.client.connect((self.ip_address, 2345))
                    fix = b'\x12'
                    self.client.send(fix)
                    message = f'{connceted.nickname}: {input("")}'
                    self.client.send(cipher.encrypt(bytes(message, 'utf-8')))
                
            if self.end == True:
                self.client.close()
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
    peers = []
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
        elif command[:5] == "!dead":
            try:
                number = p2p.nicknames.index(command[6:])
                self.voteKill(number)
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
        elif command == "!help":
            print("commands \n!start to start the game\n!vote [nickname] to vote a player\n!nicknames to get a list of nicknames")
            print("!kill [nickname] to chose a player to die\n!invest [nickname] to investigate a player")
            
        else:
            print("Not a command use !help for list of commands")
                    
      
    def start(self, other):
        num_players = len(p2p.nicknames)
        if other == 1 and not self.game:
            if num_players >= 7: 
                self.total_players = num_players
                self.mafia_player = random.randint(0, num_players)
                self.invest_player = random.randint(0, num_players)
                self.game = True
                timer_thread = threading.Thread(target=self.timer)
                timer_thread.start()
                if self.mafia_player == self.invest_player:
                    self.invest_player = random.randint(0, num_players)
                v = self.invest_player
                client.send(b'\x18' + bytes(v))
                v = self.mafia_player
                client.send(b'\x19' + bytes(v))  
            else:
                print("Not enough Players")
        elif not self.game:
            self.game = True
            timer_thread = threading.Thread(target=self.timer)
            timer_thread.start()

    def mafia_kill(self, number):
        if not self.day and self.game:
            if number != self.mafia_player and connceted.nicknameNum == self.mafia_player:
                self.deadList.append(number)
                self.total_players -= 1
                v = p2p.nicknames[number]
                client.send(b'\x17' + bytes(v))
                if self.total_players < 3:
                    self.game = False
                    self.dead = False
                    print("game end mafia wins")

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
                client.send(message.encode('utf-8'))
                v = p2p.nicknames[number]
                client.send(b'\x16' + bytes(v))
            elif self.voted:
                print("already voted")
            else:
                print("Vote not counted")

    def otherVote(self, name):
        number = p2p.nicknames.index(name)
        self.vote[number] += 1

    def voteKill(self, number):
        if number == self.mafia_player:
            self.game = False
            self.dead = False
            print("game end town wins")
        else:
            self.deadList.append(number)
            self.total_players -= 1
            if self.total_players < 3:
                self.game = False
                self.dead = False
                print("game end Mafia wins")
            
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
client = None
if __name__ == '__main__':
    if (len(sys.argv) == 1): #starts the program
        #print("here")
        server = Process(target=Server, args=())
        server.start()
        ## getting the hostname by socket.gethostname() method
        hostname = socket.gethostname()
        ## getting the IP address using socket.gethostbyname() method
        ip_address = socket.gethostbyname(hostname)
        print(ip_address)
        connceted.connected = True
        client = Client(ip_address)
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
                    server = Process(target=Server, args=())
                    server.start()
                    time.sleep(2)
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
    
