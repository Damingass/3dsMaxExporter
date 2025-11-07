-- MaxExporter 菜单宏脚本
-- 用于在3ds Max菜单栏添加导出工具入口

macroScript MaxExporterMenu
category:"MaxExporter"
tooltip:"打开导出工具"
buttonText:"导出工具"
(
    -- 执行Python脚本加载导出工具
    python.execute "
import sys
import os

# 获取用户脚本目录
try:
    import pymxs
    rt = pymxs.runtime
    script_dir = rt.getDir(rt.name('userScripts'))
    if script_dir and script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    
    # 导入并运行主程序
    from Main import main
    main()
except Exception as e:
    import pymxs
    pymxs.runtime.messageBox('加载导出工具失败: ' + str(e), title='错误')
"
)

