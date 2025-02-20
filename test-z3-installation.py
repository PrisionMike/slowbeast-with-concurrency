try:
    from z3 import *; a,b = Reals('a b')
    print("z3 installed successfully")
except:
    print('z3 installation failed')