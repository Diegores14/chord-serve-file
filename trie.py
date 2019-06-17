class trie:

    def __init__(self):

        self.m = {}
        self.isfinish = False
    
    def insert(self, s, idx=0) :

        if idx < len(s) :

            if not s[idx] in self.m :
                self.m[s[idx]] = trie()
            self.m[s[idx]].insert(s, idx+1)

        else :

            self.isfinish = True
    
    def search(self, s, idx=0) :

        if idx == len(s) :

            return self.isfinish

        if not s[idx] in self.m:

            return False
            
        return self.m[s[idx]].search(s, idx+1)

    def listkeys(self, s, idx = 0, acc, l) :
        if idx == len(s) :
            l.append(acc)
            