__author__ = 'witlox'


class Task:

    tasks = []

    def __init__(self, label):
        self.label = label
        self.input = None
        self.executable = None
        self.parameters = None
        self.output = None

    def __str__(self):
        return self.label
