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
            self.broadcast(f'{nickname} joined the chat' .encode('utf-8'))
            
            thread = threading.Thread(target=self.handle, args=(client, address))
            thread.start()


    def broadcast(self, message):
        for client in self.clients:
            client.send(message)

    def handle(self, client, address):
        while True:
            try:
                message = client.recv(1024)
                self.broadcast(message)
            except:
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast(f'{nickname} left the chat' .encode('utf-8'))
                self.nicknames.remove(nickname)
                self.peers.remove(address[0])
                self.sendPeers()
                break
    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","
        for client in self.clients:
            client.send(b'\x11' + p.encode('utf-8'))

class Client:

    
    def __init__(self, address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, 55555))
        if connceted.nickname == "":
            connceted.nickname = input("Choose a nickname ")
        receive_thread = threading.Thread(target=self.receive, args=(client,))
        receive_thread.start()

        write_thread = threading.Thread(target=self.write, args=(client,))
        write_thread.start()

    def receive(self, client):
        while True:
            try:
                message = client.recv(1024)
                if message[0:1] == b'':
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
                client.close()
                break

    def write(self, client):
        while True:
            message = f'{connceted.nickname}: {input("")}'
            client.send(message.encode('utf-8'))
    def updatePeers(self, peerData):
        p2p.peers = str(peerData, 'utf-8'). split(",")[:-1]


class p2p:
    peers = ['127.0.0.1']
class connceted:
    connected = False
    nickname = ""


if (len(sys.argv) == 2):
    pid=os.fork()
    if pid:
        server = Server()
    else:
        connceted.connected = True
        client = Client(p2p.peers[0])
if (len(sys.argv) > 2):
    connceted.connected = True
    client = Client(sys.argv[2])
while True:
    try:
        if connceted.connected == False:
            print("Connecting")
            time.sleep(randint(1, 5))
            for peer in p2p.peers:
                if connceted.connected == False:
                    try:
                        client = Client(peer)
                        connceted.connected = True
                    except:
                        pass
                    if connceted.connected == False:
                        try:
                            server = Server()
                        except:
                            print("server no start")
    except:
        pass