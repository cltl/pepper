NAOQI_PATH="$(cd ../lib; pwd)"

export DYLD_FALLBACK_LIBRARY_PATH=${NAOQI_PATH}/pynaoqi-python2.7-2.5.5.5-mac64/lib
export PYTHONPATH=.:${NAOQI_PATH}/pynaoqi-python2.7-2.5.5.5-mac64/lib/python2.7/site-packages
