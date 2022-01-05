# branch_predictor_main

# Branch_Predictor
The above attached files are the asm generation files for testing of branch predictor.
We have used these codes provided here [chromite_uatg_tests](https://github.com/incoresemi/chromite_uatg_tests)  as reference for our codes.

## Code Description
#### uatg_gshare_fa_bht.py 
- This test used to fill the branch history table with conditional Branches and jumps, calls and returns. and also verify if the replacement happening properly or not. and fill the bht completely, it will branch 512 times with different pc and ghr values.

#### uatg_gshare_fa_bht_fence_postfull.py
- This test is used to fill the branch target buffer and then it flushes using fence instruction.
#### uatg_gshare_fa_bht_rollback_postfull.py
- This test is used to Simplify the incorrect branches, then it forces the history register to roll back.
#### uatg_gshare_fa_ghr_alternating_compressed.py 
- In this test alternating ones and zeros are filled to ghr with the help of Compressed branch Instruction.
#### uatg_gshare_fa_ras_push_pop_overload.py 
- In this test ghr will overflows with maximum number of calls than the original size and then it tries to return.
l
