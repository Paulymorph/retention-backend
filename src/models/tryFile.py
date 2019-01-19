class Try:

    def __init__(self, func, *args):
        try:
            self.result = func(*args)
            self.isSuccess = True
        except Exception as ex:
            self.exception = ex
            self.isSuccess = False
