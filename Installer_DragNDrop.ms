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
	- Installer_DragNDrop.mse
==========================================================================
*/

-- 调整这部分
script_name = "MaxExporter"
script_folder_name = "\\MaxExporter\\"

-- 调整结束

-- 使用更可靠的方法获取脚本路径（支持中文路径）
script_path = getThisScriptFilename()
-- 如果 getThisScriptFilename() 返回 undefined，尝试使用其他方法
if script_path == undefined then
(
	-- 尝试使用 pathConfig 获取当前脚本路径
	try (
		script_path = pathConfig.GetCurrentPath() + "Installer_DragNDrop.ms"
	) catch (
		-- 如果还是失败，使用 sysInfo.currentDir
		script_path = sysInfo.currentDir + "\\Installer_DragNDrop.ms"
	)
)

-- 获取脚本目录路径（支持中文路径）
this_script_path = getfilenamepath script_path
-- 验证路径是否有效
if this_script_path == undefined or this_script_path == "" then
(
	messageBox ("错误：无法获取脚本路径。\n请确保安装脚本文件路径不包含特殊字符。\n当前路径：" + script_path as string)
	exit
)

-- 确保路径以反斜杠结尾（getfilenamepath 已经返回目录路径，不包含文件名）
if this_script_path[this_script_path.count] != "\\" then
	this_script_path = this_script_path + "\\"

scripts_folder = "scripts\\"

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
		try (
			-- 使用 pathConfig 构建路径，更好地支持中文路径
			local user_scripts_dir = GetDir #userScripts
			local main_py_path = pathConfig.appendPath user_scripts_dir "MaxExporter"
			main_py_path = pathConfig.appendPath main_py_path "Main.py"
			
			-- 确保路径是有效的字符串
			if classof main_py_path == String then
			(
				-- 确保路径存在
				if doesFileExist main_py_path then
				(
					-- 使用 python.ExecuteFile 执行，确保路径正确传递
					python.ExecuteFile main_py_path
				)
				else
				(
					messageBox ("错误：找不到 Main.py 文件\n路径：" + main_py_path)
				)
			)
			else
			(
				messageBox ("错误：路径类型无效\n类型：" + (classof main_py_path) as string)
			)
		)
		catch (
			messageBox ("执行错误：" + (getCurrentException()))
		)
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
scripts_path = this_script_path + scripts_folder + "*.py"
all_scripts = getFiles scripts_path

if all_scripts.count == 0 then
(
	messageBox ("错误：在以下路径找不到 Python 脚本文件：\n" + scripts_path)
)
else
(
	for item in all_scripts do
	(
		try (
			dest_path = (GetDir #userScripts) + script_folder_name + filenameFromPath item
			copyFile item dest_path
			format "已复制: %\n" (filenameFromPath item)
		) catch (
			format "复制失败: %\n错误: %\n" item (getCurrentException())
		)
	)
)

-- 创建宏脚本
create_macro_script()

-- 显示安装成功消息
messageBox ("安装成功！\n\n使用方法：\n右键点击工具栏 > 自定义...\n选择类别 \"MaxExporter\"\n将 \"" + script_name + "\" 拖拽到工具栏\n\n或者：\n按 X 键打开命令面板，搜索 'MaxExporter' 或 '导出工具'")

