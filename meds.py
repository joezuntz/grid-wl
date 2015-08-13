import sys
from Ganga.GPI import Job, ArgSplitter, Executable, File, CREAM, jobSlice, File
from itertools import cycle
import os
import time
import collections
import itertools

def wait(j, status='submitted', seconds=5):
    while j.status==status:
        time.sleep(seconds)


CE_LIST=[
    "ce01.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce02.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce03.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce6.glite.ecdf.ed.ac.uk:8443/cream-sge-ecdf",
    "hepgrid5.ph.liv.ac.uk:8443/cream-pbs-long",
    "hepgrid6.ph.liv.ac.uk:8443/cream-pbs-long",
    "hepgrid97.ph.liv.ac.uk:8443/cream-pbs-long",
]

def flatten_jobs(jobs):
    js = []
    for job in jobs:
        if job.subjobs:
            js+=job.subjobs
        else:
            js.append(job)
    return js

def job_histogram_by_ce(jobs):
    key = lambda j: j.backend.CE
    jobs = flatten_jobs(jobs)
    jobs = sorted(jobs, key=key)
    for ce, js in itertools.groupby(jobs, key):
        print ce
        job_histogram(js)
        print

    

def job_histogram(jobs):
    js = flatten_jobs(jobs)
    counts = collections.defaultdict(int)
    for j in js:
        counts[j.status]+=1
    total = sum(counts.values())
    for status, count in counts.items():
        print '%.1f%% %s' % (count*100.0/total, status)


def test_job(ce_index=0):
    meds_file='DES2214+0126-r-meds-spect1.fits.fz'
    dataset='spect1'
    ini_file = File('params_disc.ini')
    cat = 'all'
    output = 'output'
    args=[dataset, meds_file,  cat, output, 1, 10000, ini_file]
    exe=Executable(exe=File("launch_and_run.sh"), args=args)
    backend=CREAM()
    ce = CE_LIST[ce_index]
    backend.CE = ce
    j=Job(application=exe, backend=backend, name='Test')
    return j



def make_args(meds, dataset, nsplit):
    arg_list = []
    cat = 'all'
    output='output'
    ini_file = File('params_disc.ini')
    for i in xrange(nsplit):
        args = [dataset, meds, cat, output, i, nsplit, ini_file]
        arg_list.append(args)
    return arg_list


def make_job(meds_file, dataset, nsplit, ce, debug=0):
    args = make_args(meds_file, dataset, nsplit)
    if debug:
        args = args[:debug]
    name=os.path.split(meds_file)[-1][:12]
    jobs = []
    for arg in args:
        exe=Executable(exe=File("launch_and_run.sh"), args=arg)
        backend=CREAM()
        backend.CE = ce
        j=Job(application=exe, backend=backend, name=name)
        jobs.append(j)
    return jobs

def make_job_set(meds_list, dataset, nsplit, CEs=CE_LIST, debug=0):
    meds_files = [line.strip() for line in open(meds_list) if not line.strip().startswith('#')]
    if debug:
        meds_files = meds_files[:debug]
    jobs = []
    for meds_file, ce in zip(meds_files, cycle(CEs)):
        job_group = make_job(meds_file, dataset, nsplit, ce, debug=debug) 
        jobs+=job_group
    return jobSlice(jobs)
