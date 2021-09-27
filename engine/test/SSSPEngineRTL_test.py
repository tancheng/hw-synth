#=========================================================================
# SSSPEngineRTL_test.py
#=========================================================================
# Simple test for SSSPEngine
#
# Author : Cheng Tan
#   Date : Sep 23, 2021

import sys
sys.path.insert(0, '../..')#/Users/tanc839/projects/acc/framework/hw-synth')

import pytest
from pymtl3                        import *
from pymtl3.stdlib.test.test_srcs  import TestSrcRTL
from pymtl3.stdlib.test.test_sinks import TestSinkRTL, TestSinkCL
from pymtl3.stdlib.test            import TestVectorSimulator
from lib.messages                  import *
from ..SSSPEngineRTL               import SSSPEngineRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, InputDataType, OutputDataType, num_entries,
                 src_msgs, sink_msgs ):

    s.src  = TestSrcRTL ( InputDataType, src_msgs  )
    s.sink = TestSinkRTL( OutputDataType, sink_msgs )
    s.dut  = SSSPEngineRTL( InputDataType, OutputDataType, num_entries )

    # Connections
    s.src.send //= s.dut.recv
    s.dut.send //= s.sink.recv

  def done( s ):
    return s.src.done() and s.sink.done()

  def line_trace( s ):
    return s.src.line_trace() + "-> | " + s.dut.line_trace() + \
                               " | -> " + s.sink.line_trace()

#-------------------------------------------------------------------------
# run_rtl_sim
#-------------------------------------------------------------------------

def run_sim( test_harness, max_cycles=100 ):

  # Create a simulator
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation
  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout
  #assert ncycles < max_cycles

  test_harness.tick()

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

num_entries    = 6
InputDataType  = mk_data( num_entries, 1, 1 )
OutputDataType = mk_bits( clog2( num_entries * num_entries ) )
test_msgs = [ InputDataType(0,1,1,0), InputDataType(1,2,1,0), InputDataType(1,3,1,0),
              InputDataType(2,3,1,0), InputDataType(2,1,1,0), InputDataType(3,1,1,0),
              InputDataType(3,4,1,0), InputDataType(4,5,1,0), InputDataType(4,1,1,0),
              InputDataType(0,5,0,1) ]
sink_msgs = [ OutputDataType(4) ]

def test_simple():
  th = TestHarness( InputDataType, OutputDataType, num_entries,
                    test_msgs, sink_msgs)
  run_sim( th )
