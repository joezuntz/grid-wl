import Ganga.GPI
import itertools
import os
import re
import sys
import collections

CE_LIST=[
    "ce01.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce02.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce03.tier2.hep.manchester.ac.uk:8443/cream-pbs-long",
    "ce6.glite.ecdf.ed.ac.uk:8443/cream-sge-ecdf",
    "hepgrid5.ph.liv.ac.uk:8443/cream-pbs-long",
    "hepgrid6.ph.liv.ac.uk:8443/cream-pbs-long",
    "hepgrid97.ph.liv.ac.uk:8443/cream-pbs-long",
]



class MedsJobs(object):
    def __init__(self, run_name, group, ini='params_disc.ini', nsplit=100, ce_list=None, debug=0, local=False):
        self.group = group
        self.run_name = run_name
        self.tree = Ganga.GPI.jobtree
        self.ini_file = ini
        self.debug=debug
        self.local=local

        if ce_list is None:
            self.CEs = itertools.cycle(CE_LIST)
        else:
            self.CEs = itertools.cycle(ce_list)

        self.nsplit=nsplit


        self.root = '/'+run_name + '/' + self.group + '/'
        self.tree.mkdir(self.root)

    def add_meds(self, meds_file):  #can convert this to run a single tile

        #Make space for the job
        tile_name=os.path.split(meds_file)[-1][:12]

        #CE to use
        ce = self.CEs.next()

        #Fixed arguments
        cat = 'all'
        output='output'
        
        #The nsplit parameter controls two things:
        #  - the number of jobs we actually create
        #  - the number of jobs im3shape thinks there are 
        #    (which determines the number of galaxies run in each job)
        # The debug argument lets you cut the former down
        if self.debug:
            nsplit = self.debug
        else:
            nsplit = self.nsplit

        arg_sets = [[self.group, meds_file, cat, output, i, self.nsplit, self.ini_file] for i in xrange(nsplit)]
        splitter=Ganga.GPI.ArgSplitter(args=arg_sets)
        exe=Ganga.GPI.Executable(exe=Ganga.GPI.File("launch_and_run.sh"))
        if self.local:
            backend=Ganga.GPI.Local()
        else:
            backend=Ganga.GPI.CREAM()
            backend.CE = ce
        job=Ganga.GPI.Job(application=exe, backend=backend, name=tile_name, splitter=splitter)
        job.inputfiles = [Ganga.GPI.LocalFile(self.ini_file)]


        self.tree.add(job, self.root)
            
    def all_jobs(self):
        jobs = self.tree.getjobs(self.root)
        return jobs
    
    def submit(self):
        for job in self.all_jobs():
            job.submit()

    def add_list(self, meds_list):
        meds_files = [line.strip() for line in open(meds_list) if not line.strip().startswith('#')]
        for meds_file in meds_files:
            self.add_meds(meds_file)

    def status_histogram(self):
        jobs = flatten_jobs(self.all_jobs())
        job_histogram_by_ce(jobs)
        

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

