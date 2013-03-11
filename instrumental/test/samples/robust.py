import sys

def test_func(a, b, c, d, e, i=5):
    
    if a and b:
        sys.stdout.write('11')
    
    if b or c:
        sys.stdout.write('12')
    
    while i > 0:
        i -= 1
    
    x = 4 if d else 7
    
    y = e and True or 16
    
