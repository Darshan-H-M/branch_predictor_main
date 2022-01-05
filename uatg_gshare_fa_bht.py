# See LICENSE.incore for details

from yapsy.IPlugin import IPlugin
from ruamel.yaml import YAML
import uatg.regex_formats as rf
from typing import Dict, List
import re
import os


class uatg_gshare_fa_bht_fill_01(IPlugin):
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

        branch_count = int(self._bht_depth)
        # The branch_count is used equally split the instructions
        # between call, jump, branch and returns

        asm_start = "\taddi t1,x0,0\n\taddi t2,x0,1\n\n"
        asm_end = "exit:\n\n\taddi x0,x0,0\n\tadd x0,x0,0\n\n"
        # variables to store some asm boiler plate

        asm_branch = ""
        # empty string which will be populated with branching directives
        asm_jump = f"\tadd t1,t1,t2\n\tjal x0,entry_{branch_count + 1}\n\n"
        # string with jump directives which will be used in a loop
        asm_call = f"entry_{(2 * branch_count) + 1}:\n\n"
        # string with call directives

        for j in range((2 * branch_count) + 2, ((3 * branch_count) + 1)):
            # for loop to iterate through the branch counts and create a string
            # with required call directives
            asm_call += f"\tcall x1,entry_{j}\n"
        asm_call += "\tj exit\n\n"
        # final directive to jump to the exit label

        for i in range(1, self._bht_depth):
            # for loop to iterate and generate the asm string to be returned
            if i <= branch_count:
                # first populate the BHT with branch instructions
                if (i % 2) == 1:
                    # conditions to return branch and loop directives
                    asm_branch += f"entry_{i}:\n"
                    # we do this to increment/decrement control variable
                    asm_branch += f"\tadd t1,t1,t2\n\tbeq t1, t2, entry_{i}\n\n"
                    # in the loop/branch.
                else:
                    asm_branch += f"entry_{i}:\n"
                    asm_branch += f"\tsub t1,t1,t2\n\tbeq t1, t2, entry_{i}\n\n"
            elif branch_count < i <= 2 * branch_count:
                # populate the the next area in the BHT with Jump
                if (i % 2) == 1:
                    # conditions checks to populate the asm string
                    # accordingly while tracking the control variable
                    asm_jump += "entry_" + str(i) + ":\n"
                    asm_jump += "\tsub t1,t1,t2\n\tjal x0,entry_" + \
                                str(i + 1) + "\n\taddi x0,x0,0\n\n"
                else:
                    asm_jump += "entry_" + str(i) + ":\n"
                    asm_jump += "\tadd t1,t1,t2\n\tjal x0,entry_" + \
                                str(i + 1) + "\n\taddi x0,x0,0\n\n"

            else:
                # finally populate the BHT with call and return instructions
                if i >= 3 * branch_count:
                    break
                asm_call = asm_call + "entry_" + str(i + 1) + ":\n"
                for j in range(2):
                    asm_call = asm_call + "\taddi x0,x0,0\n"
                asm_call = asm_call + "\tret\n\n"

        # concatenate the strings to form the final ASM sting to be returned
        asm = asm_start + asm_branch + asm_jump + asm_call + asm_end

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

        # check if the rg_allocate register value starts at 0 and traverses
        # till 31. This makes sure that the BHT was successfully filled. Also
        # check if all the 4 Control instructions are encountered at least once
        # This can be checked from the training data -> [      5610] [ 0]BPU :
        # Received Training: Training_data........

        f = open(log_file_path, "r")
        log_file = f.read()  # open the log file for parsing
        f.close()

        alloc_newind_result = re.findall(rf.alloc_newind_pattern, log_file)
        # we choose the pattern among the pre-written patterns which we wrote
        # in the regex formats file selecting the pattern "Allocating new
        # index: dd ghr: dddddddd"

        new_arr = []
        for i in range(len(alloc_newind_result)):
            new_arr.append(alloc_newind_result[i][23:])
            # appending patterns to list based on requirement for this checking

        new_arr = list(set(new_arr))  # sorting them and removing duplicates
        new_arr.sort()
        # creating the template for the YAML report for this check.
        test_report = {
            "gshare_fa_bht_fill_01_report": {
                'Doc': "ASM should have filled {0} BHT entries. This report "
                       "verifies that.".format(self._bht_depth),
                'BHT_Depth': self._bht_depth,
                'No_filled': 0,
                'Execution_Status': ''
            }
        }

    def generate_covergroups(self, config_file):
        """
           returns the covergroups for this test. This is written as an SV file.

           The covergroups are used to check for coverage.
        """
