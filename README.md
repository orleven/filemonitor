# filemonitor Client 
---------------------------

Current Release: v0.2 (2016.10.21)

# Overview
---------------------------
file monitor client for **python2.7**

# Operating Systems supported
---------------------------

- Windows XP/7/8/10
- GNU/Linux


# Features
---------------------------

- file monitor 
- daemon
- backup
- restore
- heartbeat
- check
- rapaire
- transfer 
- remote


# Install 
---------------------------

### Windows
install pywin32-217.win32-py2.7.exe    
install pycrypto-2.6.win32-py2.7.exe  
install python module e.g. request  

### Linux 

install python module e.g. request,pyinotify,pycrypto

# Run 
---------------------------
**Please Run No Daemon where you first use the script.**

### linux(No Daemon):
```
python promain.py
```


### linux(Daemon):

```
# start 
python lindaemain.py start
# stop 
python lindaemain.py stop
# restart 
python lindaemain.py restart
```

### windows(No Daemon):
```
python promain.py
```

### windows(Daemon):
```
# install service
python windaemain.py install
# start service
python windaemain.py start
# restart service
python windaemain.py restart
# stop service
python windaemain.py stop
# remove service
python windaemain.py remove
```


# Startup
---------------------------
### linux:
```
# linux Startup£¬need root
sudo vi /etc/rc.d/rc.local  
# Add the following command before "exit", and save it.
su username -c "/usr/bin/python  path_for_lindaemain.py start "
```

### windows:
```
python PythonService.py --startup auto install  
```


