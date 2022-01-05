# python script to automate test 11 in micro-arch test

from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
import re
import os
from typing import Dict, List


class uatg_gshare_fa_ras_push_pop_overload(IPlugin):
    """
    This class contains methods to
    1. generate asm tests that pushes & pops addresses in return address stack
    2. checks the log file for correct number of push-pops
    TODO 3. generate_sv
    """

    def __init__(self):
        # initializing variables
        super().__init__()
        self.recurse_level = 10

    def execute(self, core_yaml, isa_yaml) -> bool:
        # Function to check whether to generate/validate this test or not

        # extract needed values from bpu's parameters
        _bpu_dict = core_yaml['branch_predictor']
        _en_ras = _bpu_dict['ras_depth']
        _en_bpu = _bpu_dict['instantiate']
        # conditions to check if this test needs to be implemented or not
        if _en_ras and _en_bpu:
            return True
        else:
            return False

    def generate_asm(self) -> List[Dict[str, str]]:
        # reg x30 is used as looping variable. reg x31 used as a temp variable

        recurse_level = self.recurse_level
        # number of times call-ret instructions to be implemented in assembly
        no_ops = '\taddi x31, x0, 5\n\taddi x31, x0, -5\n'
        asm = f'\taddi x30, x0, {recurse_level}\n'
        # going into the first call
        asm += '\tcall x1, lab1\n\tbeq x30, x0, end\n'
        # recursively going into calls
        for i in range(1, recurse_level + 1):
            asm += f'lab{i} :\n'
            if i == recurse_level:
                asm += '\taddi x30, x30, -1\n'
            else:
                asm += no_ops * 3 + f'\tcall x{i+1}, lab{i+1}\n'
            asm += no_ops * 3 + '\tret\n'
            # getting out recursively using rets
        asm += 'end:\n\tnop\n'
        # compile macros for the test
        compile_macros = []

        return [{
            'asm_code': asm,
            'asm_sig': '',
            'compile_macros': compile_macros
        }]

