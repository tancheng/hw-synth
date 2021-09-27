#=========================================================================
# SSSPEngineRTL.py
#=========================================================================
# RTL Single-Source Shortest Path Engine module.
#
# Author : Cheng Tan
#   Date : Sep 22, 2021

from pymtl3                   import *
from pymtl3.stdlib.ifcs       import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl.queues import NormalQueueRTL


class SSSPEngineRTL( Component ):
  def construct(s, InputDataType, OutputDataType, num_entries ):

    # Constant
    s.num_entries = num_entries
    data_mem_size = num_entries * num_entries
    ResType = mk_bits( clog2( data_mem_size ) )
    NodeType = mk_bits( clog2( num_entries ) )
    
    # OutputDataType   = mk_bits( clog2( num_entries ) )

    # Interface
    s.recv = RecvIfcRTL( InputDataType  )
    s.send = SendIfcRTL( OutputDataType )

    # Component
    s.mem   = [ [ Wire( b1 ) for _ in range( num_entries ) ] for _ in range( num_entries ) ]
    s.queue = NormalQueueRTL( NodeType, num_entries * num_entries )
    s.step = Wire( ResType )
    s.iter = Wire( NodeType )
    s.curCount = Wire( ResType )
    s.dst  = Wire( NodeType )
    s.node = Wire( NodeType )

    @s.update
    def init_process():
      s.recv.rdy = b1( 1 )
      s.send.en  = b1( 0 )
      s.queue.enq.en = b1( 0 )

      # Perform the SSSP search.
      if s.recv.msg.run == b1( 1 ):
        s.queue.enq.msg = s.recv.msg.src
        s.queue.enq.en = b1( 1 )
        s.dst = s.recv.msg.dst

      if s.queue.count > 0:
        s.node = s.queue.deq.ret
        if s.iter < s.num_entries:
          if s.mem[s.node][s.iter] == b1( 1 ):
            s.queue.enq.msg = s.iter
            s.queue.enq.en = b1( 1 )
            if s.iter == s.dst:
              s.send.msg = s.step
              s.send.en  = b1( 1 )

          if s.iter == s.num_entries - 1:
            s.queue.deq.en = b1( 1 )
          else:
            s.queue.deq.en = b1( 0 )

    @s.update_ff
    def bfs_process():
      if s.reset:
        s.curCount <<= ResType( 0 )
        s.step     <<= ResType( 0 )
        s.iter     <<= NodeType( 0 )

      # Update register file that represents the adjacent matrix.
      if s.recv.msg.init == b1( 1 ):
        s.mem[s.recv.msg.src][s.recv.msg.dst] <<= b1( 1 )
      s.mem[s.node][s.iter] <<= b1( 0 )

      if s.queue.count > 0:
        if s.curCount == 0:
          s.curCount <<= ResType( s.queue.count )
          s.step <<= s.step + 1

        if s.iter < s.num_entries - 1:
          s.iter <<= s.iter + 1
        else:
          s.iter <<= NodeType( 0 )
          s.curCount <<= s.curCount - 1

  def line_trace( s ):
    str_line = "\n"
    for i in range( s.num_entries ):
      for j in range( s.num_entries ):
        if s.mem[i][j] == b1( 1 ):
          str_line += "1"
        else:
          str_line += "0"
      str_line += "\n"
    return str_line + " -> " + s.queue.line_trace() + "; cur_node: " + str(s.node) + "; queue.count: " + str(s.queue.count) + "; iter: " + str(s.iter) + "; step: " + str(s.step) + "; queue.enq.en: " + str(s.queue.enq.en) + "; queue.deq.en: " + str(s.queue.deq.en) + "\n***********"

