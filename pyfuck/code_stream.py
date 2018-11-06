class code_stream:
    def __init__(self):
        self.code = ''

    def add(self, code):
        self.code += code

    def __str__(self):
        return self.code
