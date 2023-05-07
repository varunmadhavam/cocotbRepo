import logging
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.queue import Queue
from cocotb.utils import get_sim_time, get_time_from_sim_steps

class uartModel:
    def __init__(self,rx_in,tx_out,baudrate=9600,stopbits=1,parity="none",width=8):
        self.baudrate = baudrate
        self.stopbits = stopbits
        self.parity = parity
        self.rx = rx_in
        self.tx = tx_out
        self.width = width
        self.bitcount = 0
        self.rxBuff = 0
        self.queue = Queue()
        self.bit_time = Timer(int(1e9/self.baudrate), 'ns')
        self.half_bit_time = Timer(int(1e9/self.baudrate/2), 'ns')
    
    def set_uart_baud(self,baudrate):
        self.baudrate = baudrate
        self.bit_time = Timer(int(1e9/self.baudrate), 'ns')
        self.half_bit_time = Timer(int(1e9/self.baudrate/2), 'ns')
        
    def check_parity(self,parity_bit):
        onecount = 0
        for i in range(self.width):
            if(self.rxBuff[i]==1):
                onecount = onecount + 1
        if(parity_bit == 1):
            onecount = onecount + 1
        if(self.parity == "even"):
            assert onecount%2 == 0 , "check for even parity failed(bfm)"
        elif(self.parity == "odd"):
            assert onecount%2 == 1 , "check for odd parity failed(bfm)"
        else:
            assert 1 == 0, "unsupported parity(bfm)"
    
    def get_rx_queue(self):
        return self.queue.get_nowait()
    
    def get_sim_time_f(self):
        time_ns = get_time_from_sim_steps(get_sim_time(), "ns")
        sim_time_str = f"{time_ns:6.2f}ns"
        return sim_time_str

    async def updateRxBuff(self):
        while True:
            await FallingEdge(self.rx)
            await self.half_bit_time
            assert self.rx.value.integer == 0, "spurious start bit, rx line not 0 after half bit time following a start(bfm) @ {}".format(self.get_sim_time_f())
            while True:
                if(self.bitcount == self.width):
                    self.queue.put_nowait(self.rxBuff)
                    self.bitcount = 0
                    self.rxBuff = 0
                    break
                await self.bit_time
                self.rxBuff = self.rxBuff | self.rx.value.integer << self.bitcount
                self.bitcount = self.bitcount + 1
            await self.bit_time
            if(self.parity != "none"):
               self.check_parity(self.rx.value.integer)
               await self.bit_time
            assert self.rx.value.integer == 1, "error in stop bit(bfm)"
            if(self.stopbits == 2):
                await self.bit_time
                assert self.rx.value.integer == 1, "error in second stop it(bfm)"
    
    async def updateTxBuff(self,data):
        self.tx.value = 0
        await self.bit_time
        for i in range(self.width):
            self.tx.value = int(data[i])
            await self.bit_time
        self.tx.value = 1
        await self.bit_time
            

