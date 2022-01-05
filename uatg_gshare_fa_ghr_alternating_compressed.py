# See LICENSE.incore for details
from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
import re
import os
from typing import Dict, List


class uatg_gshare_fa_ghr_alternating_compressed(IPlugin):

    def __init__(self):
        """ The constructor for this class. """
        super().__init__()

        self._history_len = 8
        pass  # we do not have any variable to declare.

    def execute(self, core_yaml, isa_yaml) -> bool:
        """
        The method returns true or false.
        In order to make test_generation targeted, we adopt this approach. Based
        on some conditions, we decide if said test should exist.

        This method also doubles up as the only method which has access to the 
        hardware configuration of the DUt in the test_class. 
        """
        _bpu_dict = core_yaml['branch_predictor']
        _en_bpu = _bpu_dict['instantiate']
        # States if the DUT has a branch predictor
        self._history_len = _bpu_dict['history_len']
        # states the length of the history register

        if _en_bpu and self._history_len:
            # check condition, if BPU exists and history len is valid
            return True  # return true if this test can exist.
        else:
            return False  # return false if this test cannot.

    def generate_asm(self) -> List[Dict[str, str]]:
        """
        This method returns a string of the ASM file to be generated.

        This ASM file is written as the ASM file which will be run on the DUT.
        """

        # This function creates assembly code to populate the Global History
        # register with alternating 0's and 1's pattern. eg. 010101010....
        # history_len = the size of the Global History Register (ghr) in bits.
        # By default history_len is set to be 8 bits.
        # The generated assembly code will use the x8 register to alternatively
        # enter and exit branches.

        # initial section in the ASM
        asm = ""
        asm = asm + '\taddi x8,x0,1\n'
        asm = asm + '\taddi x9,x0,1\n\taddi x10,x0,2\n\n'
        asm = asm + '\tc.beqz  x8,lab0\n'

        # the assembly program is structured in a way that
        # there are odd number of labels.
        if self._history_len % 2:
            self._history_len = self._history_len + 1

        # loop to generate labels and branches
        for i in range(self._history_len):
            if i % 2:
                asm = asm + 'lab' + str(i) + ':\n'
                asm = asm + '\taddi x8,x8,1\n'
                asm = asm + '\tc.beqz  x8,lab' + str(i + 1) + '\n'
            else:
                asm = asm + 'lab' + str(i) + ':\n'
                asm = asm + '\taddi x8,x8,-1\n'
                asm = asm + '\tc.beqz  x8,lab' + str(i + 1) + '\t\n'

        asm = asm + 'lab' + str(self._history_len) + ':\n'
        asm = asm + '\taddi x8,x8,-1\n\n'
        asm = asm + '\taddi x9,x9,-1\n\taddi x10,x10,-1\n'
        asm = asm + '\tc.beqz  x9,lab0\n\taddi x8,x8,2\n'
        asm = asm + '\tc.beqz  x10,lab0\n'

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

        # check if the ghr value is alternating.
        # it should be 01010101 or 10101010 before being fenced
        # creating the template for the YAML report for this check.
        test_report = {
            "gshare_fa_ghr_alternating_01_report": {
                'Doc': "ASM should have generated either 010101... or 101010..."
                       "pattern in the GHR Register. This report show's the "
                       "results",
                'expected_GHR_pattern': '',
                'executed_GHR_pattern': [],
                'Execution_Status': ''
            }
        }
