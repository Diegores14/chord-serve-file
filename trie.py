class Trie:

    def __init__(self):

        self.m = {}
        self.isfinish = False
    
    def insert(self, s, idx=0) :

        if idx < len(s) :

            if not s[idx] in self.m :
                self.m[s[idx]] = Trie()
            self.m[s[idx]].insert(s, idx+1)

        else :

            self.isfinish = True
    
    def search(self, s, idx=0) :

        if idx == len(s) :

            return self.isfinish

        if not s[idx] in self.m:

            return False
            
        return self.m[s[idx]].search(s, idx+1)

    def listkeys(self, key1, key, l, flag = False, flag1 = False, idx = 0, acc = ""):
        if idx == len(key) :
            l.append(acc)
        else :
            for x in self.m:
                if (x >= key1[idx] or flag1) and (x <= key[idx] or flag):
                    acc += x
                    self.m[x].listkeys(key1, key, l, flag or x != key[idx], flag1 or x != key1[idx], idx+1,  acc)
                    acc = acc[:-1]



if __name__ == "__main__":
    
    # test 
    x = Trie()
    x.insert("000")
    x.insert("001")
    x.insert("002")
    x.insert("003")
    x.insert("AA0")
    l = []
    # 003 - 000 = 003 - FFF U 000 - 000
    x.listkeys("003", "FFF", l)
    x.listkeys("000", "000", l)
    print(l)