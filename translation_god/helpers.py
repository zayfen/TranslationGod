#!/usr/bin/env python
# coding: utf-8

"""
Helper functions for translation god
"""


def diff_dict(source_dict, target_dict):
    """
    以source_dict为基础，计算其与target_dict的差值
    """
    output_dict = {}

    for (k, v) in source_dict.items():
        if target_dict.get(k) is None:
            output_dict[k] = v

    return output_dict
