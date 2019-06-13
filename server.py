import zmq
import sys
tcp = "tcp://"

class Server:

    context = zmq.Context()
    listen = context.socket(zmq.REP)
    next = context.socket(zmq.REQ)

    def __init__(self, id, IPListen, portListen, IPNext, portNext, bootstrap = False, k = 156):

        self.IPListen = IPListen
        self.portListen = portListen
        self.IPNext = IPNext
        self.portNext = portNext
        self.k = k
        self.id = id
        self.listen.bind(tcp + self.IPListen + ":" + self.portListen)
        self.idPredecessor = None

        if bootstrap:
            self.bootstrap()

    def bootstrap(self):

        self.next.connect(tcp + self.IPNext + ":" + self.portNext)
        self.next.send(self.id.encode())
        self.idPredecessor = self.listen.recv().decode()
        print(self.idPredecessor)
        self.listen.send(b"OK")
        self.next.recv()

server = Server(sys.argv[1], sys.argv[2], sys.argv[3],
                sys.argv[4], sys.argv[5], True)