import winapputil

"""
Test methods without debugging
"""

myutil = winapputil.WinAppUtil()

# This should print system info
print "Printing system information"
print myutil.sysinfo()

print winapputil.get_line()

# This should print all running processes
print "Printing tunning processes"
print myutil.get_processes()

print winapputil.get_line()

# Convert some random number to hex
print "This should be 499602d2"
print winapputil.to_hex(1234567890)
