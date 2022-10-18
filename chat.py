import threading
import socket
import sys

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
            print(f"Connected with {str(address)}")

    #Sends the client a keyword so user knows to send a nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)
            self.peers.append(address)
            self.sendPeers()

    #Lets everyone know who joined the chat and the particular client it worked
            self.broadcast(f'{nickname} joined the chat' .encode('ascii'))
            client.send('Connected to the server!' .encode('ascii'))

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
                self.broadcast(f'{nickname} left the chat' .encode('ascii'))
                self.nicknames.remove(nickname)
                self.peers.remove(address)
                self.sendPeers()
                break
    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","
        for conncection in self.clients:
            conncection.send(b'\x11' + bytes(p, "ascii"))


class Client:
    nickname = ""
    
    def __init__(self, address):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, 55555))
        self.nickname = input("Choose a nickname ")
        receive_thread = threading.Thread(target=self.receive, args=(client,))
        receive_thread.start()

        write_thread = threading.Thread(target=self.write, args=(client,))
        write_thread.start()

    def receive(self, client):
        while True:
            try:
                message = client.recv(1024).decode('ascii')
                if message == 'NICK':
                    client.send(self.nickname.encode('ascii'))
                else:
                    print(message)
            except:
                print("An error occurred!")
                client.close()
                break

    def write(self, client):
        while True:
            message = f'{self.nickname}: {input("")}'
            client.send(message.encode('ascii'))


if (len(sys.argv) > 1):
    pass
else:
    server = Server()
