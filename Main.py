from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import qtmax
import os
import sys

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
        self.setWindowTitle('Pyside Qt  Dock Window')
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
        """导出Socket Bone"""
        # 获取保存路径
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存FBX文件", "", "FBX Files (*.fbx)"
        )
        if not file_path:
            return
        
        # 获取选中的对象
        selected_objs = rt.selection
        if not selected_objs:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择要导出的对象")
            return
        
        # 递归收集选中节点及其所有子节点
        def collect_children(node, collected):
            """递归收集节点及其所有子节点"""
            if node not in collected:
                collected.append(node)
            # 获取所有子节点
            for child in node.children:
                collect_children(child, collected)
        
        all_objs = []
        for obj in selected_objs:
            collect_children(obj, all_objs)
        
        objs = [obj.name for obj in all_objs]
        
        try:
            socketsOutput(objs, file_path)
            QtWidgets.QMessageBox.information(self, "成功", f"Socket Bone文件已导出到:\n{file_path}")
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