# harris.py: download, parse, and read the Harris Milky-Way globular cluster catalog
import os, os.path
import numpy
import pandas
from galdyncourse_util.load import _download_file
from galdyncourse_util.load import cache
_HARRIS_URL= 'http://physwww.mcmaster.ca/~harris/mwgc.dat'
def read(verbose=False):
    """
    NAME:
       read
    PURPOSE:
       read and parse the Harris Milky-Way globular cluster catalog
    INPUT:
       verbose= (False) if True, print some progress updates
    OUTPUT:
       pandas DataFrame with the catalog
    HISTORY:
       2017-07-26 - Started - Bovy (UofT)
    """
    filePath= os.path.join(cache._CACHE_HARRIS_DIR,'mwgc.dat')
    _download_harris(filePath,verbose=verbose)
    with open(filePath,'r') as harrisfile:
        lines= harrisfile.readlines()
        # 1st part: 72-229, 2nd part: 252-409, 3rd part: 433-590
        ids= lines[72:229]
        metals= lines[252:409]
        vels= lines[433:590]
        # Parse into dict
        ids_dict= {'ID': [],
                   'Name': [],
                   'RA': numpy.empty(len(ids)),
                   'DEC': numpy.empty(len(ids)),
                   'L': numpy.empty(len(ids)),
                   'B': numpy.empty(len(ids)),
                   'R_Sun': numpy.empty(len(ids)),
                   'R_gc': numpy.empty(len(ids)),
                   'X': numpy.empty(len(ids)),
                   'Y': numpy.empty(len(ids)),
                   'Z': numpy.empty(len(ids)),
                   '[Fe/H]': numpy.empty(len(ids)),
                   'wt': numpy.empty(len(ids)),
                   'E(B-V)': numpy.empty(len(ids)),
                   'V_HB': numpy.empty(len(ids)),
                   '(m-M)V': numpy.empty(len(ids)),
                   'V_t': numpy.empty(len(ids)),
                   'M_V,t': numpy.empty(len(ids)),
                   'U-B': numpy.empty(len(ids)),
                   'B-V': numpy.empty(len(ids)),
                   'V-R': numpy.empty(len(ids)),
                   'V-I': numpy.empty(len(ids)),
                   'spt': ['---' for ii in range(len(ids))],
                   'ellip': numpy.empty(len(ids)),
                   'v_r': numpy.empty(len(ids)),
                   'v_r_unc': numpy.empty(len(ids)),
                   'v_LSR': numpy.empty(len(ids)),
                   'sig_v': numpy.empty(len(ids)),
                   'sig_v_unc': numpy.empty(len(ids)),
                   'c': numpy.empty(len(ids)),
                   'r_c': numpy.empty(len(ids)),
                   'r_h': numpy.empty(len(ids)),
                   'mu_V': numpy.empty(len(ids)),
                   'rho_0': numpy.empty(len(ids)),
                   'lg(tc)': numpy.empty(len(ids)),
                   'lg(th)': numpy.empty(len(ids)),
                   'core_collapsed': numpy.zeros(len(ids),dtype='bool')}
        # Parse first part
        rest_keys= ['L','B','R_Sun','R_gc','X','Y','Z']
        for ii in range(len(ids)):
            # Parse ID and Name
            ids_dict['ID'].append(ids[ii][:10].strip())
            name= ids[ii][10:25].strip()
            if name == '': ids_dict['Name'].append('---')
            else: ids_dict['Name'].append(name)
            # Parse RA and Dec, Harris (l,b) don't seem exactly right...
            hms= ids[ii][25:36].split() # hour, min, sec
            ids_dict['RA'][ii]=\
                int(hms[0])*15.+int(hms[1])/4.+float(hms[2])/240.
            hms= ids[ii][38:49].split() # deg, arcmin, arcsec
            sgn= -1 if ids[ii][38] == '-' else 1
            ids_dict['DEC'][ii]=\
                int(hms[0])+sgn*(int(hms[1])/60.+float(hms[2])/3600.)
            # Split the rest
            rest= ids[ii][49:].split()
            for r,k in zip(rest,rest_keys): ids_dict[k][ii]= float(r.strip())
        # Parse second part
        idx_arr= numpy.arange(len(ids))
        for ii in range(len(metals)):
            # Not sure whether I can assume that they are in order
            idname= metals[ii][:10].strip()
            idx= idx_arr[\
                numpy.core.defchararray.equal(ids_dict['ID'],idname)][0]
            ids_dict= _parse_float_entry(ids_dict,'[Fe/H]',idx,
                                         metals[ii][13:18].strip())
            ids_dict= _parse_float_entry(ids_dict,'wt',idx,
                                         metals[ii][19:21].strip())
            ids_dict= _parse_float_entry(ids_dict,'E(B-V)',idx,
                                         metals[ii][24:28].strip())
            ids_dict= _parse_float_entry(ids_dict,'V_HB',idx,
                                         metals[ii][29:34].strip())
            ids_dict= _parse_float_entry(ids_dict,'(m-M)V',idx,
                                         metals[ii][35:40].strip())
            ids_dict= _parse_float_entry(ids_dict,'V_t',idx,
                                         metals[ii][42:46].strip())
            ids_dict= _parse_float_entry(ids_dict,'M_V,t',idx,
                                         metals[ii][48:53].strip())
            for k,si,ei in zip(['U-B','B-V','V-R','V-I'],
                               [56,62,68,74],[60,66,72,78]):
                ids_dict= _parse_float_entry(ids_dict,k,idx,
                                             metals[ii][si:ei].strip())
            ids_dict['spt'][idx]= metals[ii][80:82].strip()
            ids_dict= _parse_float_entry(ids_dict,'ellip',idx,
                                         metals[ii][86:].strip())
        # Parse third part
        idx_arr= numpy.arange(len(ids))
        for ii in range(len(vels)):
            # Not sure whether I can assume that they are in order
            idname= vels[ii][:10].strip()
            idx= idx_arr[\
                numpy.core.defchararray.equal(ids_dict['ID'],idname)][0]
            for k,si,ei in zip(['v_r','v_r_unc','v_LSR','sig_v','sig_v_unc',
                                'c','r_c','r_h','mu_V','rho_0',
                                'lg(tc)','lg(th)'],
                               [13,21,27,37,43,50,59,66,73,80,88,93],
                               [19,25,33,41,47,54,64,70,78,85,91,98]):
                ids_dict= _parse_float_entry(ids_dict,k,idx,
                                             vels[ii][si:ei].strip())
            if vels[ii][56] == 'c': ids_dict['core_collapsed'][idx]= True
        return pandas.DataFrame(ids_dict)                
        
def _parse_float_entry(ids_dict,key,idx,val):
    try:
        ids_dict[key][idx]= float(val)
    except ValueError:
        ids_dict[key][idx]= numpy.nan
    return ids_dict

def _download_harris(filePath,verbose=False):
    if not os.path.exists(filePath):
        _download_file(_HARRIS_URL,filePath,verbose=verbose)
    return None
