"""
==========================================================================
messages.py
==========================================================================
Collection of messages definition.

Author : Cheng Tan
  Date : Sep 23, 2021
"""
from pymtl3 import *

#=========================================================================
# Generic data message
#=========================================================================

def mk_data( num_entries=10, init=1, run=1, prefix="EngineData" ):

  SrcType  = mk_bits( clog2( num_entries ) )
  DstType  = mk_bits( clog2( num_entries ) )
  InitType = mk_bits( init )
  RunType  = mk_bits( run )

  new_name = f"{prefix}_{num_entries}_{num_entries}_{init}_{run}"

  def str_func( s ):
    return f"{s.src}.{s.dst}.{s.init}.{s.run}"

  return mk_bitstruct( new_name, {
      'src'  : SrcType,
      'dst'  : DstType,
      'init' : InitType,
      'run'  : RunType,
    },
    namespace = { '__str__': str_func }
  )

