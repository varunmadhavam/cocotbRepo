# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb.types import LogicArray, Range
from cocotb.queue import Queue
import random

import sys
sys.path.append('/home/varun/coding/projects/cocotbRepo/bfm/protocols/uart/model')
from uart_model import uartModel

def check_parity(txBuff,parity,width,parity_bit):
        onecount = 0
        txBuffV = LogicArray(txBuff, Range(width-1, 'downto', 0))
        for i in range(width):
            if(txBuffV[i]==1):
                onecount = onecount + 1
        if(parity_bit == 1):
            onecount = onecount + 1
        if(parity == "even"):
            assert onecount%2 == 0 , "check for even parity failed(bfm)"
        elif(parity == "odd"):
            assert onecount%2 == 1 , "check for odd parity failed(bfm)"
        else:
            assert 1 == 0, "unsupported parity(bfm)"

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
            check_parity(txBuff,parity,len,tx.value.integer)
            await bit_time
        assert tx.value.integer == 1, "error in stop bit(tb)"
        if(stopbits == 2):
            await bit_time
            assert tx.value.integer == 1, "error in second stop bit(tb)"

async def send_a_byte(byte,len,rx,bit_time,stopbits,error_stop_b,parity,error_parity):
    rx.value = 0
    pcount = 0
    await bit_time
    for i in range(len):
        rx.value = int(byte[i])
        if(int(byte[i]) == 1):
            pcount = pcount + 1
        await bit_time
    if(parity=="even" and pcount%2 != 0):
        pcount = 1
    elif(parity=="odd" and pcount%2 == 0):
        pcount = 1
    else:
        pcount = 0
    if(parity!="none"):
        if(error_parity==1):
            rx.value = not pcount
        else:
            rx.value = pcount
        await bit_time
    rx.value = 1
    await bit_time
    if(stopbits==2):
        if(error_stop_b==1):
            rx.value = 0
        else:
            rx.value = 1
        await bit_time

@cocotb.test()
async def _test_normal(dut):
    dut.rx.value = 1
    dut.tx.value = 1
    len = 8
    baudrate = 9600
    stopbits = 2
    parity = "even"
    bit_time = Timer(int(1e9/baudrate), 'ns')
    half_bit_time = Timer(int(1e9/baudrate/2), 'ns')
    uart = uartModel(dut.rx,dut.tx,baudrate,stopbits,parity,len)
    rx=cocotb.start_soon(uart.updateRxBuff())
    tx=cocotb.start_soon(recive_uart(dut.tx,bit_time,half_bit_time,8,"none",1))
    await Timer(1000, units="ns")
    for i in range(100):
        int_data = random.randint(0, 255)
        data = LogicArray(int_data, Range(7, 'downto', 0))
        await send_a_byte(data,len,dut.rx,bit_time,stopbits,0,parity,0)
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