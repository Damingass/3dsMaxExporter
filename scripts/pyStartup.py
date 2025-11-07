# -*- coding:utf8 -*-
"""
3ds Max 启动脚本 - 自动加载导出工具插件
"""
import os
import sys
import pymxs

rt = pymxs.runtime

# 获取脚本所在目录（插件安装目录）
# 在MZP包中，脚本会被安装到特定目录
try:
    # 尝试获取当前脚本的目录
    if hasattr(rt, 'getDir'):
        script_dir = rt.getDir(rt.name('userScripts'))
    else:
        # 备用方法：使用文件路径
        script_dir = os.path.dirname(__file__)
except:
    script_dir = os.path.dirname(__file__)

# 将脚本目录添加到Python路径
if script_dir and script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 导入主模块（延迟导入，避免启动时出错）
def load_exporter():
    """加载导出工具"""
    try:
        from Main import main
        return main
    except Exception as e:
        rt.messageBox(f"加载导出工具失败: {str(e)}", title="错误")
        return None

# 将加载函数存储到全局命名空间，供MacroScript调用
if 'MaxExporter' not in globals():
    MaxExporter = {'load': load_exporter}

