# MAYA - IMPORT
import maya.cmds as cmds
import maya.OpenMayaUI as omUI
from shiboken2 import wrapInstance

# -- PYSIDE2 - IMPORT -- #
import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMainWindow
from PySide2 import QtUiTools

try:
    from importlib import reload #Fixed bug in python 3
except:
    pass

# -- OTHER - IMPORT
from functools import partial
import os
import json
import getpass
username = getpass.getuser()


# -- FUNCION - IMPORT -- #
import Import_FBX_Tools.Functions.Ultilities as Ultilities
reload(Ultilities)

SOURCE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_FILE = 'PROJECT_DATA.json'
SOURCE_PATH = SOURCE_PATH.replace('\\', '/')

LOCAL_JSON = SOURCE_PATH + "/Database"

# print(SOURCE_PATH)
JSON_PATH = LOCAL_JSON + "/" +  JSON_FILE

def main_window():
    ptr = omUI.MQtUtil.mainWindow()
    try:
        maya_window = wrapInstance(long(ptr), QtWidgets.QMainWindow)
    except:
        maya_window = wrapInstance(int(ptr), QtWidgets.QMainWindow) #Fixed bug in python 3

    return maya_window

class Import_Fbx(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Import_Fbx, self).__init__(main_window())
        self.centralwidgets = None
        self.vbox_layout = None
        self.project_tab = None
        self.main_tab = None
        self.child_tab_vertical_layout = None
        self.scroll_area = None
        self.scrollAreaWidgetContents = None
        self.resize_label = None
        self.grid_layout = None
        self.resize_image_layout = None
        self.my_slider = None
        self.my_search_layout = None
        self.my_search_linedit = None
        self.my_folder_path_layout = None
        self.my_folder_path_linedit = None
        self.my_open_folder_button = None
        self.my_button_layout = None
        self.my_update_objects_button = None
        self.my_update_folder_button = None
        self.my_delete_button = None

        self.image_label = None
        self.pixmap = None
        self.default_scale_value = 100
        self.image_format = 'jpg'
        self.scale_image_value = {0:[0,40], 1:[50,90], 2:[80, 120], 3:[100, 140], 4:[120, 160], 
                                5:[150, 180], 6:[170, 200], 7:[180, 210], 8:[190, 220]}

        # Ultilities.copy_file(SOURCE_PATH + "/Database/" + JSON_FILE,
        #                     LOCAL_JSON)
        
        self.my_ui()
        # self.current_tab_change()
        self.call_back()

    def my_ui(self):
        # -- Setting window -- #
        self.setWindowTitle("__FBX LIBRARY__")
        self.setMinimumHeight(500)
        self.setMinimumWidth(550)

        # -- Create central widget -- #
        self.centralwidgets = QtWidgets.QWidget()
        self.setCentralWidget(self.centralwidgets)

        # -- Create main Vbox layout -- #
        self.vbox_layout = QtWidgets.QVBoxLayout(self.centralwidgets)

        # -- Create project maintab -- #
        self.project_tab = QtWidgets.QTabWidget(self.centralwidgets)


        self.my_project_child_tab()

        # # -- Create Slider -- #
        self.resize_image_layout = QtWidgets.QHBoxLayout(self.centralwidgets)
        self.resize_label = QtWidgets.QLabel()
        self.resize_label.setText('Resize Image')

        self.my_slider = QtWidgets.QSlider()
        self.my_slider.setMinimum(0)
        self.my_slider.setMaximum(8)
        self.my_slider.setOrientation(PySide2.QtCore.Qt.Horizontal)

        self.resize_image_layout.addWidget(self.resize_label)
        self.resize_image_layout.addWidget(self.my_slider)

        # # -- Create Search Functions -- #
        self.my_search_layout = QtWidgets.QHBoxLayout(self.centralwidgets)
        self.my_search_linedit = QtWidgets.QLineEdit()
        self.my_search_linedit.setPlaceholderText(' Search Object ')

        self.my_search_layout.addWidget(self.my_search_linedit)

        # # -- Create Folder Path View -- #
        self.my_folder_path_layout = QtWidgets.QHBoxLayout(self.centralwidgets)
        self.my_folder_path_linedit = QtWidgets.QLineEdit()
        self.my_folder_path_linedit.setReadOnly(True)

        self.my_open_folder_button = QtWidgets.QPushButton()
        self.my_open_folder_button.setText('Open Folder')

        self.my_folder_path_layout.addWidget(self.my_folder_path_linedit)
        self.my_folder_path_layout.addWidget(self.my_open_folder_button)

        # # -- Create Button -- #
        self.my_button_layout = QtWidgets.QHBoxLayout(self.centralwidgets)
        self.my_update_objects_button = QtWidgets.QPushButton()
        self.my_update_objects_button.setText('Update Object')
        self.my_update_folder_button = QtWidgets.QPushButton()
        self.my_update_folder_button.setText('Create new library')
        self.my_delete_button = QtWidgets.QPushButton()
        self.my_delete_button.setText('Delete')

        self.my_button_layout.addWidget(self.my_update_objects_button)
        self.my_button_layout.addWidget(self.my_update_folder_button)
        self.my_button_layout.addWidget(self.my_delete_button)

        # -- Add widget to main layout -- #
        self.vbox_layout.addLayout(self.my_folder_path_layout)
        self.vbox_layout.addWidget(self.project_tab)
        self.vbox_layout.addLayout(self.resize_image_layout)
        self.vbox_layout.addLayout(self.my_search_layout)
        self.vbox_layout.addLayout(self.my_button_layout)

    def call_back(self):
        try:
            self.setting_functions(mode='project_tab_change')

        except:
            pass

        self.my_slider.valueChanged.connect(partial(self.setting_functions, mode="slider_value_change"))
        self.project_tab.currentChanged.connect(partial(self.setting_functions, mode="project_tab_change"))
        self.my_update_objects_button.clicked.connect(partial(self.setting_functions, mode="update_library"))
        self.my_update_folder_button.clicked.connect(partial(self.setting_functions, mode="create_root_folder"))
        self.my_open_folder_button.clicked.connect(partial(self.setting_functions, mode='open_current_folder'))
        self.my_search_linedit.textChanged.connect(partial(self.setting_functions, mode='search_line_edit_change'))
        self.my_delete_button.clicked.connect(partial(self.setting_functions, mode='delete'))


    # -- Update - UI -- #
    def my_project_child_tab(self):
        name_project = []
        all_project = Ultilities.get_data_from_json_file(JSON_PATH, 'r')
        for project in all_project:
            name_project.append(project)
            SOURCE_FOLDER = all_project[project]
            Ultilities.check_liberary_path(SOURCE_FOLDER)
            
            new_project_child_tab = QtWidgets.QWidget()
            self.project_tab.addTab(new_project_child_tab, "")
            self.project_tab.setTabText(name_project.index(project), project)

            folder_tab = QtWidgets.QTabWidget(self.centralwidgets)
            self.my_child_tab(folder_tab, SOURCE_FOLDER)

            child_tab_vertical_layout = QtWidgets.QVBoxLayout(new_project_child_tab)
            child_tab_vertical_layout.addWidget(folder_tab)


    def my_child_tab(self, main_tab,SOURCE_FOLDER):
        array_child_tab = []

        list_all_folder = os.listdir(SOURCE_FOLDER)
        for folder in list_all_folder:
            SOURCE_IMAGE = SOURCE_FOLDER + "/" + folder
            # array_image = [file for r,d,f in os.walk(SOURCE_IMAGE) for file in f if self.image_format in file]
            new_child_tab = QtWidgets.QWidget()
            main_tab.addTab(new_child_tab, "")
            main_tab.setTabText(list_all_folder.index(folder), folder)

            child_tab_vertical_layout = QtWidgets.QVBoxLayout(new_child_tab)
            store_image = QtWidgets.QListWidget(self.centralwidgets)
            store_image.setViewMode(QtWidgets.QListWidget.IconMode)
            store_image.setIconSize(QtCore.QSize(self.default_scale_value, self.default_scale_value))
            store_image.setResizeMode(QtWidgets.QListWidget.Adjust)
            store_image.setMovement(QtWidgets.QListView.Static)
            store_image.setGridSize(QtCore.QSize(self.default_scale_value+40, self.default_scale_value+40))
            try:
                for item  in self.my_label(SOURCE_IMAGE):
                    store_image.addItem(item)
            except:
                print('IMAGE ERROR')

            child_tab_vertical_layout.addWidget(store_image)

    def my_label(self, image_path):
        array_label = []
        if os.path.isdir(image_path):
            array_image = [i for i in os.listdir(image_path) if i.split('.')[-1] == self.image_format]

            for image in array_image:
                image_name = image.split(".")[0]
                item = QtWidgets.QListWidgetItem()
                item.setIcon(QtGui.QIcon(image_path + "/" + image))
                item.setText(image_name)

                array_label.append(item)

            return array_label

        elif os.path.isfile(image_path):
            image = image_path.split('/')[-1]
            image_name = image.split('.')[0]

            item = QtWidgets.QListWidgetItem()
            item.setIcon(QtGui.QIcon(image_path))
            item.setText(image_name)

            return item

    def update_listWidget(self):
        necessary_elements = Ultilities.detach_current_ui(self.project_tab, JSON_PATH)

        folder_name = necessary_elements[2]
        SOURCE_PATH = necessary_elements[0]

        current_listwidget = Ultilities.detach_widget(self.project_tab)[2] #Current listWidget
        current_listwidget.clear()

        for item  in self.my_label(SOURCE_PATH + '/' + folder_name):
            current_listwidget.addItem(item)

    def setting_functions(self, *args, **kwargs):
        mode = kwargs['mode']
        if mode == "slider_value_change":
            self.slider_active(self.my_slider)

        elif mode == "project_tab_change":
            self.project_tab_change()
            self.setting_functions(mode='signal_edit')
            self.setting_functions(mode='update_folder_path_view')

        elif mode == "double_click":
            Ultilities.import_fbx(self.project_tab, JSON_PATH)

        elif mode == 'folder_tab_change':
            self.setting_functions(mode='signal_edit')
            self.setting_functions(mode='update_folder_path_view')

        elif mode == 'update_library':
            Ultilities.export_fbx(self.project_tab, JSON_PATH)
            self.update_listWidget()

        elif mode == 'create_root_folder':
            folder_value =  Ultilities.root_folder()
            folder_path = folder_value[1]
            folder_name = folder_value[0]
            Ultilities.check_folder_empty(folder_path, 'Library_Template')
            data_value = Ultilities.get_data_from_json_file(JSON_PATH, 'r')
            data_value[folder_name] = folder_path

            Ultilities.get_data_from_json_file(JSON_PATH, 'w', data=data_value)
            self.reload()

        elif mode == 'update_folder_path_view':
            necessary_elements = Ultilities.detach_current_ui(self.project_tab, JSON_PATH)

            SOURCE_PATH = necessary_elements[0]
            folder_name = necessary_elements[2]

            self.my_folder_path_linedit.setText(SOURCE_PATH + '/' + folder_name)

        elif mode == 'open_current_folder':
            path = self.my_folder_path_linedit.text()
            os.startfile(path)

        elif mode == 'search_line_edit_change':
            self.search_change()
            self.setting_functions(mode='signal_edit')

        elif mode == 'signal_edit':
            self.item_double_click()
            self.slider_active(self.my_slider)

        elif mode == 'delete':
            #CAll MESSAGE BOX
            self.message_box('Delete ??')

    def search_change(self):
        current_listwidget = Ultilities.detach_widget(self.project_tab)[2] #Current listWidget

        necessary_elements = Ultilities.detach_current_ui(self.project_tab, JSON_PATH)

        SOURCE_PATH = necessary_elements[0]  # Source path
        name_item_selected = necessary_elements[1]    # File name
        folder_name = necessary_elements[2]   # Folder name

        name_search = self.my_search_linedit.text()
        all_item_in_mat_view = [current_listwidget.item(index).text() for index in range(current_listwidget.count())]
        list_item_show = [item for item in all_item_in_mat_view if name_search.lower() in item.lower()]

        if name_search != '' and list_item_show != []:
            current_listwidget.clear()
            [current_listwidget.addItem(self.my_label(SOURCE_PATH+'/'+folder_name+'/'+i+'.'+self.image_format)) for i in list_item_show]

            return 1
        else:
            SOURCE_IMAGE = SOURCE_PATH + '/' + folder_name
            current_listwidget.clear()
            for item  in self.my_label(SOURCE_IMAGE):
                current_listwidget.addItem(item)

            return 1

    def project_tab_change(self):
        current_widget = self.project_tab.currentWidget() # find current project tab 
        current_child_tab = current_widget.findChildren(QtWidgets.QTabWidget)[0] # find current folder tab
        current_child_tab.currentChanged.connect(partial(self.setting_functions, mode='folder_tab_change'))

    def slider_active(self, slider_handle):
        current_widget = self.project_tab.currentWidget() # find current project tab 
        value_handle = slider_handle.value()

        current_child_tab = current_widget.findChildren(QtWidgets.QTabWidget)[0] # find current folder tab
        current_tab = current_child_tab.currentWidget()

        current_layout = current_tab.findChildren(QtWidgets.QListWidget)[0] # find QListwidget in folder tab

        icon_size_value = self.scale_image_value[value_handle][0]
        grid_size_value = self.scale_image_value[value_handle][1]

        current_layout.setIconSize(QtCore.QSize(self.default_scale_value+icon_size_value, self.default_scale_value+icon_size_value))
        current_layout.setGridSize(QtCore.QSize(self.default_scale_value+grid_size_value, self.default_scale_value+grid_size_value))


    def item_double_click(self):
        current_widget = self.project_tab.currentWidget() # find current project tab 

        current_child_tab = current_widget.findChildren(QtWidgets.QTabWidget)[0] # find current folder tab
        current_tab = current_child_tab.currentWidget()

        current_layout = current_tab.findChildren(QtWidgets.QListWidget)[0] # find QListwidget in folder tab
        current_layout.itemDoubleClicked.connect(partial(self.setting_functions, mode="double_click"))


    def message_box(self, mess):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(mess)
        item_button = msgBox.addButton(self.tr('FBX'), QtWidgets.QMessageBox.ActionRole)
        folder_button = msgBox.addButton(self.tr('Folder'), QtWidgets.QMessageBox.ActionRole)
        project_button = msgBox.addButton(self.tr('Project'), QtWidgets.QMessageBox.ActionRole)
        msgBox.addButton(self.tr('Cancel'), QtWidgets.QMessageBox.ActionRole)
        ret = msgBox.exec_()
        if msgBox.clickedButton() == item_button:
            Ultilities.delete_item_selected(self.project_tab, JSON_PATH, 'fbx')
            self.reload()

        elif msgBox.clickedButton() == folder_button:
            Ultilities.delete_item_selected(self.project_tab, JSON_PATH, 'folder')
            self.reload()

        elif msgBox.clickedButton() == project_button:
            Ultilities.delete_item_selected(self.project_tab, JSON_PATH, 'project')
            self.reload()

        msgBox.show()

    def reload(self):
        try:
            self.close()
            self.deleteLater()
        except:
            pass

        self = Import_Fbx()
        self.show()





