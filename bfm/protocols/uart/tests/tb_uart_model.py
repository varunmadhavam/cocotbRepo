# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb.types import LogicArray, Range
from cocotb.queue import Queue
import random

import sys
sys.path.append('/home/varun/coding/projects/cocotbRepo/bfm/protocols/uart/model')
from uart_model import uartModel

def check_parity(self,parity_bit):
        onecount = 0
        for i in range(self.width):
            if(self.rxBuff[i]==1):
                onecount = onecount + 1
        if(parity_bit == 1):
            onecount = onecount + 1
        if(self.parity == "even"):
            assert onecount%2 == 0 , "check for even parity failed(tb)"
        elif(self.parity == "odd"):
            assert onecount%2 == 1 , "check for odd parity failed(tb)"
        else:
            assert 1 == 0, "unsupported parity(tb)"

txqueue = Queue()
async def recive_uart(tx,bit_time,half_bit_time,len,parity,stopbits):
    bitcount = 0
    txBuff = 0
    while True:
        await FallingEdge(tx)
        await half_bit_time
        assert tx.value.integer == 0, "spurious start bit, rx line not 0 after half bit time following a start(tb)"
        while True:
            if(bitcount == len):
                txqueue.put_nowait(txBuff)
                bitcount = 0
                txBuff = 0
                break
            await bit_time
            txBuff = txBuff | tx.value.integer << bitcount
            bitcount = bitcount + 1
        await bit_time
        if(parity != "none"):
            check_parity(tx.value.integer)
            await bit_time
        assert tx.value.integer == 1, "error in stop bit(tb)"
        if(stopbits == 2):
            await bit_time
            assert tx.value.integer == 1, "error in second stop bit(tb)"

async def send_a_byte(byte,len,rx,bit_time):
    rx.value = 0
    await bit_time
    for i in range(len):
        rx.value = int(byte[i])
        await bit_time
    rx.value = 1
    await bit_time

@cocotb.test()
async def _test_normal(dut):
    dut.rx.value = 1
    dut.tx.value = 1
    len = 8
    baudrate = 9600
    stopbits = 1
    parity = "none"
    bit_time = Timer(int(1e9/baudrate), 'ns')
    half_bit_time = Timer(int(1e9/baudrate/2), 'ns')
    uart = uartModel(dut.rx,dut.tx,baudrate)
    rx=cocotb.start_soon(uart.updateRxBuff())
    tx=cocotb.start_soon(recive_uart(dut.tx,bit_time,half_bit_time,8,"none",1))
    await Timer(1000, units="ns")
    for i in range(100):
        int_data = random.randint(0, 255)
        data = LogicArray(int_data, Range(7, 'downto', 0))
        await send_a_byte(data,len,dut.rx,bit_time)
        await Timer(10, units="ns")
        received = uart.get_rx_queue()
        assert  received == int_data, "data mismatch in bfm recieved = {} expected = {} (tb)".format(hex(received),hex(int_data))
        await uart.updateTxBuff(LogicArray(received, Range(7, 'downto', 0)))
        expected = txqueue.get_nowait()
        assert  received == int_data, "data mismatch in tx recieved = {} expected = {} (tb)".format(hex(received),hex(int_data))
        await Timer(10, units="ns")
    rx.kill()
    tx.kill()

@cocotb.test()
async def _test_start_bit_error(dut):
    dut.rx.value = 1
    len = 8
    baudrate = 9600
    data = LogicArray(0xAA)
    uart = uartModel(dut.rx,9600)
    rx=cocotb.start_soon(uart.updateRxBuff())
    await Timer(1000, units="ns")
    dut.rx.value = 0
    await Timer(1, units="ns")
    dut.rx.value = 1
    await Timer(int(1e9/baudrate)*10, 'ns')
    rx.kill()