import shlex
import subprocess
from datetime import datetime
import sys
import logging

class KwArgsForwarder:

    def __init__(self, map_arg_name_to_type):
        self.map_arg_name_to_type = map_arg_name_to_type
        self.args = {}


    def check_params(self, **kwargs):
        for param_name, param_value in kwargs.items():
            if not param_name in self.map_arg_name_to_type:
                raise ValueError(f"parameter name {param_name} is not defined")
            expected_type = self.map_arg_name_to_type[param_name]
            if not isinstance( param_value, expected_type):
                raise TypeError(f"parameter {param_name} not of expected type {str(expected_type)}")

        self.args = {}
        for key, value in kwargs.items():
            self.args[key] = value

class PlatformOptionsWindows:
    def __init__(self, **kwargs):
        self.forwarder = KwArgsForwarder({ 'startupinfo': type(subprocess.STARTUPINFO), 'creationflags': type(int) })
        self.forwarder.check_params(**kwargs)

class PlatformOptionsPosix:
    def __init__(self,**kwargs):
        # preexec_fn - no longer supported in python 3.8
        #self.forwarder = KwArgsForwarder({ 'preexec_fn' : types.FunctionType,  'restore_signals': type(bool), 'start_new_session': type(bool), 'group' : type(str), 'user' : type(str),  })
        self.forwarder = KwArgsForwarder({ 'pass_fds' : type(()), 'restore_signals': type(bool), 'start_new_session': type(bool), 'group' : type(str), 'user' : type(str),  })
        self.forwarder.check_params(**kwargs)


class RunCommand:
    NO_TRACE=0
    TRACE_ON=2
    TRACE_WITH_TIMESTAMP=4
    TRACE_LOG_INFO=8
    TRACE_LOG_DEBUG=16

    def __init__(self, **kwargs):
        self.exit_code = 0
        self.command_line = ""

        if 'env' in kwargs:
            self.env = kwargs['env']
        else:
            self.env = None

        if 'use_shell' in kwargs:
            self.use_shell = kwargs['use_shell']
        else:
            self.use_shell = None

        if 'timeout_sec' in kwargs:
            self.timeout_seconds = kwargs['timeout_sec']
        else:
            self.timeout_seconds = None

        if 'trace_on' in kwargs:
            self.trace_on = kwargs['trace_on']
        else:
            self.trace_on = False

        if 'exit_on_error' in kwargs:
            self.exit_on_error = kwargs['exit_on_error']
        else:
            self.exit_on_error = False

        if 'convert_to_text' in kwargs:
            self.convert_to_text = kwargs['convert_to_text']
        else:
            self.convert_to_text = 'utf-8'

        if 'close_fds' in kwargs:
            self.close_fds = kwargs['trace_on']
        else:
            self.close_fds = False

        if 'platform_option' in kwargs:
            self.platform_option = kwargs['platform_option']
            if not isinstance(self.platform_option, PlatformOptionsWindows) and not isinstance(self.platform_option, PlatformOptionsPosix):
                print("invalid platform_option argument, must be either PlatformOptionsPosix or PlatformOptionsWindows")
                raise TypeError("allowed types: PlatformOptionsWindows or PlatformOptionsPosix")
        else:
            self.platform_option = None

        self.output = None
        self.error_out = None


    def run(self, command_line, in_arg = None):
        try:
            if self.trace_on:
                print(self.__show_trace_prefix() + command_line)


            if self.platform_option is not None:
                args = self.platform_option.forwarder.args
            else:
                args = {}

            with subprocess.Popen(
                self.__cmd(command_line),
                stdin=RunCommand.__stdin(in_arg),
                close_fds=self.close_fds,
                shell=self.use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env = self.env,
                **args
            ) as process:

                self.command_line = command_line

                (output, error_out) = process.communicate(
                        input=RunCommand.__input(in_arg),
                        timeout=self.timeout_seconds)

                self.exit_code = process.wait()
                if self.convert_to_text is not None:
                    self.output = output.decode(self.convert_to_text)
                else:
                    self.output = output

                if self.convert_to_text is not None:
                    self.error_out = error_out.decode(self.convert_to_text)
                else:
                    self.error_out = error_out

                self.exit_code = process.wait()

                if self.trace_on:
                    msg = self.__show_trace_prefix() + "exit_code: " + str(self.exit_code)
                    if self.output != "":
                        msg += "\n stdout:\n" + RunCommand.__output_rep(self.output)
                    if self.error_out != "":
                        msg += "\n  stderr:\n" + RunCommand.__output_rep(self.error_out)
                    self.__print_trace(msg)

                if self.exit_on_error and self.exit_code != 0:
                    self.__print_trace(self.__make_error_message())
                    sys.exit(1)

                return self.exit_code

        except subprocess.TimeoutExpired as exception:
            if self.trace_on:
                self.__print_trace(self.__show_trace_prefix() + "Timeout exception: " + str(exception))
            raise
        except FileNotFoundError:
            self.output = ""
            self.error_out = "file not found"

            if self.trace_on:
                self.__print_trace(self.__show_trace_prefix() + "file not found error")

            self.exit_code = 1
            return self.exit_code

    def result(self):
        return self.exit_code, self.output

    def __make_error_message(self):
        return_value = ""
        if self.command_line != "":
            return_value += f" command line: {self.command_line}."
        if self.exit_code != 0:
            return_value += f" exit status: {self.exit_code}. "
        if self.error_out != "":
            if isinstance(self.error_out,str):
                return_value += " " + self.error_out
            else:
                return_value += " " + bytes.hex(self.error_out)
        return return_value

    def __cmd(self, command_line):
        if self.use_shell is None or not self.use_shell:
            return shlex.split(command_line)
        return command_line
        #return shlex.quote(command_line)

    def __show_trace_prefix(self):
        if self.trace_on == RunCommand.TRACE_ON:
            return "> "
        if self.trace_on & RunCommand.TRACE_WITH_TIMESTAMP != 0:
            now_time = datetime.now()
            return now_time.strftime("%Z%Y-%b-%d %H:%M:%S.%f> ")
        return ""

    def __print_trace(self, msg):
        if self.trace_on & RunCommand.TRACE_LOG_INFO != 0:
            logging.info(msg)
        elif self.trace_on & RunCommand.TRACE_LOG_DEBUG != 0:
            logging.debug(msg)
        else:
            print(msg, file=sys.stderr)

    @staticmethod
    def __output_rep(rep):
        if not rep is None:
            if isinstance(rep,str):
                return str(rep)
            if isinstance(rep,bytes):
                return bytes.hex(rep)
        return None

    @staticmethod
    def __stdin(arg):
        if not arg is None:
            return subprocess.PIPE
        return None

    @staticmethod
    def __input(arg):
        if not arg is None:
            if isinstance(arg,str):
                return arg.encode("utf-8")
            if isinstance(arg,bytes):
                return arg
            raise TypeError("process input must be either string or bytes")
        return None
