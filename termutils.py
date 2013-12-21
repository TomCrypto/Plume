# From https://gist.github.com/jtriley/1108174

""" getTerminalSize()
 - get width and height of console
 - works on linux,os x,windows,cygwin(windows)
"""

try:
    # required linux imports
    import array
    import fcntl
    import os
    import struct
    import termios
except ImportError:
    pass

__all__=['getTerminalSize']


def getTerminalSize():
   import platform
   current_os = platform.system()
   tuple_xy=None
   if current_os == 'Windows':
       tuple_xy = _getTerminalSize_windows()
       if tuple_xy is None:
          tuple_xy = _getTerminalSize_tput()
          # needed for window's python in cygwin's xterm!
   if current_os == 'Linux' or current_os == 'Darwin' or  current_os.startswith('CYGWIN'):
       tuple_xy = _getTerminalSize_linux()
   if tuple_xy is None:
       print("default")
       tuple_xy = (80, 25)      # default value
   return tuple_xy

def _getTerminalSize_windows():
    res=None
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12

        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
    except:
        return None
    if res:
        import struct
        (bufx, bufy, curx, cury, wattr,
         left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
        sizex = right - left + 1
        sizey = bottom - top + 1
        return sizex, sizey
    else:
        return None

def _getTerminalSize_tput():
    # get terminal width
    # src: http://stackoverflow.com/questions/263890/how-do-i-find-the-width-height-of-a-terminal-window
    try:
       import subprocess
       proc=subprocess.Popen(["tput", "cols"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       cols=int(output[0])
       proc=subprocess.Popen(["tput", "lines"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
       output=proc.communicate(input=None)
       rows=int(output[0])
       return (cols,rows)
    except:
       return None


class LinuxTerminalSize(object):
    """
    A class of static methods for determining the size of the terminal window
    linux.
    """

    @staticmethod
    def use_termios():
        """
        Tries to determine the size of the terminal window using the standard
        streaming objects. If successful, a tuple containing the size of the
        window (rows, cols) is returned. Otherwise, returns None.

        """
        return LinuxTerminalSize._ioctl_GWINSZ(sys.stdin.fileno()) or \
               LinuxTerminalSize._ioctl_GWINSZ(sys.stdout.fileno()) or \
               LinuxTerminalSize._ioctl_GWINSZ(sys.stderr.fileno())

    @staticmethod
    def use_termid():
        """
        Tries to determine the size of the terminal window using the file
        associated with the controlling process. If successful, a tuple
        containing the size of the window (rows, cols) is returned. Otherwise,
        returns None.

        """
        try:
            with open(os.ctermid()) as fd:
                return LinuxTerminalSize._ioctl_GWINSZ(fd)
        except:
            pass

        return None

    @staticmethod
    def use_environment():
        """
        Tries to determine the size of the terminal window using the
        environmental variables LINES and COLUMNS. If these variables are not in
        the environment, their defaults are returned instead (24 for LINES and
        80 for COLUMNS).

        """
        return (os.environ.get('LINES', 24), os.environ.get('COLUMNS', 80))

    @staticmethod
    def _ioctl_GWINSZ(fd):
        """
        A utility function that is used to determine the window size using the
        provided file descriptor. If the query succeeds a tuple containing the
        number of rows and columns in the window is returned. Otherwise, None is
        returned.

        """
        try:
            # create a buffer array containing two short integers
            buf = array.array('h', [0,0])
            if fcntl.ioctl(fd, termios.TIOCGWINSZ, buf, 1) == 0:
                return tuple(buf)
        except:
            pass

        return None


def _getTerminalSize_linux():
    rows, cols = LinuxTerminalSize.use_termios() or \
                LinuxTerminalSize.use_termid() or \
                LniuxTerminalSize.use_environment()

    return int(cols), int(rows)

if __name__ == "__main__":
    sizex, sizey = getTerminalSize()
    print('width =', sizex, 'height =', sizey)
