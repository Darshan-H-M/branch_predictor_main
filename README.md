# branch_predictor_main

# Branch_Predictor
The above attached files are the asm generation files for testing of branch predictor.
We have used the demo codes provided here [chromite_uatg_tests](https://github.com/incoresemi/chromite_uatg_tests)  as templates for our codes.

## Code Description
#### uatg_fa_gshare_bht.py 
- tries to fill bht completely, by branching 512 times with different ghr and pc values.
#### uatg_gshare_fa_bht_fence_postfull.py
- fills the BTB and then flushes it using a fence instruction.
#### uatg_gshare_fa_bht_rollback_postfull.py
- fills the history registers with while adding confidence to a pariticular branch in the BHT, then it simulates an incorrect branch, which forces the history reg to rollback and the BHT to drop in confidence.
#### uatg_gshare_fa_ghr_alternating_compressed.py 
- fills ghr with alternating ones and zeros using compressed branch instruction.
#### uatg_gshare_fa_ras_push_pop_overload.py 
- overflows the ghr with more number of calls than the size and tries to return. 
l
