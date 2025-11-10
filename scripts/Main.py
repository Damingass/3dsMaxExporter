# -*- coding:utf8 -*-
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import qtmax
import os
import sys

# 确保系统默认编码支持UTF-8（用于中文路径）
if sys.platform == 'win32':
    import locale
    # 设置文件系统编码为UTF-8
    if hasattr(sys, '_enablelegacywindowsfsencoding'):
        sys._enablelegacywindowsfsencoding = False

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(__file__)

# 添加到 sys.path（优先级最高）
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)



from pymxs import runtime as rt
from ExtractAnimABC import export_mesh_abc
from socketsOutput import socketsOutput
import cameraOutput
    
class PyMaxDockWidget(QtWidgets.QDockWidget):
    def __init__(self, parent=None):
        super(PyMaxDockWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setWindowTitle('MaxExporter')
        self.initUI()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        qtmax.DisableMaxAcceleratorsOnFocus(self, True)
        
    def initUI(self):
        main_layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("导出工具")
        main_layout.addWidget(label)

        # 导出动画ABC按钮
        export_abc_btn = QtWidgets.QPushButton("导出动画ABC")
        export_abc_btn.clicked.connect(self.export_anim_abc)
        main_layout.addWidget(export_abc_btn)

        # 导出Socket Bone按钮
        export_socket_btn = QtWidgets.QPushButton("导出Socket Bone")
        export_socket_btn.clicked.connect(self.export_socket_bone)
        main_layout.addWidget(export_socket_btn)

        # 导出相机FBX按钮
        export_camera_btn = QtWidgets.QPushButton("导出相机FBX")
        export_camera_btn.clicked.connect(self.export_camera_fbx)
        main_layout.addWidget(export_camera_btn)

        widget = QtWidgets.QWidget()
        widget.setLayout(main_layout)
        self.setWidget(widget)
        self.resize(250, 150)

    def export_anim_abc(self):
        """导出动画ABC"""
        # 获取保存路径
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存ABC文件", "", "Alembic Files (*.abc)"
        )
        if not file_path:
            return
        
        # 获取选中的对象
        selected_objs = rt.selection
        meshes = [obj.name for obj in selected_objs] if selected_objs else None
        
        try:
            export_mesh_abc(file_path, meshes)
            QtWidgets.QMessageBox.information(self, "成功", f"ABC文件已导出到:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def export_socket_bone(self):
        """导出Socket Bone（兼容常规物体）"""
        # 获取保存路径
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存FBX文件", "", "FBX Files (*.fbx)"
        )
        if not file_path:
            return
        
        # 获取选中的对象
        selected_objs = rt.selection
        
        if not selected_objs:
            # 没有选中物体时，导出全部对象（包括骨骼和常规物体）
            all_objects = rt.objects
            # 过滤掉隐藏对象和系统对象（可选）
            visible_objects = [obj for obj in all_objects if not obj.isHidden]
            if not visible_objects:
                QtWidgets.QMessageBox.warning(self, "警告", "场景中没有找到可导出的对象")
                return
            objs = [obj.name for obj in visible_objects]
        else:
            # 选中物体时，导出该物体及其所有父子级和平级物体
            def find_root_node(node):
                """向上查找根节点（没有父节点的节点）"""
                current = node
                while current.parent:
                    current = current.parent
                return current
            
            def collect_all_descendants(node, collected):
                """从节点开始，向下递归收集所有后代节点（包括平级）"""
                if node not in collected:
                    collected.append(node)
                # 收集所有子节点（包括平级）
                for child in node.children:
                    collect_all_descendants(child, collected)
            
            # 找到所有选中对象的根节点
            root_nodes = set()
            for obj in selected_objs:
                root = find_root_node(obj)
                root_nodes.add(root)
            
            # 从每个根节点开始，收集所有后代节点
            all_objs = []
            for root in root_nodes:
                collect_all_descendants(root, all_objs)
            
            if not all_objs:
                QtWidgets.QMessageBox.warning(self, "警告", "没有找到可导出的对象")
                return
            objs = [obj.name for obj in all_objs]
        
        try:
            socketsOutput(objs, file_path)
            QtWidgets.QMessageBox.information(self, "成功", f"FBX文件已导出到:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def export_camera_fbx(self):
        """导出相机FBX"""
        # 获取保存路径
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存FBX文件", "", "FBX Files (*.fbx)"
        )
        if not file_path:
            return
        
        # 获取选中的相机
        selected_objs = rt.selection
        if not selected_objs:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择相机对象")
            return
        
        camera = selected_objs[0]
        # 检查是否是相机类型（支持多种相机类型：Freecamera, Targetcamera, Physical_Camera 等）
        # 使用 superClassOf 检查是否是相机的子类，这是最可靠的方法
        try:
            is_camera = rt.superClassOf(camera) == rt.Camera
            # 如果 superClassOf 检查失败，尝试检查类名
            if not is_camera:
                camera_class_str = str(rt.classOf(camera))
                is_camera = "Camera" in camera_class_str
        except:
            # 如果检查出错，尝试通过类名判断
            camera_class_str = str(rt.classOf(camera))
            is_camera = "Camera" in camera_class_str
        
        if not is_camera:
            camera_class_str = str(rt.classOf(camera))
            QtWidgets.QMessageBox.warning(
                self, 
                "警告", 
                f"选中的对象不是相机。对象类型: {camera_class_str}"
            )
            return
        
        try:
            cameraOutput.cameraOutput(camera.name, outFile=file_path)
            QtWidgets.QMessageBox.information(self, "成功", f"相机FBX文件已导出到:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

def main():
    #rt.resetMaxFile(rt.name('noPrompt'))
    main_window = qtmax.GetQMaxMainWindow()
    w = PyMaxDockWidget(parent=main_window)
    w.setFloating(True)
    w.show()

if __name__ == '__main__':
    main()