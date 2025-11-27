#!/usr/bin/env python3

# use libraries
from time import sleep, perf_counter
from threading import Thread

# program parameters
sleep_time = 5 # duration of a task
num_tasks = 10 # number of tasks to be executed

# print header
print('=======================================')
print('START X : Starting the task with ID X')
print('END X : The task with ID X completed')
print('=======================================\n\n')

# define task to be executed
def task(id):
    print(f'T={perf_counter() - start_time: 8.3f}s : START {id}')
    sleep(sleep_time)
    print(f'T={perf_counter() - start_time: 8.3f}s : END {id}')

# measure starting time
start_time = perf_counter()

# create threads
threads = []
for n in range(1, 1 + num_tasks):
    t = Thread(target = task, args = (n,))
    threads.append(t)

# start threads that each execute a task
for t in threads:
    t.start()
    sleep(0.1)

# wait for the threads to complete
for t in threads:
    t.join()

# measure time again after all tasks completed and report overall duration
end_time = perf_counter()

print(f'It took {end_time- start_time: 0.3f} second(s) to complete.')

