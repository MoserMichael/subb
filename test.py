#!/usr/bin/env python3 
import subby

cmd = subby.RunCommand(trace_on=subby.RunCommand.TRACE_WITH_TIMESTAMP) 

cmd.run("ls -al")

cmd.run("openssl rand -hex 9")

cmd.run("git ls-files")


