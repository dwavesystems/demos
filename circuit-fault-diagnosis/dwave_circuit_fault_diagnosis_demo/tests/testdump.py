from collections import OrderedDict as o
from re import match as m

r = response
a=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('a[0-9]',k)]
b=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('b[0-9]',k)]
p=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('p[0-9]',k)]

a = int("".join(str(i) for i in a), 2)
b = int("".join(str(i) for i in b), 2)
p = int("".join(str(i) for i in p), 2)

print("a = {}".format(a))
print("b = {}".format(b))
print("p = {} (should be {})".format(p, a * b))

valid = [False] * len(list(r.samples()))
for e, sample in enumerate(r.samples()):
    a = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('a[0-9]', k)]
    b = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('b[0-9]', k)]
    p = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('p[0-9]', k)]

    a = int("".join(str(i) for i in a), 2)
    b = int("".join(str(i) for i in b), 2)
    p = int("".join(str(i) for i in p), 2)

    if a * b == p:
        valid[e] = True
