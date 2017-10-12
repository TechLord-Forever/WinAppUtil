import winapputil


try:

    myutil = winapputil.WinAppUtil(cmd=["notepad.exe", "c:\log.log"])

    mydebug = myutil.debug()

    mydebug.loop()

except KeyboardInterrupt:
    mydebug.stop()
    print "exiting"
