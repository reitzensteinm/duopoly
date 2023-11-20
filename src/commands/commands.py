from .command import Command
from .command_files import Files
from .command_install_package import InstallPackage
from .command_move_file import MoveFile
from .command_replace_file import ReplaceFile
from .command_replace_node import ReplaceNode
from .command_search import Search
from .command_delete_file import DeleteFile
from .command_terminal import Terminal
from .command_think import Think
from .command_verdict import Verdict
from .command_revert import Revert

COMMANDS_CHECK = [Verdict, Files, Terminal]
COMMANDS_GENERATE = [
    Think,
    Verdict,
    Files,
    ReplaceFile,
    Search,
    DeleteFile,
    MoveFile,
    InstallPackage,
    ReplaceNode,
    Terminal,
    Revert,
]
