class tools:
    def removeFile(fileName):
        if os.path.isfile(fileName):
             os.remove(fileName)
    def restartScript():
        python = sys.executable
             os.execl(python, python, *sys.argv)
