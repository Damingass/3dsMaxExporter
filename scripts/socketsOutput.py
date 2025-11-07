# -*- coding:utf8 -*-
import pymxs
import os
import sys


def socketsOutput(objs, outFile="", timeRange=[]):
    """
    直接导出原始骨骼，保持层级关系和动画
    功能等同于在 Max 中手动选择骨骼并导出
    """
    rt = pymxs.runtime
    
    # 获取所有原始节点对象
    objNodes = []
    for obj_name in objs:
        objNode = rt.getNodeByName(obj_name)
        if objNode:
            objNodes.append(objNode)
    
    if not objNodes:
        return None
    
    if not timeRange:
        tr = rt.animationRange
        timeRange = [int(tr.start), int(tr.end)]

    if outFile:
        # 确保路径支持中文：转换为绝对路径并确保Unicode编码
        outFile = os.path.abspath(outFile)
        outDir = os.path.dirname(outFile)
        if not os.path.isdir(outDir):
            os.makedirs(outDir, exist_ok=True)

        # 直接选择原始骨骼节点进行导出
        # FBX 导出器会自动保持层级关系和动画
        rt.clearSelection()
        for objNode in objNodes:
            rt.selectMore(objNode)

        if outFile.endswith(".fbx"):
            # 重置导出设置
            rt.FBXExporterSetParam("ResetExport")
            # 启用动画导出
            rt.FBXExporterSetParam("Animation", True)
            # 烘焙动画（将控制器动画转换为关键帧）
            rt.FBXExporterSetParam("BakeAnimation", True)
            # 其他设置
            rt.FBXExporterSetParam("ScaleFactor", 1.0)
            rt.FBXExporterSetParam("Units", "cm")
            rt.FBXExporterSetParam("UpAxis", "Y-up")
            rt.FBXExporterSetParam("EmbedTextures", False)
            # 导出骨骼（包括层级关系和动画）
            # 确保路径正确传递给MaxScript（使用Unicode字符串）
            rt.exportFile(
                rt.name(outFile),
                pymxs.runtime.Name("noPrompt"),
                selectedOnly=True,
                using="FBXEXP",
            )

    # 返回第一个节点
    return objNodes[0] if objNodes else None
