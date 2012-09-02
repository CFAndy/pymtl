#=========================================================================
# TestSimpleSink Test Suite
#=========================================================================

from pymtl import *

from TestSimpleSource import TestSimpleSource
from TestSimpleSink   import TestSimpleSink

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness (Model):

  def __init__( self, nbits, msgs ):

    self.src  = TestSimpleSource ( nbits, msgs  )
    self.sink = TestSimpleSink   ( nbits, msgs )

    connect( self.src.out_msg, self.sink.in_msg )
    connect( self.src.out_val, self.sink.in_val )
    connect( self.src.out_rdy, self.sink.in_rdy )

  def done( self ):
    return self.src.done.value and self.sink.done.value

  def line_trace( self ):
    return self.src.line_trace() + " | " + self.sink.line_trace()

#-------------------------------------------------------------------------
# TestSimpleSink unit test
#-------------------------------------------------------------------------

def test_basics( dump_vcd ):

  # Test messages

  test_msgs = [
    0x0000,
    0x0a0a,
    0x0b0b,
    0x0c0c,
    0x0d0d,
    0xf0f0,
    0xe0e0,
    0xd0d0,
  ]

  # Instantiate and elaborate the model

  model = TestHarness( 16, test_msgs )
  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )
  if dump_vcd:
    sim.dump_vcd( "pmlib-TestSimpleSink_test_basics.vcd" )

  # Run the simulation

  print ""

  sim.reset()
  while not model.done():
    sim.print_line_trace()
    sim.cycle()

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

