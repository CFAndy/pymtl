#=========================================================================
# TestSource.py
#=========================================================================

from pymtl      import *
from pclib.test import TestRandomDelay
from pclib.ifcs import OutValRdyBundle

from TestSimpleSource import TestSimpleSource

#-------------------------------------------------------------------------
# TestSource
#-------------------------------------------------------------------------
class TestSource( Model ):

  def __init__( s, dtype, msgs, max_random_delay = 0 ):

    s.out  = OutValRdyBundle( dtype )
    s.done = OutPort        ( 1     )

    s.src   = TestSimpleSource( dtype, msgs )
    s.delay = TestRandomDelay ( dtype, max_random_delay )

    # Connect test source -> random delay -> output ports

    s.connect( s.src.out,   s.delay.in_ )
    s.connect( s.delay.out, s.out       )

    # Connect test source done signal to output port

    s.connect( s.src.done, s.done )

  def line_trace( s ):

    return "{}".format( s.out )

