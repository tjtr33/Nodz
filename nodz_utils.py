#10feb2022 this file is clean
import os
import json
import re

#from Qt import QtCore, QtGui
# use PyQt5 flavors to get QPainterPath.addText to work
from PyQt5 import QtCore, QtGui


def _convertDataToColor(data=None, alternate=False, av=20):
    """
     Convert a list of 3 (rgb) or 4(rgba) values from the configuration
     file into a QColor.

     :param data: Input color.
     :type  data: List.

     :param alternate: Whether or not this is an alternate color.
     :type  alternate: Bool.

     :param av: Alternate value.
     :type  av: Int.

    """

    # rgb
    if len(data) == 3:
        color = QtGui.QColor(data[0], data[1], data[2])
        return color

    # rgba
    elif len(data) == 4:
        color = QtGui.QColor(data[0], data[1], data[2], data[3])
        return color

    # wrong
    else:
        print('Color from configuration is not recognized : ', data)
        print('Can only be [R, G, B] or [R, G, B, A]')
        print('Using default color !')
        color = QtGui.QColor(120, 120, 120)
        return color

def _createPointerBoundingBox(pointerPos, bbSize):
    """
     generate a bounding box around the pointer.

     :param pointerPos: Pointer position.
     :type  pointerPos: QPoint.

     :param bbSize: Width and Height of the bounding box.
     :type  bbSize: Int.

    """
    # Create pointer's bounding box.
    point = pointerPos

    mbbPos = point
    point.setX(point.x() - bbSize / 2)
    point.setY(point.y() - bbSize / 2)

    size = QtCore.QSize(bbSize, bbSize)
    bb = QtCore.QRect(mbbPos, size)
    bb = QtCore.QRectF(bb)

    return bb

def _swapListIndices(inputList, oldIndex, newIndex):
    """
     Simply swap 2 indices in a the specified list.

     :param inputList: List that contains the elements to swap.
     :type  inputList: List.

     :param oldIndex: Index of the element to move.
     :type  oldIndex: Int.

     :param newIndex: Destination index of the element.
     :type  newIndex: Int.

    """
    if oldIndex == -1:
        oldIndex = len(inputList)-1


    if newIndex == -1:
        newIndex = len(inputList)

    value = inputList[oldIndex]
    inputList.pop(oldIndex)
    inputList.insert(newIndex, value)

# IO
def _loadConfig(filePath):
    """
     Read the configuration file and strips out comments.

     :param filePath: File path.
     :type  filePath: Str.

    """
    with open(filePath, 'r') as myfile:
        fileString = myfile.read()

        # remove comments
        cleanString = re.sub('//.*?\n|/\*.*?\*/', '', fileString, re.S)

        data = json.loads(cleanString)

    return data

def _saveData(cfilePath, data):
    """
     save data as a .json file

     :param filePath: Path of the .json file.
     :type  filePath: Str.

     :param data: Data you want to save.
     :type  data: Dict or List.

    """
    
    f = open(cfilePath, "w")
    f.write(json.dumps(data,
                       sort_keys = True,
                       indent = 4,
                       ensure_ascii=False))
    f.close()

def _loadData(dfilePath):
    """
     load data from a .json file.

     :param filePath: Path of the .json file.
     :type  filePath: Str.

    """
    
    with open(dfilePath) as json_file:
        j_data = json.load(json_file)

    json_file.close()
    
    return j_data
