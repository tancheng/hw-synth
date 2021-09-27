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
    ResType       = mk_bits( clog2( data_mem_size ) )
    NodeType      = mk_bits( clog2( num_entries ) )
    TempNodeType  = mk_bits( clog2( num_entries + 1 ) )
    
    # OutputDataType   = mk_bits( clog2( num_entries ) )

    # Interface
    s.recv = RecvIfcRTL( InputDataType  )
    s.send = SendIfcRTL( OutputDataType )

    # Component
    s.mem       = [ [ Wire( b1 ) for _ in range( num_entries ) ] for _ in range( num_entries ) ]
    s.queue     = NormalQueueRTL( NodeType, num_entries * num_entries )
    s.step      = Wire( ResType )
    s.iter      = Wire( NodeType )
    s.temp_iter = Wire( TempNodeType )
    s.cur_count = Wire( ResType )
    s.dst       = Wire( NodeType )
    s.node      = Wire( NodeType )
    s.cur_done  = Wire( b1 )
    s.start_run = Wire( b1 )

    @s.update
    def init_process():
      s.recv.rdy     = b1( 1 )
      s.send.en      = b1( 0 )
      s.queue.enq.en = b1( 0 )

      # Perform the SSSP search.
      if s.recv.msg.run == b1( 1 ):
        s.queue.enq.msg = s.recv.msg.src
        s.queue.enq.en  = b1( 1 )
        s.dst           = s.recv.msg.dst

      if s.queue.count > ResType( 0 ):
        s.node      = s.queue.deq.ret
        s.cur_done  = b1( 0 )
        s.start_run = b1( 1 )
        # The start of a for-loop must be a constant expression!
        # for i in range(s.iter, s.num_entries):
        for i in range( s.num_entries ):
          if NodeType( i ) >= s.iter:
            if not s.cur_done:
              if s.mem[s.node][i] == b1( 1 ):
                s.queue.enq.msg = NodeType(i)
                s.queue.enq.en  = b1( 1 )
                s.cur_done      = b1( 1 )
                s.temp_iter     = TempNodeType( i + 1 )
                if s.temp_iter == s.dst + TempNodeType( 1 ):
                  s.send.msg   = s.step
                  s.send.en    = b1( 1 )
  
            if not s.cur_done or s.iter == NodeType( s.num_entries - 1 ):
              s.queue.deq.en = b1( 1 )
              s.temp_iter    = TempNodeType( 0 )
            else:
              s.queue.deq.en = b1( 0 )

##########################################################################
# Sequential version for the BFS. It takes one cycle to check a connection
# exists or not. 
##########################################################################
#        if s.iter < s.num_entries:
#          if s.mem[s.node][s.iter] == b1( 1 ):
#            s.queue.enq.msg = s.iter
#            s.queue.enq.en  = b1( 1 )
#            if s.iter == s.dst:
#              s.send.msg = s.step
#              s.send.en  = b1( 1 )
#
#          if s.iter == s.num_entries - 1:
#            s.queue.deq.en = b1( 1 )
#          else:
#            s.queue.deq.en = b1( 0 )
      elif s.start_run:
        s.send.msg  = ResType( 0 )
        s.send.en   = b1( 1 )
        s.start_run = b1( 0 )

    @s.update_ff
    def bfs_process():
      if s.reset:
        s.cur_count <<= ResType( 0 )
        s.step      <<= ResType( 0 )
        s.iter      <<= NodeType( 0 )

      # Update register file that represents the adjacent matrix.
      if s.recv.msg.init == b1( 1 ):
        s.mem[s.recv.msg.src][s.recv.msg.dst] <<= b1( 1 )
      if s.cur_done:
        s.mem[s.node][s.temp_iter-TempNodeType( 1 )] <<= b1( 0 )

      if s.queue.count > ResType( 0 ):

        if s.cur_count == ResType( 0 ):
          s.cur_count <<= ResType( s.queue.count )
          s.step      <<= s.step + ResType( 1 )

        if not s.cur_done or s.temp_iter >= TempNodeType( s.num_entries ):
          s.iter      <<= NodeType( 0 )
          s.cur_count <<= s.cur_count - ResType( 1 )
        else:
          s.iter      <<= s.temp_iter

##########################################################################
# Sequential version for the BFS. It takes one cycle to check a connection
# exists or not. 
##########################################################################
#        if s.iter < s.num_entries - 1:
#          s.iter      <<= s.iter + 1
#        else:
#          s.iter      <<= NodeType( 0 )
#          s.cur_count <<= s.cur_count - 1

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

