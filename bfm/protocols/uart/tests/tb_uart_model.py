# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
import random

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

@cocotb.test()
async def _test(dut):
    dut.rx.value = 1
    await Timer(1000, units="ns")