import sys

print('script running as live app')

status='idlelib' in sys.modules

# Put this segment at the end of code
if status==False:
    input()
