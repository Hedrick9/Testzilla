"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                 HEADER 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Title:       sys_utils.py 
Origin Date: 04/02/2025
Revised:     04/02/2025
Author(s):   Russell Hedrick
Contact:     rhedrick@frontierenergy.com
Description:

The following script is designed to handle all system related tasks such as, 
preventing the system from sleeping.

"""
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                               Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import ctypes


# Flags for SetThreadExecutionState:
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001
def prevent_sleep():
    """
    Prevents the system from sleeping, but allows the display to sleep.
    """
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            )

def allow_sleep():
    """
    Reverts to the default behavior allowing the system to sleep again.
    """
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS
    )
