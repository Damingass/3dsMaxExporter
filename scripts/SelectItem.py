# -*- coding:utf8 -*-
"""
选择功能模块
包含选中父子级、选中关联项、全选组等功能
不包含任何UI逻辑，仅返回操作结果
"""
from pymxs import runtime as rt


def select_hierarchy(ancestor_depth=0):
    """
    选中父子级
    
    返回:
        tuple: (success: bool, error_msg: str)
    """
    from ExportItem import collect_export_nodes
    
    success, nodes, _, error_msg = collect_export_nodes(ancestor_depth=ancestor_depth)
    if not success:
        return False, error_msg
        
    rt.clearSelection()
    for node in nodes:
        rt.selectMore(node)
    
    return True, None


def select_related():
    """
    选中关联项
    以句柄为唯一依据，避免串选；先扩展上下级（到组头或骨架连通），再选出被骨骼影响的网格
    
    返回:
        tuple: (success: bool, error_msg: str)
    """
    current = [n for n in rt.selection]
    if not current:
        return False, "请先选择一个节点"

    def is_geometry(node):
        try:
            return rt.superClassOf(node) == rt.GeometryClass
        except Exception:
            return False

    def get_skin_modifier(node):
        try:
            for m in node.modifiers:
                if rt.classOf(m) == rt.Skin:
                    return m
        except Exception:
            pass
        return None

    def iter_skin_bones(skin_mod):
        try:
            count = int(rt.skinOps.GetNumberBones(skin_mod))
        except Exception:
            count = 0
        for i in range(1, count + 1):
            try:
                bn = rt.skinOps.GetBoneNode(skin_mod, i)
            except Exception:
                bn = None
            if bn:
                yield bn

    def gather_scene_skin_bones():
        bones = set()
        for obj in rt.objects:
            if not is_geometry(obj):
                continue
            skin = get_skin_modifier(obj)
            if not skin:
                continue
            for bn in iter_skin_bones(skin):
                bones.add(bn)
        return bones

    def skin_has_bone_by_handle(skin_mod, bone_node):
        try:
            target_handle = int(bone_node.handle)
        except Exception:
            return False
        try:
            count = int(rt.skinOps.GetNumberBones(skin_mod))
        except Exception:
            count = 0
        for i in range(1, count + 1):
            try:
                bn = rt.skinOps.GetBoneNode(skin_mod, i)
            except Exception:
                bn = None
            if not bn:
                continue
            try:
                if int(bn.handle) == target_handle:
                    return True
            except Exception:
                pass
        return False

    # 1) 计算组边界（若有组头则用组头内的网格作为查询范围）
    def find_group_head(node):
        cur = node
        while cur:
            try:
                if rt.isGroupHead(cur):
                    return cur
            except Exception:
                pass
            try:
                h = rt.groupHead(cur)
            except Exception:
                h = None
            if h:
                return h
            try:
                cur = cur.parent
            except Exception:
                cur = None
        return None

    def collect_descendants(root):
        result = []
        if not root:
            return result
        stack = [root]
        visited = set()
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            result.append(node)
            try:
                for ch in node.children:
                    stack.append(ch)
            except Exception:
                pass
        return result

    gh = find_group_head(current[0])
    group_nodes = collect_descendants(gh) if gh else None

    # 2) 选中集合拆分
    selected_meshes = [n for n in current if is_geometry(n) and get_skin_modifier(n)]
    selected_bones = [n for n in current if n not in selected_meshes]

    # 3) 初始骨骼集合
    initial_bones = []
    seen_b = set()
    # 来自已选网格
    for mesh in selected_meshes:
        skin = get_skin_modifier(mesh)
        if not skin:
            continue
        for bn in iter_skin_bones(skin):
            if bn not in seen_b:
                initial_bones.append(bn)
                seen_b.add(bn)
    # 叠加已选骨骼
    for bn in selected_bones:
        if bn not in seen_b:
            initial_bones.append(bn)
            seen_b.add(bn)

    if not initial_bones:
        return False, "未能从选择中识别到骨骼或蒙皮网格"

    # 4) 在"全场景被 Skin 引用的骨骼集合"中扩展父/子，形成连通骨架
    bone_pool = gather_scene_skin_bones()
    pool_set = set(bone_pool)
    expanded_bones = []
    visited = set()
    queue = [b for b in initial_bones if b in pool_set]
    while queue:
        cur = queue.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        expanded_bones.append(cur)
        try:
            p = cur.parent
        except Exception:
            p = None
        if p and p in pool_set and p not in visited:
            queue.append(p)
        try:
            for ch in cur.children:
                if ch in pool_set and ch not in visited:
                    queue.append(ch)
        except Exception:
            pass

    if not expanded_bones:
        return False, "未找到可扩展的骨骼层级"

    # 5) 查找受这些骨骼影响的网格（句柄匹配）。若存在组头，则仅在组内网格查找；否则全场景
    candidate_nodes = group_nodes if group_nodes is not None else [obj for obj in rt.objects]
    related_meshes = []
    seen_mesh = set()
    for obj in candidate_nodes:
        if not is_geometry(obj):
            continue
        skin = get_skin_modifier(obj)
        if not skin:
            continue
        for b in expanded_bones:
            if skin_has_bone_by_handle(skin, b):
                if obj not in seen_mesh:
                    related_meshes.append(obj)
                    seen_mesh.add(obj)
                break

    # 6) 输出选择：扩展后的骨骼 + 关联网格
    rt.clearSelection()
    for b in expanded_bones:
        rt.selectMore(b)
    for m in related_meshes:
        rt.selectMore(m)
    
    return True, None


def select_group():
    """
    全选组
    
    返回:
        tuple: (success: bool, error_msg: str)
    """
    selected_nodes = [n for n in rt.selection]
    if not selected_nodes:
        return False, "请先选择一个组内的节点或组头"

    def find_group_head(node):
        cur = node
        while cur:
            try:
                if rt.isGroupHead(cur):
                    return cur
            except Exception:
                pass
            # direct groupHead if member
            try:
                h = rt.groupHead(cur)
            except Exception:
                h = None
            if h:
                return h
            try:
                cur = cur.parent
            except Exception:
                cur = None
        return None

    group_heads = set()
    for n in selected_nodes:
        h = find_group_head(n)
        if h:
            group_heads.add(h)

    if not group_heads:
        return False, "所选对象不在任何组内"

    # 收集所有属于这些组头的成员（包含组头本身）
    result = set()
    for obj in rt.objects:
        # 同样向上查找是否属于这些组
        h2 = find_group_head(obj)
        if h2 and h2 in group_heads:
            result.add(obj)
    for h in group_heads:
        result.add(h)

    if not result:
        return False, "未找到组成员"

    rt.clearSelection()
    for node in result:
        rt.selectMore(node)
    
    return True, None
