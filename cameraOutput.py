import pymxs
import os


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
        outDir = os.path.dirname(outFile)
        if not os.path.isdir(outDir):
            os.makedirs(outDir)

        rt.select(newCamNode)
        if outFile.endswith(".fbx"):
            rt.FBXExporterSetParam("ResetExport")
            rt.FBXExporterSetParam("Animation", 1)
            rt.FBXExporterSetParam("ScaleFactor", 1)
            rt.FBXExporterSetParam("UpAxis", "Y-up")
            rt.exportFile(
                outFile,
                pymxs.runtime.Name("noPrompt"),
                selectedOnly=True,
                using="FBXEXP",
            )
        elif outFile.endswith(".abc"):
            rt.exportFile(
                outFile,
                pymxs.runtime.Name("noPrompt"),
                selectedOnly=True,
                using="AlembicExport",
                start=timeRange[0],
                end=timeRange[1],
                coordinateSystem="Y-up",
            )

    return newCamNode
