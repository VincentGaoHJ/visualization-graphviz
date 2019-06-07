# -*- coding: utf-8 -*-
"""
@Date: Created on 2019/4/30
@Author: Haojun Gao
@Description: 
"""
file_name = ['.', '2019-04-30-09-06-30', '2', 'result', '4-word.csv']

file_name = ''.join(filter(lambda s: isinstance(s, str) and len(
                    s) == 1 or ".csv" in s, file_name))

print(file_name)