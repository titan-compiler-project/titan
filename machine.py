class Machine:
    options = []
    output_options = []
    processed_text = []
    files = []
    parsed_modules = []

    def __init__(self):
        pass

    def set_options(self, options):
        self.options = options

class Function:
    name = ""
    params = []
    body = []
    returns = []

    def __init__(self, name, params, body, returns):
        self.name = name
        self.params = params
        self.body = body
        self.returns = returns
