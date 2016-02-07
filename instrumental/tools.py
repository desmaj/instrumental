# 
# Copyright (C) 2012-2013  Matthew J Desmarais

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from optparse import OptionParser
import os
import sys

from instrumental.recorder import ExecutionRecorder
from instrumental.storage import ResultStore

usage = """instrumental-tools [options] COMMAND ARG1 ARG2 ...

Commands:
- combine: combine coverage files args: outfile infiles+
- list: list available commands args:
"""
parser = OptionParser(usage=usage)

class Commands(object):
    
    @staticmethod
    def list():
        commands = [attr for attr in dir(Commands)
                    if not attr.startswith('__')]
        sys.stdout.write("\n".join(commands) + "\n")
    
    @staticmethod
    def combine(outfile, *infiles):
        combined = ExecutionRecorder()
        for filename in infiles:
            store = ResultStore(os.path.dirname(filename), None,
                                os.path.basename(filename))
            single = store.load()
            combined.merge(single)
        combined_store = ResultStore(os.path.dirname(outfile), None,
                                     os.path.basename(outfile))
        combined_store.save(combined)

def main():
    opts, args = parser.parse_args(sys.argv[1:])
    if not args:
        parser.print_help()
        return
    
    command, args = args[0], args[1:]
    
    if hasattr(Commands, command):
        getattr(Commands, command)(*args)
    else:
        parser.print_help()
