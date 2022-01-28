import os
import json
import re

#from Qt import QtCore, QtGui
# use PyQt5 flavors to get QPainterPath.addText to work
from PyQt5 import QtCore, QtGui


#03dec2021
# i want to use the 'alternate' attribute for another purpose
# i want to use it as a filename to be loaded when node is dbl clicked
#  needs study to see if alternate is same thing as item of concern
# well, 'alternate' orig is read from default_config.json
# and it only appears once   alternate = 20
# so its pretty much a constant, and is not neccesary
# i can rem the 3 uses of 'alternate' and loose nothing
#
#06dec i see alternate slots have diff color bg's  grey or black
# its due to the chg on 03dec ^^
# TODO find out whre the bg chgs and make it consistant, not alternating
# hahah this happened when messing with attrib 'alternate'
#
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
        #03dec2021  this vvv could be rem-ed, i dont use it
        #if alternate:
        #    mult = _generateAlternateColorMultiplier(color, av)
        #
        #
        #    color = QtGui.QColor(max(0, data[0]-(av*mult)), max(0, data[1]-(av*mult)), max(0, data[2]-(av*mult)))
        return color

    # rgba
    elif len(data) == 4:
        color = QtGui.QColor(data[0], data[1], data[2], data[3])
        #03dec2021 this vvv could be rem-ed, i dont use it
        #if alternate:
        #    mult = _generateAlternateColorMultiplier(color, av)
        #    color = QtGui.QColor(max(0, data[0]-(av*mult)), max(0, data[1]-(av*mult)), max(0, data[2]-(av*mult)), data[3])
        #
        #06dec what is format of 'color' ?
        #06dec  printing got me an empty dict  '{}'

        return color

    # wrong
    else:
        print('Color from configuration is not recognized : ', data)
        print('Can only be [R, G, B] or [R, G, B, A]')
        print('Using default color !')
        color = QtGui.QColor(120, 120, 120)
        #03dec2021 this vvv could be rem-ed, i dont use it
        #if alternate:
        #    color = QtGui.QColor(120-av, 120-av, 120-av)
        return color


#03dec2021 neutered ( not called and non existant )
# i want to use 'alternate' as a filename to be loadGraph'ed when node is dbl clicked
# this vvv code is only called by ^^^ code and &&& code ^^^ does not need the 'alternate; if modified accord to notes above
# so this VVV code can be rem-ed out as well as ^^^ code

#def _generateAlternateColorMultiplier(color, av):
"""
     Generate a multiplier based on the input color lighness to increase
     the alternate value for dark color or reduce it for bright colors.

     :param color: Input color.
     :type  color: QColor.

     :param av: Alternate value.
     :type  av: Int.

"""
"""
    lightness = color.lightness()
    mult = float(lightness)/255

    return mult
"""

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
    #strg1="in _saveData, cfilePath is "
    #strg2=cfilePath
    #strg3=strg1+strg2
    #print(strg3)
    
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
    #strg1="in _loadData, dfilePath ="
    #strg2=dfilePath
    #strg3=strg1+strg2
    #print(strg3)
    
    with open(dfilePath) as json_file:
        j_data = json.load(json_file)

    json_file.close()

    #10nov reduce clutter
    #print("Data successfully loaded !")
    
    return j_data
