import asyncio
import time
from threading import Thread
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor
import os
COUNT = 500_000_000
i_o_count = 10
cpu_count = 10
MAX_THREAD = 5
CPU_WORKER = os.cpu_count()-1

def print_time_report(i_o_total_time,cpu_total_time,total_time):
    print(
        f"\nI-O Tasks in: {i_o_total_time:.2f} seconds. {(i_o_total_time / total_time) * 100:.2f}% of total time",
    )
    print(
        f"CPU Tasks in: {cpu_total_time:.2f} seconds. {(cpu_total_time / total_time) * 100:.2f}% of total time",
    )
    print(
        f"\nTotal execution time: {total_time:.2f} seconds. {(total_time / total_time) * 100:.2f}% of total time",
    )

async def func1():
    print("func1 started!")
    await asyncio.sleep(10)
    print("func1 finished!!")
    return "This is func1 result."

async def func2():
    print("func2 started!")
    await asyncio.sleep(1)
    print("func2 finished!!")
    return "This is func2 result."

async def execute():
    task1 = asyncio.create_task(func1())
    task2 = asyncio.create_task(func2())
    # await asyncio.sleep(1.5)
    res1 = await task1
    print("Task 1 is fully finished!")
    res2 = await task2
    print("Task 2 is fully finished!")
    print(f"Results: {[res1,res2]}")

# async I/O bound function
async def async_i_o_bound_func(index: int)->str:
    print(f"async_i_o_bound_func with index:{index} has started!")
    await asyncio.sleep(3)
    print(f"async_i_o_bound_func with index:{index} has finished!")
    return f"async_i_o_bound_func({index})"

async def async_i_o_bound_func_semaphore(index: int, semaphore: asyncio.Semaphore)->str:
    print(f"async_i_o_bound_func with index:{index} has started!")
    async with semaphore:
        await asyncio.sleep(3)
    print(f"async_i_o_bound_func with index:{index} has finished!")
    return f"async_i_o_bound_func({index})"


# sync I/O bound function
def sync_i_o_bound_func(index: int)->str:
    print(f"sync_i_o_bound_func with index:{index} has started!")
    time.sleep(5)
    print(f"sync_i_o_bound_func with index:{index} has finished!")
    return f"sync_i_o_bound_func({index})"

# async CPU bound function
async def async_process_count_down(n: int, index:int)->str:
    print(f"async_process_count_down with index:{index} has started!")
    while n>0:
        n -= 1
    print(f"async_process_count_down with index:{index} has finished!")
    return f"async_process_count_down({index})"

# sync CPU bound function
def sync_process_count_down(n: int, index:int)->str:
    print(f"sync_process_count_down with index:{index} has started!")
    while n>0:
        n -= 1
    print(f"sync_process_count_down with index:{index} has finished!")
    return f"sync_process_count_down({index})"

def sync_execute():
        
    start_time = time.perf_counter()
    for index in range(i_o_count):
        res = sync_i_o_bound_func(index)

    proc_start_time = time.perf_counter()    
    for index in range(cpu_count):
        res = sync_process_count_down(COUNT/cpu_count,index)

    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)
    

async def async_execute():    
    i_o_tasks = [asyncio.create_task(async_i_o_bound_func(index)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    # for task in i_o_tasks:
    #     res = await task
    results = await asyncio.gather(*i_o_tasks, return_exceptions=True)
    proc_start_time = time.perf_counter()
    cpu_tasks = [asyncio.create_task(async_process_count_down(COUNT/cpu_count,index)) for index in range(cpu_count)]
    results2 = await asyncio.gather(*cpu_tasks,return_exceptions=True)
    

    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)

def sync_execute_multi_thread_on_i_o_v1():
    i_o_threads = [Thread(target=sync_i_o_bound_func,args=(index,)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    for thread in i_o_threads:
        thread.start()
    for thread in i_o_threads:
        thread.join()
    proc_start_time = time.perf_counter()
    for index in range(cpu_count):
        res = sync_process_count_down(COUNT/cpu_count,index)

    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)

async def async_execute_multi_thread_on_i_o_v1():
    i_o_tasks = [asyncio.create_task(asyncio.to_thread(sync_i_o_bound_func,index)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    # for task in i_o_tasks:
    #     await task
    results = await asyncio.gather(*i_o_tasks,return_exceptions=True)
    proc_start_time = time.perf_counter()
    for index in range(cpu_count):
        res = sync_process_count_down(COUNT/cpu_count,index)

    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)

def sync_execute_multi_thread_multi_process_on_i_o():
    i_o_threads = [Thread(target=sync_i_o_bound_func,args=(index,)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    for thread in i_o_threads:
        thread.start()
    for thread in i_o_threads:
        thread.join()
    
    cpu_processes = [Process(target=sync_process_count_down,args=(COUNT/cpu_count,index)) for index in range(cpu_count)]
    proc_start_time = time.perf_counter()
    for cpu_process in cpu_processes:
        cpu_process.start()
    for cpu_process in cpu_processes:
        cpu_process.join()
    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)

async def async_execute_multi_thread_multi_process_on_i_o():
    i_o_tasks = [asyncio.create_task(asyncio.to_thread(sync_i_o_bound_func,index)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    results = await asyncio.gather(*i_o_tasks,return_exceptions=True)
    loop = asyncio.get_running_loop()
    proc_start_time = time.perf_counter()
    with ProcessPoolExecutor(max_workers=CPU_WORKER) as executor:
        tasks = [loop.run_in_executor(executor,sync_process_count_down, COUNT/cpu_count,index) for index in range(cpu_count)]
        results = asyncio.gather(*tasks,return_exceptions=True)
    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)

async def async_execute_multi_thread_multi_process_on_i_o_semaphore():
    semaphore = asyncio.Semaphore(MAX_THREAD)
    i_o_tasks = [asyncio.create_task(async_i_o_bound_func_semaphore(index,semaphore)) for index in range(i_o_count)]
    start_time = time.perf_counter()
    results = await asyncio.gather(*i_o_tasks,return_exceptions=True)
    loop = asyncio.get_running_loop()
    proc_start_time = time.perf_counter()
    with ProcessPoolExecutor(max_workers=CPU_WORKER) as executor:
        tasks = [loop.run_in_executor(executor,sync_process_count_down, COUNT/cpu_count,index) for index in range(cpu_count)]
        results = asyncio.gather(*tasks,return_exceptions=True)
    finished_time = time.perf_counter()
    i_o_total_time = proc_start_time - start_time
    cpu_total_time = finished_time - proc_start_time
    total_time = finished_time - start_time
    print_time_report(i_o_total_time,cpu_total_time,total_time)
    
if __name__ == "__main__":
    # asyncio.run(execute())
    # sync_execute()
    # asyncio.run(async_execute())
    # sync_execute_multi_thread_on_i_o_v1()
    # asyncio.run(async_execute_multi_thread_on_i_o_v1())
    # sync_execute_multi_thread_multi_process_on_i_o()
    asyncio.run(async_execute_multi_thread_multi_process_on_i_o_semaphore())
    