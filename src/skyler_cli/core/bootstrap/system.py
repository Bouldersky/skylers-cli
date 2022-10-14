from enum import Enum
from pathlib import Path
import chevron
import importlib.resources
from skyler_cli.core.bootstrap import system_template
import shutil


class OS(Enum):
    OS_X = "OS X"
    LINUX = "LINUX"


class MachineType(Enum):
    DEV = 0
    SERVER = 1


_BASE_ALIASES = {
    "ls": "ls -F",
    "ll": "ls -lh",
    "l": "ls",
    "dtd": "pwd > /tmp/defaultTerminalLocation",
    "grep": "grep --color=auto",
    "egrep": "egrep --color=auto",
    "fgrep": "fgrep --color=auto",
    "c": "clear",
    "j": "jobs",
    "k": "kill",
    "p8": "ping 8.8.8.8",
    "t8": "traceroute 8.8.8.8",
    "src": "source ~/.bash_profile",
    "make": "make -j 6",
    "pm": "sudo pacman",
    "mnv": "mvn -T 6",
    "ebrc": "vi ~/.bashrc && source ~/.bashrc",
    "ei3": "vi ~/.config/i3/config",
    "pdb": "python3.9 -m pdb",
    "python": "python3.9",
    "pip": "pip3",
    "tree": "tree -C",
    "..": "cd ..",
    "...": "cd ../..",
    "....": "cd ../../..",
    ".....": "cd ../../../..",
    "......": "cd ../../../../..",
    ".......": "cd ../../../../../..",
    "........": "cd ../../../../../../..",
    ".........": "cd ../../../../../../../..",
    "gs": "git status",
    "gpush": "git push",
    "gpul": "git pull",
    "gpull": "git pull",
    "gc": "git commit",
    "ga": "git add",
    "gb": "git branch",
    "gch": "git checkout",
    "gl": "git log --graph",
    "glo": "git log --oneline --graph",
    "gla": "git log --graph --all",
    "gloa": "git log --oneline --graph --all",
    "glav": "git log --graph --all",
    "gsta": "git stash",
    "sctl": "sudo systemctl",
    "jctl": "sudo journalctl",
    "ack": "ag --pager='less -r'",
}

CLIPBOARD_ALIASES = {
    OS.OS_X: {
        "paste": "pbpaste",
        "clip": "pbcopy",
    },
    OS.LINUX: {
        "paste": "xclip -o -selection clipboard",
        "clip": "xclip -i -selection clipboard",
    },
}


class SystemBootstrapper:
    def __init__(
        self,
        os: OS,
        machine_type: MachineType,
        is_personal: bool,
        home_path=Path.home(),
    ):
        """

        :param os: Operating system of the computer to be bootstrapped
        :param machine_type: Whether the machine is a dev machine (laptop/desktop)
            vs a server
        :param is_personal: Whether this is a personal machine, or a work machine
        :param home_path: Only used for testing: the home directory to bootstrap
            configurations in
        """
        self.os = os
        self.machine_type = machine_type
        self.is_personal = is_personal
        self.home_path = home_path

    @staticmethod
    def _read_template_resource(resource: str) -> str:
        return importlib.resources.read_text(system_template, resource)

    @staticmethod
    def _cmd_exists(cmd: str) -> bool:
        return shutil.which(cmd) is not None

    def bootstrap_system(self) -> None:
        self.bootstrap_bashrc()
        self.bootstrap_initrc()
        self.bootstrap_tmux_conf()

    def bootstrap_bashrc(self) -> None:
        template_data = self._calculate_bashrc_template_data()
        result = chevron.render(self._read_template_resource(".bashrc"), template_data)
        with (self.home_path / ".bashrc").open("w") as bashrc_f:
            bashrc_f.write(result)

    def _calculate_bashrc_template_data(self):
        default_location_file_path = (
            "/tmp/defaultTerminalLocation"
            if self.is_personal
            else str(self.home_path / ".defaultTerminalLocation")
        )
        aliases_list = self._calculate_aliases()
        template_data = {
            "default_location_file_path": default_location_file_path,
            "aliases": aliases_list,
        }
        return template_data

    def _calculate_aliases(self):
        alias_dict = dict(_BASE_ALIASES)
        if self._cmd_exists("htop"):
            alias_dict["top"] = "htop"
        if self._cmd_exists("pacman"):
            alias_dict["pm"] = "sudo pacman"
        if self._cmd_exists("nvim"):
            alias_dict["vi"] = "nvim"

        if self.machine_type != MachineType.SERVER and self.os in CLIPBOARD_ALIASES:
            alias_dict |= CLIPBOARD_ALIASES[self.os]

        aliases_list = [{"key": k, "value": v} for k, v in alias_dict.items()]
        return aliases_list

    def bootstrap_initrc(self) -> None:
        data = self._read_template_resource("inputrc")
        with (self.home_path / ".inputrc").open("w") as inputrc_f:
            inputrc_f.write(data)

    def bootstrap_tmux_conf(self) -> None:
        data = self._read_template_resource("tmux.conf")
        with (self.home_path / ".tmux.conf").open("w") as inputrc_f:
            inputrc_f.write(data)
