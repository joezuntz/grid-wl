#inputs.  could load the meds list from file easily
import sys
meds_list = sys.argv[1]
ini_file = sys.argv[2]

meds = [line.strip() for line in open(meds_list) if not line.strip().startswith('#')]


#meds=['DES0456-2345.txt', 'DES0456-2348.txt']
chunksize=3
catdir='cats'
ini=File(ini_file)

#create the basic job from the ini file
#and the main script.  The cat dir and meds files are
#not actually passed to jobs but used by the splitter
#to make the subjob tasks
exe=File("run_im3shape.sh")
args = [ini, catdir] + meds
app=Executable(exe=exe, args=args)
j=Job(application=app)


m=MedsSplitter(chunksize=3)
j.splitter=m

t=TextMerger()
t.files=['output.main.txt','output.epoch.txt']
t.ignorefailed=True
j.postprocessors=t

print j

