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
from random import randint



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
        self.clients[0] = None
        
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
        for peer in self.peers:
            p = p + peer + ","
        for client in self.clients:
            try:
                client.send(b'\x11' + p.encode('utf-8'))
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
            message = f'{connceted.nickname}: {input("")}'
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


class p2p: # holds list of connected ip_Addresses
    peers = ['127.0.0.1']
    ipAddress = ''
    knowIP = False
class connceted: #checks connection and holds nickname
    connected = False
    nickname = ""
    isServer = False




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
    
