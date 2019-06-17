import zmq
import sys

from bin import Bin
from folder import Folder


tcp = "tcp://"

class Server:

    context = zmq.Context()
    listen = context.socket(zmq.REP)
    next = context.socket(zmq.REQ)
    

    def __init__(self, id, IPListen, portListen, IPNext, portNext, bootstrap, k = 156):

        self.folder = Folder(id =portListen)

        self.IPListen = IPListen
        self.portListen = portListen
        self.IPNext = IPNext
        self.portNext = portNext
        self.k = k

        self.numElements = Bin(hex((2**k)-1)[2:])

        self.id = Bin(id)#aca va entrar la mac, debe crear una funcion que cuadre la mac como sha1
        print("my id:", self.id.getHex())
        self.listen.bind(tcp + self.IPListen + ":" + self.portListen)
        self.idPredecessor = None
        self.idSuccessor = None


        #query of disponible operations in the server's
        self.operation = {"updatePredecessor": self.updatePredecessor, 
                            "idIsInMySuccesor": self.idIsInMySuccesor,
                            "idIsInMyInterval": self.idIsInMyInterval,
                            "getSuccessor": self.getSuccessor,
                            "getServerID": self.getServerID,
                            "changeTheSuccessorInformation": self.changeTheSuccessorInformation,
                            "upload": self.upload,
                            "download": self.download }

        print("Server IP:", self.IPListen + ":" + self.portListen)

        if bootstrap:

            self.bootstrap()
            self.run()
        else :
            
            #self.find()
            self.addServerToChord()
            self.run()


    def idIsInMyInterval(self,data):
        """recive data with id hex wanted, return 1 if the id is in my interval, else return 0"""
        ans = None
        num = Bin(data[1].decode())

        if self.idPredecessor < self.id:

            ans = self.idPredecessor < num <= self.id
        
        else:
            #el id del predecesor es mayor que mi id
            ans = self.idPredecessor < num <= self.numElements or Bin("0") <= num <= self.id

        ans = str(int(ans))
        self.listen.send(ans.encode())


    def idIsInMySuccesor(self, data):
        """
            recive data with id hex wanted, return 1 if the id is in the succesor interval, else return 0
        """
        ans = None
        num = Bin(data[1].decode())
        
        #print("id:", self.id)
        #print("idSuccessor:", self.idSuccessor)
        #print("numero que busco", num)
        if self.idSuccessor > self.id :
            #print("por el if")
            ans = (self.id < num <= self.idSuccessor)

        else :
            #print("por el else")
            ans = (self.id < num <= self.numElements or Bin("0") <= num <= self.idSuccessor) # convertir esto como un string hexadecimal

        ans = str(int(ans))
        self.listen.send(ans.encode())

    def getSuccessor(self, data):

        self.listen.send_multipart([self.IPNext.encode(),self.portNext.encode()])
        #cuando exista finger table hay que hacer un get succesor para cliente como para 
        #servidor, este sera el del servidor

    def bootstrap(self):

        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send_multipart([b"updatePredecessor", self.id.getHex().encode()])

        data = self.listen.recv_multipart()
        self.operation[data[0].decode()](data)

        self.idSuccessor = Bin(self.idPredecessor.getHex())
        
        self.next.recv()

    def updatePredecessor(self, data):
        """the predecessor tell me who is him, his id"""
        
        self.idPredecessor = Bin(data[1].decode())
        print("New Predecessor :", self.idPredecessor)
        self.listen.send(b"OK")
        

    def find(self):

        """find the ip and port of the server that contain my id, i am his new predeccessor"""
        while True:

            ip_port = tcp + self.IPNext + ":" + self.portNext
            print("Search ubication in:", ip_port)

            self.next.connect(ip_port)

            self.next.send_multipart([b"idIsInMySuccesor", self.id.getHex().encode()])#my id is in the next of my next
            ifind = int(self.next.recv().decode())

            self.next.send_multipart([b"getSuccessor"])#i get the ip of the next
            res = self.next.recv_multipart()
                    
            if ifind:
                
                #print(res)
                return (res[0].decode() , res[1].decode())#ip_port for my ubication

            else:
                print("Move to:", res[0].decode() + ":" + res[1].decode())
                self.IPNext = res[0].decode()
                self.portNext = res[1].decode()
                self.next.disconnect(ip_port)

    def getServerID(self, data):
        """return the id server"""

        self.listen.send(self.id.getHex().encode())

    def changeTheSuccessorInformation(self, data):
        
        ip = data[1].decode()
        port = data[2].decode()
        ids = data[3].decode()

        self.next.disconnect(tcp + self.IPNext + ":" + self.portNext)
        self.IPNext = ip
        self.portNext = port
        self.idSuccessor = Bin(ids)
        self.next.connect(tcp + self.IPNext + ":" + self.portNext)

        self.listen.send(b'Se actualiza successor')

    def addServerToChord(self):
        """Add in the middel to two server in the chord
            TODO 
            send all files in the new successor server and me    
        """
        #init the socket listen, that is in the __init__


        ipNewSuccessor, portNewSuccessor = self.find()
        #send to my predecessor my ip, port and id
        self.next.send_multipart([b'changeTheSuccessorInformation', self.IPListen.encode(), self.portListen.encode(), self.id.getHex().encode()])
        print(self.next.recv().decode())

        #get id of my predeccessor
        self.next.send_multipart([b'getServerID'])
        idp = self.next.recv().decode()
        self.next.disconnect(tcp + self.IPNext + ":" + self.portNext)
        print("id new predeccessor:", idp)
        self.idPredecessor = Bin(idp)

        #connect to my successor
        self.IPNext = ipNewSuccessor
        self.portNext = portNewSuccessor
        print("my successor is:", tcp + self.IPNext + ":" + self.portNext)
        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send_multipart([b'getServerID'])
        ids = self.next.recv().decode()
        self.idSuccessor = Bin(ids)

        #tell to successor the id of his new predecessor
        self.next.send_multipart([b"updatePredecessor", self.id.getHex().encode()])
        print("update successor id",self.next.recv())

        #tell to succesor thah send me my files


        #tell to all servers to update the finger table



    def upload(self, data):
        """data = [operation, sha, bytestosave] """

        shaname = data[1].decode()
        path = self.folder.getpath(shaname)
        print("save into server:", path)
        with open(path, "ab") as f:
            f.write(data[2])

        msj = "Chunk saved in " + self.id.getHex()
        self.listen.send(msj.encode())

    def download(self, data):
        """data = [operation, sha] """
        
        shaname = data[1].decode()
        path = self.folder.getpath(shaname)
        print("send form server:", path)

        with open(path, "rb") as f:
            byte = f.read()
            self.listen.send(byte)


    

    def run(self):

        print("Server is running")
        while True:

            msj = self.listen.recv_multipart()
            print(msj)
            self.operation[msj[0].decode()](msj)

bs = False
try:
    bs = int(sys.argv[6])
except:
    pass


"""
argv[1] -> id:
argv[2] -> ipListen:
argv[3] -> portListen:
argv[4] -> ipNext:
argv[5] -> portNext:
argv[6] -> bootstrap: values 1 o 0// opcional
"""
server = Server(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], bs, k = 4)