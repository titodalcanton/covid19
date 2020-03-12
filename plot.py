import numpy as np
import pylab as pl


counts = np.loadtxt('count_vs_time.txt')

time = np.arange(counts.shape[0])

pl.plot(time, counts[:,3], 'o')

pl.show()
