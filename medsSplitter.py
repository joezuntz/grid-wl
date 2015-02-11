from Ganga.GPIDev.Adapters.ISplitter import ISplitter
from Ganga.GPIDev.Schema import *
from Ganga.GPIDev.Base.Proxy import addProxy, stripProxy

import re
import os

tile_pattern = re.compile(r'DES[0-9][0-9][0-9][0-9][+-][0-9][0-9][0-9][0-9]')
tile_band_pattern = re.compile(r'DES[0-9][0-9][0-9][0-9][+-][0-9][0-9][0-9][0-9][_-][ugrizy]')
run_pattern = re.compile(r'[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_DES[0-9][0-9][0-9][0-9][+-][0-9][0-9][0-9][0-9]')
great_des_pattern=re.compile(r"nbc(.)+\.meds\.([0-9][0-9][0-9])\.g([0-9][0-9])\.fits")


def find_tilename(name):
    m = tile_pattern.search(name)
    if m is None:
        m = great_des_pattern.search(name)
        if m is None:
            return "unknown"
    return m.group()

def read_uncommented(filename):
    lines = []
    for line in open(filename):
        line=line.strip()
        if not line.startswith('#'): lines.append(line)
    return lines

def split_chunks(x,n):
    chunks = [x[i:i+n] for i in xrange(0, len(x), n)]
    return chunks


class MedsSplitter(ISplitter):
    """
Split a collection of MEDS files up into chunks
    """
    _name = "MedsSplitter"
    _schema = Schema(Version(1,0), {
            'meds': SimpleItem(defvalue=[], 
                               typelist=None,
                               sequence=1,
                               checkset='_checksetNestedLists', 
                               doc='List of MEDS files to process'),
            'chunksize': SimpleItem(defvalue=500, 
                                    typelist=['int'],
                                    sequence=0,
                                    doc='Size of object chunks'),
            'catdir': SimpleItem(defvalue='cats',
                                 typelist=['str'],
                                 sequence=0,
                                 doc='Relative directory containing selection catalogs')
            })
    def split(self, job):
        subjobs = []
        try:
            os.mkdir('chunks')
        except OSError:
            pass
        cats = os.listdir(self.catdir)
        for meds in self.meds:
            for chunk_file in self.splitMeds(meds,cats):
                j=self.createSubjob(job)
                j.application.args = [meds,chunk_file]
                logger.debug('Made a job for meds file %s and chunk %s'%(meds,chunk_file))
                subjobs.append(j)
        return subjobs

    def splitMeds(self, meds, cats):
        #meds is the filename for a meds file.
        #cats is a list of catalog files

        #Find the name of the tile from the meds filename
        tile=find_tilename(meds)
        print "Splitting meds file:",meds, ' with tile: ', tile

        #In catdir, find the corresponding catalog file
        matching_cat=None
        for cat in cats:
            #print 'tile for cat %s = %s (want %s), %s' % (cat, find_tilename(cat), tile, tile==find_tilename(cat))
            if find_tilename(cat)==tile:
                matching_cat=cat
                break
        if matching_cat is None:
            raise ValueError("No catalog matches meds %s (tile %s)"%(meds,tile))

        #Read all the non-commented lines in catdir and
        cat_lines = read_uncommented('%s/%s'%(self.catdir,matching_cat))

        #split them into chunks of size chunksize
        chunks = split_chunks(cat_lines, self.chunksize)
        
        task_list = []
        #Save each chunk as a new file and save the name of this chunk file
        for c,chunk in enumerate(chunks):
            chunk_file='chunks/%s-%d.txt'%(meds,c)
            f=open(chunk_file,'w')
            for line in chunk:
                f.write(line)
                f.write("\n")
            task_list.append(chunk_file)

        return task_list
