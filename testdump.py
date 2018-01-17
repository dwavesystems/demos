from collections import OrderedDict as o
from re import match as m

r = response
a=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('a[0-9]',k)]
b=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('b[0-9]',k)]
p=[v if v==1 else 0 for (k,v) in o(sorted({str(k):v for (k,v) in next(r.samples()).items()}.items(),reverse=True)).items() if m('p[0-9]',k)]

print(int("".join(str(i) for i in a), 2))
print(int("".join(str(i) for i in b), 2))
print(int("".join(str(i) for i in p), 2))


for sample in r.samples():
    a = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('a[0-9]', k)]
    b = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('b[0-9]', k)]
    p = [v if v == 1 else 0 for (k, v) in o(sorted({str(k): v for (k, v) in sample.items()}.items(), reverse=True)).items() if m('p[0-9]', k)]

    print("a = %i" % int("".join(str(i) for i in a), 2))
    print("b = %i" % int("".join(str(i) for i in b), 2))
    print("p = %i (should be %i)" % (int("".join(str(i) for i in p), 2), int(
        "".join(str(i) for i in a), 2) * int("".join(str(i) for i in b), 2)))
    print()

