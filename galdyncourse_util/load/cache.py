# cache.py: functions to deal with caching for galdyncourse_util
import os, os.path
_CACHE_BASEDIR= os.path.join(os.getenv('HOME'),'.galdyncourse','cache')
_CACHE_RAW_ARXIV_DIR= os.path.join(_CACHE_BASEDIR,'arxiv_raw')
_CACHE_HARRIS_DIR= os.path.join(_CACHE_BASEDIR,'harris')
