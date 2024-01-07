#!/usr/bin/env python
# coding: utf-8

import os

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


def merge_json_dict(a_json_dict, b_json_dict):
    """
    Merge b_json_dict to a_json_dict, and output result
    result = { ...a_json_dict, ...b_json_dict }
    """
    c_json_dict = { **a_json_dict, **b_json_dict }

    return c_json_dict


def copy_file(input_file_path, target_file_path):
    """
    Copy data from input_file_path to target_file_path, if target_file_path
    doesn't exist, then create it.
    """
    with open(input_file_path) as f:
        data = f.read()

        with open(target_file_path, "w+") as wf:
            wf.write(data)
    
