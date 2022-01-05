# See LICENSE.incore for details

from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
from typing import Dict, List
import re
import os


class uatg_gshare_fa_bht_rollback_postfull(IPlugin):
    """
    The test is used to fill the Branch Target Buffer with addresses. 
    It fills the BHT with Conditional Branches and Jumps, Calls and Returns.
    As the replacement algorithm in this implementation of the BHT is round
    robin, hence it also checks if the replacement happens
    properly. 
    """

    def __init__(self):
        """
        The constructor for this class.
        We assume that the default BHT depth is 512
        """
        super().__init__()
        self._bht_depth = 512

    def execute(self, core_yaml, isa_yaml):
        """
        The method returns true or false.
        In order to make test_generation targeted, we adopt this approach. Based
        on some conditions, we decide if said test should exist.

        This method also acts as the only method which has access to the
        hardware configuration of the DUt in the test_class. 
        """
        _bpu_dict = core_yaml['branch_predictor']
        _en_bpu = _bpu_dict['instantiate']
        # States if the DUT has a branch predictor
        self._bht_depth = _bpu_dict['bht_depth']
        # states the depth of the BHT to customize the test
        if _en_bpu and self._bht_depth:
            # check condition, if BPU exists as well as bht_depth is an integer.
            return True
            # return true if this test is to be executed
        else:
            return False
            # return false if this test cannot.

    def generate_asm(self) -> List[Dict[str, str]]:
        """
        This method returns a string of the ASM file to be generated.

        This ASM file is written as the ASM file which will be run on the DUT.
        """
        asm_start = "\taddi t3,x0,3\n\n"
        asm_end = "exit:\n\n\taddi x0,x0,0\n\tadd x0,x0,0\n\n"
        asm = ''
        # variables to store some asm boiler plate
        
        no_ops = '\taddi x31, x0, 5\n\taddi x31, x0, -5\n\n'

        for i in range(1,self._bht_depth):        
        	asm += f"entry{i} :\n"
        	if i == 10:
        		asm += '\taddi t3,t3,-1\n'
        		asm += '\tbeqz t3,exit\n'
        	asm += f'\taddi t1,x0,0\n\taddi t1,t1,1\n\tbeq t1,t1,entry{i+1}\n\n'
        asm += "entry512 :\n\tj entry1\n\n'
        
        asm = asm_start + asm + asm_end

        # compile macros for the test
        compile_macros = []

        return [{
            'asm_code': asm,
            'asm_sig': '',
            'compile_macros': compile_macros
        }]

    def check_log(self, log_file_path, reports_dir):
        """
        This method performs a minimal check of the logs genrated from the DUT
        when the ASM test generated from this class is run.

        We use regular expressions to parse and check if the execution is as 
        expected. 
        """
