def step(x0:int, x1:int, x2:int, x3:int) -> int:
    w0 = 3
    w1 = 4
    w2 = -1
    w3 = -2
    
    a = ((w0*x0) + (w1*x1)) + ((w2*x2) + (w3*x3))
    r = a if a > 0 else 0
    return r 