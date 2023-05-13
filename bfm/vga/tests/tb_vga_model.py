# test_my_design.py (extended)

import cocotb
from cocotb.triggers import FallingEdge, RisingEdge, Timer
from cocotb.types import LogicArray, Range
from cocotb.queue import Queue
import random

import sys
sys.path.append('/home/varun/coding/projects/cocotbRepo/bfm/protocols/uart/model')
