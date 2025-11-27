#!/usr/bin/env python3

from time import sleep
import threading

# global counter variable (shared resource)
global_counter = 0

# the function that each thread runs
def add_value(increment):
    global global_counter

    # read global value into local variable
    local_value = global_counter

    # add increment
    local_value += increment

    # wait -> increases chance of race condition
    sleep(0.1)

    # write back result to global variable
    global_counter = local_value

    print(f"Thread adding {increment}: counter now = {global_counter}")

# create threads
t1 = threading.Thread(target=add_value, args=(10,))
t2 = threading.Thread(target=add_value, args=(20,))

# start threads
t1.start()
t2.start()

# wait for threads to finish
t1.join()
t2.join()

print(f"\nFinal global counter = {global_counter}")
