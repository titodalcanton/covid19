import sys
import numpy as np
import pylab as pl


input_file = sys.argv[1] if len(sys.argv) > 1 else 'count_vs_time_it.txt'

counts = np.loadtxt(input_file)

time = np.arange(counts.shape[0])

pl.semilogy(time, counts[:,3], 'o')

pl.xlabel('Time')
pl.ylabel('Number of cases')
pl.title(input_file)

pl.show()
