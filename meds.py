import sys
from Ganga.GPI import Job, ArgSplitter, Executable, File, CREAM, jobSlice, File
from itertools import cycle

def test_job():
    meds_file='DES0541-5914-r-meds-spt-e-gold.fits.fz'
    ini_file = File('params_disc.ini')
    cat = File('cats/DES0541-5914.txt')
    args=[meds_file,  cat, "output", 1, 10000, ini_file]
    exe=Executable(exe=File("grid-wl/launch_and_run.sh"), args=args)
    ce='ce02.tier2.hep.manchester.ac.uk:8443/cream-pbs-long'
    backend=CREAM()
    backend.CE = ce
    j=Job(application=exe, backend=backend)
    return j



def make_args(meds, nsplit):
    arg_list = []
    for i in xrange(nsplit):
        args = [meds, "all", "output", i, nsplit]
        arg_list.append(args)
    return arg_list



def make_job(meds_file, nsplit, ce, debug=0):
    args = make_args(meds_file, nsplit)
    if debug:
        args = args[:debug]
    exe=Executable(exe=File("grid-wl/launch_and_run.sh"))
    backend=CREAM()
    backend.CE = ce
    return Job(application=exe, splitter=ArgSplitter(args=args), backend=backend)

def make_job_set(meds_list, nsplit, CEs, debug=0):
    meds_files = [line.strip() for line in open(meds_list) if not line.strip().startswith('#')]
    if debug:
        meds_files = meds_files[:debug]
    jobs = []
    for meds_file, ce in zip(meds_files, cycle(CEs)):
        job = make_job(meds_file, nsplit, ce, debug=debug) 
        jobs.append(job)
    return jobSlice(jobs)
