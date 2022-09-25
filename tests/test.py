from memhole import memhole
import sys
import time

if(len(sys.argv) != 5):
    print("Usage: " + sys.argv[0] + " <pid> <address> <size> <runs>")
    sys.exit(1)

mh = memhole.Memhole()
print("Connect: " + str(mh.connect_memhole()))
print("Attach: " + str(mh.attach_to_pid(int(sys.argv[1]))))
print("Set memory position: " + str(mh.set_memory_position(int(sys.argv[2], 16))))

lengths = [1,
10,
100,
1000,
5000,
10000,
25000,
50000,
100000,
500000,
1000000,
5000000,
10000000,
100000000,
1000000000,
2000000000,
16000000000,
28000000000]

runs = int(sys.argv[4])

for leng in lengths:
    total = 0
    for i in range(0, runs):
        start = time.perf_counter_ns()
        mh.read_memory(leng)
        total += time.perf_counter_ns() - start

    print("Data length:" + f'{leng:,}')
    print("Average time: " + str(total / runs) + " ns")
    print("Speed: " + str(leng / (total / runs) * 1000) + " MB/s\n")

print("Disconnect: " + str(mh.disconnect_memhole()))


