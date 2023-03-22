import logging
from cocotb.triggers import RisingEdge, FallingEdge, Timer

class uartModel:
    def __init__(self,baudrate=9600,stopbits=1,parity="none",rx_in=0,width=8):
        self.baudrate = baudrate
        self.stopbits = stopbits
        self.parity = parity
        self.rx = rx_in
        self.width = width
        self.bitcount = 0
        self.rxBuff = 0
        self.rx_queue = []
        self.bit_time = Timer(int(1e9/self.baudrate), 'ns')
        self.half_bit_time = Timer(int(1e9/self.baudrate), 'ns')

    async def updateRxBuff(self):
        while True:
            await FallingEdge(self.rx)
            await self.half_bit_time
            assert self.rx.value.integer == 0, "spurious start bit, rx line not 0 after half bit time following a start"
            while True:
                await self.bit_time
                if(self.bitcount == self.width):
                    self.rx_queue.append(self.rxBuff)
                    self.bitcount = 0
                    self.rxBuff = 0
                    break
                else:
                    self.bitcount = self.bitcount + 1
                self.rxBuff = self.rxBuff<<1 & self.rx.value.integer
            await self.bit_time
            assert self.rx.value.integer == 1, "error in stop it"
            if(self.stopbits == 2):
                await self.bit_time
                assert self.rx.value.integer == 1, "error in stop it"
            

