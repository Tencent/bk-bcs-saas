# -*- coding: utf-8 -*-
from typing import Dict, List, NewType, Optional, Union

Flag = NewType('Flag', Union[Dict[str, Union[str, bool]], str])


class Options:
    """
    支持Helm Options命令行组装
    """

    def __init__(self, init_options: Optional[List[Flag]] = None):
        self._options = init_options if init_options else []

    def add(self, flag: Flag):
        self._options.append(flag)

    def options(self) -> List[str]:
        """
        example _options: [{"--set": "a=1,b=2"}, {"--values": "data.yaml"}, "--debug", {"--force": True}]
        return options: ["--set", "a=1,b=2", "--values", "data.yaml", "--debug", "--force"]
        """
        options = []

        for flag in self._options:
            if not flag:
                continue

            if isinstance(flag, str):
                options.append(flag)
            elif isinstance(flag, dict):
                k = list(flag.keys())[0]
                v = flag[k]
                if v is True:
                    options.append(k)
                elif v:
                    options.extend([k, v])

            else:
                raise ValueError(f"invalid option flag {type(flag)}")

        return options
