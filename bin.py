

class Bin:

    def __init__(self, hexa):
        """
            Recibe string de un numero  HEXADECIMAL


            parametros

            self.binary -> String de 1,0
            self.n -> tamaño del string
        """
        self.binary = self.create(hexa)
        self.n = len(self.binary)

    def create(self, hexa):

        ans = ""
        for x in hexa:
            ans = ans + (bin( int( x, 16) )[2:].zfill(4))
        return ans

    def sumKBit(self, k):

        ans = self.binary
        i = self.n-k-1

        while i >= 0 and ans[i] == '1' :
            ans = ans[0:i] + '0' + ans[i+1:]
            i -= 1

        if i >= 0 :
            ans = ans[0:i] + '1' + ans[i+1:]
            
        return ans

    def getBinary(self):

        return self.binary

    def getHex(self):

        return hex(int(self.binary, 2)).upper()[2:]
    

    #definicio de metodos magicos para usarlo en todo lado sin problema
    def __lt__(self,other):
        
        return self.getBinary() < other.getBinary()
    
    def __le__(self, other):

        return self.getBinary() <= other.getBinary()

    def __eq__(self, other):

        return self.getBinary() == other.getBinary()

    def __gt__(self, other):

        return self.getBinary() > other.getBinary()
    
    def __ge__(self, other):

        return self.getBinary() >= other.getBinary()


# testing
x = Bin("0FF")
y = Bin("00F")
print(x.sumKBit(0))
print(y.getHex())
print(x == y)
