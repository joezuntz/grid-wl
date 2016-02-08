import Ganga.GPI
import itertools
import os
import re
import sys
import collections
import itertools

creams = [line.strip() for line in open('working_ces.txt').readlines() if line.strip()]
cream_cycle = itertools.cycle(creams)

class MedsJobs(object):
    code_root='srm://gridpp09.ecdf.ed.ac.uk/dpm/ecdf.ed.ac.uk/home/gridpp/lsst/zuntz'
    output_root=code_root #'srm://gridpp09.ecdf.ed.ac.uk/dpm/ecdf.ed.ac.uk/home/gridpp/lsst/zuntz'
    data_root='srm://gridpp09.ecdf.ed.ac.uk/dpm/ecdf.ed.ac.uk/home/lsst'
    def __init__(self, tree_name, run_name, code_date, blacklist_file='blacklist-y1.txt', ini='params_bd.ini', nsplit=20, debug=0, local=False):
        self.run_name = run_name
        self.code_date = code_date
        self.tree = Ganga.GPI.jobtree
        self.blacklist_file=blacklist_file
        self.ini_file = ini
        self.debug=debug
        self.local=local
        self.nsplit=nsplit
        self.root='/'+tree_name
        self.tree.mkdir(self.root)

    def add_meds(self, tile_file): #e.g. tile_file='DES0001-4914-z-meds-y1a1-beta.fits.fz'
        run_name=self.run_name #e.g. "y1a1-v2-z"
        code_date=self.code_date #e.g. "2016-02-01"
        output_root=self.output_root
        code_root=self.code_root
        data_root=self.data_root
        split_count=self.nsplit
        ini=self.ini_file
        cat='all'
        import os
        tile_name = os.path.basename(tile_file)
        job_name='{0}.{1}.{2}'.format(run_name, code_date, tile_name)
        
        code_remote_path="{code_root}/{run_name}/software/{code_date}/im3shape-grid.tar.gz".format(**locals())        
        data_remote_path="{data_root}/{tile_file}".format(**locals())
        
        
        

        #The nsplit parameter controls two things:
        #  - the number of jobs we actually create
        #  - the number of jobs im3shape thinks there are 
        #    (which determines the number of galaxies run in each job)
        # The debug argument lets you cut the former down
        if self.debug:
            job_count = self.debug
        else:
            job_count = split_count

        # The arguments, a list, one for each sub-job
        #The list is of lists, containing the arguments to each subjob.
        arg_sets=[
            [code_remote_path, data_remote_path, 
             "{output_root}/{run_name}/results/{tile_file}.{job_rank}.{split_count}".format(**locals()),  #output path difference for each subjob
             ini, cat, job_rank, split_count,
             self.blacklist_file,
            ] 
            for job_rank in xrange(job_count)
        ]

        splitter=Ganga.GPI.ArgSplitter(args=arg_sets)
        exe=Ganga.GPI.Executable(exe=Ganga.GPI.File("launch_and_run.sh"))
        backend=self.get_backend()

        job=Ganga.GPI.Job(application=exe, backend=backend, name=job_name, splitter=splitter)
        job.inputfiles = [Ganga.GPI.LocalFile(self.ini_file), Ganga.GPI.LocalFile(self.blacklist_file)]

        self.tree.add(job, self.root)

    def get_backend(self):
        if self.local:
            backend=Ganga.GPI.Local()
        else:
            backend=Ganga.GPI.CREAM()
            backend.CE = self.get_cream()
        return backend

    def get_cream(self):
        return cream_cycle.next()
        #alter this to do dynamic selection
#        return 'grid002.jet.efda.org:8443/cream-pbs-gridpp'
            
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

def test_one():
    run_name="y1a1-v2-z"
    tree_name='run1'
    tile_file='DES2356-4831-z-meds-y1a1-alpha.fits.fz'
    code_date="2016-02-01" #for file path
    debug=5 #actual number of jobs created
    j=MedsJobs(tree_name, run_name, code_date, local=False, debug=debug)
    j.add_meds(tile_file)
    return j

def test_33():
    tree_name='run33'
    run_name="y1a1-v2-z"
    tile_file='DES2356-4831-z-meds-y1a1-alpha.fits.fz'
    code_date="2016-02-01" #for file path                                                                                                                                          
    j=MedsJobs(tree_name, run_name, code_date, local=False)
    tile_files = [line.strip() for line in open('meds-y1.txt').readlines() if line.strip()]
    tile_files = tile_files[:33]
    for tile_file in tile_files:
        j.add_meds(tile_file)


if __name__=="__main__":
    j = test()
#    j.submit()
