# turtle_back_zoo
The Turtleback Zoo is interested in an online application program interface that is easy to use so that they do not have to spend time unnecessarily to train their employees.

`
export FLASK_APP=turtlezoo.py`

#for debug mode
`export FLASK_DEBUG=1` 


python 3.10  and above deletes the local lib file, just in case you come across a  DYLD_LIBRARY missing, run this command

`export DYLD_LIBRARY_PATH=/usr/local/mysql/lib`



**kill server**

`sudo lsof -i -P | grep LISTEN | grep 5000`

`kill -9 PID`