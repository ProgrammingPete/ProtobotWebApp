import socket
import _thread
import threading
from socketserver import ThreadingMixIn
import api_tabulated_new
import queue


class workerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            print("waiting")
            request = requests.get()  # empty queue blocks the thread
            datastr = str(api_tabulated_new.rawtable)
            request[2].sendall(datastr.encode())
            print('sent %d bytes of data to %s port: %s' % (len(datastr.encode()), request[0], request[1]))
            print("Finished Request for ", request[0])


class ClientThread(threading.Thread):
    def __init__(self, ip, port, sock):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock

    def run(self):
        data, address = self.sock.recvfrom(1024)

        # valid login
        if data.decode() == 'bitcoinrulez123':
            login = 'Logged in to ProtoBot server.\n\nEnter '"update"' for current data.\n'"exit"' to disconnect.'
            self.sock.sendall(login.encode())
            try:
                while True:
                    # Listen for client request
                    data, addr = self.sock.recvfrom(1024) #this block the thread

                    if data:
                        if data.decode() == 'update':
                            #this is where request will be added to a queue
                            requests.put([self.ip,self.port,self.sock])

                        elif data.decode() == 'exit':
                            self.sock.sendall('Exiting.'.encode())
                            self.sock.close()
                            break

                        else:
                            self.sock.sendall('invalid command. Please Try again'.encode())
            except ConnectionResetError:
                print("Lost connection to: ", self.ip, self.port)

        # invalid login
        elif data.decode() != 'bitcoinrulez123':
            fail = 'Login failed.'
            self.sock.sendall(fail.encode())
            self.sock.close()
            # stop thread and disconnect client

        for thread in threads:
            if self.getName() == thread.getName():
                print("Thread has ended: ", thread)
                threads.remove(thread)
                print(threads)

def server_start():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname() #apparently not needed
    print(host)
    # Establish server IP/port then bind the socket
    server_address = ('', 5678)
    serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSock.bind(server_address)

    print('Initialized ProtoBot server on %s port %s' % server_address)

    # Listen for incoming connections
    while True:

        serverSock.listen(4)

        (conn, (ip,port)) = serverSock.accept()
        print(conn)
        # start new thread for each new connection
        newThread = ClientThread(ip, port, conn)
        newThread.start()
        threads.append(newThread)
        print(threads)


if __name__ == '__main__':
    # List for all running threads
    threads = []
    requests = queue.Queue()  # store client information here
    serverThread = threading.Thread(target=server_start, name= "serverThread")
    rawTab = threading.Thread(target= api_tabulated_new.rawtab, name = 'Table')
    worker = workerThread()
    threads.append(serverThread)
    threads.append(rawTab)
    threads.append(worker)
    for thread in threads:
        thread.start()
    print(threads)
