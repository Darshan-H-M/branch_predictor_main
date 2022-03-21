# python program to generate an assembly file which fills the ghr with zeroes or ones
# the ghr either will have a zero entry or one entry when the loop exits
from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
import re
import os
from typing import Dict, Union, Any, List

class uatg_gshare_fa_ghr_ones_zeroes(IPlugin):
  
    """
    1. generate asm tests that fills global history register with zeroes or ones
    2. and also verify the log file whether the history register is filled with 1's or 0's
       at least once.
    """
    
    
    def __init__(self):
        # initializing variables
        self.isa = 'RV32I'
        self.isa = 'RV64I'
        super().__init__()
        self._history_len = 8
        self.modes = []
   
    
    def execute(self, core_yaml, isa_yaml) -> bool:
        # Function to check whether to generate/validate this test or not

        # extract needed values from bpu's parameters
        _bpu_dict = core_yaml['branch_predictor']
        _en_bpu = _bpu_dict['instantiate']
        self._history_len = _bpu_dict['history_len']
        self.isa = isa_yaml['hart0']['ISA']
        self.modes = ['machine']

        if 'S' in self.isa:
            self.modes.append('supervisor')

        elif 'S' in self.isa and 'U' in self.isa:
            self.modes.append('user')

        elif _en_bpu and self._history_len:
            return True
        else:
            return False 

    def generate_asm_zero(self) -> List[Dict[str, Union[Union[str, list], Any]]]:
        """
          the for loop iterates ghr_width + 2 times printing an
          assembly program which contains ghr_width + 2 branches which
          will are NOT TAKEN. This fills the ghr with zeros
        """ 
        for mode in self.modes:

            loop_count = self._history_len + 2
            asm = "\n\n## test: gshare_fa_ghr_zeros_01 ##\n\n\taddi t0,x0,1\n"

            for i in range(1, loop_count):
                asm += f"branch_{i}:\n\tbeq t0, x0, branch_{i}\n\t" \
                       f"addi t0, t0, 1\n"

            # trap signature bytes
            trap_sigbytes = 24

            # initialize the signature region
            sig_code = 'mtrap_count:\n .fill 1, 8, 0x0\n' \
                       'mtrap_sigptr:\n' \
                       f' .fill {trap_sigbytes // 4},4,0xdeadbeef\n'
            # compile macros for the test
            if mode != 'machine':
                compile_macros = ['rvtest_mtrap_routine', 's_u_mode_test']
            else:
                compile_macros = []
            
    def generate_asm_one(self) -> List[Dict[str, Union[Union[str, list], Any]]]:
        """
          the for loop iterates ghr_width + 2 times printing an
          assembly program which contains ghr_width + 2 branches which
          will are TAKEN. This fills the ghr with ones
        """
        
        for mode in self.modes:

            loop_count = self._history_len + 2  # here, 2 is added arbitrarily.
            # it makes sure the loop iterate 2 more times keeping the ghr filled
            # with ones for 2 more predictions

            asm = f"\n\taddi t0, x0, {loop_count}\n\taddi t1, x0, 0 \n\nloop:\n"
            asm += "\taddi t1, t1, 1\n\tblt t1, t0, loop\n\tc.nop\n"

            # trap signature bytes
            trap_sigbytes = 24

            # initialize the signature region
            sig_code = 'mtrap_count:\n .fill 1, 8, 0x0\n' \
                       'mtrap_sigptr:\n' \
                       f' .fill {trap_sigbytes // 4},4,0xdeadbeef\n'
            # compile macros for the test
          
            if mode != 'machine':
                compile_macros = ['rvtest_mtrap_routine', 's_u_mode_test']
            else:
                compile_macros = []
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
          
            
