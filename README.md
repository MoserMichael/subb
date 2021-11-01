# subb a nice wrapper for python's subprocess module

I am often using python as a scripting language, now shelling out to external programs is probably the most common thing done by a script. 
Python has the [subprocess module](https://docs.python.org/3/library/subprocess.html) for this task, which has a very general interface. 
I think it is not very well suitable for a quick script.

That's why I often find myself writing a wrapper object for the submodule process. Now the ```subb``` package is supposed to be a general wrapper that would cover most use cases.

## install it

```pip3 install subb```


## The interface

The ```subb.RunCommand``` class is exported,  The ```RunCommand.run``` method runs one process, and waits for it to terminate. Upon completion of the run, you have the following members set: ```output``` - standart output, ```error``` standard error, ```status``` the ```status.exit_code``` is the status of the command.

The ```subb.RunCommand``` constructor is receiving options for each call to the ```run``` method.

See the [test](https://github.com/MoserMichael/subb/blob/master/test.py) for example usages


Now some examples:

### Basic test 

This shows the standard output of the commands, now optional argument ```trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP``` means that the command and its output are printed to standard error, just like  ```set -x``` in bash.

```
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP)

        cmd.run("ls -al")

        print("Command standard output: ", cmd.output)

        cmd.run("openssl rand -hex 9")

        print("Command standard output: ", cmd.output)

        cmd.run("git ls-files")

```

Option exit_on_error means that if the status of a command is not zero, then call ```sys.exit```, just like shell's ```set -e```

```
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, exit_on_error = True)

        got_exit = False
        try:
            cmd.run("false")
        except SystemExit as ex:
            print("caught SystemExit from run('false')", str(ex))
            got_exit = True

        self.assertTrue(got_exit)
```

Option ```convert_to_text``` is by default on, the output is converted to text (utf-8) if it is set to ```None```, then you get binary output

```
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, exit_on_error = True, convert_to_text = None)

        cmd.run("openssl rand 16")

        self.assertTrue( isinstance(cmd.output, bytes), "hex output expected")

```

The ```use_shell``` option is off by default, if you set it then the shell will be used to run the command

```
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, use_shell = True, exit_on_error = True)

        cmd.run("""find . -name "*.py" | grep -c subb.py""")

        print("shell output: ", cmd.output)
```

By default there is no timeout, but you can set one with the ```timeout_sec``` option

```
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP, timeout_sec=7)

        got_timeout = False
        try:
            cmd.run("python3 stuck.py")
        except subprocess.TimeoutExpired as exc:
            print("got timeout exception: ", exc)
            got_timeout = True

        self.assertTrue(got_timeout)
```


Platform specific options held in either ```subb.PlatformOptionsPosix``` or ```subb.PlatformOptionsWindows``` (arguments to constructors are just like the platform options is ```subprocess.Popen```, and passed via the ```platform_option``` option in RunCommand constructor.


```
        if sys.platform not in ("linux", "darwin"):
            return

        key = "secret secret"
        read_end, write_end = os.pipe()
        os.write(write_end, bytes(key, encoding='utf-8'))
        os.close(write_end)
        os.set_inheritable(read_end, True)

        print("parent read_fd: ", read_end)

        env = {**os.environ, "read_fd": str(read_end)}

        posix_opts = subb.PlatformOptionsPosix( pass_fds=(read_end,) )
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, platform_option=posix_opts, env=env)
        cmd.run("python3 read.py")

        print("posix test output: ", cmd.output)
        self.assertTrue(cmd.output == "message from parent: " + key + "\n")

```





