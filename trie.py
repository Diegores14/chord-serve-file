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
	x.insert("0")
	x.insert("1")
	x.insert("2")
	x.insert("3")
	x.insert("4")
	x.insert("5")
	x.insert("6")
	x.insert("7")
	x.insert("8")
	x.insert("9")
	x.insert("A")
	x.insert("B")
	x.insert("C")
	x.insert("D")
	x.insert("E")
	x.insert("F")
	
	l = []
	# 003 - 000 = 003 - FFF U 000 - 000
	x.listkeys("9", "F", l)
	x.listkeys("0", "3", l)
	print(l)