import sys
import json


class client:
    
    def __init__(self):
        self.route = {"server": self.server, "submit": self.submit, "download": self.download,
                        "help": self.help, "-h" : self.help}

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

    def server(self, data):
        
        if len(data) < 3 :
            print("Faltan parametros")

        else :
            with open("dataServer.json", "w+") as f:
                f.write( "{ \"IP\" : \"" + sys.argv[1] + "\", \"Port\" : \"" + sys.argv[2] + "\" }" )
            print("Server save successfully.")
    
    def submit(self):
        pass

    def download(self):
        pass

x = client()
sys.argv.pop(0)
x.command(sys.argv)