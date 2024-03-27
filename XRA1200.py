# SPDX-FileCopyrightText: Copyright (c) 2024 Chris Burton
#
# SPDX-License-Identifier: MIT

"""
`XRA1200`
=======

CircuitPython library for MaxLinear XRA1200/XRA1200P enhanced pin and software comptaible versions of the CAT9534/PCA9534 and CAT9554/PCA9554.

* Author(s): Chris Burton

Usage Notes
-----------
Inversion only applies when reading a pin.

"""

try:
    # This is only needed for typing
    from typing import Optional
    import busio
except ImportError:
    pass

from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const
import digitalio

_XRA1200_DEFAULT_I2C_ADDR: int = const(0x20)                # Default I2C address
_XRA1200_REGISTER_INPUT_PORT: int = const(0x00)             # Default XXXX XXXX
_XRA1200_REGISTER_OUTPUT_PORT: int = const(0x01)            # Default 1111 1111 
_XRA1200_REGISTER_INVERSION: int = const(0x02)              # Default 0000 0000 (No inversion)
_XRA1200_REGISTER_CONFIGURATION: int = const(0x03)          # Default 1111 1111 (All Inputs)
_XRA1200_REGISTER_PULLUP: int = const(0x04)                 # Default 0000 0000 (XRA1200) / 1111 1111 (XRA1200P)
_XRA1200_REGISTER_INTERRUPT_ENABLE: int = const(0x05)       # Default 0000 0000
_XRA1200_REGISTER_THREE_STATE: int = const(0x06)            # Default 0000 0000
_XRA1200_REGISTER_INTERRUPT_STATUS: int = const(0x07)       # Default 0000 0000
_XRA1200_REGISTER_RISING_EDGE_INTERRUPT: int = const(0x08)  # Default 0000 0000
_XRA1200_REGISTER_FALLING_EDGE_INTERRUPT: int = const(0x09) # Default 0000 0000
_XRA1200_REGISTER_INPUT_FILTER: int = const(0x0A)           # Default 1111 1111

class XRA1200:
    def __init__(self, i2c: I2C, address: int = _XRA1200_DEFAULT_I2C_ADDR, reset: bool = True, p: bool = False) -> None:
        self.i2c_device = I2CDevice(i2c, address)
        self._p = p
        self._output = bytearray([0])
        self._inversion = bytearray([0])
        self._configuration = bytearray([0])
        self._pullup = bytearray([0])
        self._interrupt_enable = bytearray([0])
        self._three_state = bytearray([0])
        self._rising_edge_interrupt = bytearray([0])
        self._falling_edge_interrupt = bytearray([0])
        self._input_filter = bytearray([0])

        if reset:
            # Reset to all inputs, disable inversion, set outputs to 1, etc.
            with self.i2c_device as i2c:
                i2c.write( bytearray([_XRA1200_REGISTER_CONFIGURATION, 0xFF]) )
                i2c.write( bytearray([_XRA1200_REGISTER_INVERSION, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_OUTPUT_PORT, 0xFF]) )
                if p:
                        i2c.write( bytearray([_XRA1200_REGISTER_PULLUP, 0xFF]) )
                else:
                        i2c.write( bytearray([_XRA1200_REGISTER_PULLUP, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_INTERRUPT_ENABLE, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_THREE_STATE, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_INTERRUPT_STATUS, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_RISING_EDGE_INTERRUPT, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_FALLING_EDGE_INTERRUPT, 0x00]) )
                i2c.write( bytearray([_XRA1200_REGISTER_INPUT_FILTER, 0xFF]) )

        with self.i2c_device as i2c:
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_OUTPUT_PORT, ]), self._output )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_INVERSION, ]), self._inversion )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_CONFIGURATION, ]), self._configuration )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_PULLUP, ]), self._pullup )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_INTERRUPT_ENABLE, ]), self._interrupt_enable )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_THREE_STATE, ]), self._three_state )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_RISING_EDGE_INTERRUPT, ]), self._rising_edge_interrupt )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_FALLING_EDGE_INTERRUPT, ]), self._falling_edge_interrupt )
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_INPUT_FILTER, ]), self._input_filter )

    def read_gpio(self) -> int:
        buf = bytearray([0])
        with self.i2c_device as i2c:
            i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_INPUT_PORT, ]), buf )
        return buf[0]

    def write_gpio(self, val: int) -> None:
        self._output[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_OUTPUT_PORT, self._output[0]]) )

    def set_iodir(self, val: int) -> None:
        self._configuration[0] = (val & 0xFF)
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_CONFIGURATION, self._configuration[0]]) )

    def get_iodir(self) -> int:
        return self._configuration[0]

    def get_inv(self) -> int:
        return self._inversion[0]

    def set_inv(self, val: int) -> None: # Inversion only applies to inputs
        self._inversion[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_INVERSION, self._inversion[0]]) )

    def get_pullup(self) -> int:
        return self._pullup[0]

    def set_pullup(self, val: int) -> None:
        self._pullup[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_PULLUP, self._pullup[0]]) )

    def get_interrupt_enable(self) -> int:
	return self._interrupt_enable[0]

    def set_interrupt_enable(self, val: int) -> None:
        self._interrupt_enable[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_INTERRUPT_ENABLE, self._interrupt_enable[0]]) )

    def get_three_state(self) -> int:
        return self._three_state[0]

    def set_three_state(self, val: int) -> None:
        self._three_state[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_THREE_STATE, self._three_state[0]]) )

    def get_interrupt_status(self) -> int:
	buf = bytearray([0])
	with self.i2c_device as i2c:
		i2c.write_then_readinto( bytearray([_XRA1200_REGISTER_INTERRUPT_STATUS, ]), buf )
        return buf[0]

    def get_rising_edge_interrupt(self) -> int:
        return self._rising_edge_interrupt[0]

    def set_rising_edge_interrupt(self, val: int) -> None:
        self._rising_edge_interrupt[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_RISING_EDGE_INTERRUPT, self._rising_edge_interrupt[0]]) )

    def get_falling_edge_interrupt(self) -> int:
        return self._falling_edge_interrupt[0]

    def set_falling_edge_interrupt(self, val: int) -> None:
        self._falling_edge_interrupt[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_FALLING_EDGE_INTERRUPT, self._falling_edge_interrupt[0]]) )

    def get_input_filter(self) -> int:
        return self._input_filter[0]

    def set_input_filter(self, val: int) -> None:
        self._input_filter[0] = val & 0xFF
        with self.i2c_device as i2c:
            i2c.write( bytearray([_XRA1200_REGISTER_INPUT_FILTER, self._input_filter[0]]) )

    def get_pin(self, pin: int) -> "DigitalInOut":
        assert 0<= pin <= 7
        return DigitalInOut(pin, self)

    def write_pin(self, pin: int, val: bool) -> None:
        if val:
            self.write_gpio(self.output | (1<<pin))
        else:
            self.write_gpio(self.output & ~(1<<pin))

    def read_pin(self, pin: int) -> bool:
        return (self.read_gpio() >> pin) & 0x1

class DigitalInOut:
    def __init__(self, pin_number: int, xra: XRA1200) -> None:
        self._pin = pin_number
        self._xra = xra 

    def switch_to_output(self, value: bool = False, **kwargs) -> None:
        if value:
            self._xra.write_gpio( self._xra._output[0] | ( 1<<self._pin ) )
        else:
            self._xra.write_gpio( self._xra._output[0] & ~( 1<<self._pin ) )
        self._xra.set_iodir( ((self._xra._configuration[0] & (1<<self._pin)) >> self._pin) & ~( 1<<self._pin ) )

    def switch_to_input(self, **kwargs) -> None:
        self._xra.set_iodir( ((self._xra._configuration[0] & (1<<self._pin)) >> self._pin) | ( 1<<self._pin ) )

    @property
    def value(self) -> bool:
		return (self._xra.read_gpio() & (1<<self._pin)) > 0

    @value.setter
    def value(self, val: bool) -> None:
        if val:
            self._xra.write_gpio( self._xra._output[0] | ( 1<<self._pin ) )
        else:
            self._xra.write_gpio( self._xra._output[0] & ~( 1<<self._pin ) )

    @property
    def direction(self) -> digitalio.Direction:
        if ((self._xra._configuration[0] & (1<<self._pin)) >> self._pin):
            return digitalio.Direction.INPUT
        else:
            return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self,val: digitalio.Direction) -> None:
        if val == digitalio.Direction.INPUT:
            self._xra.set_iodir( self._xra.get_iodir() | (1<<self._pin) )
        elif val == digitalio.Direction.OUTPUT:
            self._xra.set_iodir( self._xra.get_iodir() & ~(1<<self._pin) )
        else:
            raise ValueError("Expected INPUT or OUTPUT direction!")

    @property
    def invert_polarity(self) -> bool:
        return self._xra._inversion[0] & (1<<self._pin) > 0

    @invert_polarity.setter
    def invert_polarity(self, val: bool) -> None:
        if val:
            self._xra.set_inv( self._xra.get_inv() | (1<<self._pin) )
        else:
            self._xra.set_inv( self._xra.get_inv() & ~(1<<self._pin) )

    @property
    def pullup(self) -> bool:
        return self._xra._pullup[0] & (1<<self._pin) > 0

    @pullup.setter
    def pullup(self, val: bool) -> None:
        if val:
            self._xra.set_pullup( self._xra.get_pullup() | (1<<self._pin) )
        else:
            self._xra.set_pullup( self._xra.get_pullup() & ~(1<<self._pin) )

    @property
    def interrupt_enable(self) -> bool:
        return self._xra.get_interrupt_enable() & (1<<self._pin) > 0

    @interrupt_enable.setter
    def interrupt_enable(self, val: bool) -> none:
        if val:
            self._xra.set_interrupt_enable( self._xra.get_interrupt_enable() | (1<<self._pin) )
        else:
            self._xra.set_interrupt_enable( self._xra.get_interrupt_enable() & ~(1<<self._pin) )

    @property
    def three_state(self) -> bool:
        return self._xra._three_state[0] & (1<<self._pin) > 0

    @three_state.setter
    def three_state(self, val: bool) -> None:
        if val:
            self._xra.set_three_state( self._xra.get_three_state() | (1<<self._pin) )
        else:
            self._xra.set_three_state( self._xra.get_three_state() & ~(1<<self._pin) )

    @property
    def interrupt_status(self) -> bool:
        return self._xra.get_interrupt_status() & (1<<self._pin) > 0

    @property
    def rising_edge_interrupt(self) -> bool:
        return self._xra._rising_edge_interrupt[0] & (1<<self._pin) > 0

    @rising_edge_interrupt.setter
    def rising_edge_interrupt(self, val: bool) -> None:
        if val:
            self._xra.set_rising_edge_interrupt( self._xra.get_rising_edge_interrupt() | (1<<self._pin) )
        else:
            self._xra.set_rising_edge_interrupt( self._xra.get_rising_edge_interrupt() & ~(1<<self._pin) )

    @property
    def falling_edge_interrupt(self) -> bool:
        return self._xra._falling_edge_interrupt[0] & (1<<self._pin) > 0

    @falling_edge_interrupt.setter
    def falling_edge_interrupt(self, val: bool) -> None:
        if val:
            self._xra.set_falling_edge_interrupt( self._xra.get_falling_edge_interrupt() | (1<<self._pin) )
        else:
            self._xra.set_falling_edge_interrupt( self._xra.get_falling_edge_interrupt() & ~(1<<self._pin) )

    @property
    def input_filter(self) -> bool:
        return self._xra._input_filter[0] & (1<<self._pin) > 0

    @input_filter.setter
    def input_filter(self, val: bool) -> None:
        if val:
            self._xra.set_input_filter( self._xra.get_input_filter() | (1<<self._pin) )
        else:
            self._xra.set_input_filter( self._xra.get_input_filter() & ~(1<<self._pin) )
