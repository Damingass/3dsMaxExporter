# -*- coding:utf8 -*-
"""
平滑法线功能模块
将选中对象的平滑法线烘焙到顶点色通道
不包含任何UI逻辑，仅返回操作结果
"""
from pymxs import runtime as rt


def smooth_normal_to_vertex_color():
    """
    将平滑法线烘焙到顶点色通道
    
    返回:
        tuple: (success: bool, error_msg: str)
    """
    maxscript_code = r'''
fn smoothNormalToVertexColor obj:undefined = (
    
    if obj == undefined then (
        if selection.count == 0 then (
            return false
        )
        obj = selection[1]
    )
    
    format "========================================\n"
    format "开始处理对象: %\n" obj.name
    format "对象类型: %\n" (classOf obj)
    
    -- 如果不是Editable Poly，直接转换
    if classOf obj != Editable_Poly then (
        format "对象不是Editable Poly，正在转换...\n"
        try (
            convertTo obj Editable_Poly
            format "转换成功\n"
        ) catch (
            format "转换失败: %\n" (getCurrentException())
            return false
        )
    )
    
    numVerts = polyOp.getNumVerts obj
    numFaces = polyOp.getNumFaces obj
    
    format "顶点数: %\n" numVerts
    format "面数: %\n" numFaces
    
    -- 启用顶点色通道（通道0）
    polyOp.setMapSupport obj 0 true
    
    -- ★ 第一步：计算每个面的法线
    format "正在计算面法线...\n"
    faceNormals = #()
    for faceIdx = 1 to numFaces do (
        faceVerts = polyOp.getFaceVerts obj faceIdx
        
        v1 = polyOp.getVert obj faceVerts[1]
        v2 = polyOp.getVert obj faceVerts[2]
        v3 = polyOp.getVert obj faceVerts[3]
        
        edge1 = v2 - v1
        edge2 = v3 - v1
        faceNormal = normalize (cross edge1 edge2)
        
        append faceNormals faceNormal
    )
    format "面法线计算完成\n"
    
    -- ★ 第二步：计算每个几何顶点的平滑法线
    format "正在计算平滑法线...\n"
    vertexNormals = #()
    for vertIdx = 1 to numVerts do (
        -- 获取与该顶点相关的所有面
        vertFaces = (polyOp.getFacesUsingVert obj vertIdx) as array
        
        -- 累加所有相邻面的法线
        sumNormal = [0,0,0]
        for faceIdx in vertFaces do (
            sumNormal += faceNormals[faceIdx]
        )
        
        -- 归一化得到平滑法线
        smoothNormal = normalize sumNormal
        append vertexNormals smoothNormal
    )
    format "平滑法线计算完成\n"
    
    -- ★ 第三步：建立几何顶点到贴图顶点的映射（关键！）
    format "正在建立顶点映射...\n"
    
    -- 首先设置贴图顶点数量等于几何顶点数量
    polyOp.setNumMapVerts obj 0 numVerts
    
    -- 为每个几何顶点创建对应的贴图顶点颜色
    for vertIdx = 1 to numVerts do (
        normal = vertexNormals[vertIdx]
        
        -- 将法线从 [-1,1] 映射到 [0,1]
        r = (normal.x + 1.0) * 0.5
        g = (normal.y + 1.0) * 0.5
        b = (normal.z + 1.0) * 0.5
        
        -- 设置贴图顶点颜色（索引与几何顶点一致）
        vertColor = color (r) (g) (b)
        polyOp.setMapVert obj 0 vertIdx vertColor
    )
    
    -- ★ 第四步：为每个面设置贴图面（直接映射到几何顶点索引）
    format "正在设置贴图面映射...\n"
    for faceIdx = 1 to numFaces do (
        -- 获取该面的几何顶点索引
        faceVerts = polyOp.getFaceVerts obj faceIdx
        
        -- 直接使用相同的索引作为贴图顶点索引
        polyOp.setMapFace obj 0 faceIdx faceVerts
    )
    
    format "顶点色写入完成\n"
    format "========================================\n"
    format "处理完成！\n"
    format "贴图顶点数: %\n" (polyOp.getNumMapVerts obj 0)
    
    return true
)

-- 执行函数
smoothNormalToVertexColor()
'''
    try:
        result = rt.execute(maxscript_code)
        if not result:
            return False, "操作未完成，请检查是否选择了对象"
        return True, None
    except Exception as e:
        return False, f"执行失败: {str(e)}"
