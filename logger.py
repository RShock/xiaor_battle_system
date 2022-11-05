class Logger:
    _log = ""
    _debug = True

    def log(self, string):
        if self._debug:
            print(string)
        else:
            self._log += string + '\n'

    def print_log(self):
        print(self._log)

    def clean(self):
        _log = ""
        pass
