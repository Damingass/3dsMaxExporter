# -*- coding:utf8 -*-
"""
法线可视化模块
在场景中绘制顶点法线方向（调试用）
不包含任何UI逻辑，仅返回操作结果
"""
from pymxs import runtime as rt


def visualize_normals(normal_length=10.0):
    """
    可视化显示顶点法线方向
    
    参数:
        normal_length: 法线长度
        
    返回:
        tuple: (success: bool, error_msg: str)
    """
    maxscript_code = r'''
-- 可视化法线方向（修复缩放问题）
fn visualizeNormals obj:$ normalLength:5.0 drawArrows:true = (
    if obj == undefined then (
        if selection.count == 0 then (
            return false
        )
        obj = selection[1]
    )
    
    if not (polyOp.getMapSupport obj 0) then (
        return false
    )
    
    numVerts = polyOp.getNumVerts obj
    
    -- 删除之前的可视化对象
    delete $NormalVisualizer_*
    
    if drawArrows then (
        -- 创建一个组来存放所有箭头
        normalGroup = dummy name:"NormalVisualizer_Group"
        normalGroup.boxsize = [0.1, 0.1, 0.1]
        
        -- ★ 关键：将组设为模型的子对象，这样就在模型的局部空间中绘制
        normalGroup.parent = obj
        
        for i = 1 to numVerts do (
            -- 获取顶点色并解码
            vertColor = polyOp.getMapVert obj 0 i
            
            nx = (vertColor.x) * 2.0 - 1.0
            ny = (vertColor.y) * 2.0 - 1.0
            nz = (vertColor.z) * 2.0 - 1.0
            normal = normalize [nx, ny, nz]
            
            -- ★ 关键：使用局部空间的顶点位置
            vertPos = polyOp.getVert obj i
            
            -- ★ 关键：计算局部空间的法线终点
            endPos = vertPos + (normal * normalLength)
            
            -- 创建线条显示法线（在局部空间）
            normalLine = SplineShape name:("NormalVisualizer_" + i as string) wirecolor:yellow
            addNewSpline normalLine
            addKnot normalLine 1 #corner #line vertPos
            addKnot normalLine 1 #corner #line endPos
            updateShape normalLine
            
            -- 设置线条属性
            normalLine.render_displayRenderMesh = false
            normalLine.steps = 0
            normalLine.wirecolor = yellow
            
            -- ★ 关键：添加到组（组已经是模型的子对象）
            normalLine.parent = normalGroup
        )
    )
    
    return true
)

-- 使用示例
visualizeNormals normalLength:10.0
'''
    try:
        result = rt.execute(maxscript_code)
        if not result:
            return False, "操作未完成，请检查是否选择了对象并已运行平滑法线功能"
        return True, None
    except Exception as e:
        return False, f"执行失败: {str(e)}"
