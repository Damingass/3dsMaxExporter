# -*- coding:utf8 -*-
"""
导出功能模块
包含FBX导出相关的所有功能
不包含任何UI逻辑，仅返回操作结果
"""
from pymxs import runtime as rt
from socketsOutput import socketsOutput


def make_safe_filename(name: str) -> str:
    """将文件名中的非法字符替换为下划线"""
    invalid_chars = '\\/:*?"<>|'
    safe = ''.join('_' if ch in invalid_chars else ch for ch in name)
    return safe or "export"


def collect_export_nodes(ancestor_depth=0):
    """
    收集导出所需的节点列表及默认命名
    
    返回:
        tuple: (success: bool, nodes: list, export_name: str, error_msg: str)
    """
    selected_objs = [obj for obj in rt.selection]

    if not selected_objs:
        all_objects = rt.objects
        visible_objects = [obj for obj in all_objects if not obj.isHidden]
        if not visible_objects:
            return False, None, None, "场景中没有找到可导出的对象"
        return True, list(visible_objects), None, None

    def find_ancestor_by_depth(node, depth):
        chain = []
        current = node
        while current:
            chain.append(current)
            current = current.parent
        chain.reverse()  # 根节点在前
        target_index = min(max(depth, 0), len(chain) - 1)
        return chain[target_index]

    def collect_all_descendants(node, collected, collected_set):
        if node in collected_set:
            return
        collected.append(node)
        collected_set.add(node)
        for child in node.children:
            collect_all_descendants(child, collected, collected_set)

    root_nodes = []
    seen_roots = set()
    for obj in selected_objs:
        root = find_ancestor_by_depth(obj, ancestor_depth)
        if root not in seen_roots:
            root_nodes.append(root)
            seen_roots.add(root)

    all_nodes = []
    collected_set = set()
    for root in root_nodes:
        collect_all_descendants(root, all_nodes, collected_set)

    if not all_nodes:
        return False, None, None, "没有找到可导出的对象"

    export_name = root_nodes[0].name if root_nodes else None

    return True, all_nodes, export_name, None


def get_default_export_name():
    """
    获取默认导出文件名
    
    返回:
        str: 默认文件名
    """
    scene_name = str(rt.maxFileName)
    return make_safe_filename(scene_name) if scene_name else "export"


def export_fbx(nodes, file_path):
    """
    导出节点到FBX文件
    
    参数:
        nodes: 要导出的节点列表
        file_path: FBX文件路径
        
    返回:
        tuple: (success: bool, error_msg: str)
    """
    try:
        socketsOutput([node.name for node in nodes], file_path)
        return True, None
    except Exception as e:
        return False, str(e)
