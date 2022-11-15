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
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 55555))
        server.listen()
        while True:
            client, address = server.accept()
            

    #Sends the client a keyword so user knows to send a nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
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
    
    def __init__(self, address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, 55555))
        if connceted.nickname == "":
            connceted.nickname = input("Choose a nickname ")
        receive_thread = threading.Thread(target=self.receive, args=(client,))
        receive_thread.start()

        write_thread = threading.Thread(target=self.write, args=(client,))
        write_thread.start()

    def receive(self, client): #recive message from server
        while True:
            try:
                message = client.recv(1024)
                if message[0:1] == b'': #biggest pain right here
                    print("An error occurred!")
                    connceted.connected = False
                    client.close()
                    break
                if str(message, 'utf-8') == 'NICK':
                    client.send(connceted.nickname.encode('utf-8'))
                elif message[0:1] == b'\x11':
                    self.updatePeers(message[1:])
                else:
                    print(str(message, 'utf-8'))
            except:
                print("An error occurred!")
                connceted.connected = False
                Client.end = True
                client.close()
                break

    def write(self, client): #send message to server
        while True:
            message = f'{connceted.nickname}: {input("")}'
            client.send(message.encode('utf-8'))
            if Client.end == True:
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
                print("Starting Server")
                try:
                    pid=os.fork()
                    if pid:
                        server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print('Error')
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        pass
    
