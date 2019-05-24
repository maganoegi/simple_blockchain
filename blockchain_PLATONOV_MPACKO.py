# ------------------------------------------------------------------ #
# ------------ Blockchain Application ------------------------------ #
# ------------ HEPIA 2018-2019 ITI 1 ------------------------------- #
# ------------------------------------------------------------------ #
# ------- Main --------- Sergey PLATONOV & Dylan MPACKO ------------ #
# ------------------------------------------------------------------ #
#------------------------------------------------------------------- #

# ------------------------------ Assets ---------------------------- #

from blockchain_lib import *                         # NOTE: Partitioning predetermined:
import os                                            # header: 8 bits
from datetime import datetime                        # hash: 256 bits
from tqdm import tqdm                                # content: 256 bits
import time                                          # nonce: 64 bits
                                                     # TOTAL: 584 bits -> 73 bytes!
# keyword 'analyze' reserved                         # --- please don't modify! ---

# --------------------------- Main --------------------------------- #
start = time.time()

filename = read_user_input() # SWITCH THESE TWO FOR DIFFERENT TESTING MODES
#filename = 'analyze'

dir = 'blockchain'
zero_hash = format(0, '064x') # -> hex string 256 bits = 64 bytes no prefix
date_string = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
this_data = string_2_256bHex(date_string)# -> hex string 256 bits = 64 bytes no prefix

# ------- Different User Scenarios ------- #
#os.system('cls' if os.name == 'nt' else 'clear')
if not os.path.isdir(dir): # ------------------------------------- Blockchain folder doesn't exist --- #
    if (filename == 'analyze') | (filename == 'wipe'):
        raise Exception('Nothing to Analyze or Wipe!')
    else:
        os.mkdir(dir)
        block_to_be = prepare_block(0, this_data, zero_hash)
        end = time.time()
        block_to_be = insert_exec_time(block_to_be, end-start)
        write_block(bytes.fromhex(block_to_be), filename)
        print_results(filename, 0, date_string, end, start)

elif os.path.isdir(dir) & (len(os.listdir(dir)) == 0): # --- Blockchain folder exists but empty ------ #
    if (filename == 'analyze') | (filename == 'wipe'):
        raise Exception('Nothing to Analyze or Wipe!')
    else:
        block_to_be = prepare_block(0, this_data, zero_hash)
        end = time.time()
        block_to_be = insert_exec_time(block_to_be, end-start)
        write_block(bytes.fromhex(block_to_be), filename)
        print_results(filename, 0, date_string, end, start)

else: # ---------------------------------------------------------- Blockchain exists and is intact --- #
    if filename == 'analyze': ## 1ST case not covered with analyze!!
        print_blockchain_data()
    elif filename == 'wipe':
        wipe_all()
    else:
        print("\n")
        bar_format = '{l_bar}{bar}| {n_fmt}/{total_fmt}'
        with tqdm(total=5, ncols=80, bar_format=bar_format) as pbar:
            this_number = len(os.listdir(dir))

            update_bar(pbar, 'Find Prev   ')
            previous_filename = find_prev(this_number, dir)

            update_bar(pbar, 'Hash Prev   ')
            previous_hash = hash_a_file(previous_filename)

            update_bar(pbar, 'Preparing...') # POW BECOMES NOTICEABLE AFTER +/- 20TH FILE
            block_to_be = prepare_block(this_number, this_data, previous_hash)
            end = time.time()
            block_to_be = insert_exec_time(block_to_be, end - start)
            update_bar(pbar, 'Writing     ')
            write_block(bytes.fromhex(block_to_be), filename)

            update_bar(pbar, 'Done        ')
            time.sleep(0.1)
            pbar.close()

        print_results(filename, this_number, date_string, end, start)






