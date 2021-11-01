#!/usr/bin/env python3
import os
import unittest
import sys
import subby

def show_pid():
    print("subprocess pid: ", os.getpid())

class TestSubby(unittest.TestCase):

    def test_trace_on(self):
        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_WITH_TIMESTAMP)

        cmd.run("ls -al")

        cmd.run("openssl rand -hex 9")

        cmd.run("git ls-files")

    def test_exit_on_error(self):
        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_ON, exit_on_error = True)

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
        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_ON, exit_on_error = True, convert_to_text = None)

        in_plain = b'123123'

        cmd.run("openssl enc -e -aes-256-ecb -pass pass:blabla", in_plain)

        self.assertTrue( isinstance(cmd.output, bytes) )

        enc = cmd.output

        cmd.run("openssl enc -d -aes-256-ecb -pass pass:blabla", enc)

        self.assertTrue( isinstance( cmd.output, bytes) )

        print("in_plain", bytes.hex(in_plain), "result: ", bytes.hex(cmd.output))
        self.assertTrue( bytes.hex(in_plain) == bytes.hex(cmd.output), "match encryption results")

    def test_binary_out(self):

        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_ON, exit_on_error = True, convert_to_text = None)

        cmd.run("openssl rand 16")

        self.assertTrue( isinstance(cmd.output, bytes), "hex output expected")

        self.assertTrue( len(cmd.output) == 16 )

    def test_use_shell(self):

        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_ON, use_shell = True, exit_on_error = True)

        cmd.run("""find . -name "*.py" | grep -c subby.py""")

        print("shell output: ", cmd.output)
        self.assertTrue( cmd.output.rstrip() == "1" )

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

        posix_opts = subby.PlatformOptionsPosix( pass_fds=(read_end,) )
        cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_ON, platform_option=posix_opts, env=env)
        cmd.run("python3 read.py")

        print("posix test output: ", cmd.output)
        self.assertTrue(cmd.output == "message from parent: " + key + "\n")


if __name__ == '__main__':
    unittest.main()
    print("*** eof test ***")
