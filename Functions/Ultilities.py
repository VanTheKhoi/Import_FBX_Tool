# MAYA - IMPORT
import maya.cmds as cmds
import maya.mel as mel
import maya.app.general.createImageFormats as createImageFormats

# -- PYSIDE2 - IMPORT -- #
import PySide2
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QMainWindow
from PySide2 import QtUiTools

# -- OTHER - IMPORT
from functools import partial
import os
import json
import subprocess
import shutil

def delete_item_selected(widget, JSON_PATH, mode):
    file_format = ".fbx"
    image_format = ".jpg"

    #Get path , and layout info
    # current_layout = detach_widget(widget)[2]

    necessary_elements = detach_current_ui(widget, JSON_PATH)

    source_fbx = necessary_elements[0]
    name_item_selected = necessary_elements[1]
    folder_item_selected = necessary_elements[2]

    data = get_data_from_json_file(JSON_PATH, mode='r')

    # Delete FBX
    if mode == 'fbx': 
        os.remove(source_fbx + "/" + folder_item_selected + "/" + name_item_selected + file_format)
        os.remove(source_fbx + "/" + folder_item_selected + "/" + name_item_selected + image_format)

    # Delete folder
    elif mode == 'folder' and len(os.listdir(source_fbx))>1:
        list_folder_content = os.listdir(source_fbx+"/"+folder_item_selected)
        shutil.rmtree(source_fbx+"/"+folder_item_selected)

    # Delete project
    elif mode == 'project' and len(data)>1:
        index = widget.currentIndex()
        title_tab = widget.tabText(index)
        folder_remove = data[title_tab]
        del data[title_tab]
        get_data_from_json_file(JSON_PATH, mode='w', data=data) #update data in Json

def check_folder_empty(path, folder_name):
    folder_children = os.listdir(path)

    if folder_children == []:
        folder = folder_name
        os.makedirs(path+"/"+folder)

        return 1

    else:
        return 1


def get_data_from_json_file(data_path, mode, data=None):
    if mode == 'r':
        json_file = open(data_path, mode)
        data_handle = json.load(json_file)
        json_file.close()

        return data_handle

    elif mode == 'w':
        print(data)
        json_file = open(data_path, mode)
        json.dump(data, json_file)
        json_file.close()

        return True

def check_liberary_path(path):
    if not os.path.exists(path):
        os.makedirs(path)

        #Open window explorer
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(path)
        dialog.getExistingDirectory()

def copy_file(src, dest, json_file = 'PROJECT_DATA.json'):
    if not os.path.exists(dest+"/"+json_file):
        robocopy([src], dest)

    else:
        pass

def robocopy(source, des):
    #source is list full file name or folder
    #des is full folder path destination
    file = {}
    folder = []
    for f in source:
        if os.path.isfile(f):
            file[os.path.split(f)[1]] = os.path.split(f)[0]
        else:
            folder.append(f)
    folderFromFile = {}
    for key, value in file.iteritems():
        if value not in folderFromFile:
            folderFromFile[value] = [key]
        else:
            folderFromFile[value].append(key)
    cmd =  r"C:\Windows\System32\Robocopy.exe "
    if file:
        for k, v in folderFromFile.iteritems():
            cmd += '"' + k + '" "' + des + '" '
            for f in v:
                cmd += '"' + f + '" '
            cmd += "/Z" + " /MT"
            out = subprocess.call(cmd, shell = False)
            cmd = r"C:\Windows\System32\Robocopy.exe "
    if folder:
        for f in folder:
            cmd += '"' + f + '" "' + des + '/' + os.path.split(f)[1] + '"' + " /S" + " /Z" + " /MT"
            subprocess.call(cmd, shell = False)
            cmd = r"C:\Windows\System32\Robocopy.exe "


def root_folder():
    dialog = QtWidgets.QFileDialog()
    folder_create = dialog.getExistingDirectory()
    folder_create = folder_create.replace('\\', '/')
    folder_name = folder_create.split('/')[-1]

    return (folder_name, folder_create)

def detach_widget(widget):
    current_widget = widget.currentWidget() # find current project tab 
    current_child_tab = current_widget.findChildren(QtWidgets.QTabWidget)[0] # find current folder tab
    current_tab = current_child_tab.currentWidget()
    current_layout = current_tab.findChildren(QtWidgets.QListWidget)[0] # find QListwidget in folder tab

    return (current_widget, current_child_tab, current_layout)

def detach_current_ui(widget, JSON_PATH):
    SOURCE_FBX_PATH = ''
    neccesary_elements = detach_widget(widget)

    current_child_tab = neccesary_elements[1] # find current folder tab
    current_layout = neccesary_elements[2] # find QListwidget in folder tab

    current_project_index = widget.currentIndex()

    name_tab = widget.tabText(current_project_index)
    try:
        selected_item = current_layout.selectedItems()[0]
        name_item_selected = selected_item.text()
    except:
        name_item_selected = None

    all_data_source = get_data_from_json_file(JSON_PATH, 'r')
    for data in all_data_source:
        if data == name_tab:
            SOURCE_FBX_PATH = all_data_source[data]

    current_folder_index = current_child_tab.currentIndex()
    folder_name = current_child_tab.tabText(current_folder_index)
    return (SOURCE_FBX_PATH, name_item_selected, folder_name)

def import_fbx(widget, JSON_PATH):
    necessary_elements = detach_current_ui(widget, JSON_PATH)

    SOURCE_FBX_PATH = necessary_elements[0]  # Source path
    name_item_selected = necessary_elements[1]    # File name
    folder_name = necessary_elements[2]   # Folder name

    FBX_PATH = SOURCE_FBX_PATH + "/" + folder_name + "/" + name_item_selected + ".fbx"
    # print(FBX_PATH)
    #--- IMPORT FBX -- #
    mel.eval('FBXImportUnlockNormals -v true')
    mel.eval('FBXImport -f \"{f}\";'.format(f = FBX_PATH))

def render_image(mesh, path):
    mel.eval('setCurrentRenderer "mayaHardware2";')
    mel.eval('setAttr hardwareRenderingGlobals.renderMode 4;')
    mel.eval('RenderIntoNewWindow;')
    mel.eval('updateRenderOverride;')
    mel.eval('renderWindowRender redoPreviousRender renderView')
    editor = 'renderView'
    formatManager = createImageFormats.ImageFormats()
    formatManager.pushRenderGlobalsForDesc("JPEG")
    cmds.renderWindowEditor(editor, e=True, writeImage=path + '/' + mesh)
    formatManager.popRenderGlobals()

def Screenshot_mesh_in_Scene(path, mesh, list_mesh_selected):
    # print(mesh)
    cameras = cmds.listCameras()
    name_mesh = mesh.split('|')[-1]
    [cmds.setAttr(m + ".visibility", 0) for m in [t for t in cmds.ls(tr=True, l=True) if cmds.listRelatives(t, s=True)]]
    cmds.setAttr(mesh + ".visibility", 1)
    cmds.select(mesh, replace=True)
    cmds.viewFit('perspShape')
    cmds.setAttr("perspShape.backgroundColor", 0.451, 0.451, 0.451,type='double3')
    render_image(name_mesh, path)
    [cmds.setAttr(m + ".visibility", 1) for m in list_mesh_selected]    

def do_export(full_path):
    mel.eval('FBXExportSmoothingGroups -v false;')
    mel.eval('FBXExportHardEdges -v false;')
    mel.eval('FBXExportTangents -v false;')
    mel.eval('FBXExportSmoothMesh -v false;')
    
    mel.eval('FBXExportInstances -v false;')
    mel.eval('FBXExportReferencedAssetsContent -v false;')

    mel.eval('FBXExportAnimationOnly -v false;')
    mel.eval('FBXExportApplyConstantKeyReducer -v false;')
    mel.eval('FBXExportBakeComplexAnimation -v false;')
    mel.eval('FBXExportBakeResampleAnimation -v false;')
    mel.eval('FBXExportCacheFile -v false; ')
    mel.eval('FBXExportColladaSingleMatrix false;')
    mel.eval('FBXExportColladaTriangulate false;')
    mel.eval('FBXExportConstraints -v false;')
    mel.eval('FBXExportInstances -v false;')
    mel.eval('FBXExportShapes -v false;')
    mel.eval('FBXExportSkins -v false;')
    mel.eval('FBXExportTriangulate -v false;')
    mel.eval('FBXExportUseSceneName -v false; ')

    mel.eval('FBXExportCameras -v false;')
    mel.eval('FBXExportLights -v false;')
    mel.eval('FBXExportEmbeddedTextures -v false;')
    mel.eval('FBXExportConvertUnitString "cm";')
    mel.eval('FBXExportFileVersion "FBX201400";')
    mel.eval('FBXExportUpAxis "y";')
    mel.eval('FBXExportScaleFactor 1.0;')
    mel.eval('FBXExportGenerateLog -v false;')

    mel.eval('FBXExport -f \"{f}\" -s'.format(f = full_path))

def export_fbx(widget, JSON_PATH):
    necessary_elements = detach_current_ui(widget, JSON_PATH)

    SOURCE_FBX_PATH = necessary_elements[0]
    folder_name = necessary_elements[2]
    selected = cmds.ls(sl=True, fl=True, l=True)

    #Find Current layout active 
    current_widget = widget.currentWidget() # find current project tab 
    current_child_tab = current_widget.findChildren(QtWidgets.QTabWidget)[0] # find current folder tab
    current_tab = current_child_tab.currentWidget()
    current_layout = current_tab.findChildren(QtWidgets.QListWidget)[0] # find QListwidget in folder tab

    all_Items = [current_layout.item(i).text() for i in range(current_layout.count())] 
    for s in selected:
        result = cmds.promptDialog(title='Rename Object',
                                    message='Enter Name:',
                                    button=['OK', 'Cancel'],
                                    defaultButton='OK',
                                    cancelButton='Cancel',
                                    dismissString='Cancel')

        if cmds.promptDialog(query=True, text=True) and result == 'OK':
            newName = cmds.promptDialog(query=True, text=True)
            full_path = (SOURCE_FBX_PATH + '/' + folder_name + '/' + newName + ".fbx")

            if newName in all_Items:
                print('ASSETS EXISTS')

            else: 
                objExport = cmds.duplicate(s, n = newName)
                objExport = cmds.ls(objExport, l=True)[0]
                cmds.select(objExport, replace=True)
                do_export(full_path)
                Screenshot_mesh_in_Scene(SOURCE_FBX_PATH + '/' + folder_name, objExport, selected)
                cmds.delete(objExport)

        elif not cmds.promptDialog(query=True, text=True) and result == 'OK':
            name_mesh_select = s.split('|')[-1]
            full_path = (SOURCE_FBX_PATH + '/' + folder_name + '/' + name_mesh_select + ".fbx")

            if s in all_Items:
                print('ASSETS EXISTS')

            else:
                cmds.select(s, replace=True)
                do_export(full_path)
                Screenshot_mesh_in_Scene(SOURCE_FBX_PATH + '/' + folder_name, s, selected)
