# Test 10
class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

g = Greeter("Bob")
g.greet()
