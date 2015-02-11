meds=['DES0456-2345.txt', 'DES0456-2348.txt']
m=MedsSplitter(meds=meds,chunksize=3)
j=Job()
j.splitter=m
j.submit()

