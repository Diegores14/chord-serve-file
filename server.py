import zmq
import sys
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
        self.numElements = (2**k)
        self.id = id
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
        """recive data with id wanted, return 1 if the id is in my interval, else return 0"""
        ans = None
        num = data[1].decode()

        if self.idPredecessor < self.id:

            ans = self.idPredecessor < num <= self.id
        
        else:
            #el id del predecesor es mayor que mi id
            ans = self.idPredecessor < num < str(self.numElements) or "0" <= num <= self.id

        ans = str(int(ans))
        self.listen.send(ans.encode())


    def idIsInMySuccesor(self, data):
        
        ans = None
        num = data[1].decode()
        
        #print("id:", self.id)
        #print("idSuccessor:", self.idSuccessor)
        #print("numero que busco", num)
        if self.idSuccessor > self.id :
            #print("por el if")
            ans = (self.id < num <= self.idSuccessor)

        else :
            #print("por el else")
            ans = (self.id < num < str(self.numElements)) or ("0" <= num <= self.idSuccessor) # convertir esto como un string hexadecimal

        ans = str(int(ans))
        self.listen.send(ans.encode())

    def getSuccessor(self, data):

        self.listen.send_multipart([self.IPNext.encode(),self.portNext.encode()])
        #cuando exista finger table hay que hacer un get succesor para cliente como para 
        #servidor, este sera el del servidor

    def find(self):

        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send_multipart([b"getSuccessor"])
        print("getSuccessor:", self.next.recv_multipart())

    def bootstrap(self):

        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send_multipart([b"updatePredecessor", self.id.encode()])

        data = self.listen.recv_multipart()
        self.operation[data[0].decode()](data)

        self.idSuccessor = self.idPredecessor
        self.next.recv()

    def updatePredecessor(self, data):

        self.idPredecessor = data[1].decode()
        print("New Predecessor :", self.idPredecessor)
        self.listen.send(b"OK")

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

argv[1] -> ipListen:
argv[2] -> portListen:
argv[3] -> ipNext:
argv[4] -> portNext:
argv[5] -> bootstrap: values 1 o 0

"""
server = Server(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], bs, k = 3)