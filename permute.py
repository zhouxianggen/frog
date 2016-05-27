
import random
from simhash import simhash

class Permute(object):
    def __init__(self, size, count):
        self.size = size
        self.count = count
        self.permutation = []
        ks = set()
        while len(self.permutation) < count:
            a = [i for i in range(size)]
            random.shuffle(a)
            k = '.'.join([str(x) for x in a])
            if k not in ks:
                self.permutation.append(a)
                ks.add(k)

    def permute(self, s):
        for i in range(self.count):
            yield ''.join([s[self.permutation[i][j]] for j in range(self.size)])

N = 128
sh = simhash(sys.argv[1], N)
print sh

p = Permute(size=7, count=4)
for x in p.permute('1234567'):
    print x
