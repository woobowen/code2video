from manim import *

class DebugCode(Scene):
    def construct(self):
        c = Code(code_string="print('hello')", language="python", background="window")
        print("CHECK: Code attribute?", hasattr(c, 'code'))
        if hasattr(c, 'code'):
             print("CHECK: Code type:", type(c.code))
        else:
             print("CHECK: Code attribute missing!")
             
        # Check indices
        for i, sub in enumerate(c):
             print(f"CHECK: Index {i}: {type(sub)}")