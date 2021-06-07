# -*- coding: utf-8 -*-
from typing import Any, Dict, List, NewType, Optional, Union

RawFlag = NewType('RawFlag', Union[Dict[str, Any], str])


class Flag:
    """
    支持的raw_flag类型示例
    dict: {"--set": "a=1"}  to_cmd_options=> ["--set", "a=1"]
    dict: {"--reuse-db": True} to_cmd_options=> ["--reuse-db"]
    dict: {"--reuse-db": False} to_cmd_options=> []
    str: "--reuse-db" to_cmd_options=> ["--reuse-db"]
    """

    def __init__(self, raw_flag: RawFlag):
        self.raw_flag = raw_flag

    def to_cmd_options(self) -> List[str]:
        raw_flag = self.raw_flag

        if isinstance(raw_flag, str):
            return [raw_flag]
        elif isinstance(raw_flag, dict):
            k = list(raw_flag.keys())[0]
            v = raw_flag[k]
            if v is True:
                return [k]
            elif v:
                return [k, str(v)]
            return []

        raise NotImplementedError(f"unsupported type {type(raw_flag)}")


class Options:
    """
    支持Helm Options命令行组装
    """

    def __init__(self, init_options: Optional[List[RawFlag]] = None):
        self._options = []

        if not init_options:
            return

        for raw_flag in init_options:
            self._options.append(Flag(raw_flag))

    def add(self, raw_flag: RawFlag):
        self._options.append(Flag(raw_flag))

    def options(self) -> List[str]:
        """
        example init_options: [{"--set": "a=1,b=2"}, {"--values": "data.yaml"}, "--debug", {"--force": True}]
        return options: ["--set", "a=1,b=2", "--values", "data.yaml", "--debug", "--force"]
        """
        options = []

        for flag in self._options:
            options.extend(flag.to_cmd_options())

        return options
