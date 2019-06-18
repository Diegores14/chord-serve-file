import sys
import json
import zmq
import hashlib
import random

from folder import Folder

tcp = "tcp://"
class Client:

    ctx = zmq.Context()
    server = ctx.socket(zmq.REQ)
    
    def __init__(self,ipServer, portServer):
        self.route = {"server": self.server, "submit": self.submit, "download": self.download,
                        "help": self.help, "-h" : self.help}

        self.ipServer = ipServer
        self.portServer = portServer


        self.folderUpload = Folder(basename= 'upload')
        self.folderDownload = Folder(basename= 'download')
        self.folderJson = Folder(basename= 'jsons')

        self.chunck = 1204*1024*10 #10 MB

        self.server.connect(tcp + self.ipServer + ":" + self.portServer)

    def find(self, filesha):

        """find the ip and port of the server that contain my id, i am his new predeccessor"""
        while True:

            ip_port = tcp + self.ipServer + ":" + self.portServer
            print("Search ubication in:", ip_port)

            #self.server.connect(ip_port)

            self.server.send_multipart([b"idIsInMyInterval", filesha.encode()])#my id is in the next of my next
            ifind = int(self.server.recv().decode())# 1 or 0

            
                    
            if ifind:
                
                #print(res)
                #return (res[0].decode() , res[1].decode())#ip_port for my ubication
                print("ubication:", self.ipServer, self.portServer)
                return

            else:

                self.server.send_multipart([b"getSuccessor"])#i get the ip of the next
                res = self.server.recv_multipart()
                print("Move to:", res[0].decode() + ":" + res[1].decode())
                self.ipServer = res[0].decode()
                self.portServer = res[1].decode()

                self.server.disconnect(ip_port)

                ip_port = tcp + self.ipServer + ":" + self.portServer
                self.server.connect(ip_port)


    def submit(self, dir, sha, pos):

        self.find(sha) # i am in the server for submmit this

        #question to server if he has the file and look what to do
        msjToExist = [b'existsFileNow', sha.encode()]
        self.server.send_multipart(msjToExist)
        resToExist = self.server.recv().decode()
        resToExist = int(resToExist) # 1 or 0

        if resToExist:

            print("The part of file is in the chord, i dont send that")
        
        else:

            print("sending part",pos,"from",dir)
            path = self.folderUpload.getpath(dir)
            with open(path, "rb") as f:

                f.seek(pos * self.chunck)
                byte = f.read(self.chunck)
                data = [b'upload',sha.encode(), byte]
                self.server.send_multipart(data)
                res = self.server.recv()
                print(res.decode())



    def submitFile(self,dir):
        
        distribution = self.makeSHAFile(dir)
        trozos = distribution['trozos']

        for i in range(len(trozos)):

            self.submit(dir,trozos[i], i)

    def download(self, dir, sha):

        self.find(sha) # i am in the server for download this

        #question to server if he has the file and look what to do
        msjToExist = [b'existsFileNow', sha.encode()]
        self.server.send_multipart(msjToExist)
        resToExist = self.server.recv().decode()
        resToExist = int(resToExist) # 1 or 0

        if resToExist:

            print("receving file ",dir ,"from server ")
            msj = [b'download', sha.encode()]
            self.server.send_multipart(msj)
            byte = self.server.recv()
            path = self.folderDownload.getpath(dir)
            with open(path , "ab") as f:

                f.write(byte)

        else:
            print("No se pudo descargar una parte, el server,", self.ipServer + ":" +self.portServer, "no tiene la parte")

    def downloadFile(self,dirjson):

        fileDistribution = {}
        pathjson = self.folderJson.getpath(dirjson)
        with open(pathjson, "r") as f:
            fileDistribution = json.load(f)
        

        namefile = fileDistribution['name']
        trozos = fileDistribution['trozos']

        for trozo in trozos:
            self.download(namefile, trozo)

        

    def makeSHAFile(self, dir):


        sha1 = hashlib.sha1()
        shas = []

        path = self.folderUpload.getpath(dir)
        with open(path, "rb") as f:
            while True:
                byte = f.read(self.chunck)
                if not byte:
                    break

                sha2 = hashlib.sha1()
                sha2.update(byte)
                shas.append(sha2.hexdigest())

                sha1.update(byte)
        print("cantidad de trozos que genera el archivo para upload: ",len(shas))

        res = {'hashfile' : sha1.hexdigest(),
                'trozos' :shas,
                'name' : dir}
        

        archivochord = dir.split('.')[0] + ".json"
        pathjson = self.folderJson.getpath(archivochord)
        with open(pathjson, "w+") as filejson:
            json.dump(res , filejson , indent= 4)

        return res

    def command(self, data):

        if len(data) == 0:
            print("No tiene parametros, hacer help o -h")

        elif data[0] in self.route :
            self.route[data[0]]( data )

        else :
            print("No está el comando, hacer help o -h")

    def help(self, data):

        print("help, -h,             show commands")
        print("server IP Port,       set the server's IP and Port")
        print("submit Path-File,     submit file to the cloud")
        print("download File")

    def saveServer(self, data):
        
        if len(data) < 3 :
            print("Faltan parametros")

        else :
            with open("dataServer.json", "w+") as f:
                f.write( "{ \"IP\" : \"" + sys.argv[1] + "\", \"Port\" : \"" + sys.argv[2] + "\" }" )
            print("Server save successfully.")


x = Client("127.0.0.1", "3000")
#sys.argv.pop(0)
#x.command(sys.argv)


x.downloadFile("aquaman.json")
#x.submitFile("aquaman.mp4")