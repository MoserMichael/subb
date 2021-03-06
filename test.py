#!/usr/bin/env python3
import os
import unittest
import sys
import subprocess
import subb

class TestSubb(unittest.TestCase):

    def setUp(self):
        sys.stdout.flush()
        print("\n*** testing: ", self._testMethodName, "***\n")
        sys.stdout.flush()

    def tearDown(self):
        sys.stdout.flush()

    def test_trace_on(self):
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP)

        cmd.run("ls -al")

        cmd.run("openssl rand -hex 9")

        cmd.run("git ls-files")

    def test_trace_on_logger(self):
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP|subb.RunCommand.TRACE_LOG_INFO)

        cmd.run("ls -al")

        print("Command standard output: ", cmd.output)

        cmd.run("openssl rand -hex 9")

        print("Command standard output: ", cmd.output)

        cmd.run("git ls-files")


    def test_exit_on_error(self):

        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, exit_on_error = True)

        cmd.run("git branch -vv")

        cmd.run("true")

        got_exit = False
        try:
            cmd.run("false")
        except SystemExit as ex:
            print("caught SystemExit from run('false')", str(ex))
            got_exit = True

        self.assertTrue(got_exit)

    def test_binary_in_out(self):
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, exit_on_error = True, convert_to_text = None)

        in_plain = b'123123'

        cmd.run("openssl enc -e -aes-256-ecb -pass pass:blabla", in_plain)

        self.assertTrue( isinstance(cmd.output, bytes) )

        enc = cmd.output

        cmd.run("openssl enc -d -aes-256-ecb -pass pass:blabla", enc)

        self.assertTrue( isinstance( cmd.output, bytes) )

        print("in_plain", bytes.hex(in_plain), "result: ", bytes.hex(cmd.output))
        self.assertTrue( bytes.hex(in_plain) == bytes.hex(cmd.output), "match encryption results")

    def test_binary_out(self):

        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, exit_on_error = True, convert_to_text = None)

        cmd.run("openssl rand 16")

        self.assertTrue( isinstance(cmd.output, bytes), "hex output expected")

        self.assertTrue( len(cmd.output) == 16 )

    def test_use_shell(self):

        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_ON, use_shell = True, exit_on_error = True)

        cmd.run("""ls *.py | grep -c test.py""")

        print("shell output: ", cmd.output)
        self.assertTrue( cmd.output.rstrip() == "1" )

    def test_stderr_stdout(self):
        # is bash available on windows? not sure.
        if sys.platform not in ("linux", "darwin"):
            return

        cmd = subb.RunCommand(stderr_as_stdout=True)
        cmd.run("bash -x fac.sh")
        print("stderr and stdout:", cmd.output)

    def test_posix(self):
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

    def test_timeout(self):
        cmd = subb.RunCommand(trace_on=subb.RunCommand.TRACE_WITH_TIMESTAMP, timeout_sec=7)

        got_timeout = False
        try:
            cmd.run("python3 stuck.py")
        except subprocess.TimeoutExpired as exc:
            print("got timeout exception: ", exc)
            got_timeout = True

        self.assertTrue(got_timeout)



if __name__ == '__main__':
    #unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
    print("*** eof test ***")
