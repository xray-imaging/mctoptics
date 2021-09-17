TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS BELOW HERE

# Build the IOC application
PROD_IOC = mctOpticsApp

# mctOpticsApp.dbd will be created and installed
DBD += mctOpticsApp.dbd

# test.dbd will include these files:
mctOpticsApp_DBD += base.dbd
mctOpticsApp_DBD += busySupport.dbd
mctOpticsApp_DBD += asSupport.dbd

# mctOpticsApp_registerRecordDeviceDriver.cpp derives from test.dbd
mctOpticsApp_SRCS += mctOpticsApp_registerRecordDeviceDriver.cpp

# Build the main IOC entry point where needed
mctOpticsApp_SRCS_DEFAULT += mctOpticsMain.cpp
mctOpticsApp_SRCS_vxWorks += -nil-

mctOpticsApp_LIBS += autosave
mctOpticsApp_LIBS += busy
#mctOpticsApp_LIBS += asyn

# Finally link IOC to the EPICS Base libraries
mctOpticsApp_LIBS += $(EPICS_BASE_IOC_LIBS)

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD EXTRA GNUMAKE RULES BELOW HERE
