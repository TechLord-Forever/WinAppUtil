from winappdbg import EventHandler, Logger
from winappdbg.win32 import *
import winapputil

import argparse

# -------------------
# eventhandler class
# event: https://github.com/MarioVilas/winappdbg/blob/master/winappdbg/event.py
class DebugEvents(EventHandler):

    def create_process(self, event):
        process = event.get_process()
        pid     = event.get_pid() # or process.get_pid()

        logger.log_text("Debugging %d - %s" % (pid, process.get_filename()))

    def exit_process(self, event):
        process = event.get_process()

        logger.log_text("Exit process %d - %s" % (process.get_pid(), process.get_filename()))

    # better hooking
    # http://winappdbg.readthedocs.io/en/latest/Debugging.html#example-9-intercepting-api-calls

    apiHooks = {

        # HINTERNET InternetConnect(
        #   _In_ HINTERNET     hInternet,
        #   _In_ LPCTSTR       lpszServerName,
        #   _In_ INTERNET_PORT nServerPort,
        #   _In_ LPCTSTR       lpszUsername,
        #   _In_ LPCTSTR       lpszPassword,
        #   _In_ DWORD         dwService,
        #   _In_ DWORD         dwFlags,
        #   _In_ DWORD_PTR     dwContext
        # );

        # Hooks for the wininet.dll library - note this is case-sensitive
        'wininet.dll' : [

            # InternetConnectW
            # https://msdn.microsoft.com/en-us/library/windows/desktop/aa384363(v=vs.85).aspx
            ('InternetConnectW', (HANDLE, PVOID, WORD, PVOID, PVOID, DWORD,
                                  DWORD, PVOID)),

        ],
    }

    # Now we can simply define a method for each hooked API.
    # Methods beginning with "pre_" are called when entering the API,
    # and methods beginning with "post_" when returning from the API.

    def pre_InternetConnectW(self, event, ra, hInternet, lpszServerName,
                             nServerPort, lpszUsername, lpszPassword,
                             dwService, dwFlags, dwContext):

        process = event.get_process()
        process.suspend()
        serverName = process.peek_string(lpszServerName, fUnicode=True)

        logger.log_text("server name: %s" % (serverName))

        process.resume()

# -------------------

"""
debug an app with parameters passed by -r
e.g. python 02-debug2.py -r c:\windows\system32\notepad.exe c:\somerandomtextfile.txt
print system info with -i or --sysinfo
print current processes if nothing is passed
attach to a process with --attach-process or -pid
attach to a process using name with -pname or --attach-process-name
optional logfile name -o or --output
"""


def main():
    parser = argparse.ArgumentParser(description="WinAppDbg stuff.")
    # Make -r, -pid and -pname mutually exclusive
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--run", nargs="+",
                       help="path to instrumented application followed by parameters")
    group.add_argument("-pid", "--attach-process", type=int, dest="pid",
                       help="pid of process to attach and instrument")
    group.add_argument("-pname", "--attach-process-name", dest="pname",
                       help="pid of process to attach and instrument")

    parser.add_argument("-i", "--sysinfo", action="store_true",
                        help="print system information")

    # Add optional log file
    parser.add_argument("-o", "--output", dest="output", help="log filename")

    # Parse arguments
    args = parser.parse_args()

    # -------------------
    # Setup logging
    # https://github.com/MarioVilas/winappdbg/blob/master/winappdbg/textio.py#L1766

    global logger
    # log to file
    if args.output:
        # verbose=False disables print to stdout
        logger = Logger(args.output, verbose=False)
    else:
        logger = Logger()

    # Create eventhandler
    myeventhandler = DebugEvents()

    if args.run:
        try:
            myutil = winapputil.WinAppUtil(cmd=args.run,
                                           eventhandler=myeventhandler,
                                           logger=logger)

            debug = myutil.debug()

            debug.loop()

        except winapputil.DebugError as error:
            logger.log_text("Exception in %s: %s" %
                            (error.pid_pname, error.msg))

        except KeyboardInterrupt:

            debug.stop()
            logger.log_text("Killed process")

    elif args.pid:
        try:
            myutil = winapputil.WinAppUtil(pid_pname=args.pid, logger=logger,
                                           eventhandler=myeventhandler,
                                           attach=True)
            debug = myutil.debug()

            debug.loop()

        except winapputil.DebugError as error:
            logger.log_text("Exception in %s: %s" % (error.pid_pname,
                                                     error.msg))

        except KeyboardInterrupt:

            debug.stop()
            logger.log_text("Killed process")

    elif args.pname:
        try:
            myutil = winapputil.WinAppUtil(pid_pname=args.pname, logger=logger,
                                           eventhandler=myeventhandler,
                                           attach=True)
            debug = myutil.debug()

            debug.loop()

        except winapputil.DebugError as error:
            logger.log_text("Exception in %s: %s" % (error.pid_pname,
                                                     error.msg))

        except KeyboardInterrupt:

            debug.stop()
            logger.log_text("Killed process")

    elif args.sysinfo:
        myutil = winapputil.WinAppUtil()
        print (myutil.sysinfo())

    else:
        myutil = winapputil.WinAppUtil()
        print (myutil.get_processes())

    pass


if __name__ == "__main__":
    main()
