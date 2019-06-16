import zmq
import sys

from bin import Bin


tcp = "tcp://"

class Server:

    context = zmq.Context()
    listen = context.socket(zmq.REP)
    next = context.socket(zmq.REQ)

    def __init__(self, id, IPListen, portListen, IPNext, portNext, bootstrap, k = 156):

        self.IPListen = IPListen
        self.portListen = portListen
        self.IPNext = IPNext
        self.portNext = portNext
        self.k = k

        self.numElements = Bin(hex((2**k)-1)[2:])

        self.id = Bin(id)#aca va entrar la mac, debe crear una funcion que cuadre la mac como sha1
        
        self.listen.bind(tcp + self.IPListen + ":" + self.portListen)
        self.idPredecessor = None
        self.idSuccessor = None

        self.operation = {"updatePredecessor": self.updatePredecessor, 
                            "idIsInMySuccesor": self.idIsInMySuccesor,
                            "idIsInMyInterval": self.idIsInMyInterval,
                            "getSuccessor": self.getSuccessor}

        print("Server IP:", self.IPListen + ":" + self.portListen)

        if bootstrap:

            self.bootstrap()
            self.run()
        else :
            
            self.find()


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

    def updateSucessor(self, data):
        """one server tell me who is him, his id is my new successor"""
        pass

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
                
                return (res[0].decode() , res[1].decode())

            else:
                print("Move to:", res[0].decode() + ":" + res[1].decode())
                self.IPNext = res[0].decode()
                self.portNext = res[1].decode()
                self.next.disconnect(ip_port)
                
            
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