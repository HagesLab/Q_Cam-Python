# -*- coding: utf-8 -*-
"""
Created on Tue Sep 19 16:40:44 2023

@author: cfai2304
"""
import serial

DEFAULT_BAUDRATE = 9600
DEFAULT_PORT = "COM11"
DEFAULT_TIMEOUT = 10 # ms

class Mono:
    """Control class for a Princeton instruments HRS300 monochromator"""
    
    def __init__(self, port=DEFAULT_PORT):
        self.ser=serial.Serial(port,baudrate=DEFAULT_BAUDRATE,
                               parity=serial.PARITY_NONE,
                               bytesize=serial.EIGHTBITS,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=DEFAULT_TIMEOUT)
        self.clear_ser()
        
    def close(self):
        """Close monochromator connection"""
        self.ser.close()
        
    def clear_ser(self):
        """Clear port buffer"""
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        
    def wait_for_serial(self):
        """ Block until 'ok' received from mono"""
        flagStop = 0
        response = ""
        response = self.ser.read(1).decode()
        while flagStop == 0:
            response += self.ser.read(1).decode()
            if "ok" in response:
                flagStop = 1
        self.clear_ser()
        return response
    
    def get_gratings(self):
        """Get list of installed gratings"""
        self.ser.write("?GRATINGS".encode()+ b"\x0d")
        return self.wait_for_serial()
    
    def set_wavelength(self, w):
        """Move mono to wavelength w, in nm"""
        self.ser.write("{:.3f} GOTO".format(w).encode()+ b"\x0d")
        return self.wait_for_serial()

if __name__ == "__main__":
    m = Mono()
    print(m.get_gratings())
    m.set_wavelength(1000)
    m.set_wavelength(100)
    m.close()
    
    