import os, os.path
import re
import subprocess
import numpy
import pandas
from galdyncourse_util.load import _download_file
from galdyncourse_util.load import cache
_ARXIV_URL= 'https://arxiv.org/e-print/'
_NON_DECIMAL= re.compile(r'[^\d.-]+')  # to strip non-numeric characters
def non_decimal_converter(s):
    try:
        return _NON_DECIMAL.sub('',s)
    except TypeError:
        return numpy.nan
def muticolumn_converter(s):
    try:
        return re.split('{',s)[3].split('}')[0]
    except IndexError:
        return s
def read_table_from_arxiv(eprint,tablename,
                          names=None,
                          skip_header=0,skip_footer=0,
                          converters=None,
                          na_values=None,
                          verbose=False):
    """
    NAME:
       read_table_from_arxiv
    PURPOSE:
       Read a table from arXiv; assumed to be a LaTeX table
    INPUT:
       eprint - eprint number (e.g., '1704.05063v2')
       tablename - name of the file in the arxiv source that holds the table
       names= (None) names of the columns (become keys of the dataframe)
       skip_header= (0) number of lines to skip before the table
       skip_footer= (0) number of lines to skip after the table
       converters= (None) see numpy.genfromtxt; galdyncourse.load.arxiv includes two converters that may be useful: non_decimal_converter which removes all characters but for [0-9].-  and muticolumn_converter which extracts multicolumn data
       na_values= (None) additional strings to treat as N/A
       verbose= (False) be verbose or not
    OUTPUT:
       pandas dataframe
    HISTORY:
       2017-07-24 - Written - Bovy (UofT)
    """
    download_source_from_arxiv(eprint,verbose=verbose)
    filePath= os.path.join(cache._CACHE_RAW_ARXIV_DIR,eprint,tablename)
    data= pandas.read_csv(filePath,
                          skiprows=skip_header,skipfooter=skip_footer,
                          header=None,na_values=na_values,
                          delimiter='&',converters=converters,names=names)
    return data
    
def download_source_from_arxiv(eprint,verbose=False):
    """
    NAME:
       download_source_from_arxiv
    PURPOSE:
       Download the full source for an article on arXiv
    INPUT:
       eprint - eprint number (e.g., '1704.05063v2')
       verbose= (False) be verbose or not
    OUTPUT:
       (none; just downloads and unpacks)
    HISTORY:
       2017-07-24 - Written - Bovy (UofT)
    """
    filePath= os.path.join(cache._CACHE_RAW_ARXIV_DIR,eprint,
                                eprint+'.tar.gz')
    if not os.path.exists(filePath):
        _download_file(_ARXIV_URL+eprint,filePath,
                       curl=True,verbose=verbose)
    # Untar.gz
    cmd= ['tar','xzf',filePath,'-C',os.path.dirname(filePath)]
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError("Untarring file %s downloaded from arXiv failed with error %s" % (filePath,e.strerror))
    return None

