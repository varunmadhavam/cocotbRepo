# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb.types import LogicArray, Range
import random

import sys
sys.path.append('/home/varun/coding/projects/cocotbRepo/bfm/protocols/uart/model')
from uart_model import uartModel


async def do_reset(dut):
    dut.rst.value = 1
    await Timer(20, units="ns")
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0

async def generate_clock(dut):
    while True:
        dut.clk.value = 0
        await Timer(5, units="ns")
        dut.clk.value = 1
        await Timer(5, units="ns")

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
    len = 8
    baudrate = 9600
    bit_time = Timer(int(1e9/baudrate), 'ns')
    uart = uartModel(dut.rx,9600)
    rx=cocotb.start_soon(uart.updateRxBuff())
    await Timer(1000, units="ns")
    for i in range(100):
        int_data = random.randint(0, 255)
        data = LogicArray(int_data, Range(7, 'downto', 0))
        await send_a_byte(data,len,dut.rx,bit_time)
        await Timer(10, units="ns")
        expected = uart.get_rx_queue()
        assert  expected == int_data, "data mismatch recieved = {} expected = {}".format(expected,int_data)
    rx.kill()

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