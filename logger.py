class Logger:
    _log = ""
    _debug_log = ""
    _debug = False

    def log(self, string):
        if self._debug:
            print(string)
        else:
            self._log += string + '\n'

    def print_log(self):
        print(self._log)

    def clean(self):
        self._log = ""
        pass

    def get_log(self):
        # print(self._log)
        return self._log

    def debug_log(self, string):
        print(string)