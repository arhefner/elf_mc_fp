"""ELF/MC control class using MCP23017."""
from enum import Enum
import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017

OUTPUT = 0

WAIT_N      = (1 << 4)
CLEAR_N     = (1 << 3)
MEM_PROTECT = (1 << 0)
EF4_N       = (1 << 2)
STB_N       = (1 << 1)

MODE = CLEAR_N | WAIT_N

class Elf:
    """Represents the ELF/MC control interface."""

    # pylint: disable=too-many-instance-attributes

    class Mode(Enum):
        """Current machine mode."""
        LOAD = 0x0
        RESET = 0x10
        PAUSE = 0x08
        RUN = 0x18

        def __str__(self):        #pylint: disable=invalid-str-returned
            return self.name

    def __init__(self):
        self._mcp = MCP23017(busio.I2C(board.SCL, board.SDA))

        if self._mcp.iodira != OUTPUT:
            self._mcp.iodira = OUTPUT
            self.data = 0x00
        else:
            self._data = self._mcp.gpioa

        if self._mcp.iodirb != OUTPUT:
            self._mcp.iodirb = OUTPUT
            self.mode = self.Mode.RESET
            self.ef4_n = False
            self.stb_n = False
            self.mem_protect = False
        else:
            state = self._mcp.gpiob
            self._mode = self.Mode(state & MODE)
            self._ef4_n = not state & EF4_N
            self._stb_n = not state & STB_N
            self._mem_protect = bool(state & MEM_PROTECT)

    @property
    def data(self):
        """Output data bus value."""
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._mcp.gpioa = self._data

    @property
    def mode(self):
        """Current machine mode."""
        return self._mode

    @mode.setter
    def mode(self, value):
        if isinstance(value, self.Mode):
            self._mode = value
            self._mcp.gpiob = (self._mcp.gpiob & ~MODE) | value.value

    @property
    def mem_protect(self):
        """Toggle memory protection."""
        return self._mem_protect

    @mem_protect.setter
    def mem_protect(self, value):
        if value:
            self._mem_protect = True
            self._mcp.gpiob |= MEM_PROTECT
        else:
            self._mem_protect = False
            self._mcp.gpiob &= ~MEM_PROTECT

    @property
    def ef4_n(self):
        """State of the EF4_N flag line."""
        return self._ef4_n

    @ef4_n.setter
    def ef4_n(self, value):
        if value:
            self._ef4_n = True
            self._mcp.gpiob &= ~EF4_N
        else:
            self._ef4_n = False
            self._mcp.gpiob |= EF4_N

    @property
    def stb_n(self):
        """State of the keyboard strobe line."""
        return self._stb_n

    @stb_n.setter
    def stb_n(self, value):
        if value:
            self._stb_n = True
            self._mcp.gpiob &= ~STB_N
        else:
            self._stb_n = False
            self._mcp.gpiob |= STB_N
