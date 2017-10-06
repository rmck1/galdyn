import sys
import os, os.path
import shutil
import subprocess
import tempfile
_MAX_NTRIES= 2
_ERASESTR= "                                                                                "
def _download_file(downloadPath,filePath,verbose=False,spider=False,
                   curl=False):
    sys.stdout.write('\r'+"Downloading file %s ...\r" \
                         % (os.path.basename(filePath)))
    sys.stdout.flush()
    try:
        # make all intermediate directories
        os.makedirs(os.path.dirname(filePath)) 
    except OSError: pass
    # Safe way of downloading
    downloading= True
    interrupted= False
    file, tmp_savefilename= tempfile.mkstemp()
    os.close(file) #Easier this way
    ntries= 1
    while downloading:
        try:
            if curl:
                cmd= ['curl','%s' % downloadPath,
                      '-o','%s' % tmp_savefilename,
                      '--connect-timeout','10',
                      '--retry','3']
            else:
                cmd= ['wget','%s' % downloadPath,
                      '-O','%s' % tmp_savefilename,
                      '--read-timeout=10',
                      '--tries=3']
            if not verbose and curl: cmd.append('-silent')
            elif not verbose: cmd.append('-q')
            if not curl and spider: cmd.append('--spider')
            subprocess.check_call(cmd)
            if not spider or curl: shutil.move(tmp_savefilename,filePath)
            downloading= False
            if interrupted:
                raise KeyboardInterrupt
        except subprocess.CalledProcessError as e:
            if not downloading: #Assume KeyboardInterrupt
                raise
            elif ntries > _MAX_NTRIES:
                raise IOError('File %s does not appear to exist on the server ...' % (os.path.basename(filePath)))
            elif not 'exit status 4' in str(e):
                interrupted= True
            os.remove(tmp_savefilename)
        finally:
            if os.path.exists(tmp_savefilename):
                os.remove(tmp_savefilename)
        ntries+= 1
    sys.stdout.write('\r'+_ERASESTR+'\r')
    sys.stdout.flush()        
    return None
