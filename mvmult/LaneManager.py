#==============================================================================
# LaneManager.py
#==============================================================================

from new_pymtl import *
from new_pmlib import InValRdyBundle

STATE_IDLE = 0
STATE_CFG  = 1
STATE_CALC = 2

class LaneManager( Model ):

  def __init__( s, nlanes, addr_nbits=3, data_nbits=32 ):

    # CPU <-> LaneManager
    s.from_cpu    = InValRdyBundle( addr_nbits + data_nbits )

    # LaneManager -> Lanes
    s.size    = [ OutPort( data_nbits ) for x in range( nlanes ) ]
    s.r_baddr = [ OutPort( data_nbits ) for x in range( nlanes ) ]
    s.v_baddr = [ OutPort( data_nbits ) for x in range( nlanes ) ]
    s.d_baddr = [ OutPort( data_nbits ) for x in range( nlanes ) ]
    s.go      = [ OutPort( 1 )          for x in range( nlanes ) ]
    s.done    = [ InPort ( 1 )          for x in range( nlanes ) ]

    # Config fields
    s.nlanes         = nlanes
    s.addr_nbits     = addr_nbits
    s.data_nbits     = data_nbits

  def elaborate_logic( s ):

    #--------------------------------------------------------------------------
    # state_update
    #--------------------------------------------------------------------------
    s.state      = Wire( 2 )
    s.state_next = Wire( 2 )
    @s.posedge_clk
    def state_update():

      if s.reset: s.state.next = STATE_IDLE
      else:       s.state.next = s.state_next

    #--------------------------------------------------------------------------
    # config_update
    #--------------------------------------------------------------------------
    s.addr = Wire( s.addr_nbits )
    s.data = Wire( s.data_nbits )
    s.connect( s.addr, s.from_cpu.msg[s.data_nbits:s.from_cpu.msg.nbits] )
    s.connect( s.data, s.from_cpu.msg[0:s.data_nbits] )

    @s.posedge_clk
    def config_update():

      # TODO: would like to be able to move this outside function def to create
      #       multiple posedge_clk instances!
      for i in range( s.nlanes ):

        if s.reset:
          s.go     [i].next = 0
          s.size   [i].next = 0
          s.r_baddr[i].next = 0
          s.v_baddr[i].next = 0
          s.d_baddr[i].next = 0

        elif s.from_cpu.val and s.from_cpu.rdy:
          if s.addr == 0: s.go     [i].next = s.data[0]
          if s.addr == 1: s.size   [i].next = s.data
          if s.addr == 2: s.r_baddr[i].next = s.data + (i*4*s.size[i])
          if s.addr == 3: s.v_baddr[i].next = s.data
          if s.addr == 4: s.d_baddr[i].next = s.data + (i*4)

    #--------------------------------------------------------------------------
    # state_transition
    #--------------------------------------------------------------------------
    @s.combinational
    def state_transition():

      # Status

      do_config  = s.from_cpu.val and s.from_cpu.rdy
      do_compute = s.go[0]
      is_done    = 1
      for i in range( s.nlanes ):
        is_done = s.done[i] & is_done

      # State update

      s.state_next.value = s.state

      if   s.state == STATE_IDLE and do_config:
        s.state_next.value = STATE_CFG

      elif s.state == STATE_CFG  and do_compute:
        s.state_next.value = STATE_CALC

      elif s.state == STATE_CALC and is_done:
        s.state_next.value = STATE_IDLE

      # Output ready

      if   s.state == STATE_IDLE: s.from_cpu.rdy.value = True
      elif s.state == STATE_CFG:  s.from_cpu.rdy.value = True
      elif s.state == STATE_CALC: s.from_cpu.rdy.value = False

  def line_trace( s ):
    return 'from_cpu: {} state: {} () go: {} done: {}'.format(
        s.from_cpu, s.state,
        " ".join([str(x.uint()) for x in s.go  ]),
        " ".join([str(x.uint()) for x in s.done]), )

