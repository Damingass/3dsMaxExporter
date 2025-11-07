# -*- coding:utf8 -*-
"""
mxthread 模块 - 用于在 3ds Max 主线程上运行代码

这个模块提供了一个简单的接口来确保代码在 3ds Max 的主线程上运行。
在大多数情况下，通过 MaxScript 或 UI 调用的 Python 代码已经在主线程上，
所以这里提供一个简单的包装器直接执行函数。
"""
import pymxs


def run_on_main_thread(func, *args, **kwargs):
    """
    在主线程上运行函数
    
    在 3ds Max 的 Python 环境中，通过 MaxScript 或 UI 调用的代码
    通常已经在主线程上，所以可以直接执行函数。
    
    Args:
        func: 要执行的函数
        *args: 函数的位置参数
        **kwargs: 函数的关键字参数
    
    Returns:
        函数的返回值
    """
    # 在 3ds Max 中，通过 UI 或 MaxScript 调用的 Python 代码
    # 通常已经在主线程上，所以可以直接执行
    return func(*args, **kwargs)
