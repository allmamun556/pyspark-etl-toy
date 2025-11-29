#!/usr/bin/env python3

# use libraries
from time import sleep, perf_counter

# program parameters
num_iterations = 12*10**7 # iterations of a compute task = x * 10^7
num_tasks = 1 # number of tasks to be executed

# print header
print('=======================================')
print('START X : Starting the task with ID X')
print('END X : The task with ID X completed')
print('=======================================\n\n')

# define task to be executed
def task(id):
    result = 0
    print(f'T={perf_counter() - start_time: 8.3f}s : START {id}')
    for _ in range(num_iterations):
        result += 1
    print(f'T={perf_counter() - start_time: 8.3f}s : END {id}')
    return result
    
# measure starting time
start_time = perf_counter()

# execute tasks
for n in range(1, 1 + num_tasks):
    task(n)
    sleep(0.1)

# measure time again after all tasks completed and report overall duration
end_time = perf_counter()

print(f'It took {end_time- start_time: 0.3f} second(s) to complete.')

