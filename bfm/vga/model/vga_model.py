import logging
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.queue import Queue
from cocotb.utils import get_sim_time, get_time_from_sim_steps

class VGA():
    def __init__(self,pixels,lines,dut):
        self.pixels = pixels
        self.lines  = lines
        self.dut = dut
        self.hvisible_area = 0
        self.hfront_porch = 0
        self.hsync_pulse = 0
        self.hback_porch = 0
        self.hwhole = 0
        self.vvisible_area = 0
        self.vfront_porch = 0
        self.vsync_pulse = 0
        self.vback_porch = 0
        self.vwhole = 0

    def get_timing_from_resolution(self):
        if(self.pixels==640 and self.lines==480):
            self.hvisible_area = 640
            self.hfront_porch = 16
            self.hsync_pulse = 96
            self.hback_porch = 48
            self.hwhole = 800
            self.vvisible_area = 480
            self.vfront_porch = 10
            self.vsync_pulse = 2
            self.vback_porch = 33
            self.vwhole = 525
        else:
            assert 1==0, "unsupported resoution"
    
    async def run(self):
        while True:
            pass

