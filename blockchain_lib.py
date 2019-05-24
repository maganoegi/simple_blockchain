# ------------------------------------------------------------------ #
# ------------ Blockchain App Support Library ---------------------- #
# ------------ HEPIA 2018-2019 ITI 1 ------------------------------- #
# ------------------------------------------------------------------ #
# ------- Lib ---------- Sergey PLATONOV & Dylan MPACKO ------------ #
# ------------------------------------------------------------------ #

# ------------------------------ Assets ---------------------------- #

import sys
import time
import hashlib
import os
from prettytable import PrettyTable
import random
import struct
import shutil

# ----------------------- Function Definitions --------------------- #
def read_user_input():
    args = sys.argv
    if len(args) == 2:
        filename = args[1]
        return filename
    elif len(args) == 1:
        return format(random.randint(1, 7000) * 5, '06x')
    else:
        raise Exception('Please provide the name of your block-file!')


def find_prev(my_number, dir): # Looks in all the files until matching header signature found
    target_number = my_number - 1
    entries = os.listdir(dir)
    for entry in entries:
        with open('blockchain/' + entry, "rb") as f:
            first_byte_val = int.from_bytes(f.read(1), 'little')
        f.close()
        if first_byte_val == target_number:
            return entry
        else:
            continue

def hash_a_file(filename):
    with open('blockchain/' + filename, "rb") as f:
        byte = bytes.fromhex(f.read().hex()[:-8]) #remove the timestamp, and move on (32 bit float)
        #byte = f.read()
        m = hashlib.sha256(byte).hexdigest()
    f.close()
    return m

def prepare_block(this_number, this_data, previous_hash): # prepares the block to be written into the chain
    nonce = 0 #zero_xbit(64)
    content = format(this_number, '02x') + previous_hash + this_data + format(nonce, '016x')
    next_hash = hashlib.sha256(bytes.fromhex(content)).hexdigest()

    while not is_hash_ok(this_number, next_hash):
        nonce += 1
        content = content[:-16] + format(nonce, '016x')
        next_hash = hashlib.sha256(bytes.fromhex(content)).hexdigest()

    return content

def is_hash_ok(number, hash_string): # checks whether the signature of the next hash is correct
    binary = format(int(hash_string, 16), '0256b')
    if number == 0:
        return (binary[0] == '1')
    else:
        i = 0
        counter = 0
        while binary[i] == '0':
            counter += 1
            i += 1
        return True if counter == number else False # set number (lab) or number (increments)

def write_block(data, filename):
    f = open('blockchain/' + filename, "wb")
    f.write(data)
    f.close()

def print_blockchain_data(): # prints upon request (analyse performance)
    print("\n")
    number_of_blocks = len(os.listdir('blockchain'))

    numbers = [0] * number_of_blocks
    names = [""] * number_of_blocks
    zeros = [0] * number_of_blocks
    contents = [""] * number_of_blocks
    nonces = [0] * number_of_blocks
    times = [0.0] * number_of_blocks

    entries = os.listdir('blockchain')
    for entry in entries:
        with open('blockchain/' + entry, "rb") as f:
            data = ""
            byte = f.read(1)
            data += format(ord(byte), '08b')
            while byte:
                byte = f.read(1)
                if not byte:
                    break
                data += format(ord(byte), '08b')

            number = int(data[0:8], 2)
            numbers[number] = number
            names[number] = entry
            content_string = ""
            for j in range(272, 528, 8):
                if data[(j-8):j] == "11111111": # signal sequence to detect where the content ends in partition
                    break
                else:
                    content_string += chr(int(data[(j-8):j], 2))
            contents[number] = content_string[:-12] ## FIND PROBLEM!
            nonces[number] = int(data[520:584], 2)
            times[number] = struct.unpack('f', struct.pack('I', int(data[584:616], 2)))[0]
            for i in range(256):
                if data[(8 + i)] == '0':
                    zeros[number] += 1
                else:
                    break
        f.close()
    t = PrettyTable(["\033[91mFilename\033[0m", "\033[91mNumber\033[0m", "\033[91mZeros in Hash\033[0m",
                     "\033[91mContent\033[0m", "\033[91mNonce increments*\033[0m", "\033[91mCalc Duration**\033[0m", "\033[91mProof Of Work\033[0m"])
    for i in range(number_of_blocks):
        pow = 0.0 if i == 0 else (float(times[i] - times[(i-1)])/(float(times[(i-1)]) if float(times[(i-1)]) > 0.0
                                                                    else 1) * 100.0)
        if pow > 0.0:
            pow_color = "\033[92m"
            arrow = u'\u2191'
        elif pow == 0.0:
            pow_color = "\033[94m"               # Code a bit messy, but only serves display purposes
            arrow = u'\u003D'
        else:
            pow_color = "\033[91m"
            arrow = u'\u2193'

        pow = pow if pow >= 0.0 else (-1.0 * pow)

        t.add_row(["\033[92m" + names[i] + "\033[0m", numbers[i], "-" if i == 0 else zeros[i], contents[i],
                   "{:,}".format(nonces[i]), ("%.3f" % times[i]) + " s",  pow_color + ("%.1f" % pow) + " %" + " \033[1m" + arrow + "\033[0m"])
    print(t)
    print("* Nonce increments until the number of leading 0's in content-hash equals this file's number")
    print("** Duration proportional to Nonce Increments in Increment mode: see is_hash_ok()")

    print("\n")


def string_2_256bHex(s): # used to convert the data string into an appropriate format
    hex_string = ""
    for i in s:
        hex_string += format(ord(i), '02x')
    hex_string += "1111"
    for j in range((64 - len(hex_string))):
        hex_string += "0"
    return hex_string

def update_bar(pbar, processname):
    time.sleep(0.1)
    pbar.update(1)
    pbar.set_description(processname, refresh=True)

def print_results(filename, this_number, date_string, end, start): # prints after addition of a new block
    print("\n")
    print("File\033[92m\033[1m " + filename, "\033[0mwith the number\033[92m\033[1m", this_number,
          "\033[0mcreated \033[92m\033[1msuccessfully\033[0m")
    print("Data: \033[94m\033[1m" + date_string + "\033[0m" + "         Duration: \033[91m\033[1m",
          ("%.4f" % (end - start)), "s\033[0m\n")

def insert_exec_time(contentStr, time):
    time_str = hex(struct.unpack('<I', struct.pack('<f', time))[0])[2:]
    return contentStr + time_str

def wipe_all():
    folder = 'blockchain'
    if os.path.exists(folder):
        shutil.rmtree(folder)
    print("\n--- Blockchain deleted ---\n")

def hepia_print():
    line = [""] * 14
    line[0] = "MMMMMMMMMMMMMMMMMMMMMMWWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWWWMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[1] = "MMMMMMMMMMMMMMMMMMMMMO:;OMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWx,;OMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[2] = "MMMMMMMMMMMMMMMMMMMMMd  oX00XWMMMMMMMMMMMMMWK0O0NMMMMMMMMMMMMMNKXNKO0NMMMMMMMMMMMMWkcl0MMMMMMMMMMMWN0OOKNMMMMMMMM"
    line[3] = "MMMMMMMMMMMMMMMMMMMMMd  ';...xWMMMMMMMMMMM0:.',.'xNMMMMMMMMMMWd..,;..,OWMMMMMMMMMMWo.'kMMMMMMMMMMNd'.,'.,kWMMMMMM"
    line[4] = "MMMMMMMMMMMMMMMMMMMMMd  cKd. ;XMMMMMMMMMMX; .xO; .OMMMMMMMMMMWl  cKx. :XMMMMMMMMMMWl .xMMMMMMMMMMXd:d0o. :NMMMMMM"
    line[5] = "MMMMMMMMMMMMMMMMMMMMMd  oMO. ;XMMMMMMMMMM0' .;c;':0MMMMMMMMMMWl  dM0' ,KMMMMMMMMMMWl .xMMMMMMMMMMNkc;:,  :NMMMMMM"
    line[6] = "MMMMMMMMMMMMMMMMMMMMMd  oMO. ;XMMMMMMMMMMK, 'OXxcoXMMMMMMMMMMWl  oWO. ;XMMMMMMMMMMWl .xMMMMMMMMMMk. :Kk. :NMMMMMM"
    line[7] = "MMMMMMMMMMMMMMMMMMMMMd. dMO. :XMMMMMMMMMMWx. ,;..lNMMMMMMMMMMWl  .;. .xWMMMMMMMMMMWl .xMMMMMMMMMMO' .c;. :XMMMMMM"
    line[8] = "MMMMMMMMMMMMMMMMMMMMMXkkXMNOx0WMMMMMMMMMMMWKkddx0WMMMMMMMMMMMWl .lkdxKWMMMMMMMMMMMWKxkXMMMMMMMMMMWKxdx0OxONMMMMMM"
    line[9] = "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMWd.'kMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[10] ="MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMN..WMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[11] ="MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMNXXWMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[12] ="\033[91mMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\033[0mMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
    line[13] ="\033[91mMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\033[0mMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM\n"

    for i in range(len(line)):
        for j in range(len(line[i])):
            if j < (len(line[i])-1):
                print(line[i][0:j], end = "\r")
            else:
                print(line[i][0:j], end = "\n")
        time.sleep(0.01)












































