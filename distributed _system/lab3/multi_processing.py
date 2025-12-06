#!/usr/bin/env python3

# use libraries
from time import sleep, perf_counter
import multiprocessing

# program parameters
num_iterations = 15*10**7 # iterations of a compute task = x * 10^7
num_tasks = 2# number of tasks to be executed

# print header
print('=======================================\n\n')

# define task to be executed
def task():
    result = 0
    for _ in range(num_iterations):
        result += 1
    return result

if __name__ == '__main__':
    
    # measure starting time
    start_time = perf_counter()

    # create processes
    procs = []
    for n in range(1, 1 + num_tasks):
        p = multiprocessing.Process(target = task)
        procs.append(p)
           
    # start processes that each execute a task
    for p in procs:
        p.start()
        print(f'T={perf_counter() - start_time: 8.3f}s : New process started')
        sleep(0.1)

    # wait for the processes to complete
    for p in procs:
        p.join()
        print(f'T={perf_counter() - start_time: 8.3f}s : Process completed')
            
    # measure time again after all tasks completed and report overall duration
    end_time = perf_counter()

    print(f'It took {end_time- start_time: 0.3f} second(s) to complete.')

