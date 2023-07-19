# commands/commands.py

from .command import Command
from .command_think import Think
from .command_verdict import Verdict
from .command_files import Files
from .command_replace_file import ReplaceFile
from .command_search import Search
from .command_delete_file import DeleteFile
from .command_install_package import InstallPackage

COMMANDS_CHECK = [Think, Verdict]
COMMANDS_GENERATE = [
    Think,
    Verdict,
    Files,
    ReplaceFile,
    Search,
    DeleteFile,
    InstallPackage,
]
