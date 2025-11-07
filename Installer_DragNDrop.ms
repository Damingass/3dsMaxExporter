/*
==========================================================================
MaxExporter 安装脚本
==========================================================================
文件夹结构:
+ /MaxExporter/
	+ /MaxExporter/scripts
		- Main.py
		- cameraOutput.py
		- socketsOutput.py
		- ExtractAnimABC.py
		- ExtractAnimBone.py
		- ExtractCameraFBX.py
		- pyStartup.py
	- Installer_DragNDrop.mse
==========================================================================
*/

-- 调整这部分
script_name = "MaxExporter"
script_folder_name = "\\MaxExporter\\"

-- 调整结束

script_path = getThisScriptFilename()
this_script_path = getfilenamepath script_path
scripts_folder = "\\scripts\\"

-- 格式化输出脚本目录（调试用）
-- format "Script DIR : %\n" this_script_path

-- 创建宏脚本
fn create_macro_script =
(
	-- 主导出工具宏脚本
	macroScript MaxExporter
	Category:"MaxExporter" 
	toolTip:"打开导出工具"
	buttonText:"导出工具"
	(
		python.ExecuteFile ((GetDir #userScripts) + script_folder_name + "Main.py")
	)
)

-- 创建 MaxExporter 目录
makeDir ((GetDir #userScripts) + script_folder_name)

-- 删除之前的文件（用于更新插件）
destination_path = getFiles ((GetDir #userScripts) + script_folder_name + "*.*")

for item in destination_path do
(
	try(deleteFile item) catch()
)

-- 获取 scripts 文件夹中的所有 Python 脚本并复制
all_scripts = getFiles (this_script_path + scripts_folder + "*.py")

for item in all_scripts do
(
	copyFile item ((GetDir #userScripts) + script_folder_name + filenameFromPath item)
	format "已复制: %\n" (filenameFromPath item)
)

-- 创建宏脚本
create_macro_script()

-- 显示安装成功消息
messageBox ("安装成功！\n\n使用方法：\n右键点击工具栏 > 自定义...\n选择类别 \"MaxExporter\"\n将 \"" + script_name + "\" 拖拽到工具栏\n\n或者：\n按 X 键打开命令面板，搜索 'MaxExporter' 或 '导出工具'")

