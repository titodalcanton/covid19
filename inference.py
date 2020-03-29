import sys
from datetime import date, timedelta
import numpy as np
import pylab as pl
import emcee
from scipy.stats import logistic
import corner


def model(t, params):
    return params[2] * logistic.cdf(t, loc=params[0], scale=params[1])

def ln_prob(params, time, counts):
    # inflexion point is limited to 1 year:
    # after that it will essentially never end
    if params[0] <= 0 or params[0] > 365:
        return -np.inf

    if params[1] <= 0:
        return -np.inf

    # final cases is limited to the entire population
    if params[2] <= 0 or params[2] > 60e6:
        return -np.inf

    if params[3] <= 0:
        return -np.inf

    preds = model(time, params)
    if np.any(np.isnan(preds)):
        return -np.inf

    # FIXME this is a simple Gaussian likelihood,
    # not appropriate for a correlated count time series
    lnp = -np.sum((counts - preds) ** 2) / 2 / params[3] - len(time) // 2 * np.log(2 * np.pi * params[3])
    return lnp

def starting_point():
    loc = np.random.uniform(1, 365)
    scale = abs(4 + np.random.normal(0, 2))
    amp = 10 ** np.random.uniform(np.log10(90000), np.log10(60e6))
    variance = np.random.uniform(0, 10000)
    return [loc, scale, amp, variance]


input_file = sys.argv[1] if len(sys.argv) > 1 else 'count_vs_time_it.txt'

data = np.loadtxt(input_file)

start_date = date(2000 + int(data[0,2]), int(data[0,0]), int(data[0,1]))

time = np.arange(data.shape[0])
counts = data[:,3]

mask = counts > 10

param_names = ['inf_time', 'scale', 'final_cases', 'variance']

ndim, nwalkers = len(param_names), 200
p0 = np.array([starting_point() for _ in range(nwalkers)])

sampler = emcee.EnsembleSampler(nwalkers, ndim, ln_prob,
                                args=[time[mask], counts[mask]])

# burn in
print('Burn in')
state = sampler.run_mcmc(p0, 30000)
sampler.reset()

# production run
print('Production sampling')
sampler.run_mcmc(state[0], 10000)

# check
maf = np.mean(sampler.acceptance_fraction)
print("Mean acceptance fraction: {0:.3f}".format(maf))

# trim samples
chain = sampler.chain[:,::100,:]

# plot chain evolution
for p in range(ndim):
    pl.figure()
    for w in range(nwalkers):
        pl.plot(chain[w,:,p], '-', color='C0', alpha=0.1)
    pl.xlabel('Step')
    pl.ylabel(param_names[p])
    pl.savefig('chains_{}.png'.format(param_names[p]), dpi=200)

# plot data and model
pl.figure()

t = np.arange(200)
samples_loc = chain[:,:,0].ravel()
samples_scale = chain[:,:,1].ravel()
samples_amp = chain[:,:,2].ravel()
for j in range(100):
    i = int(np.random.uniform(0, len(samples_loc)))
    label = 'Model' if j == 0 else None
    preds = model(t, (samples_loc[i], samples_scale[i], samples_amp[i]))
    pl.plot(t, preds, '-', color='C1', alpha=0.1, label=label)

pl.plot(time, counts, '.', color='C0', label='Data')

pl.axvspan(np.percentile(samples_loc, 5),
           np.percentile(samples_loc, 95),
           facecolor='C2', edgecolor='none', alpha=0.25)

pl.axhspan(np.percentile(samples_amp, 5),
           np.percentile(samples_amp, 95),
           facecolor='C2', edgecolor='none', alpha=0.25)

pl.semilogy()
pl.ylim(0.9, 70e6)
pl.legend()
pl.xlabel('Time (days since {})'.format(start_date.strftime('%Y-%m-%d')))
pl.ylabel('Number of cases')
pl.savefig('cases_vs_time.png', dpi=200)

# plot marginal posterior for inflection point
pl.figure()
pl.hist(samples_loc, 500, histtype='stepfilled')
pl.xlabel('Inflection point (days since {})'.format(start_date.strftime('%Y-%m-%d')))
p5 = start_date + timedelta(days=np.percentile(samples_loc, 5))
p95 = start_date + timedelta(days=np.percentile(samples_loc, 95))
title = '90% interval: {} - {}'.format(p5.strftime('%Y-%m-%d'),
                                        p95.strftime('%Y-%m-%d'))
pl.title(title)
pl.savefig('inflection_time.png', dpi=200)

# plot marginal posterior for asymptotic number of cases
pl.figure()
pl.hist(samples_amp, 500, histtype='stepfilled')
pl.xlabel('Asymptotic number of cases')
title = '90% interval: {:.0f} - {:.0f}'.format(np.percentile(samples_amp, 5),
                                                np.percentile(samples_amp, 95))
pl.title(title)
pl.savefig('asymptotic_cases.png', dpi=200)

# posterior corner plot
ca = np.vstack((np.log10(samples_loc),
                np.log10(samples_scale),
                np.log10(samples_amp))).T
corner.corner(ca, bins=200, color='C0',
              labels=['log_10(' + pn + ')' for pn in param_names[:3]])
pl.savefig('corner.png', dpi=200)
