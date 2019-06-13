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
        self.numElements = 2**k
        self.id = id
        self.listen.bind(tcp + self.IPListen + ":" + self.portListen)
        self.idPredecessor = None
        self.idSuccessor = None
        self.operation = {"updatePredecessor": self.updatePredecessor, 
                            "idIsInMySuccesor": self.idIsInMySuccesor}

        print("Server IP:", self.IPListen + ":" + self.portListen)

        if bootstrap:

            self.bootstrap()
        else :
            
            self.find()
        self.run()

    def idIsInMySuccesor(self, data):
        
        ans = None
        num = data[1].decode()
        if self.idSuccessor > self.id :
            ans = (self.id < num <= self.idSuccessor)
        else :
            ans = (self.id < num < str(self.numElements)) and ("0" <= num <= self.idSuccessor) # convertir esto como un string hexadecimal
        ans = str(int(ans))
        self.listen.send(ans.encode())

    def find(self):

        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send_multipart([b"idIsInMySuccesor", self.id.encode()])
        print("idIsInMySuccesor:", self.next.recv().decode())

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
server = Server(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], bs, k = 3)