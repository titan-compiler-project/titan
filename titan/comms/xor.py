import random

# simple sanity check script to calculate XOR checksums

def main():

    usr_input = input("enter hex (dont add 0x): ")

    # remove whitespace
    usr_input = usr_input.replace(" ", "")

    # append zero if odd number of values
    # might not be necessary but it makes it easier to loop through stuff
    if len(usr_input) % 2 != 0:
        usr_input = "0" + usr_input

        # debug stuff
        # for x in range(0, len(usr_input)-1, 2):
        #     print(f"{usr_input[x]}{usr_input[x+1]}", end=" ")

        # print()

    
    byte_list = []

    for x in range(0, len(usr_input), 2):
        byte_list.append(int(usr_input[x] + usr_input[x+1], 16))

    checksum = 0
    for byte in byte_list:
        print(hex(byte), end=" ")

        checksum ^= byte
    print()
    print(f"checksum: {hex(checksum)} ({checksum})")

if __name__ == "__main__":
    main()