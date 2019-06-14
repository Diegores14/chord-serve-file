

class Bin:

    def __init__(self, hexa):
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

"""
# testing
x = Bin("7FF")
y = Bin("7FE")
print(x.sumKBit(0))
print(x.getBinary() <= y.getBinary())
"""