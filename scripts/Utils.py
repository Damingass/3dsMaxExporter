from pymxs import runtime as rt
from PySide6 import QtCore
from PySide6 import QtWidgets

def _make_safe_filename(name: str) -> str:
    invalid_chars = '\\/:*?"<>|'
    safe = ''.join('_' if ch in invalid_chars else ch for ch in name)
    return safe or "export"


def _collect_export_nodes(parent_widget=None, ancestor_depth=0):
    """收集导出所需的节点列表及默认命名。"""
    selected_objs = [obj for obj in rt.selection]

    if not selected_objs:
        all_objects = rt.objects
        visible_objects = [obj for obj in all_objects if not obj.isHidden]
        if not visible_objects:
            QtWidgets.QMessageBox.warning(parent_widget, "警告", "场景中没有找到可导出的对象")
            return None, None
        return list(visible_objects), None

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
        QtWidgets.QMessageBox.warning(parent_widget, "警告", "没有找到可导出的对象")
        return None, None

    export_name = root_nodes[0].name if root_nodes else None

    return all_nodes, export_name
