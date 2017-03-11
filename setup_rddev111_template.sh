
# Python Package directories
export FEB_DIR=${PWD}/../firmware/common/AtlasChess2Feb
export SURF_DIR=${PWD}/../firmware/submodules/surf
export ROGUE_DIR=${PWD}/rogue

# Setup enivorment
#source /afs/slac.stanford.edu/g/reseng/python/3.5.2/settings.csh
source /home/robmina/usr/local/python3/3.5.3/settings.sh
#source /afs/slac.stanford.edu/g/reseng/boost/1.62.0_p3/settings.csh
source /home/robmina/usr/local/boost/1.62.0_p3/settings.sh
#source /afs/slac.stanford.edu/g/reseng/zeromq/4.2.0/settings.csh
source /home/robmina/usr/local/zeromq/4.2.0/settings.sh
#source /afs/slac.stanford.edu/g/reseng/epics/base-R3-16-0/settings.csh
source /home/robmina/usr/local/epics/base-3.16.0.1

# Setup python path
export PYTHONPATH=${PWD}/python:${SURF_DIR}/python:${FEB_DIR}/python:${ROGUE_DIR}/python

# Setup library path
export LD_LIBRARY_PATH=${ROGUE_DIR}/python::${LD_LIBRARY_PATH}

# Setup library path
export LD_LIBRARY_PATH=${ROGUE_DIR}/python::${LD_LIBRARY_PATH}

# Setup root
source /home/robmina/usr/local/ROOT/6.08.00/bin/thisroot.sh
