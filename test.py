class s:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3

    def set(self, m):
        self.a = 11
        self.b = 12
        self.c = m

class s1(s):
    def __init__(self):
        super().__init__()
        self.d = 4
        self.e = 5
        print(self.a, self.b, self.c, self.d, self.e)
    def set(self):
        super().set(self, 5)
        self.d = 14
        self.e = 15
        print(self.a, self.b, self.c, self.d, self.e)

s = s1()
s.set()