import numpy as np
import threading
import time

def run_multithread(file_list, function, Num_Parallel=10, output_folder=None, verbose=True, replace=False):
    # To speed-up the download of data we use multithreading.
    # In this example, the field list is split into 10 parts and each part is processed using a different thread. This way we can download 10 fields in parallel
    # You may need to adapt this code by changing the "Num_Threads" and removing/adding a few 'process_x' lines below.
    Threads = np.arange(0, len(file_list)+1, 1) # The number of threads (each thread will be used to download a field)
    if verbose:
        print('# Number of fields:', len(file_list))
        print('# Number of simultaneous processes:', Num_Parallel)

    # Create a dictionary to store the processes (threads)
    Processes = {}

    # Populating the dictionary with the processes (one thread per item of the dictionary, each thread downloads a field)
    for i in range(len(Threads)-1):
        Processes[i] = threading.Thread(target=function, args=(file_list[Threads[i]: Threads[i+1]], output_folder, replace, verbose))

    # Starting the threads
    n=Num_Parallel
    start_total = time.time()
    for list_of_fields in np.array_split(np.arange(0, len(Threads)-1), np.ceil(len(Threads)/Num_Parallel)):
        start = time.time()
        if verbose:
            print('# Starting threads:', list_of_fields)
        for i in list_of_fields:
            Processes[i].start()
            time.sleep(1.5)

        for i in list_of_fields:
            Processes[i].join()

        if verbose:
            print('# Finished %s/%s threads. Total elapsed time: %s min' %(n, len(file_list), '{:,.3f}'.format((time.time()-start_total)/60)))
            velocity = Num_Parallel/((time.time()-start)/60)
            remaining_fields = len(file_list)-n
            if remaining_fields > 0:
                print('Expected remaining time for %s fields: %s min' % (remaining_fields, '{:,.3f}'.format(remaining_fields/velocity)))
                print()
        n=n+Num_Parallel
