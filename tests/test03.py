import winapputil
import winappdbg

log1 = winappdbg.Logger()

try:

    myutil = winapputil.WinAppUtil(cmd=["notepad.exe"],
                                   attach=True, logger=log1)

    mydebug = myutil.debug()

    mydebug.loop()

except winapputil.DebugError as error:
    print error.pid_pname
    print error.msg

except KeyboardInterrupt:
    mydebug.stop()
    print "exiting"
