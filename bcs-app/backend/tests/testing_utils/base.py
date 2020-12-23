# -*- coding: utf-8 -*-
from typing import Dict
import random

RANDOM_CHARACTER_SET = 'abcdefghijklmnopqrstuvwxyz0123456789'


def generate_random_string(length=30, chars=RANDOM_CHARACTER_SET):
    """Generates a non-guessable OAuth token"""
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for x in range(length))


def dict_is_subequal(data: Dict, full_data: Dict) -> bool:
    """检查两个字典是否相等，忽略在 `full_data` 中有，但 `data` 里没有提供的 key"""
    for key, value in data.items():
        if key not in full_data:
            return False
        if value != full_data[key]:
            return False
    return True
