import unittest

class Thing(unittest.TestCase):
    def setUp(self):
        print("setup")

    def testFoo(self):
        print("Foo")
