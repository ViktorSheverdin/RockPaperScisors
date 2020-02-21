import socket
import sys
import pickle
from _thread import *
from game import Game

server = "10.65.0.202"
port = 5555

# Creates a socket and init the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the port to the local server
try:
    s.bind((server, port))
except socket.error as e:
    print(e)

# Always listens for the other connections
s.listen()
print("Waiting for connection, Server Started")

connected = set()
games = {}
idCount = 0

def threaded_client(conn, p, gameID):
    global idCount
    conn.send(str.encode(str(p)))
    reply = ""
    while True:
        try:
            data = conn.recv(4096).decode()

            if gameID in games:
                game = games[gameID]
                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()
                    elif data != "get":
                        game.play(p, data)

                    reply = game
                    conn.sendall(pickle.dumps(reply))

            else:
                break
        except:
            break


    print("Lost connection")
    try:
        del games[gameID]        
        print("Closing game: ", gameID)
    except:
        pass
    idCount -= 1
    conn.close()

while True:
    # Always accept the connection
    conn, addr = s.accept()
    print("Connected to: ", addr)
    
    idCount += 1
    p = 0
    gameID = (idCount -1 )//2
    if idCount % 2 == 1:
        games[gameID] = Game(gameID)
        print("Creating a new game...")
    else:
        games[gameID].ready = True
        p = 1


    # After the connection was accepted, start multythreading so many connections could be established simoltaniously
    start_new_thread(threaded_client, (conn, p, gameID))