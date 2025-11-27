#!/usr/bin/env python3

from time import sleep
import threading

# global counter variable
global_counter = 0

# create a lock object
lock = threading.Lock()

def add_value(increment):
    global global_counter

    # enter exclusive section
    lock.acquire()

    # critical section
    local_value = global_counter
    local_value += increment
    sleep(0.1)
    global_counter = local_value

    print(f"Thread adding {increment}: counter now = {global_counter}")

    # leave exclusive section
    lock.release()

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
