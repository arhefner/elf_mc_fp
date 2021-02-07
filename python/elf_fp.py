#!/usr/bin/env python3
"""ELF/MC front panel program"""
from enum import Enum, auto
import sys
import time
import keyboard
import elf

class Mode(Enum):
    """Current control mode."""
    CONTROL = auto()
    KEYBOARD = auto()

CARD = elf.Elf()

if sys.platform == 'win32':
    import msvcrt   # pylint: disable=import-error
    getch = msvcrt.getch
    getche = msvcrt.getche
else:
    import termios  # pylint: disable=import-error
    def __gen_ch_getter(echo):
        def __fun():
            fdesc = sys.stdin.fileno()
            oldattr = termios.tcgetattr(fdesc)
            newattr = oldattr[:]
            try:
                if echo:
                    # disable ctrl character printing, otherwise, backspace will be printed as "^?"
                    lflag = ~(termios.ICANON | termios.ECHOCTL)
                else:
                    lflag = ~(termios.ICANON | termios.ECHO)
                newattr[3] &= lflag
                termios.tcsetattr(fdesc, termios.TCSADRAIN, newattr)
                char = sys.stdin.read(1)
                if echo and ord(char) == 127: # backspace
                    # emulate backspace erasing
                    # https://stackoverflow.com/a/47962872/404271
                    sys.stdout.write('\b \b')
            finally:
                termios.tcsetattr(fdesc, termios.TCSADRAIN, oldattr)
            return char
        return __fun
    getch = __gen_ch_getter(False)
    getche = __gen_ch_getter(True)

def update_status(mode):
    """Update status display line."""
    print(f'\rMode: {"KEYBD" if mode == Mode.KEYBOARD else CARD.mode:5} '
        f'Mem Protect: {"ON" if CARD.mem_protect else "OFF":3} '
        f'Data: {CARD.data:02X}', end='')

def press_input():
    """Press the input key on the computer."""
    CARD.ef4_n = True
    time.sleep(0.005)
    CARD.ef4_n = False

def load_program(bin_file):
    """Load the contents of a binary file."""
    with open(bin_file, 'rb') as file:
        byte = file.read(1)
        while byte:
            CARD.data = byte[0]
            press_input()
            byte = file.read(1)

def load_monitor():
    """Load the MAX monitor and BIOS."""
    CARD.mode = CARD.Mode.RESET
    CARD.mode = CARD.Mode.LOAD
    CARD.mem_protect = False
    load_program('bootstrap.bin')
    CARD.mode = CARD.Mode.RESET
    CARD.mode = CARD.Mode.RUN
    CARD.data = 0x80
    press_input()
    CARD.data = 0x00
    press_input()
    load_program('max_mon.bin')
    CARD.mode = CARD.Mode.RESET
    CARD.mode = CARD.Mode.RUN
    CARD.data = 0x84
    press_input()
    CARD.data = 0x00
    press_input()
    load_program('max_bios.bin')
    CARD.mode = CARD.Mode.RESET

def run_monitor():
    """Reset the machine and run the monitor."""
    CARD.mode = CARD.Mode.RESET
    CARD.mode = CARD.Mode.LOAD
    CARD.data = 0xC0
    press_input()
    CARD.data = 0x80
    press_input()
    CARD.data = 0x00
    press_input()
    CARD.mode = CARD.Mode.RESET
    CARD.mode = CARD.Mode.RUN

def on_key(key):    #pylint: disable=too-many-branches
    """Callback for when a keyboard key is pressed."""
    if key in ('i', '\n', ' '):
        CARD.ef4_n = True
    elif key == '0':
        CARD.data = (CARD.data << 4 | 0x0) & 0xff
    elif key == '1':
        CARD.data = (CARD.data << 4 | 0x1) & 0xff
    elif key == '2':
        CARD.data = (CARD.data << 4 | 0x2) & 0xff
    elif key == '3':
        CARD.data = (CARD.data << 4 | 0x3) & 0xff
    elif key == '4':
        CARD.data = (CARD.data << 4 | 0x4) & 0xff
    elif key == '5':
        CARD.data = (CARD.data << 4 | 0x5) & 0xff
    elif key == '6':
        CARD.data = (CARD.data << 4 | 0x6) & 0xff
    elif key == '7':
        CARD.data = (CARD.data << 4 | 0x7) & 0xff
    elif key == '8':
        CARD.data = (CARD.data << 4 | 0x8) & 0xff
    elif key == '9':
        CARD.data = (CARD.data << 4 | 0x9) & 0xff
    elif key == 'a':
        CARD.data = (CARD.data << 4 | 0xA) & 0xff
    elif key == 'b':
        CARD.data = (CARD.data << 4 | 0xB) & 0xff
    elif key == 'c':
        CARD.data = (CARD.data << 4 | 0xC) & 0xff
    elif key == 'd':
        CARD.data = (CARD.data << 4 | 0xD) & 0xff
    elif key == 'e':
        CARD.data = (CARD.data << 4 | 0xE) & 0xff
    elif key == 'f':
        CARD.data = (CARD.data << 4 | 0xF) & 0xff
    elif key == 'l':
        CARD.mode = CARD.Mode.LOAD
    elif key == 'r':
        CARD.mode = CARD.Mode.RESET
    elif key == 'g':
        CARD.mode = CARD.Mode.RUN
    elif key == 'w':
        CARD.mode = CARD.Mode.PAUSE
    elif key == 'p':
        CARD.mem_protect = not CARD.mem_protect
    elif key == 'z':
        load_monitor()
    elif key == 'm':
        run_monitor()

def on_release(_key):
    """Callback when keyboard key is released."""
    CARD.ef4_n = False
    CARD.stb_n = False

def run_card():
    """Set up keyboard callbacks and respond to keys."""
    done = False

    keyboard.on_release_key('i', on_release)
    keyboard.on_release_key('\n', on_release)
    keyboard.on_release_key(' ', on_release)

    mode = Mode.CONTROL

    update_status(mode)

    while not done:
        char = getch().lower()
        if char == 'q':
            done = True
        else:
            if ord(char) == 0:
                if mode == Mode.CONTROL:
                    mode = Mode.KEYBOARD
                else:
                    mode = Mode.CONTROL
            else:
                if mode == Mode.KEYBOARD:
                    CARD.data = ord(char)
                    CARD.stb_n = True
                else:
                    on_key(char)
        update_status(mode)

    print() # Print new line

if __name__ == "__main__":
    run_card()
