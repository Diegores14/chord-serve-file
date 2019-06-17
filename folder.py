import os


class Folder:

    def __init__(self, basename = 'archivos', id = ''):

        self.path = os.getcwd() + "/" + basename + id
        try:
            os.mkdir(self.path)
        except OSError:
            print("Creación de carpeta fallida posiblemente ya existe: ", self.path)

    def getpath(self, file = ''):

        return self.path + '/' + file


if __name__ == "__main__":
    
    f = Folder(id = '1')
    g = Folder(id = '2')
    h = Folder(id = '1')
    i = Folder(id = '2')


    print(f.getpath())
    print(g.getpath())
