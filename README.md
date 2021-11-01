# subb a nice wrapper for python's subprocess module

I am often using python as a scripting language, now shelling out to external programs is probably the most common thing done by a script. 
Python has the [subprocess module](https://docs.python.org/3/library/subprocess.html) for this task, which has a very general interface. 
I think it is not very well suitable for a quick script.

That's why I often find myself writing a wrapper object for the submodule process. Now the ```subb``` package is supposed to be a general wrapper that would cover most use cases.

## The interface

The ```subb.RunCommand``` class is exported,  The ```RunCommand.run``` method runs one process, and waits for it to terminate. Upon completion of the run, you have the following members set: ```output``` - standart output, ```error``` standard error, ```status``` the ```status.exit_code``` is the status of the command.

The ```subb.RunCommand``` constructor is receiving options for each call to the ```run``` method.

See the [test](https://github.com/MoserMichael/subb/blob/master/test.py) for example usages







