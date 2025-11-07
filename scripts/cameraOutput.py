# -*- coding:utf8 -*-
import pymxs
import os
import sys


def cameraOutput(cam, outFile="", timeRange=[]):
    rt = pymxs.runtime
    camNode = rt.getNodeByName(cam)

    if not timeRange:
        tr = rt.animationRange
        timeRange = [int(tr.start), int(tr.end)]

    newCamNode = None
    newCamNode = rt.Freecamera()
    """
    if str(rt.classof(camNode)) == "Physical":
        newCamNode = rt.Physical_Camera()
        setattr(newCamNode, "targeted", 0)
    elif str(rt.classof(camNode)) == "Freecamera":
        newCamNode = rt.Freecamera()
    else:
        return None
    """
    cAttrs = dir(camNode)
    nAttrs = dir(newCamNode)
    rAttrs = list(set(cAttrs).intersection(set(nAttrs)))
    # if "targeted" in rAttrs:
    #     rAttrs.remove("targeted")

    for attr in rAttrs:
        setattr(newCamNode, attr, getattr(camNode, attr))

    with pymxs.animate(1):
        for i in range(timeRange[0], timeRange[1] + 1):
            with pymxs.attime(i):
                newCamNode.transform = camNode.transform
                for attr in rAttrs:
                    setattr(newCamNode, attr, getattr(camNode, attr))

    if outFile:
        # 确保路径支持中文：转换为绝对路径并确保Unicode编码
        outFile = os.path.abspath(outFile)
        outDir = os.path.dirname(outFile)
        if not os.path.isdir(outDir):
            os.makedirs(outDir, exist_ok=True)

        rt.select(newCamNode)
        if outFile.endswith(".fbx"):
            rt.FBXExporterSetParam("ResetExport")
            rt.FBXExporterSetParam("Animation", 1)
            rt.FBXExporterSetParam("ScaleFactor", 1)
            rt.FBXExporterSetParam("Units", "cm")
            rt.FBXExporterSetParam("UpAxis", "Y-up")
            # 确保路径正确传递给MaxScript（使用Unicode字符串）
            rt.exportFile(
                rt.name(outFile),
                pymxs.runtime.Name("noPrompt"),
                selectedOnly=True,
                using="FBXEXP",
            )
        elif outFile.endswith(".abc"):
            # 统一导出单位为厘米
            # 获取场景单位并计算ScaleFactor
            try:
                # 获取场景系统单位（0=英寸, 1=英尺, 2=英里, 3=毫米, 4=厘米, 5=米, 6=千米）
                system_unit = rt.units.SystemType
                if system_unit == 4:  # 厘米
                    scale_factor = 1.0
                elif system_unit == 5:  # 米
                    scale_factor = 100.0  # 米转厘米
                elif system_unit == 3:  # 毫米
                    scale_factor = 0.1  # 毫米转厘米
                else:
                    # 其他单位，默认使用1.0
                    scale_factor = 1.0
                # 设置Alembic导出器的ScaleFactor
                rt.AlembicExport.setmxsprop("ScaleFactor", scale_factor)
            except:
                # 如果获取单位失败，使用默认值1.0
                rt.AlembicExport.setmxsprop("ScaleFactor", 1.0)
            
            # 确保路径正确传递给MaxScript（使用Unicode字符串）
            rt.exportFile(
                rt.name(outFile),
                pymxs.runtime.Name("noPrompt"),
                selectedOnly=True,
                using="AlembicExport",
                start=timeRange[0],
                end=timeRange[1],
                coordinateSystem="Y-up",
            )

    return newCamNode
