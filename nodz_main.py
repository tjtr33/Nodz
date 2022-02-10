import os
import re
import json
import sys

from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import *

import nodz_utils as utils


#ng  blows up   from nodz_demo import app
#import nodz_demo as demo
#demo.getScreenStuff()


#nodzd needs to be global
nodzd = {}

#22jan2022  these lines give real value to tokens rtnd by several funcs
isFirstLine  = 1
notFirstLine = 0
isPlugLine   = 2
isSocketLine = 3
notPinLine   = 0

#09jan2022 chg from global filePath to workingFile  bein null$ , use fpicker
workingFile = ""

# 06nov2021  heavy handed global aliasing
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtCore.Property = QtCore.pyqtProperty

defaultConfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_config.json')


class Nodz(QtWidgets.QGraphicsView):
    # class Nodz
    """
     The main view for the node graph representation.

     The node view implements a state pattern to control all the
     different user interactions.

    """
    # 08nov2021 these Signals played hell with PyQt5 so there are aliases to calls that are PyQt5 safe
    # 08jan2022 these lines vvv create signals
    signal_NodeCreated = QtCore.Signal(object)
    signal_NodeDeleted = QtCore.Signal(object)
    signal_NodeEdited = QtCore.Signal(object, object)
    signal_NodeSelected = QtCore.Signal(object)
    signal_NodeMoved = QtCore.Signal(str, object)
    signal_NodeDoubleClicked = QtCore.Signal(str)

    signal_AttrCreated = QtCore.Signal(object, object)
    signal_AttrDeleted = QtCore.Signal(object, object)
    signal_AttrEdited = QtCore.Signal(object, object, object)

    signal_PlugConnected = QtCore.Signal(object, object, object, object)
    signal_PlugDisconnected = QtCore.Signal(object, object, object, object)
    signal_SocketConnected = QtCore.Signal(object, object, object, object)
    signal_SocketDisconnected = QtCore.Signal(object, object, object, object)
    # 08jan try to make  a new sgl UNFINISHED
    signal_PlugSelected = QtCore.Signal(object)

    signal_GraphSaved = QtCore.Signal()
    signal_GraphLoaded = QtCore.Signal()
    signal_GraphCleared = QtCore.Signal()
    signal_GraphEvaluated = QtCore.Signal()

    signal_KeyPressed = QtCore.Signal(object)
    signal_Dropped = QtCore.Signal()

    def __init__(self, parent, configPath=defaultConfigPath):
        #30jan class Nodz func __init__
        """
         Initialize the graphics view.
        """
        # class Nodz  func __init__
        super(Nodz, self).__init__(parent)

        # Load nodz configuration.
        self.loadConfig(configPath)

        # General data.
        self.gridVisToggle = True
        self.gridSnapToggle = False
        self._nodeSnap = False
        #08jan selectedNodes is invented by author it is not a property in qt
        self.selectedNodes = None

        # Connections data.
        self.drawingConnection = False
        self.currentHoveredNode = None
        self.sourceSlot = None

        # Display options.
        self.currentState = 'DEFAULT'
        self.pressedKeys = list()

        #03feb2022 added for wheelzoom
        #08FEB2022 wheel zoom disbale dfor tests, just use +/- keys
        #  wheel zoom was integers 0-10, 
        #    +/- is floats,so better zoom  rez
        """
        #04feb was  self.zoomClamp = False
        #  making False allowed zoom in AND out ( else not both )
        self.zoomClamp = False
        self.zoomInFactor = 1.25
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0,8]
        """
    #funcs to get fnames for open and save
    def getFileNameForOpen(self):
        #30jan  class Nodz func getFileName
        #22jan2022 i think i dont need to have self in the parens
        #17dec  found on web vvv but if here it belongs to class Nodz
        # and my use case is down in slot/plug/socket
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"File to Load",workingFile,"All Files (*);;Text Files (*.txt)", options=options)
        #print("in getFileNameForOpen ", fileName)
        return fileName    

    def getFileNameForSave(self,suggestedFname):
        #30jan  class Nodz func getFileNameForSave
        #22jan2022 i think i dont need to have self in the parens
        #09jan2022 a fsaver dlog found on web for pyqt5
        # note saveGraph gets fname passed
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save to File",suggestedFname,"All Files (*);;Text Files (*.txt)", options=options)
        return fileName

    # func for rats nest layout
    def rowcol(self,ndx,gridW):
        #30jan  class Nodz func rowcol
        rnum= int(ndx / gridW)
        cnum= ndx -( rnum * gridW)
        return rnum,cnum

    # func to process show sig   capture  into json
    def chkFirstLine(self,line):
        #30jan  class Nodz func chkFirstLine
        first3char = line[:3]
        if((first3char == 'bit' ) or (first3char == 'flo' ) or (first3char == 'u32' ) or (first3char == 's32' )):
            return isFirstLine
        else:
            return notFirstLine

    def extractDatatypeNetname(self,line):
        #30jan  class Nodz func extractDatatypeNetname
        lparts=[]
        lparts=line.split(" ")
        dataType=lparts[0]
        netName = lparts[len(lparts)-1]
        return dataType, netName
    
    def chkPinDir(self,line):
        #30jan  class Nodz func chkPinDir
        first3char = line[:3]
        if first3char == '<==' :
            return isPlugLine
        else:
            if first3char == "==>":
                return isSocketLine
            else:
                return notPinLine

    def getNodePinName(self,fullName):
        #30jan  class Nodz func getNodePinName
        lparts=[]
        lparts=fullName.rsplit(".",1)
        nodeName=lparts[0]
        pinName=lparts[1]
        return nodeName, pinName

    def printOneAttrBlock(self,nodeName, pinName,lp):
        #30jan  class Nodz func printOneAttrBlock
        global nodzd
        strg1="\t\t\t\t{\n"
        nodzFile.write( strg1)
        strg1="\t\t\t\t\t\"dataType\": \"<type '"
    
        #22jan2022 ShowMe has no datatype, use 'npne' until edited by user
        # thats up to user to edit hypermedia filename and datatype
        if(pinName == "ShowMe"):
            strg2="none"
        else:
            strg2=nodzd[nodeName][pinName]['datatype']
        strg3="'>\",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
    
        strg1="\t\t\t\t\t\"cnxnSide\": \"right\",\n"
        if(pinName == "ShowMe"):
            strg1="\t\t\t\t\t\"cnxnSide\": \"none\",\n"
        nodzFile.write( strg1)
    
        strg1="\t\t\t\t\t\"name\": \""
        strg2=pinName
        strg3="\",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write( strg4)
    
        strg1="\t\t\t\t\t\"netname\": \""
        if(pinName == "ShowMe"):
            strg2="-"
        else:
            strg2=nodzd[nodeName][pinName]['netname']
        strg3="\",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
    
        strg1="\t\t\t\t\t\"plug\": "
        if(pinName == "ShowMe"):
            strg2="false"
        else:
            pinIsPlug = nodzd[nodeName][pinName]['isPlug']
            strg2="false"
            if pinIsPlug:
                strg2="true"
        strg3=",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
    
        strg1="\t\t\t\t\t\"plugMaxConnections\": -1,\n"
        nodzFile.write( strg1)
    
        strg1="\t\t\t\t\t\"preset\": \"attr_preset_1\",\n"
        nodzFile.write( strg1)
    
        strg1="\t\t\t\t\t\"socket\": "
        if(pinName == "ShowMe"):
            strg2="false"
        else:
            pinIsSocket = nodzd[nodeName][pinName]['isSocket']
            strg2="false"
            if pinIsSocket:
                strg2="true"
        strg3=",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
    
        strg1="\t\t\t\t\t\"socketMaxConnections\": 1\n"
        nodzFile.write( strg1)
    
        strg1="\t\t\t\t}"
        if not lp:
            strg1=strg1+","
        strg1=strg1+"\n"
        nodzFile.write( strg1)

    def nodeTail(self,lastNode, numNodesPrinted, gridSide, gridPixels):
        #30jan  class Nodz func nodeTail
        #02feb2022 i see the min Y value is 12  not 0  & never neg
        # this is a tail.suffix for each node, not for whole NODES stanza
    
        strg1="\t\t\t\"position\": [\n"
        nodzFile.write( strg1)

        row,col = self.rowcol(numNodesPrinted,gridSide)
    
        xpixels = col * gridPixels
        if xpixels == 0:
            xpixels += 1
        strg1="\t\t\t\t"
        strg2=str(xpixels)
        strg3=",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
        
        ypixels = row * gridPixels
        if ypixels == 0:
            #02feb2022 i simply make 1st row at y value of 12
            # was  ypixels += 1
            ypixels = 12
            
        strg1="\t\t\t\t"
        strg2=str(ypixels)
        strg3="\n"
        strg4=strg1+strg2+strg3
        nodzFile.write(strg4)
    
        strg1="\t\t\t],\n"
        nodzFile.write( strg1)
    
        strg1="\t\t\t\"preset\": \"node_preset_2\"\n"
        nodzFile.write( strg1)
    
        strg1="\t\t}"
        if not lastNode:
            strg1=strg1+","
        strg1=strg1+"\n"
    
        nodzFile.write( strg1)

    def storePinfo(self,nodeName,pinName,dataType,netName,isPlug,isSocket):
        #30jan  class Nodz func storePinfo
        global nodzd
        if not(nodeName in nodzd):
            nodzd[nodeName]={}
    
        nodzd[nodeName][pinName]={}
    
        nodzd[nodeName][pinName].update({"datatype":dataType})
        nodzd[nodeName][pinName].update({"netname":netName})
        nodzd[nodeName][pinName].update({"isPlug":isPlug})
        nodzd[nodeName][pinName].update({"isSocket":isSocket})

    def showall():
        #30jan  class Nodz func showall
        # prints to screen does not write to file
        # not used, just for debug, so prints wont happen unless code instructed to use this func
        # it walks thru dict 'nodzd' and prints everything ( does not write )
        global nodzd
        for nodeName in nodzd.keys():
            print(nodeName)
            for pinName in nodzd[nodeName].keys():
                strg1="\t"
                strg2=pinName
                strg3=strg1+strg2
                print(strg3)
                for attrName in nodzd[nodeName][pinName].keys():
                    strg1="\t\t"
                    strg2=attrName
                    attrValue=nodzd[nodeName][pinName][attrName]
        
                    # just for printing & concatenation
                    if attrValue == None:
                        attrValue="None"
                    if attrValue == True:
                        attrValue="true"
                    if attrValue == False:
                        attrValue="false"
            
                    strg3=" is "
                    strg4=attrValue
                    strg5=strg1+strg2+strg3+strg4
                    print(strg5)

            print("")

    def printNodeName(self,nodeName):
        #30jan  class Nodz func peinrNodeName
        strg1="\t\t\""
        strg2=nodeName
        strg3="\": {\n"
        strg4=strg1+strg2+strg3
        nodzFile.write( strg4)

    def printAlternate(self,alternate):
        #30jan  class Nodz func printAlternate
        strg1="\t\t\t\"alternate\": \""
        strg2=alternate
        strg3="\",\n"
        strg4=strg1+strg2+strg3
        nodzFile.write( strg4)

    def printAttrHdr(self):
        #30jan  class Nodz func printAttrHdr
        strg1="\t\t\t\"attributes\": [\n"
        nodzFile.write( strg1)




    #funcs for hypermedia  ( fname stored in 'alternate'  viewer hint stored in 'datatype')
    
    #04feb2022 remove doSCH requires special eschema app and user have wars over favorite
    #  so circumvent by allowing SVG of circuit (zommable pannable)
    # doSch depricated, requires eschema app installed, so use doSVG , smaller faster and independant of ecad on user system
    #def doSch(self,proFile):
    #    #30jan  class Nodz func doSch
    #    strg1="kicad "
    #    strg2=proFile
    #    strg3=strg1+strg2
    #    os.system(strg3)
    #    #subprocess.run(strg3)

    def doTxt(self,txtFile):
        #30jan  class Nodz func doTxt
        #19dec using just "nano fname" 
        #  would run nano in termnl that ran python nodz_demo.py
        #  and that was a mess when nano exited
        # so try openng a new terminal to run nanao from
        #04feb2022 a non-chg! i was looking howto cmd open radonly, and found it '-v'
        #   but instead will make dir/files ro
        strg1="xfce4-terminal -H --command \"nano "
        strg2=txtFile
        strg3="\""
        strg4=strg1+strg2+strg3
        os.system(strg4)
    
    def doSVG(self,svgFile):
        #30jan  class Nodz func doSVG
        #19dec  this vvv removes need for local ecad pgm
        # just make an svg of the schematic and mark attr <dataType = "svg">
        self.svgWidget = QtSvg.QSvgWidget(svgFile)
        self.svgWidget.show()
        
    def doMan(self,manItem):
        #30jan  class Nodz func doMan
        strg1="xfce4-terminal -H --command \"man "
        strg2=manItem
        strg3="\""
        strg4=strg1+strg2+strg3
        os.system(strg4)
    
    def doUrl(self,url):
        #30jan  class Nodz func doUrl
        strg1="firefox-esr "
        #19dec spcl invocation of chromium to stop it bitching about keyring
        #strg1="chromium --password-store=basic "
        strg2=url
        strg3=strg1+strg2
        os.system(strg3)
    
    def doImg(self,imgFname):
        #30jan  class Nodz func doImg
        self.w = MyPopup(imgFname)
        #17dec the popup wndo size is set by  setPixmap in class mypopup
        #17dec TODO this fx should get image fname
        # the class should NOT set img pixmap sizes
        self.w.show()

    def doEditSaveMe(self,txtFile):
        #30jan  class Nodz func doEditSaveMe
        
        #14jan2022 this is very handy
        # select a node, press F, the screen is full with just the 1 node
        # then ctrl dbl clk the node( not a slot )
        # the a texteditlr opens with entire json file
        # scroll to the node stanza and edit anything
        # esp cnxnSide ( to prevent wires hidden under nod (
        # esp slot order ( to untwist nets cnxd to node )
    
        #09jan2022   works and single wndo to close :-)
        strg1="scite "
        strg2=txtFile
        strg3=strg1+strg2
        os.system(strg3)
    
    #funcs for qt events------------------------------------
    def mousePressEvent(self, event):
        
        #09feb inhibit any mouse evt
        #return True
        #class Nodz func mousePressEvenet
        """
         Initialize tablet zoom, drag canvas and the selection.
        """
                
        """
        # mycode was just for dbug
        #08jan   beg my code---------------------
        
        #08jan these vvv turn itemAt into english
        clkontype = (type(self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform())))
    
        #14jan get some info about thing clkd on
        if clkontype == NodeItem:
            print("Node clkd")
        if clkontype == PlugItem:
            print("PlugItem")
        if clkontype == SocketItem:
            print("SocketItem")
            
        #14jan for CnxnItem, additionally display the key modifier(s)
        if clkontype == ConnectionItem:
            if (event.modifiers() == QtCore.Qt.ControlModifier):    
                print("class Nodz func mousePress ANY BTN CTRL  ConnectionItem")
                # NB  ctrl left clk  does NOTHING
                # NB  ctrl l btn DRAG  DOES  ( it selects nodes , aka lasoo)
                
        #08jan   end my code---------------------
        """
        
        #14jan new top of pinball if/elif..
        #14jan my own select all code ^shiftMetLeftPress
        #elif ((event.button() == QtCore.Qt.LeftButton ) and 
        
        if ((event.button() == QtCore.Qt.LeftButton ) and 
              (event.modifiers() & QtCore.Qt.ShiftModifier ) and
              (event.modifiers() & QtCore.Qt.MetaModifier ) and
              (event.modifiers() & QtCore.Qt.ControlModifier ) and
              (self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform()) is None)):
            #14jan MY select all  ^shiftMetaLpress
            #  long ago i made ^shiftMetaLeftPress a 'select all'	    
            # a lasoo rqrs two points to define the rect to be selected
            # i ignore the clk posn and use 0,0 for topleftcorner
            # and a qt5 func to get me botright corner of everything
            # so the rect will enclose all 
            # I  BEGIN the state of SELECTION here, only here
            #print("l btn and SHIFTCONTROLMETA---------------****")
            self.currentState = 'SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)

        #04feb2022 from orig code, alt midl press give blackhand mano nero
        # Drag view
        elif (event.button() == QtCore.Qt.MiddleButton and
              event.modifiers() == QtCore.Qt.AltModifier):
            self.currentState = 'DRAG_VIEW'
            self.prevPos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setInteractive(False)

        elif (event.button() == QtCore.Qt.LeftButton and
              QtCore.Qt.Key_Shift in self.pressedKeys and
              QtCore.Qt.Key_Control in self.pressedKeys):
            # Add selection
            #04jan2022 2146
            # this is CTL SHIFT LBTN PRESS ( other code handle release)
            #  it sets up a STATE  'ADD_SELECTION'        
            # THIS is start of ghost rect enveloping nodes.. before Focus is used
            self.currentState = 'ADD_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)

        # Subtract selection
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ControlModifier):
            self.currentState = 'DEFAULT'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Toggle selection
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ShiftModifier):
            self.currentState = 'TOGGLE_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)
            
        else:
            self.currentState = 'DEFAULT'

        super(Nodz, self).mousePressEvent(event)

    #end -----class Nodz func mousePressEvenet

    #03feb2022  added from web,, works but range is wrong
    #   if i start with overview, i cant get closer, only firther away ( making small smal even smaller)
    #08feb defeat heel zooom for tests, on;y use +/- key zoom
    """
    def wheelEvent(self, event): 
        '''override wheel event'''
        # calculate zoom factor  
        
        #03feb fulfill a dangling var
        #self.zoomInFactor = 1.25
        
        zoomOutFactor = 1 / self.zoomInFactor

        # store scene position

        # calculate zoom
        #self.zoomStep = 1
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        
        #self.zoomRange = [0,8]
        
        if self.zoom < self.zoomRange[0]: 
            self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: 
            self.zoom, clamped = self.zoomRange[1], True   

        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)
        #08feb2022 i dont want to know zoomFactor or scale
        #  i want to know what those scalars are applied to
        # and print with the h v scrollbars in another place
    """    
    def mouseMoveEvent(self, event):
        #return
        #class Nodz  func  mouseMoveEvent
        """
         Update tablet zoom, canvas dragging and selection.
        """

        #14jan there is no ZOOM VIEW state (alt and whell nfg in xfce4)
        # so rem out
        
        # Drag canvas.
        if self.currentState == 'DRAG_VIEW':
            offset = self.prevPos - event.pos()
            self.prevPos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())
        # which leaves the single last stanza 'RubberBand Selectiom
        #14jan i can lassoo the nodes i want ok
        elif (self.currentState == 'SELECTION' or
              self.currentState == 'ADD_SELECTION' or
              self.currentState == 'SUBTRACT_SELECTION' or
              self.currentState == 'TOGGLE_SELECTION'):
            # RubberBand selection
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

        super(Nodz, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        #return True

        #class Nodz func mouseReleaseEvent
        """
         Apply tablet zoom, dragging and selection.
        """
        #14jan state Zoom View only set with wheel event or an Alt Press
        # i use neither becuz: both wheel event and alt modifier bad in xfce4
        # so remove that stanza off the pinball top
    
        #04feb DRAG VIEW reinstated from orig  alt midl drag
        # Drag View.
        if self.currentState == 'DRAG_VIEW':
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setInteractive(True)
            #print("vscroll is ",self.verticalScrollBar().value())
            #print("hscroll is ",self.horizontalScrollBar().value())
            #08feb disable wheel zoom which owned self.zoom
            # print("zoom is ",self.zoom)
            
        elif self.currentState == 'SELECTION':
            # if state == SELECTION then mouseReleas will choose ALL
            #05jan2022 why was i in SELECTION state? 
            #  in class Nodz mousePress, in ^shiftMteLeft press, i set state = SELECTION
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            painterPath = self._releaseRubberband()
                
            self.setInteractive(True)
        
            # 09jan2022 found   itemsArea = self.scene().itemsBoundingRect()
            # cool it works, i didnt like my hard numbered kludge
            ppath = QPainterPath()
            ppath.addRect(self.scene().itemsBoundingRect())
            #22jan2022 this vvv does NOT print when i drag a ghost rect over alll nodes
            #22jan i thought i'd be in this part of if/elif but NO, in next!
            #  actually in ADD_SELECTION
            #print("class Nodz func mouseRelease state SELECTION itemsBoundingRect ",self.scene().itemsBoundingRect().x(),self.scene().itemsBoundingRect().y(),self.scene().itemsBoundingRect().width(),self.scene().itemsBoundingRect().height())
            self.scene().setSelectionArea(ppath)

        elif self.currentState == 'ADD_SELECTION':
            #22jan2022 this is where i am when i drag a ghost rect over any
            # this code iterates over all nodes
            # 27nov  add selection means add to selected list
            #print("class Nodz func mouseRelease state ADD_SELECTION ")
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(True)

        elif self.currentState == 'SUBTRACT_SELECTION':
            #print("class Nodz func mouseRelease state SUBTRACT_SELECTION ")
            # 27nov what does subtract mean? delete? i think de-selected
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(False)

        elif self.currentState == 'TOGGLE_SELECTION':
            #print("class Nodz func mouseRelease state TOGGLE_SELECTION ")
            # 27nov what does toggle mean? i think toggle selected-ness
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                if item.isSelected():
                    item.setSelected(False)
                else:
                    item.setSelected(True)

        self.currentState = 'DEFAULT'
        #print("class Nodz func mouseRelease exit") 	
        super(Nodz, self).mouseReleaseEvent(event)
     
    def keyPressEvent(self, event):
        #30jan class Nodz func keyPressEvent()
        """
         #03feb2022 TODO redo all these infos in tripple quotes
         Save pressed key and apply shortcuts.

         Shortcuts are:
         DEL - Delete the selected nodes
         F - Focus view on the selection
         + zoom in
         - zoom out
         L load scene
         S save scene
         R estore scene to full scale ( usually way too big for screen, worls but most outside of viewport
        """
        #22jan2022
        global nodzd
        global sigF
        global nodzFile
    
        #05dec use global  keyword with filePath
        #09jan2022 rename global filePath to workingFile
        global workingFile
            
        #09jan2022   it is concatenating a string afaict
        # useful?  not afaict   the list is just tossed later
        if event.key() not in self.pressedKeys:
            self.pressedKeys.append(event.key())

        #09jan2022 ERASE vvv works  del or b/s
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self._deleteSelectedNodes()

        #03FEB2022 TODO add arrow key pan udlr from web
        
        #03FEB2022 TODO replace this vvv with wheel zoom code found on web
        #09jan2022 ZOOM IN works  either keypad or shift'='
        if event.key() == QtCore.Qt.Key_Plus:
            self.scale(1.03,1.03)
            self.currentState = 'DEFAULT'

            #the current scale can be calcd from self.sceneRect()
            # in view coords vs in scene coords
            w = self.sceneRect().width()
            h = self.sceneRect().height()
            #
            #print("self.sceneRect w is ",w," h is ",h)
            spoint=self.mapFromScene(w,h)
            sw=spoint.x()
            sh=spoint.y()
            #print("self.sceneRect mapFromScene is ",sw,sh)        
            #09feb the ratio of viewWidth / scebeWidth is THEscale
            THEscale = sw/w
            #print("THEscale is ",THEscale)
            
            
            #09jan2022 ZOOM OUT works  either keypad or '-'
        if event.key() == QtCore.Qt.Key_Minus:
            self.scale(0.970873786408,0.970873786408)
            self.currentState = 'DEFAULT'
            #print("self.sceneRect w is ",self.sceneRect().width()," h is ",self.sceneRect().height())

            #the current scale can be calcd from self.sceneRect()
            # in view coords vs in scene coords
            w = self.sceneRect().width()
            h = self.sceneRect().height()
            #
            #print("self.sceneRect w is ",w," h is ",h)
            spoint=self.mapFromScene(w,h)
            sw=spoint.x()
            sh=spoint.y()
            #print("self.sceneRect mapFromScene is ",sw,sh)        
            #09feb the ratio of viewWidth / scebeWidth is THEscale
            THEscale = sw/w
            #print("THEscale is ",THEscale)

        #22jan2022 R is very bad
        #09jan2022
        # R  RESIZE  restore full size   not very usefuL
        # I DID find i can restore the original scale ( or unscaled scene )
        #  on Stack Overflow
        # To reset the index you must reset the transformation:
        #  {your_graphicsview}.setTransform(QtGui.QTransform())
        # so self.setTransform(QtGui.QTransform())  should work
        # try it in key 'R'  for resize
        # WORKS  but not very useful, becuz that size doesnt fit on screem (usually, or you have a 2node graph ;-/
        if event.key() == QtCore.Qt.Key_R:
            self.setTransform(QtGui.QTransform())


        #10jan2022 open halsignal file
        ############  CONVERT  open hal signal file  key C    ###################
        if event.key() == QtCore.Qt.Key_C:
            #03feb2022  TODO break this out to a func (or many )
            if event.modifiers() == QtCore.Qt.NoModifier:

                #,,,,,,,,,,,open input file, read to list, close file
                #sigF = open('/home/tomp/Nodz/parseHal/file-IN/haledm11jan2022.signals', 'r')
                sigFname = self.getFileNameForOpen()

                sigF = open(sigFname, 'r')
                Lines = sigF.readlines()
                for ndx in range(0,len(Lines)-1):
                    Lines[ndx]=Lines[ndx].strip()
                sigF.close()
                #,,,,,,,,,,,close input file ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,


                #process lines read frpm halcmd show sig

                #nodzd={}
                ndx=2
                while ndx < (len(Lines)-1):
                    thisLine=Lines[ndx]
                    if self.chkFirstLine(thisLine) == isFirstLine:
                        dataType,netName=self.extractDatatypeNetname(Lines[ndx])
                        ndx += 1
                    else:
                        while True:
                            thisLine = Lines[ndx]
                            isPlug=False
                            isSocket=False
                            if not (self.chkFirstLine(thisLine) == isFirstLine):
                                lineType = self.chkPinDir(thisLine)
                                if not(lineType == notPinLine):
                                    if lineType == isPlugLine:
                                        isPlug=True
                                    elif lineType == isSocketLine:
                                        isSocket=True
                                    lparts=thisLine.split(" ")
                                    lpartsLen = len(lparts)
                                    nodeName,pinName = self.getNodePinName(lparts[lpartsLen-1])
                                    self.storePinfo(nodeName,pinName,dataType,netName,isPlug,isSocket)
                                    ndx += 1
                                    break
                            break
                        else:
                            break
                #22jan2022 sndt{} a dict   sn  signalname (key)  dt  datatype (value)
                sndt={}
                for nodname in nodzd:
                    for pnam in nodzd[nodname]:
                        sn = nodzd[nodname][pnam]['netname']
                        dt = nodzd[nodname][pnam]['datatype']
                        sndt.update({sn:dt})
                #------------end main code parse input file to dict ---------------------------------------

                #-----------------begin collecting all cnxn pairs----------
                cnxns=[]
                for nodeName in nodzd.keys():
                    for pinName in nodzd[nodeName].keys():
                        pinfo=[]
                        pinfo.append(nodzd[nodeName][pinName]['netname'])
                        fqpn=nodeName+"."+pinName
                        pinfo.append(fqpn)
                        pinfo.append(nodzd[nodeName][pinName]['isPlug'])
                        pinfo.append(nodzd[nodeName][pinName]['isSocket'])
                        cnxns.append(pinfo)
                cnxns.sort()
                cnxnsets=[]
                ndx = 0
                while ndx < (len(cnxns)-1):
                    netset=[]
                    nn=cnxns[ndx][0]
                    netset.append(cnxns[ndx])
                    ndx += 1
                    limit=len(cnxns)-1
                    while(cnxns[ndx][0]== nn):
                        netset.append(cnxns[ndx])
                        ndx+=1
                        if(ndx > limit):
                            break
    
                    cnxnsets.append(netset)
                #-----------------end collecting all cnxn pairs----------

                suggestedFirstName = sigFname.rsplit('.',1)[0]
                suggestedFname = suggestedFirstName + ".json"
                nodzFname = self.getFileNameForSave(suggestedFname)
                nodzFile = open(nodzFname,"w")

                #22jan begin writing CONNECTIONS stanza----------------
                nodzFile.write("{\n")
                nodzFile.write("\t\"CONNECTIONS\": [\n")
                netSetsPrinted =0
                netSetLimit = len(cnxnsets)
                onLastLoop = False
                for netset in cnxnsets:
                    signalName=netset[0][0]
                    numlists=len(netset)
                    defaultPlugName=signalName+"Source.out"
                    plugName=""
                    plcount=0
                    hasPlug = False
                    for line in netset:
                        if line[2] == True:
                            hasPlug = True
                            plugName=line[1]
                            break
                        plcount += 1
                    if not plugName:
                        plugName = defaultPlugName
                        nodeName=signalName+"Source"
                        pinName="out"
                        dataType = sndt[signalName]
                        netName=signalName
                        isPlug=True
                        isSocket=False
                        self.storePinfo(nodeName,pinName,dataType,netName,isPlug,isSocket)
                    #################### END PlugName ########################

                    #################### BEG SocketName(s) ########################
                    hasSocket=[]
                    for line in netset:
                        hasSock=False
                        if line[3] == True:
                            hasSock = True
                        hasSocket.append(hasSock)
                    slcount=0
                    for line in netset:
                        if line[3] == True:
                            hasSock=True
                        else:
                            hasSock=False
                        slcount += 1
                    numSocks=0
                    for n in hasSocket:
                        if n==True:
                            numSocks+=1
                    defaultSocketName=signalName+"Dest.in"
                    socketName=""
                    if numSocks == 0:
                        socketName=defaultSocketName
                        nodeName=signalName+"Dest"
                        pinName="in"
                        dataType = sndt[signalName]
                        netName="-"
                        isPlug=False
                        isSocket=True
                        self.storePinfo(nodeName,pinName,dataType,netName,isPlug,isSocket)
                    #################### END SocketName(s) ########################
        
                    #  i am duplicating code maybe
                    for pndx in range(0,len(netset)):
                        isPlug = netset[pndx][2]
                        if (isPlug):
                            plugName=netset[pndx][1]
                            break
                    theseSockets = []
                    for sndx in range(0,len(netset)):
                        isSocket = netset[sndx][3]
                        if (isSocket):
                            theseSockets.append(netset[sndx][1])
                    if len(theseSockets) == 0:
                        theseSockets.append(defaultSocketName)
                    for x in range(0,len(theseSockets)):
                        strg1="\t\t[\n"
                        nodzFile.write(strg1)
                        strg1="\t\t\t\""
                        strg2=plugName
                        strg3="\",\n"
                        strg4=strg1+strg2+strg3
                        nodzFile.write(strg4)
                        strg1="\t\t\t\""
                        strg2=theseSockets[x]
                        strg3="\"\n"
                        strg4=strg1+strg2+strg3
                        nodzFile.write(strg4)
                        strg1="\t\t]"
                        if onLastLoop:
                            strg2="\n"
                        else:
                            strg2=",\n"
                        strg3=strg1+strg2
                        nodzFile.write(strg3)
                    netSetsPrinted +=1
                    if(netSetsPrinted==netSetLimit-1):
                        onLastLoop=True
                strg1=("\t],\n")
                nodzFile.write(strg1)
                ######## END printing output for CONNECTIONS stanza############




                ############### begin printing NODES stanza #############
                strg1="\t\"NODES\": {\n"
                nodzFile.write( strg1)

                numNodesPrinted=0
                nodzdLen = len(nodzd)-1
                lastNode=False

                maxGridWideCount = 10
                gridXstep = 400
                gridYstep = 600
                gridPixels = 600
                # determine smallest gs (nodegridsize) that contains numNodes
                for gridWideCount in range(1,(maxGridWideCount+1)):
                    if (gridWideCount * gridWideCount ) >= nodzdLen + 1:
                        break
                gridW = gridWideCount
                gridH = gridWideCount
                gridSide = gridWideCount
                #some loops and some counts are 0 based and other 1 based
                # so i adjustthe num nodez (nodzdLen) for the current use case


                #22jan2022 oops forgot to write the Nodes section! already closed the file!

                for nodeName, pinDictList in nodzd.items():
                    self.printNodeName(nodeName)
                    self.printAlternate("ShowMe")
                    self.printAttrHdr()
                    self.printOneAttrBlock(nodeName,"ShowMe",False)
                    if numNodesPrinted == nodzdLen:
                        lastNode = True
                    numPinsPrinted=0	
                    pinsLimit = len(nodzd[nodeName])-1
                    lastPin = False
                    for pinName in nodzd[nodeName]:
                        if numPinsPrinted >= pinsLimit:
                            lastPin = True
                        self.printOneAttrBlock(nodeName,pinName,lastPin)
                        if lastPin == True:
                            if lastNode:
                                strg1="\t\t\t],\n"
                                nodzFile.write(strg1)
                                self.nodeTail(lastNode,numNodesPrinted,gridSide, gridPixels)
                                break
                            else:
                                strg1="\t\t\t],\n"
                                nodzFile.write(strg1)
                                self.nodeTail(lastNode,numNodesPrinted,gridSide,gridPixels)
                        numPinsPrinted += 1
                    numNodesPrinted += 1
                strg1="\t}\n"
                nodzFile.write( strg1)
                strg1="}\n"
                nodzFile.write( strg1)
                nodzFile.close()
        #-----------------end writing json file ----------

        ################# SAVE graph OR save view #################
        if event.key() == QtCore.Qt.Key_S:
            #01feb2022 use S fro save graph , but s fro save view
            # no need for fox spcl 'save as' thats up to user
            #if event.modifiers() == QtCore.Qt.NoModifier:
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                workingFile = self.getFileNameForSave(workingFile)
                
                #09jan2022 if fname from dlog has value, then save
                if workingFile:
                    self.saveGraph(workingFile)
                    #30jan load after d=save to reconnect all nets to nodes
                    #05feb2022 loadgraph rtns w,h
                    #09feb why am i loading in the save func?
                    w,h = self.loadGraph(workingFile)
                    #05feb try to make all node fit in scene and keep scene sized to all nodes
                    self.updateSceneRect(QRectF(0, 0, w, h))
                    
                    #09feb cant drag scene to see spind;e nodes
                    # i think the v scroll bat is liimited 
                    #self.fitInView(0,0,w,h, QtCore.Qt.KeepAspectRatio)

            #------END SAVE GRAPH-----------------------
        
            #------begin save view------------------
            #01feb2022 use 's' to save view
            #  works BUT i can see LASOO fails if zoomed way out and sloppy lassoo
            #   the reported list is not as expected
            #  but, if default is to show the Zoomed selectionlist
            #   then it is immediately seen and can be easily re-tried
            #   this is a fail inside qt lasoo
            #
            elif event.modifiers() == QtCore.Qt.NoModifier:
                #get list Of selected nodes
                selected_nodes = list()
                for node in self.scene().selectedItems():
                    selected_nodes.append(node.name)
                if len(selected_nodes) > 0:
                    #json_string = json.dumps(selected_nodes)
                    #print(json_string)
                    
                    # get fname for view
                    viewFname = self.getFileNameForSave("FileNameForView")
                    if viewFname:
                        viewFname = viewFname+".json"
                        with open(viewFname, 'w') as viewFile:
                            json.dump(selected_nodes, viewFile)
                        viewFile.close()
                # else do nada, if user wants to see /verify , they can 'l' load view
                
        ################# LOAD ############################
        if event.key() == QtCore.Qt.Key_L:
            #01feb2022 add l vs L difference  L loads scene l loads view in scene
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                #09feb2022 this is "L" capital   load  fro whole scene
                fileNameToOpen = self.getFileNameForOpen()
                if fileNameToOpen:
                    w,h= self.loadGraph(fileNameToOpen)
                    #09feb the scrollbars. or range of drag seem clipped, i cant get to spindle nodes at bot
                    # still ng  is h tool small? add 1000  no diff
                    #self.horizontalScrollBar().setRange(0,w)
                    #self.verticalScrollBar().setRange(0,h)
                    
                    #08feb i get wildly diff value for same .json  why?                    #09feb fixed minx maxx miny maxy and thus w,h too
                    #print("in key L  w,h are", w,h)
                    
                    workingFile = fileNameToOpen
                    
                    #05feb2022 loadGraph must calc the scene rect
                    
                    #print("self.scene().sceneRect() is ",self.scene().sceneRect())
                    
                    #09feb this vvv got me access to spindle nodes 
                    self.scene().setSceneRect(0, 0, w, h-600)
                    #self.scene.updateSceneRect(const QRectF &rect)

                    self.updateSceneRect(QRectF(0, 0, w, h))
                    
                    #self.fitInView(0,0,w,h, QtCore.Qt.KeepAspectRatio)
                    # vvv works 10x  gives top left of scene
                    #self.horizontalScrollBar().setValue(0)
                    #self.verticalScrollBar().setValue(0)
                    
                    # vvv works 10x  see bot rt corner of scene
                    #self.horizontalScrollBar().setValue(2965)
                    #self.verticalScrollBar().setValue(567)
                    
                    #08feb can i get the value of scroll bar?
                    

            elif event.modifiers() == QtCore.Qt.NoModifier:
                # 01feb2022 this is 'l'   load view, just a list of node names to fill viewport
                
                
                viewNameToOpen = self.getFileNameForOpen()
                if viewNameToOpen:
                    #print("viewNameToOpen is >",viewNameToOpen,"<")
                    
                    nodesToView = []
                    with open(viewNameToOpen) as json_file:
                        nodesToView = json.load(json_file)
                    json_file.close()
                    
                    #10feb de-sel all before selecting only wanted nodes
                    nodes = self.scene().nodes.keys()
                    for thisNode in nodes:
                        #self.scene().nodes.values()
                        self.scene().nodes[thisNode].setSelected(False)

                    #10feb select nodes from file
                    for thisNode in nodesToView:
                        #thisNode.setSelected(True)
                        self.scene().nodes[thisNode].setSelected(True)
                        
                    #10feb now call focus
                    self._focus()

        ################## FOCUS ###############################
        #27nov  ctrs the selection on screen
        if event.key() == QtCore.Qt.Key_F:
            #07feb dont focus for test, just set scrollbars to 650,650
            self._focus()
            
        #03feb2022  removed V(iew)  , s & l view file works well
        
        ################ EMIT KeyPressed SIGNAL ################
        # Emit signal.
        self.signal_KeyPressed.emit(event.key())
        
        #03feb2022 anpther app uses udlr keys to pan and tilt
        # but i see nothing in that code body that senses the keys or does the pan/tilt
        # so, on a guess that the qt system somehow does it, i pass event along
        # result, well,, ud works to some degree but lr  nada
        super().keyPressEvent(event)
        ################### end key press func ########################

    def keyReleaseEvent(self, event):
        #30jan class Nodz func keyReleaseEvent()
        """
         Clear the key from the pressed key list.
        """
        """
         03nov2021 S key used for save file now 
         so undo old usage
         if event.key() == QtCore.Qt.Key_S:
            self._nodeSnap = False
        """

        #09jan2022  keys that were pressed but not used 
        #  are added to a list, and the list is trashed here
        #  sounds stupid
        if event.key() in self.pressedKeys:
            self.pressedKeys.remove(event.key())

    def _initRubberband(self, position):
        #30jan class Nodz func _initRubberband
        """
         Initialize the rubber band at the given position.
        """
        self.rubberBandStart = position
        self.origin = position
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()

    def _releaseRubberband(self):
        #30jan class Nodz func _releaseRubberband
        """
         Hide the rubber band and return the path.
         20nov is this the bez? YES bez is a QPainterPath
        """
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self.rubberband.geometry())
        #print("_releaseRubberBand rect is ",rect.boundingRect())
        painterPath.addPolygon(rect)
        self.rubberband.hide()
        
        return painterPath

    def _focus(self):
        # class Nodz func _focus
        # 03feb2022 not broken but doesnt ctr nodes selected into viewport
        
        """
         Center on selected nodes or all of them if no active selection.
        """

        if self.scene().selectedItems():
            #print("in _focus  there are selected nodes")
            #for selname in self.scene().selectedItems():
            #    print(selname)
            # ^^^ i get the desired nodes lised but focus doesnt ctr on them
            
            itemsArea = self._getSelectionBoundingbox()
            #print("in _focus selected bbox is ", itemsArea)
            self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)
        else:
            #22jan2022  if NO nodes selected, then Focus on ALL
            #print("in _focus  there are NO selected nodes")
            bbox=self.sceneRect()
            #print("in _focus  automatically selected bbox is ", bbox)
            self.fitInView(bbox, QtCore.Qt.KeepAspectRatio)

    def _getSelectionBoundingbox(self):
        #30jan class Nodz func _getSelectionBoundingbox
        #03feb2022 TODO is this used? canit be used more?
        """
         Return the bounding box of the selection.
        """
        bbx_min = None
        bbx_max = None
        bby_min = None
        bby_max = None
        bbw = 0
        bbh = 0
        for item in self.scene().selectedItems():
            pos = item.scenePos()
            x = pos.x()
            y = pos.y()
            w = x + item.boundingRect().width()
            h = y + item.boundingRect().height()

            # bbx min
            if bbx_min is None:
                bbx_min = x
            elif x < bbx_min:
                bbx_min = x
            # end if

            # bbx max
            if bbx_max is None:
                bbx_max = w
            elif w > bbx_max:
                bbx_max = w
            # end if

            # bby min
            if bby_min is None:
                bby_min = y
            elif y < bby_min:
                bby_min = y
            # end if

            # bby max
            if bby_max is None:
                bby_max = h
            elif h > bby_max:
                bby_max = h
            # end if
        # end if
        bbw = bbx_max - bbx_min
        bbh = bby_max - bby_min
        return QtCore.QRectF(QtCore.QRect(bbx_min, bby_min, bbw, bbh))

    def _deleteSelectedNodes(self):
        #30jan class Nodz func _deleteSelectedNodes
        """
         Delete selected nodes.
        """
        selected_nodes = list()
        for node in self.scene().selectedItems():
            selected_nodes.append(node.name)
            node._remove()

        # Emit signal.
        self.signal_NodeDeleted.emit(selected_nodes)

    def _returnSelection(self):
        #30jan class Nodz func _returnSelection
        """
         Wrapper to return selected items.
        """
        selected_nodes = list()
        if self.scene().selectedItems():
            for node in self.scene().selectedItems():
                selected_nodes.append(node.name)

        # Emit signal.
        self.signal_NodeSelected.emit(selected_nodes)
        

    ##################################################################
    # API
    ##################################################################

    #05dec    filePath is ng from config file  default_config.json
    def loadConfig(self, somecfgpath):
        #30jan class Nodz func loadConfig
        """
         Set a specific configuration for this instance of Nodz.

         :type  somecfg: str.
         :param somecfgpath: The path to the config file that you want to use
        """
        self.config = utils._loadConfig(somecfgpath)

    def initialize(self):
        #30jan class Nodz func initialize
        """
         Setup the view's behavior.
        """
        # Setup view.
        config = self.config
        self.setRenderHint(QtGui.QPainter.Antialiasing, config['antialiasing'])
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, config['antialiasing'])
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, config['antialiasing_boost'])
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, config['smooth_pixmap'])
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        #09jan2022 scrol and pan suck  not clear on what ot is that i dislike
        # 03nov2021 ena scrolbars self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        # Setup scene. NB initially crazy eaxaggerated area from default_config
        scene = NodeScene(self)
        #30jan try to use calc'd width height from loadraph ( to b e coded still 30jan2022)
        #  use code for w h from...TBD
        # 05feb2022 need to use wdth & hght calculated from loadGraph
        #   but that code hasn't exec'd yet
        #   so a dummy value in default_config is ok for now
        #   no, easily too small so use exaggerated cfg w & h until resolved
        # try 8000 6000 (4:3) untill calc resolved
        sceneWidth = config['scene_width']
        sceneHeight = config['scene_height']
        scene.setSceneRect(0, 0, sceneWidth, sceneHeight)
        self.setScene(scene)
        # Connect scene node moved signal
        scene.signal_NodeMoved.connect(self.signal_NodeMoved)

        # Tablet zoom.
        #27nov  what is 'tablet zoom'?
        self.previousMouseOffset = 0
        self.zoomDirection = 0

        # Connect signals.
        self.scene().selectionChanged.connect(self._returnSelection)

        
    # NODES
    # TODO svg output of whole scene, may be useful w/o all this code, just for viewing

    #05dec HYPERMEDIA nodes have an 'alternate' property
    # I use alternate for multimeda add'l info about node
    # and to jump to sub graphs and back ( as deep as desired)
    # and manpages, svgPix, web urls, textfiles &more can be accessed
    # the top of a node with such xtra info has 'ShowMe'.
    #  just clk on that text and the dataType attribute will determine the viewer
    #  and the viewer will open a filename in 'alternate'
    
    def createNode(self, name='default', preset='node_default', position=None, alternate=""):
        #30jan class Nodz func createNode
        #22jan2022 creatNode is called for every node stanza in json file
        #  so the node DOES know its own x y posn
        """
         Create a new node with a given name, position and color.

         :type  name: str.
         :param name: The name of the node. The name has to be unique
                     as it is used as a key to store the node object.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :type  position: QtCore.QPoint.
         :param position: The position of the node once created. If None,
                         it will be created at the center of the scene.

         :type  alternate: bool.
         :param alternate: The attribute color alternate state, if True,
                          every 2 attribute the color will be slightly
                          darker.

         :return : The created node
        """
        # Check for name clashes
        if name in self.scene().nodes.keys():
            print('A node with the same name already exists : {0}'.format(name))
            print('Node creation aborted !')
            return
        else:
            nodeItem = NodeItem(name=name, alternate=alternate, preset=preset, config=self.config)

            # Store node in scene.
            self.scene().nodes[name] = nodeItem

            if not position:
                # Get the center of the view.
                #05jan2022 i think this vvv is where the 1st node in grid was put at scene center
                # so the test 'if not position' fails when position is 0,0
                # i _think_ ( i think thats why i use 1,1 someplace)
                position = self.mapToScene(self.viewport().rect().center())

            # Set node position.
            self.scene().addItem(nodeItem)
            # 22jan2022 is this vvv making xcoord == -(nodewidth/2)?
            nodeItem.setPos(position - nodeItem.nodeCenter)

            # Emit signal.
            self.signal_NodeCreated.emit(name)

            return nodeItem

    def deleteNode(self, node):
        #30jan class Nodz func deleteNode
        """
         Delete the specified node from the view.

         :type  node: class.
         :param node: The node instance that you want to delete.
        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Node deletion aborted !')
            return

        if node in self.scene().nodes.values():
            nodeName = node.name
            node._remove()

            # Emit signal.
            self.signal_NodeDeleted.emit([nodeName])

    def editNode(self, node, newName=None):
        #30jan class Nodz func editNode
        """
         Rename an existing node.

         :type  node: class.
         :param node: The node instance that you want to delete.

         :type  newName: str.
         :param newName: The new name for the given node.
        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Node edition aborted !')
            return

        oldName = node.name

        if newName != None:
            # Check for name clashes
            if newName in self.scene().nodes.keys():
                print('A node with the same name already exists : {0}'.format(newName))
                print('Node edition aborted !')
                return
            else:
                node.name = newName

        # Replace node data.
        self.scene().nodes[newName] = self.scene().nodes[oldName]
        self.scene().nodes.pop(oldName)

        # Store new node name in the connections
        if node.sockets:
            for socket in node.sockets.values():
                for connection in socket.connections:
                    connection.socketNode = newName

        if node.plugs:
            for plug in node.plugs.values():
                for connection in plug.connections:
                    connection.plugNode = newName
            
        # 12nov the cmd  node.update updates the dict 'node'  
        #  meaning   any new values for key:value pairs are updated in the dict
        #  there are other ways to use  somedict.update, but they need new key:value pairs passed to update('shoesize' : 12 ) 
        node.update()

        # Emit signal.
        self.signal_NodeEdited.emit(oldName, newName)

    #----------------------------------------------------------
    #                  ATTRS ( attributes of plugs/sockets )
    #----------------------------------------------------------

    #09jan2022 nodes dont have dots anymore, they have connection side = left or right
    # TODO a visual cnxn point , arrowheads?
    #  there is nothing visible to where the bezier comes from or goes to
    #  but user can see where it is by dragging out from a plug
    #   the user will notice a bit of the netname appear on mousepress
    #  and the acceptable sockets will highlight when the bezier nears them
    def createAttribute(self, node, cnxnSide='default', name='default', netname='defaultnetname', index=-1, preset='attr_default', plug=True, socket=True, dataType=None, plugMaxConnections=-1, socketMaxConnections=1):	    
        #30jan class Nodz func createAttribute
        """
         Create a new attribute with a given name.

         :type  node: class.
         :param node: The node instance that you want to delete.

         : type  name: str.
         :param name: The name of the attribute. The name has to be
                     unique as it is used as a key to store the node
                     object.

         :type  netname: str.
         :param netname: The name of the signal on the 'wire'

         :type  index: int.
         : param index: The index of the attribute in the node.

         : type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :type  plug: bool.
         :param plug: Whether or not this attribute can emit connections.

         :type  socket: bool.
         :param socket: Whether or not this attribute can receive
                       connections.

         type  dataType: type.
         :param dataType: Type of the data represented by this attribute
                         in order to highlight attributes of the same
                         type while performing a connection.

         :type  plugMaxConnections: int.
         :param plugMaxConnections: The maximum connections that the plug can have (-1 for infinite).

         :type  socketMaxConnections: int.
         :param socketMaxConnections: The maximum connections that the socket can have (-1 for infinite).

        """
        
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if name in node.attrs:
            print('An attribute with the same name already exists : {0}'.format(name))
            print('Attribute creation aborted !')
            return

        
        #22nov this vvv call also needs 'cnxnSide' passed
        #23nov creating a single attribute can onlu have 1 cnxnSide ( maybe none if attr is a parameter)
        node._createAttribute(cnxnSide=cnxnSide, name=name, netname=netname, index=index, preset=preset, plug=plug, socket=socket, dataType=dataType, plugMaxConnections=plugMaxConnections, socketMaxConnections=socketMaxConnections)


        # Emit signal.
        self.signal_AttrCreated.emit(node.name, index)

    def deleteAttribute(self, node, index):
        #30jan class Nodz func deleteAttribute
        """
         Delete the specified attribute.

         type  node: class.
         :param node: The node instance that you want to delete.

         :type  index: int.
         :param index: The index of the attribute in the node.
        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute deletion aborted !')
            return

        node._deleteAttribute(index)

        # Emit signal.
        self.signal_AttrDeleted.emit(node.name, index)

    def editAttribute(self, node, index, newName=None, newIndex=None):
        #30jan class Nodz func editAttribute
        """
         Edit the specified attribute.

         :type  node: class.
         :param node: The node instance that you want to delete.

         :type  index: int.
         param index: The index of the attribute in the node.

         :type  newName: str.
         :param newName: The new name for the given attribute.

         :type  newIndex: int.
         :param newIndex: The index for the given attribute.
        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if newName != None:
            if newName in node.attrs:
                print('An attribute with the same name already exists : {0}'.format(newName))
                print('Attribute edition aborted !')
                return
            else:
                oldName = node.attrs[index]

            # Rename in the slot item(s).
            #27nov   i dont think this code is used, i have never renamed a Node
            #  its a good idea. well, good names is a good idea
            # 09nov a slot may be a plug OR a socket
            if node.attrsData[oldName]['plug']:
                node.plugs[oldName].attribute = newName
                node.plugs[newName] = node.plugs[oldName]
                node.plugs.pop(oldName)
                for connection in node.plugs[newName].connections:
                    connection.plugAttr = newName

            if node.attrsData[oldName]['socket']:
                node.sockets[oldName].attribute = newName
                node.sockets[newName] = node.sockets[oldName]
                node.sockets.pop(oldName)
                for connection in node.sockets[newName].connections:
                    connection.socketAttr = newName

            # Replace attribute data.
            node.attrsData[oldName]['name'] = newName
            node.attrsData[newName] = node.attrsData[oldName]
            node.attrsData.pop(oldName)
            node.attrs[index] = newName

        if isinstance(newIndex, int):
            attrName = node.attrs[index]

            utils._swapListIndices(node.attrs, index, newIndex)

            # Refresh connections.
            # a cnxn is between a plug and a socket, in that order ( From Plug TO Socket)
            for plug in node.plugs.values():
                #12nov this vvv update any new values for keys in the dict 'plug'
                plug.update()
                if plug.connections:
                    for connection in plug.connections:
                        if isinstance(connection.source, PlugItem):
                            connection.source = plug
                            connection.source_point = plug.center()
                        else:
                            connection.target = plug
                            connection.target_point = plug.center()
                        if newName:
                            connection.plugAttr = newName
                        connection.updatePath()

            for socket in node.sockets.values():
                # 12nov this updates any new values for keys in dict 'socket'
                socket.update()
                if socket.connections:
                    for connection in socket.connections:
                        if isinstance(connection.source, SocketItem):
                            connection.source = socket
                            connection.source_point = socket.center()
                        else:
                            connection.target = socket
                            connection.target_point = socket.center()
                        if newName:
                            connection.socketAttr = newName
                        connection.updatePath()

            # 12nov this vvv is a spcl func for scenes ( not a dict update() )
            self.scene().update()

        # 12nov this vvv is puts any new values into dict 'node'
        node.update()

        # Emit signal.
        if newIndex:
            self.signal_AttrEdited.emit(node.name, index, newIndex)
        else:
            self.signal_AttrEdited.emit(node.name, index, index)



    def findBbox(self,listOfNodes):
        #03feb2022 TODO is this used? NO
        #  is _getboundingbox sufficient/better?
        #30jan i just wrote this today, i dont think its used
        #30jan class Nodz func findBbox
        #class nodes  func findBbox
        nodesMinX=0.0
        nodesMaxX=0.0
        nodesMinY=0.0
        nodesMaxY=0.0
        nodeW=200.0
        nodeRtOverhang=100.0
        # detect 1st pass, where data read become compare val
        ctr=0.0
    
        for node in listOfNodes:
            nodeInst = self.scene().nodes[node] 

            #find min & max X
            nix = nodeInst.pos().x()
    
            # spcl code for 1st node, make that node the std by which others are msrd
            if ctr == 0.0:
                nodesMinX = nix
            if nix < nodesMinX:
                nodesMinX = nix
            if nix > nodesMaxX:
                nodesMaxX = nix
        
            #find min and max Y
            niy = nodeInst.pos().y()

            # spcl code for 1st node, make that node the std by which others are msrd
            if ctr == 0.0 :
                nodesMinY = niy
        
            if niy < nodesMinY:
                nodesMinY = niy
            if niy > nodesMaxY:
                nodesMaxY = niy

            ctr += 1.0

        return(minx,miny,maxx,maxy)        


    # GRAPH
    #def saveGraph(self, xfilePath):
    #05dec remove file[path from calls, use globale filePath
    #09jan2022 chgd to have file passed , an fqfn
    #09jan2022 fqfn is fully qualified file name  a full fspec  with full path
    def saveGraph(self,fqfn):
        #30jan class Nodz func saveGraph
        """
         Get all the current graph infos and store them in a .json file
         at the given location.

         :type  filePath: str.
         :param filePath: The path where you want to save your graph at.

        """
        
        # TODO make dlogs to aid in editing  SwapDotSide, restack slots
        #   add alternate fqfn and media type
        
        data = dict()
        #27dec data is a dict, has 2 entries 'NODES' and 'CONNECTIONS'
        # the dict is private to this func
        
        data['NODES'] = dict()
    
        nodes = self.scene().nodes.keys()

        #03feb2022 TODO is _getboundingbox() sufficient?

        #    listOfNodes = ???
        listOfNodes = []
        for node in nodes:
            listOfNodes.append(self.scene().nodes[node].name)
        #print(listOfNodes)
        #30jan2022 dontuse the list yet, just looksee
        
        
        # TBD    nodesMinX, nodesMinY, nodesMaxX, nodesMaxY = findBbox( listOfNodes )
        
        #03feb2022 is this duplicated code? can _getboundingbox be used?
        nodesMinX=0.0
        nodesMaxX=0.0
        nodesMinY=0.0
        nodesMaxY=0.0
        nodeW=200.0
        nodeRtOverhang=100.0
        # detect 1st pass, where data read become compare val
        ctr = 0.0
    
        for node in nodes:
            nodeInst = self.scene().nodes[node] 

            #find min & max X
            nix = nodeInst.pos().x()
            #print("nodeInst.pos().x() is ", nix)
            if ctr == 0.0:
                nodesMinX = nix
            if nix < nodesMinX:
                nodesMinX = nix
            if nix > nodesMaxX:
                nodesMaxX = nix

            #find min and max Y
            niy = nodeInst.pos().y()
            #print("nodeInst.pos().y() is ", niy)

            if ctr == 0.0 :
                nodesMinY = niy
                
            if niy < nodesMinY:
                nodesMinY = niy
            if niy > nodesMaxY:
                nodesMaxY = niy
                
            #print("niY ", niy, " nodesMiny ",nodesMinY, " ctr ", ctr)		
            
            ctr += 1.0
            
            #30jan i think maxy should be maxY + typical node height, say 600
            nodesMaxY += 600
        
        #print("w is ",nodesMaxX-nodesMinX,"h is ", nodesMaxY-nodesMinY)
        self.scene().setSceneRect( 0, 0, nodesMaxX-nodesMinX, nodesMaxY-nodesMinY)
        
        #22jan2022 normalize all x y  to be inside quadrant IV with 0,0 at top left
        for node in nodes:
            nodeInst = self.scene().nodes[node] 
            # 22jan2022 confusing but seems like i should always subrtact the nodesminX from node x
            oldx=nodeInst.x()
            oldy=nodeInst.y()
            
            #02feb2022 make pady = 12.0
            # this is becuz the y of 0 is underneath the title bar by about 13 pixels
            pady = 12
            
            newx=oldx - nodesMinX
            newy=oldy - nodesMinY + pady
            
            new_pos = QtCore.QPointF(newx, newy)
            self.scene().nodes[node].setPos(new_pos)
            
        for node in nodes:
            nodeInst = self.scene().nodes[node] 
            preset = nodeInst.nodePreset
            nodeAlternate = nodeInst.alternate
            data['NODES'][node] = {'preset': preset, 'position': [nodeInst.pos().x(), nodeInst.pos().y()], 'alternate': nodeAlternate, 'attributes': []}

            attrs = nodeInst.attrs
            for attr in attrs:
                attrData = nodeInst.attrsData[attr]
                # serialize dataType if needed.
                if isinstance(attrData['dataType'], type):
                    attrData['dataType'] = str(attrData['dataType'])
                data['NODES'][node]['attributes'].append(attrData)
                
        data['CONNECTIONS'] = self.evaluateGraph()

        # Save data.
        try:
            #09jan2022 chg to use passed fqfn instead of global filePath
            utils._saveData(fqfn, data=data)
        except:
            print('Invalid path : {0}'.format(fqfn))
            print('Save aborted !')
            return False
        
        # Emit signal.
        self.signal_GraphSaved.emit()
        
    #09jan chg save to use fqfn not global filePath
    def loadGraph(self,fqfn):
        #30jan class Nodz func loadGraph
        """
         Get all the stored info from the .json file at the given location
         and recreate the graph as saved.

         :type  filePath: str.
         :param filePath: The path where you want to load your graph from.
        """	
        #09jan2022 dont use global, use passed fname fqfn
        
        # Load data.
        #if os.path.exists(filePath):
        if os.path.exists(fqfn):

            #data = utils._loadData(filePath)
            data = utils._loadData(fqfn)
        else:
            #print('Invalid path : {0}'.format(filePath))
            print('Invalid path : {0}'.format(fqfn))
            print('Load aborted !')
            return False

        #02jan2022
        # the 'data' has 2 sections 'CONNECTIONS' and 'NODES'
        # the CONNECTIONS is a list fo PAIRS or pins (fqpn)
        # it has NO sense of dir, 
        # dir is inferred from plug true and socket false (means out )
        #  or                  socket true and plug false ( means in )
        # there can be neither in or out ( for hypermedia)
        # BUT i dont allow for 'io' pins
        #

        #start clean
        self.clearGraph()
        
        # Apply nodes data.
        nodesData = data['NODES']
        #03dec2021  is nodesData available outside of this func? outside of this class?
        
        nodesName = nodesData.keys()

        #09feb i see bad printout,
        # had err  used y when comparing x, i think xmin ymin xmax ymax , w,h ok now
        #
        #05feb2022 add calc of wdth hght while loading
        #   later: adj wdth by nodewide + overhang  200, 150
        minx = 0
        maxx = 0
        #   later: ad hght by height of bottmmost node ( or swag 800)
        miny = 0
        maxy = 0 
        
        pylist=[]
        
        firstLoop = True
        #26nov this vvv loop will go thru all nodes ( widgets/comps )
        for name in nodesName:
            preset = nodesData[name]['preset']
            position = nodesData[name]['position']
            px=position[0]
            py=position[1]
            pylist.append(py)
            
            #05feb calc minx maxx miny maxy, 
            #    later calc w=maxx-minx + adjustement
            #    later calc h-maxy-miny + adjustment
                
            if firstLoop == True:
                minx=px
                maxx=px
                
                miny=py
                maxy=py
                
                #print("1stloop")
                
                firstLoop = False
            else:

                #05feb2022 calc wdth hght durinh load
                #09feb damn has if py vvv !S
                if px < minx:
                    minx = px

                if px > maxx:
                    maxx = px


                if py < miny:
                    miny = py

                if py > maxy:
                    #dman had px
                    maxy = py

            
            #09feb show me minx miny maxx maxy
            #  i want to see they grow in a reasonable way 
            #print("name ",name,"miny ",miny)    
            
            #09feb use px py vvv 
            position = QtCore.QPointF(px,py)
                                    
            #09feb hide till initl calc minx maxx miny maxy are ok
            #09feb  self is a view, so ok to ask mapTOscene, ng to ask mapFromScene
            #  i thinks...
            
            #print("qrqbrx=",self.mapFromScene(QRectF(minx,miny,maxx-minx,maxy-miny)).boundingRect().x())
            #print("qrqbry=",self.mapFromScene(QRectF(minx,miny,maxx-minx,maxy-miny)).boundingRect().y())
            #print("qrqbrw=",self.mapFromScene(QRectF(minx,miny,maxx-minx,maxy-miny)).boundingRect().width())
            #print("qrqbrh=",self.mapFromScene(QRectF(minx,miny,maxx-minx,maxy-miny)).boundingRect().height())
                        
            alternate = nodesData[name]['alternate']
                
            node = self.createNode(name=name,
                                   preset=preset,
                                   position=position,
                                   alternate=alternate)
            #03dec the 'node' contains the name and the alternate
            # but how to acceess from outside this func this class??
            
            # Apply attributes data container 
            #	( each node will have some attributes (aka slot  and a socket can be a plug or socket, 
            #     each attr(slot) will have some porperties
            attrsData = nodesData[name]['attributes']

            #30jan find scene x y w h, and set scene().rect to that
            
            #26 nov this vvv will go thru all the slots for a node(widghet)
            for attrData in attrsData:
                #gather all the properties for this slot in this node

                #07jan 2022 
                #  note:  strategy... chg index to move the attr uo or down in stack
                index = attrsData.index(attrData)
                #09jan2022 chg dotPosn to cnxnSide EXCEPT in SRC FILE SAVE and others
                #  see that the chg is ok before chging the input file 
                # AND chging hal2json script
                # 09jan2022 well i was ok in loadGraph
                # see what saveGraph does (is attr name cnxnSide?) YES ok
                # so i can convert any file from doyPosn to cnxnSide 
                # using save as, then del the oldstyle
                # still need to edit the hal2json code!
                #cnxnSide = attrData['dotPosn']
                cnxnSide = attrData['cnxnSide']
                attrname = attrData['name']
                netname=attrData['netname']		
                
                plug = attrData['plug']
                socket = attrData['socket']
                
                preset = attrData['preset']
                dataType = attrData['dataType']
                #27dec2021 this ^^^ got the 'dataType va;ue from the node stanza in SaveMe or test3
                # dataType will contain 'bool' 'float' 'u32' or 's32'
                plugMaxConnections = attrData['plugMaxConnections']
                socketMaxConnections = attrData['socketMaxConnections']
                
                """
                #27 dec i dont hink this code is executed, not ever
                # un-serialize data type if needed
                if (isinstance(dataType, str) and dataType.find('<') == 0):
                #27dec when is there a '<' in a datatype???
                # i find none in SaveMe or test3
                # i dont think this code ever gets executed
                # the code chks that dataType is a string and that 1st char is '<'
                dataType = eval(str(dataType.split('\'')[1]))
                """
        
                #  this call needs gnrc   cnxnSide   NOT sourcecnxnSide  not targetcnxnSide
                self.createAttribute(node=node, cnxnSide=cnxnSide, name=attrname, netname=netname, index=index, preset=preset, plug=plug, socket=socket, dataType=dataType, plugMaxConnections=plugMaxConnections, socketMaxConnections=socketMaxConnections )     
                
                
                
        # Apply connections data.
        
        #27nov the cnxns are read from SaveMe they are not created from data and logic
        # the cnxns come form the 'CONNECTIONS' >list< in SaveMe
        #  the CONNECTIONS >list< is pairs of Node.Slot thingys
        #  each pair is a connection FROM 1st TO 2nd 
        #   so 1st Node.Slot iten is always a Plug,   always a Source
        #      2nd                is always a Socket, always a Target
        # 28dec2021 revisited...
        # break the string using string.rsplit('.',1)
        # using rsplit
        # halui.program.resume
        # will give you halui.program and resume
        #
        #02jan2022
        # vvv connectionsData is a list of a pair of pins ALWAYS a pair
        #  where does the None come from??
        connectionsData = data['CONNECTIONS']
    
        for connection in connectionsData:
            #02dec2022
            # the connection may not have a source (1st line is None/none)
            # the connection may not have a dest   (2nd line is None/noe
            # i need to autogenerate a plug or socket as needed
            #  the name of the plug/socket will be created 
            #    signalnameDOTsource
            # or signalnameDOTdest
            # 
            # will these 'none' couplets have 1 or 2  lines?
            #
            # the file beg=ing read may only have 1 pin line
            # 
            # well we just read the halcmd show sig file..
            # and it has lines like...
            # bit           FALSE  adir
            #                      ==> parport.0.pin-09-out
            # i can get thge dir, 
            #  and thus the 'source/destination quality 
            #    from ==> and <==
            #
        
            source = connection[0] # the 1ts Node.Slot item is a source
            #27dec these 2 lines , given halui.program.resume
            #   will set sourceNode as halui
            #   and      sourceAttr as program.resume
            #
            #27dec2021  use string.rsplit('.',1)
            # which, when given halui.program.resume
            # yields sourceNode = halui.program
            # yields sourceAttr = resume
            #sourceNode = source.split('.')[0] # the first name is the sourceNode
            #sourceAttr = source.split('.')[1] # the last  name is the sourceSlot ( a Plug)
            #NOTE SaveMe must be adjusted for multiple nodes
            #  like halui AND halui.program
            #  maybe others
            sourceNode = source.rsplit('.',1)[0] # the first name is the sourceNode
            sourceAttr = source.rsplit('.',1)[1] # the last  name is the sourceSlot ( a Plug)
            
            target = connection[1] # the 2nd Node.Slot utem is a target
        
            #01jan2021 2301 target was "None"
            #dbug print("target is ",str(target))
        
            #27dec2021 these 2 lines vvv given halui.program.resume
            #   will set targetNode as halui
            #   and      targetAttr as program.resume
            #21dec2021 use rsplit see above
            #NOTE SaveMe must be adjusted for multiple nodes
            #  like halui AND halui.program
            #  maybe others
            #targetNode = target.split('.')[0] # the first name is the targetNode
            #targetAttr = target.split('.')[1] # the last  name is the targetSlot ( a Socket)
        
            targetNode = target.rsplit('.',1)[0] # the first name is the targetNode
            targetAttr = target.rsplit('.',1)[1] # the last  name is the targetSlot ( a Socket)


            #27nov  find the netname for the sourceNode.sourceAttr
            #   meaning  find the netname of the PLUG of interest
            nname = None
            n = 0
            
            #print(sourceNode)
            
            for m in nodesData[sourceNode]['attributes']:
                if(str(m['name']) == sourceAttr):
                    nname = nodesData[sourceNode]['attributes'][n]['netname']
                    #print("for node ", sourceNode, " for Plug ", sourceAttr, "netname is ", nname)
                n = n + 1
            
            
            self.createConnection(sourceNode, sourceAttr, targetNode, targetAttr, nname, cnxnSide )
        
        #05feb2022 adjust wdth by nodewidth and rt side loopbacks
        #05feb2022 unrepeatable... run app open same .json, clsoe app repeat-->see dif width views
        #   but,, aceptable ater adding extra extra width
        #   untested with tall nodes near bottom, but fudge +800 my suffuce
        #
        wdth = (maxx - minx ) + 200 +150 +300
        #05feb2022 adjust hgt by height of bottommost node OR swag 800
        hght = (maxy - miny) + 800

        #05feb2022 now set scenerect to wdth hght
        # ??? how> well 'self' is a class Nodz, and has a self.scene().
        # try handing w,h back to caller
        
        # 12nov this vvv is a spcl method for scene(s)  (Not a dict update )
        self.scene().update()

        #05dec the dbug print of filePath is ok in this func loadGraph at top and at bot
        #05dec filePath is a unique name so it will have to be the passed val bfilePath
    
        #29jan2022 dbug
        #print("loadGraph done")
        
        # Emit signal.
        self.signal_GraphLoaded.emit()

        # print AFTER all, there is no order so waiy
        # check it repets 10x OK 09feb2022 26:16
        """
        sx=self.mapToScene(QRect(minx,miny,maxx-minx,maxy-miny)).boundingRect().x()
        sy=self.mapToScene(QRect(minx,miny,maxx-minx,maxy-miny)).boundingRect().y()
        sw=self.mapToScene(QRect(minx,miny,maxx-minx,maxy-miny)).boundingRect().width()
        sh=self.mapToScene(QRect(minx,miny,maxx-minx,maxy-miny)).boundingRect().height()
        print("scene",sx,sy,sw,sh)
        print("minx",minx,"miny",miny,"maxx",maxx,"maxy",maxy)
        print("wdth ",wdth," hght ",hght)
        #print("miny =",miny)
        #print(pylist)
        """
        
        #05feb2022 return wdth hght to caller, so callr can set scenerect
        return wdth,hght
        
    def createConnection(self, sourceNode, sourceAttr, targetNode, targetAttr, netname, cnxnSide):
        #30jan class Nodz func createConnection
        
        plug = self.scene().nodes[sourceNode].plugs[sourceAttr]

        socket = self.scene().nodes[targetNode].sockets[targetAttr]
                    
        connection = ConnectionItem(plug.center(), socket.center(), plug, socket, netname, plug.cnxnSide )
        
        connection.plugNode = plug.parentItem().name
        connection.plugAttr = plug.attribute
        connection.socketNode = socket.parentItem().name
        connection.socketAttr = socket.attribute
        
        connection.netname = netname        
        
        #14dec why does this vvv read like 2 cnxns, one each direction?
        plug.connect(socket, connection)
        socket.connect(plug, connection)
        
        connection.updatePath()
        
        self.scene().addItem(connection)
            
        return connection
    
    def evaluateGraph(self):
        #30jan class Nodz func evaluateGraph
        """
         Create a list of connection tuples.
         [("sourceNode.attribute", "TargetNode.attribute"), ...]
        """
        scene = self.scene()

        data = list()
        
        for item in scene.items():
        
            if isinstance(item, ConnectionItem):
                connection = item

                data.append(connection._outputConnectionData())

        # Emit Signal
        self.signal_GraphEvaluated.emit()

        return data

    def clearGraph(self):
        #30jan class Nodz func clearGraph
        """
         Clear the graph.
        """
        self.scene().clear()
        self.scene().nodes = dict()

        # Emit signal.
        self.signal_GraphCleared.emit()

    ##################################################################
    # END API
    ##################################################################

class MyPopup(QWidget):
    # class MyPopup   used for hypermedia links to grfx
    #18dec i read that the class decl does not get the arg, that the __init___ does
    def __init__(self,pixFname):
        QWidget.__init__(self)
        lbl1 = QLabel(self)
        #17dec this vvv sets popup wndo automagicly
        lbl1.setPixmap(QPixmap(pixFname))
        lbl1.move(1,1)
        lbl1.show()
    
class NodeScene(QtWidgets.QGraphicsScene):

    """
     The scene displaying all the nodes.
    """
    #21nov TODO should this vvv be here?, all alone, in a bunch by itself?
    signal_NodeMoved = QtCore.Signal(str, object)

    def __init__(self, parent):
        #class NodeScene func __init__
        """
         Initialize the class.
        """
        super(NodeScene, self).__init__(parent)

        # General.
        self.gridSize = parent.config['grid_size']

        # Nodes storage.
        self.nodes = dict()

    def dragEnterEvent(self, event):
        #class NodeScene func dragEnterEvent
        """
         Make the dragging of nodes into the scene possible.
        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dragMoveEvent(self, event):
        #class NodeScene dragMoveEvent
        """
         Make the dragging of nodes into the scene possible.
        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dropEvent(self, event):
        #class NodeScene dropEvent
        """
         Create a node from the dropped item.
        """
        # Emit signal.
        self.signal_Dropped.emit(event.scenePos())

        event.accept()

    
    def drawBackground(self, painter, rect):
        #class NodeScene drawBackground
        """
         Draw a grid in the background.
        """
        config = self.parent().config

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(utils._convertDataToColor(config['bg_color']))

        painter.fillRect(rect, self._brush)

        if self.views()[0].gridVisToggle:
            leftLine = rect.left() - rect.left() % self.gridSize
            topLine = rect.top() - rect.top() % self.gridSize
            lines = list()

            i = int(leftLine)
            while i < int(rect.right()):
                lines.append(QtCore.QLineF(i, rect.top(), i, rect.bottom()))
                i += self.gridSize

            u = int(topLine)
            while u < int(rect.bottom()):
                lines.append(QtCore.QLineF(rect.left(), u, rect.right(), u))
                u += self.gridSize

            self.pen = QtGui.QPen()
            self.pen.setColor(utils._convertDataToColor(config['grid_color']))
            self.pen.setWidth(0)
            painter.setPen(self.pen)
            painter.drawLines(lines)
            
    def updateScene(self):
        #class NodeScene updateScene
        """
         Update the connections position.
        """
        #15dec2021 errs no attr center()
        for connection in [i for i in self.items() if isinstance(i, ConnectionItem)]:
            #ok rmvd if(hasattr(connection.target,'center()')):
            connection.target_point = connection.target.center()
            #ok rmvd if(hasattr(connection.source,'center()') ):
            connection.source_point = connection.source.center()
            connection.updatePath()

class NodeItem(QtWidgets.QGraphicsItem):

    """
     A graphic representation of a node containing attributes.
    """
    def __init__(self, name, alternate, preset, config):
        # class NodeItem  method __init__
        """
         Initialize the class.

         :type  name: str.
         :param name: The name of the node. The name has to be unique
                     as it is used as a key to store the node object.

         :type  alternate: bool.
         :param alternate: The attribute color alternate state, if True,
                          every 2 attribute the color will be slightly
                          darker.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.
        """
        super(NodeItem, self).__init__()

        self.setZValue(1)

        # Storage
        self.name = name
        self.alternate = alternate
        self.nodePreset = preset
        self.attrPreset = None

        # Attributes storage.
        self.attrs = list()
        self.attrsData = dict()
        self.attrCount = 0
        self.currentDataType = None

        #17dec there is no dict for slots ( esp for those slots that are not plugs and not sockets)
        self.plugs = dict()
        self.sockets = dict()

        # Methods.
        self._createStyle(config)
        
        #14dec2021 add tooltip for nodeIten
        # this works, but clobbers any tooltip meant fo a slot in the NodeItem
        #  meaning the NodeItem tooltip pops up ANTWHERE inside node
    
        strg1="NodeItem "
        strg2=self.name
        strg3=strg1+strg2
        """
            print(strg3)
        """
        self.setToolTip(strg3)
        
    @property
    def height(self):
        """
         Increment the final height of the node every time an attribute
         is created.
        """
        if self.attrCount > 0:
            return (self.baseHeight +
                    self.attrHeight * self.attrCount +
                    self.border +
                    0.5 * self.radius)
        else:
            return self.baseHeight

    @property
    def pen(self):
        """
         Return the pen based on the selection state of the node.
        """
        if self.isSelected():
            return self._penSel
        else:
            return self._pen

    def _createStyle(self, config):
        
        """
         Read the node style from the configuration file.
        """
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # Dimensions.
        self.baseWidth  = config['node_width']
        self.baseHeight = config['node_height']
        self.attrHeight = config['node_attr_height']
        self.border = config['node_border']
        self.radius = config['node_radius']

        #17dec are these useful now ? i chgd to cnxnpt being v ctr'd on left or rt edge of gui box
        self.nodeCenter = QtCore.QPointF()
        self.nodeCenter.setX(self.baseWidth / 2.0)
        self.nodeCenter.setY(self.height / 2.0)

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(utils._convertDataToColor(config[self.nodePreset]['bg']))

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self.border)
        self._pen.setColor(utils._convertDataToColor(config[self.nodePreset]['border']))

        self._penSel = QtGui.QPen()
        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(self.border)
        self._penSel.setColor(utils._convertDataToColor(config[self.nodePreset]['border_sel']))

        self._textPen = QtGui.QPen()
        self._textPen.setStyle(QtCore.Qt.SolidLine)
        self._textPen.setColor(utils._convertDataToColor(config[self.nodePreset]['text']))

        self._nodeTextFont = QtGui.QFont(config['node_font'], config['node_font_size'], QtGui.QFont.Bold)
        self._attrTextFont = QtGui.QFont(config['attr_font'], config['attr_font_size'], QtGui.QFont.Normal)

        self._attrBrush = QtGui.QBrush()
        self._attrBrush.setStyle(QtCore.Qt.SolidPattern)

        self._attrBrushAlt = QtGui.QBrush()
        self._attrBrushAlt.setStyle(QtCore.Qt.SolidPattern)

        self._attrPen = QtGui.QPen()
        self._attrPen.setStyle(QtCore.Qt.SolidLine)

    def _createAttribute(self, cnxnSide, name, netname, index, preset, plug, socket, dataType, plugMaxConnections, socketMaxConnections):
        #23nov an attribute can only have 1 cnxnSide

        """
         Create an attribute by expanding the node, adding a label and
         connection items.

         :type  name: str.
         :param name: The name of the attribute. The name has to be
                     unique as it is used as a key to store the node
                     object.

         netname: str.
         param netname: The name of the net, or wire for a plug
        
         :type  index: int.
         :param index: The index of the attribute in the node.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :type  plug: bool.
         :param plug: Whether or not this attribute can emit connections.

         :type  socket: bool.
         :param socket: Whether or not this attribute can receive
                       connections.

         :type  dataType: type.
         :param dataType: Type of the data represented by this attribute
                         in order to highlight attributes of the same
                         type while performing a connection.
        """
            
        if name in self.attrs:
            print('An attribute with the same name already exists on this node : {0}'.format(name))
            print('Attribute creation aborted !')
            return

        self.attrPreset = preset

        # Create a plug connection item.
        if plug:
            plugInst = PlugItem(parent=self, cnxnSide=cnxnSide, attribute=name, netname=netname, index=self.attrCount, preset=preset, dataType=dataType, maxConnections=plugMaxConnections)
            self.plugs[name] = plugInst
                
        # Create a socket connection item.
        if socket:
            socketInst = SocketItem(parent=self, cnxnSide=cnxnSide, attribute=name, netname='-', index=self.attrCount, preset=preset, dataType=dataType, maxConnections=socketMaxConnections)
            self.sockets[name] = socketInst

        self.attrCount += 1

        # Add the attribute based on its index.
        # 19nov index of -1 mean not used so far
        if index == -1 or index > self.attrCount:
            self.attrs.append(name)
        else:
            self.attrs.insert(index, name)

        self.attrsData[name] = {'cnxnSide': cnxnSide,
            'name': name,
            'netname': netname,
            'socket': socket,
            'plug': plug,
            'preset': preset,
            'dataType': dataType,
            'plugMaxConnections': plugMaxConnections,
            'socketMaxConnections': socketMaxConnections
        }

        # 12nov this updates the values for keys in the NODE dict
        self.update()

    def _deleteAttribute(self, index):
        #class nodeitem _deleteAttribute
        """
         Remove an attribute by reducing the node, removing the label
         nd the connection items.

         :type  index: int.
         :param index: The index of the attribute in the node.
        """
        name = self.attrs[index]

        # Remove socket and its connections.
        if name in self.sockets.keys():
            for connection in self.sockets[name].connections:
                connection._remove()

            self.scene().removeItem(self.sockets[name])
            self.sockets.pop(name)

        # Remove plug and its connections.
        if name in self.plugs.keys():
            for connection in self.plugs[name].connections:
                connection._remove()

            self.scene().removeItem(self.plugs[name])
            self.plugs.pop(name)

        #30jan TODO  why this -1??   Reduce node height.
        if self.attrCount > 0:
            self.attrCount -= 1

        # Remove attribute from node.
        if name in self.attrs:
            self.attrs.remove(name)

        # 12nov this updates values for keys in the NODE dict
        self.update()

    def _remove(self):
        #class nodeitem func _remove
        """
         Remove this node instance from the scene.

         Make sure that all the connections to this node are also removed
         in the process
        """
        self.scene().nodes.pop(self.name)

        # Remove all sockets connections.
        for socket in self.sockets.values():
            while len(socket.connections)>0:
                socket.connections[0]._remove()

        # Remove all plugs connections.
        for plug in self.plugs.values():
            while len(plug.connections)>0:
                plug.connections[0]._remove()

        # Remove node.
        scene = self.scene()
        scene.removeItem(self)
        
        #12nov scene.update() is NOT a dict update
        scene.update()

    def boundingRect(self):
        #16dec class NodeItem method boundingRect()  overloaded i think
        """
         The bounding rect based on the width and height variables.
        """
        #04feb  i think very wrong,  do i call this?
        rect = QtCore.QRect(0, 0, self.baseWidth, self.height)
        rect = QtCore.QRectF(rect)
        return rect

    def shape(self):
        #16dec class NodeItem method shape()
        """
         The shape of the item.
        """
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget):
        #16dec class NodeItem method paint()
        """
         Paint the node and attributes.
        """
        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)

        painter.drawRoundedRect(0, 0,
                                self.baseWidth,
                                self.height,
                                self.radius,
                                self.radius)

        # Node title , located outside above node
        #02feb2022 bad location, when a node is at top of screen, the title is outside view
        # move it down onto orange bar DONE
        #  but still some view have the orange bar clipped off
        #   see  display.json   and   left.json
        # i checked the .json file and saw that node 'pyvcp' (common to both problem views),
        #  had y posn of 0.0, i chgd to 12 and now ok
        # REMEMBER a 0 y coord for a node is BAD
        # check the C(convert) and saveGraph code
        #
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)

        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self.name).width() + 14
        text_height = metrics.boundingRect(self.name).height() + 14
        margin = (text_width - self.baseWidth) * 0.5
        # 02feb2022 orig was   -text_height,
        #  i tried   text_height,  and got no title
        textRect = QtCore.QRect(-margin,
                                -9,
                                text_width,
                                text_height)
        #10dec this text is above node, it is title of node
        painter.drawText(textRect,
                         QtCore.Qt.AlignCenter,
                         self.name)


        # Attributes.
        offset = 0
        for attr in self.attrs:
            nodzInst = self.scene().views()[0]
            config = nodzInst.config

            # Attribute rect.
            rect = QtCore.QRect(self.border / 2,
                                self.baseHeight - self.radius + offset,
                                self.baseWidth - self.border,
                                self.attrHeight)

            attrData = self.attrsData[attr]
            name = attr

            preset = attrData['preset']
            
            
            #17dec ng for my purpose, this is in a loop so i get sevral answer
            #datatype = attrData['dataType']
            #print(datatype)



            # Attribute base.
            #06dec i dont see any alternating color based on attr index.. so try
            # orig self._attrBrush.setColor(utils._convertDataToColor(config[preset]['bg']))
            # ng  find out hwat is eval ^^ self._attrBrush.setColor(Qt::white)
            #
            #06dec2021  this vvv got me all black bg for all slots
            # this avoids using nodz_utils.convertDataToColor
            #  which was giving me alternating bg colors for slots ( grey black grey black.... )
            self._attrBrush.setColor(QtGui.QColor(0,0,0))
            
            #03dec2021
            # i want to use alternate as a filename to be loaded when noded is dblclicked
            # so this vvv line would be removed
            
            #05dec  did not chg the new atrifact of slots being black or grey vs prev  all grey
            #if self.alternate:
            #    self._attrBrushAlt.setColor(utils._convertDataToColor(config[preset]['bg'], True, config['alternate_value']))

            self._attrPen.setColor(utils._convertDataToColor([0, 0, 0, 0]))
            painter.setPen(self._attrPen)
            painter.setBrush(self._attrBrush)
            if (offset / self.attrHeight) % 2:
                painter.setBrush(self._attrBrushAlt)

            painter.drawRect(rect)

            # Attribute label.
            painter.setPen(utils._convertDataToColor(config[preset]['text']))
            painter.setFont(self._attrTextFont)

            # Search non-connectable attributes.
            if nodzInst.drawingConnection:
                if self == nodzInst.currentHoveredNode:
                    if (attrData['dataType'] != nodzInst.sourceSlot.dataType or
                        (nodzInst.sourceSlot.slotType == 'plug' and attrData['socket'] == False or
                         nodzInst.sourceSlot.slotType == 'socket' and attrData['plug'] == False)):
                        # Set non-connectable attributes color.
                        painter.setPen(utils._convertDataToColor(config['non_connectable_color']))

            textRect = QtCore.QRect(rect.left() + self.radius,
                                     rect.top(),
                                     rect.width() - 2*self.radius,
                                     rect.height())
            # TODO this vvv looks like where left center right align happens
            #06dec yes i can chg l r ctr here  
            # but need to do so based on cnxnSide
            # cnxnSide can have value none left right
            #06dev vvv works! :-)
            if (attrData['cnxnSide'] == "left" ):
                painter.drawText(textRect, (QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom), name)
            elif (attrData['cnxnSide'] == "right" ):
                painter.drawText(textRect, (QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom), name)
            else:
                painter.drawText(textRect, QtCore.Qt.AlignHCenter, name)
            #orig  painter.drawText(textRect, QtCore.Qt.AlignVCenter, name)

            offset += self.attrHeight

    def mousePressEvent(self, event):
        #return True
        
        # class NodeItem  method mousePressEvent
        """
         Keep the selected node on top of the others.
        """
        nodes = self.scene().nodes
        for node in nodes.values():
            node.setZValue(1)

        for item in self.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(1)

        self.setZValue(2)

        super(NodeItem, self).mousePressEvent(event)

    #notes:
    # if (event.button() == QtCore.Qt.LeftButton and
    #      event.modifiers() == QtCore.Qt.NoModifier and
    #      event.modifiers() == QtCore.Qt.AltModifier):
    #      event.modifiers() == QtCore.Qt.ControlModifier):
    #      event.modifiers() == QtCore.Qt.ShiftModifier):

    def mouseDoubleClickEvent(self, event):
        #return True
        
        # class NodeItem func mouseDoubleClickEvent

        global workingFile
        #print("workingFile is ", workingFile)
    
        nodeClicked=self.name
        if event.button() == Qt.LeftButton:
            if((event.modifiers() & QtCore.Qt.ControlModifier ) and (event.modifiers() & QtCore.Qt.ShiftModifier )):
                #print("shift control modifier")
                #nodeclkd=self.name
                #strg1=("shift ctrl left dbl click on node ")
                #strg2=nodeClicked;
                #strg3=workingFile
                #strg4=strg1+strg2+strg3
                #print(strg4)
                self.scene().views()[0].doEditSaveMe(workingFile)
                return

        #12jan orig starts here----------
        """
        Emit a signal.

        """
        super(NodeItem, self).mouseDoubleClickEvent(event)
        self.scene().parent().signal_NodeDoubleClicked.emit(self.name)
        #12jan orig ends here-------------
    
        if(self.alternate != "" ):
            # TODO handle door(hierarchical graph) and circuit/code/thing
            # what if door AND a circuit?
            # like on SaveMe , ArduinoSPindleControl
            #   has a door AND can have a circuit
            # A: pick one ( door/hypermedia )  cant do two            
            key1 = 'ENTER'
            key2 = 'EXIT'
            if((key1 in self.attrsData) or (key2 in self.attrsData)):
                #05feb laodgraph rtns w,h 
                w,h =self.scene().views()[0].loadGraph(self.alternate)
                #05feb try to make all node fit in scene and keep scene sized to all nodes
                self.updateSceneRect(QRectF(0, 0, w, h))
                self.fitInView(0,0,w,h, QtCore.Qt.KeepAspectRatio)

            else:            
                # check for ShowMe
                key = 'ShowMe'
                if(key in self.attrsData):
                    if(self.attrsData['ShowMe']['dataType'] == "<type 'thing'>"):
                        picFile=self.alternate
                        self.scene().views()[0].doImg(picFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'code'>"):
                        #print('its code, need a text viewer')
                        txtFile=self.alternate
                        self.scene().views()[0].doTxt(txtFile)
                    #04feb remove doSCH which requires eschema appm use SVG instead
                    #elif(self.attrsData['ShowMe']['dataType'] == "<type 'circuit'>"):
                    #    proFile=self.alternate
                    #    self.scene().views()[0].doSch(proFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'manpage'>"):
                        #print('its a manpage, need a man page viewer')
                        manKey=self.alternate
                        self.scene().views()[0].doMan(manKey)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'svg'>"):
                        svgFile=self.alternate
                        self.scene().views()[0].doSVG(svgFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'url'>"):
                        url=self.alternate
                        self.scene().views()[0].doUrl(url)
                else:
                    print('its a not thing,text.circuit , yet alternate is not empty, why am i here?')
        else:
            self.scene().parent().signal_NodeDoubleClicked.emit(self.name)

    def mouseMoveEvent(self, event):
        #return True
        
        #class slotItem func mouseMoveEvent
        if self.scene().views()[0].gridVisToggle:
            if self.scene().views()[0].gridSnapToggle or self.scene().views()[0]._nodeSnap:
                gridSize = self.scene().gridSize

                currentPos = self.mapToScene(event.pos().x() - self.baseWidth / 2,
                                             event.pos().y() - self.height / 2)

                snap_x = (round(currentPos.x() / gridSize) * gridSize) - gridSize/4
                snap_y = (round(currentPos.y() / gridSize) * gridSize) - gridSize/4
                snap_pos = QtCore.QPointF(snap_x, snap_y)
                self.setPos(snap_pos)

                self.scene().updateScene()
            else:
                self.scene().updateScene()
                super(NodeItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        #return True
        
        # class NodeItem func mouseRelaseEvent
        
        # Emit node moved signal.
        self.scene().signal_NodeMoved.emit(self.name, self.pos())
        
        super(NodeItem, self).mouseReleaseEvent(event)

    def hoverLeaveEvent(self, event):
        #return True
        
        nodzInst = self.scene().views()[0]

        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)

        super(NodeItem, self).hoverLeaveEvent(event)

#13nov  a horz field in a widget is a 'slot' ( horrible overloading of terms )
#  and a slot can be a plug or a socket, (or both [untested]  or neither [ a param?] ) based on properties of the slot
class SlotItem(QtWidgets.QGraphicsItem):
    #class SlotItem

    """
     The base class for graphics item representing attributes hook.
    """

    def __init__(self, parent, cnxnSide, attribute, netname, preset, index, dataType, maxConnections):
        #class slotItem func __init__
        """
         Initialize the class.

         :param parent: The parent item of the slot.
         :type  parent: QtWidgets.QGraphicsItem instance.

         :param attribute: The attribute associated to the slot.
         :type  attribute: String.

         :param netname: str
         :type  netname The text to be put on the wire.cnxn/net index of the attribute in the node.

         :param index: int.
         :type  index: The index of the attribute in the node.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :param dataType: The data type associated to the attribute.
         :type  dataType: Type.
        """
        
        # parent is a NodeItem  has self, name, alternate, preset, config)
        super(SlotItem, self).__init__(parent)

        # Status.
        self.setAcceptHoverEvents(True)

        # Storage.
        self.cnxnSide = cnxnSide
        
        self.slotType = None
        self.attribute = attribute
        
        self.preset = preset
        self.index = index
        self.dataType = dataType
        
        # Style.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        
        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)
        
        # Connections storage.
        self.connected_slots = list()
        self.newConnection = None
        self.connections = list()
        self.maxConnections = maxConnections
        
        #14dec2021 add tooltip for slot
        strg1="slot "
        strg2=self.attribute
        strg3=strg1+strg2
        self.setToolTip(strg3)

    
    def accepts(self, slot_item):
        #class slotItem func accepts
        """
            Only accepts plug items that belong to other nodes, 
            and only if the max connections count is not reached yet.
        """
        #22nov i need loopbacks so the rule ^^^ is ng for me
        
        # no plug on plug or socket on socket
        #20nov should be  only plug to socket
        #20nov needs DONE  socket can only have 1 plug
        hasPlugItem = isinstance(self, PlugItem) or isinstance(slot_item, PlugItem)
        
        hasSocketItem = isinstance(self, SocketItem) or isinstance(slot_item, SocketItem)
        
        if not (hasPlugItem and hasSocketItem):
            return False

        #21nov i dont lkike orig logic
        """
            #no more than maxConnections
            if self.maxConnections>0 and len(self.connected_slots) >= self.maxConnections:
                return False
        """
        
        numcnxns = len(self.connections)
        
        if( numcnxns >= self.maxConnections ):
            #need to erase the bez if rtn is false
            return False
        
        
        #no connection with different types
        if slot_item.dataType != self.dataType:
            return False

        #otherwize, all fine.
        # 20nov hahaha ^^^

        return True

    def mousePressEvent(self, event):
        #return True
        
        #class slotItem func mousePress
        """
         class SocketItem  Start the connection process.
        """    
        #08jan i dont see this printed on startup, i think useless
        if (event.button() == QtCore.Qt.LeftButton):
            if( not hasattr(self, 'netname') ):
                #08jan
                #print("netname set to - char")
                self.netname = "-"
            
            if ( self.netname != '-' ):
                #08jan  this is class SlotItem func mousePressEvent
                # this is where drag bezier begins
                self.newConnection = ConnectionItem(self.center(), self.mapToScene(event.pos()), self, None, self.netname, self.cnxnSide )
                
                self.connections.append(self.newConnection)
                self.scene().addItem(self.newConnection)
                nodzInst = self.scene().views()[0]
                nodzInst.drawingConnection = True
                nodzInst.sourceSlot = self
                nodzInst.currentDataType = self.dataType
            
            else:
                #08jan else pass the event along... to parent = Node?
                super(SlotItem, self).mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        #return True
        
        #class SlotItem method mouseMove
        """
         Update the new connection's end point position.
        """
        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            mbb = utils._createPointerBoundingBox(pointerPos=event.scenePos().toPoint(),
                                                  bbSize=config['mouse_bounding_box'])
            # Get nodes in pointer's bounding box.
            targets = self.scene().items(mbb)

            if any(isinstance(target, NodeItem) for target in targets):
                if self.parentItem() not in targets:
                    for target in targets:
                        if isinstance(target, NodeItem):
                            nodzInst.currentHoveredNode = target
            else:
                nodzInst.currentHoveredNode = None

            # Set connection's end point.HEREHEREHEREwhereiEFFEDuP
            ep = self.mapToScene(event.pos())
            self.newConnection.target_point = ep
        
            self.newConnection.updatePath()
        else:
            super(SlotItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        #return True
        
        # class SlotItem method mouseRelease
    
        # 23nov a slot has a single cnxnSide
        # yet this code makes a cnxn, which rwrs 2 cnxnSides, 2 slotItems, (1 plugItem 1 SocketItem)
        # the 2 cnxnSides are available IF the self is one slotItem 
        #                              and the thing 'under' the mouseRelease is another
        # see the code where target is identified by the mouseReleaseEvent
        #  so 'self' is the plug, and target is the socket
        #
        """
            Apply the connection if target_slot is valid.
        """
        nodzInst = self.scene().views()[0]

        #23nov if the left mouse btn is released...
        if event.button() == QtCore.Qt.LeftButton:
            #16dec try to get response from a slotitem
            #17dec only prints on SKT not PLUG !?!?!
            # TODO fix   fix what??
            #print("in mouseReleaseEvent in class SlotItem, mouse was released")
            
            nodzInst.drawingConnection = False
            nodzInst.currentDataType = None
            
            target = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

            #23nov  i think the magic is here
            # when we enter this func we have no target object 
            # but using the xy of the release, we find the target

            # 20nov 2 patches needed for corner cases
            # a) when plug circle dragged to space that is X-Y+ of plug circle
            # b) when socket circle dragged to space
            # c) when socket circle dragged onto plug circle
            if(target is None):
                #20nov necc  vvv   it stops loose noodle from plug to X-Y+ of plug circle
                # AND for blow up when socket dragged into space
                if( not( self.newConnection is None)):
                    self.newConnection._remove()
                    
                super(SlotItem, self).mouseReleaseEvent(event)
                return
            
            if( target ): 
                if( not isinstance(target, SocketItem)):
                    #20nov necc for when socket circle  dragged onto plug circle
                    if( not( self.newConnection is None)):
                        self.newConnection._remove()
                    
                    super(SlotItem, self).mouseReleaseEvent(event)
                    return
            
            if (target):
                if( target.accepts(self)) :
                
                    #13nov dont compute if newConnection = None
                    if(self.newConnection != None):
                        self.newConnection.target = target
                        self.newConnection.source = self
                        self.newConnection.target_point = target.center()
                        self.newConnection.source_point = self.center()
                            
                        self.connect(target, self.newConnection)
                        target.connect(self, self.newConnection)
                        
                        self.newConnection.updatePath()
                    
                else:
                    self.newConnection._remove()
        else:
            super(SlotItem, self).mouseReleaseEvent(event)
        
        nodzInst.currentHoveredNode = None

    def shape(self):
        # class SlotItem method shape()
        #16dec this code is not called in this program 
        # BUT it IS called, must be that 'shape()' is some basic method
        # and the code here overloads it ( i guess)
        
        """
         The shape of the Slot is a RECT was circle.
        """
        #17dec this code is for the sensitive rectangle NOT gui rect
        #
        path = QtGui.QPainterPath()
        
        br=self.boundingRect()
        
        xpos=br.left()
        
        ypos=br.top()
        #wide=br.width()
        wide=200
        ht=br.height()

        if(self.netname == "-"):
            xpos = xpos + 7
            wide = wide + 7
            
        #print(xpos,ypos,wide,ht)
        newRect = QtCore.QRectF( xpos, ypos, wide, ht) 
        
        path.addRect(newRect)
        
        return path

    def paint(self, painter, option, widget):
        #16dec class SlotItem method paint()
        #17dec this is just the gui part of slot
        # NOT the sensitive area of the slot
        """
         Paint the Slot.
        """
        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            if self.parentItem() == nodzInst.currentHoveredNode:
                painter.setBrush(utils._convertDataToColor(config['non_connectable_color']))
                if (self.slotType == nodzInst.sourceSlot.slotType or (self.slotType != nodzInst.sourceSlot.slotType and self.dataType != nodzInst.sourceSlot.dataType)):
                    painter.setBrush(utils._convertDataToColor(config['non_connectable_color']))
                else:
                    _penValid = QtGui.QPen()
                    _penValid.setStyle(QtCore.Qt.SolidLine)
                    _penValid.setWidth(2)
                    _penValid.setColor(QtGui.QColor(255, 255, 255, 255))
                    painter.setPen(_penValid)
                    painter.setBrush(self.brush)
        #16dec chgd from ellipse (circle) to rect
        br=self.boundingRect()
        bw = config['node_width']
        
        #17dec this is the orange gui rect NOT the sensitive rect
        xpos=br.x()
        ypos=br.y()
        wide=bw
        ht  =br.height()
        
        #17dec all skts were -7 too much
        if(self.netname == "-"):
            xpos = xpos + 7
        
        # was painter.drawEllipse(self.boundingRect())
        painter.drawRect(xpos,ypos,wide,ht)

    def center(self):
        #16dec class SlotItem method center()
        #17dec TODO this is the cnxn point  , no longer have circle
        # so will need spot on left or right edge depending on cnxnSide
        """
         was  Return The center of the Slot.
         TODO Return The cnxn point Slot.
        """
        rect = self.boundingRect()
        #17dec the word 'center' should be 'cnxnpoint'
        # and that will be left edge ctr or rt edge ctr
        # depending on cnxnSide
        # who calls this fx?
        #center = QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        if(self.cnxnSide == "left"):
            #27jan2022  looking at gap between bez end and skt
            #  at 4 i see gap , at 5 no gap
            # why any gap?
            center = QtCore.QPointF(rect.x() + 5.0, rect.y() + rect.height() * 0.5)
        else:
            #27jan2022
            # bez ending at right side had no gaps
            # maybe whole painterpath was shifted ~5 to 7 units to right
            center = QtCore.QPointF(rect.x() + rect.width() , rect.y() + rect.height() * 0.5)

        return self.mapToScene(center)

class PlugItem(SlotItem):
    """
     A graphics item representing an attribute out hook.
    """
    def __init__(self, parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections):
        #class PlugItem func __init__
        """
         Initialize the class.

         :param parent: The parent item of the slot.
         :type  parent: QtWidgets.QGraphicsItem instance.

         :param attribute: The attribute associated to the slot.
         :type  attribute: String.

         :param netname: The signal ID for the wire/bezier
         :type  netanme: String.

         :param index: int.
         :type  index: The index of the attribute in the node.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :param dataType: The data type associated to the attribute.
         :type  dataType: Type.
        """
        super(PlugItem, self).__init__(parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections)
        
        # Storage.
        self.attributte = attribute
        self.preset = preset
        self.slotType = 'plug'
        
        self.netname = netname
        
        # Methods.
        self._createStyle(parent)
        
        #14dec2021 add tooltip for plug
        strg1="plug "
        strg2=self.attribute
        strg3=strg1+strg2
        self.setToolTip(strg3)
    
    def _createStyle(self, parent):
        #class PlugItem func _createStyle
        """
        Read the attribute style from the configuration file.

        identical to _createStyle of SocketItem  
        ( except the  utils._convertsDataToColor get the strg 'socket' there
        """
        config = parent.scene().views()[0].config
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(utils._convertDataToColor(config[self.preset]['plug']))

    def boundingRect(self):
        #16dec class PlugItem method boundingRect
        """
         The bounding rect based on the width and height variables.
        """
        
        #width = height = self.parentItem().attrHeight / 2.0
        #17dec text runs outside of gui rect and theres space between
        #height = self.parentItem().attrHeight / 2.0
        # 30jan vvv is bbox of plugitem
        height = self.parentItem().attrHeight -4
        width  = self.parentItem().baseWidth
        
        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        
        x = 0
        y = (self.parentItem().baseHeight - config['node_radius'] +
            self.parentItem().attrHeight / 4 +
            self.parentItem().attrs.index(self.attribute) * self.parentItem().attrHeight)
        rect = QtCore.QRectF(QtCore.QRect(x, y, width, height))
        return rect

    def connect(self, socket_item, connection):
        # class PlugItem method connect()
        """
         Connect to the given socket_item.
         i think it means
         Connect Plug to given Socket item
        """	    
        if self.maxConnections>0 and len(self.connected_slots) >= self.maxConnections:
            # Already connected.
            self.connections[self.maxConnections-1]._remove()
        
        #19nov add the parent into the struct
        #27nov TODO  is this needed? used?
        socket_item.parent = socket_item.parentItem().name
        
        # Populate connection. plug,socket, plugAttrs
        connection.socketItem = socket_item
        connection.plugNode = self.parentItem().name
        connection.plugAttr = self.attribute
        
        # Add socket to list of connected slots.
        if socket_item in self.connected_slots:
            self.connected_slots.remove(socket_item)
        
        self.connected_slots.append(socket_item)
        
        # Add connection.
        #20nov this vvv looks like it ensures no duplicate cnxns 
        #  ( like on top of itself, which you would not see )
        if connection not in self.connections:
            self.connections.append(connection)
        
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

    def disconnect(self, connection):
        #class PlugItm func disconnect   
        #14jan this had been removed by remming entire func
        """
        Disconnect the given connection from this plug item.

        """
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected socket from plug
        if connection.socketItem in self.connected_slots:
            self.connected_slots.remove(connection.socketItem)
        # Remove connection
        self.connections.remove(connection)

        #14jan 2022 this whole func had been remmed out, reinstate above 14jan
        #def disconnect(self, connection):
        """
         Disconnect the given connection from this plug item.
        """
        """    
        # class PlugItem func diconnect
        print("class PlugItem func disconnect")
    
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected socket from plug
        if connection.socketItem in self.connected_slots:
            self.connected_slots.remove(connection.socketItem)
        # Remove connection
        self.connections.remove(connection)
        """
    
class SocketItem(SlotItem):
    """
     A graphics item representing an attribute in hook.
    """
    
    def __init__(self, parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections):
        #class SocketItem func __init__
        """
         Initialize the socket.

         :param parent: The parent item of the slot.
         :type  parent: QtWidgets.QGraphicsItem instance.

         :param attribute: The attribute associated to the slot.
         :type  attribute: String.

         :param netname: The str text to be put on the wire/cnxn/edge.netattribute associated to the slot.
         :type  netname: String.

         :param index: int.
         :type  index: The index of the attribute in the node.

         :type  preset: str.
         :param preset: The name of graphical preset in the config file.

         :param dataType: The data type associated to the attribute.
         :type  dataType: Type.
        """
        super(SocketItem, self).__init__(parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections)
        
        # Storage.
        self.attributte = attribute
        self.preset = preset
        self.slotType = 'socket'

        #----beg tjp additions------- my own attrs
        self.cnxnSide=cnxnSide
        self.parent=parent
        self.index= index
        self.netname=netname
        #----end tjp additions-------

        # Methods.
        self._createStyle(parent)

        
        #----beg more tjp additions-------
        #14dec2021 add tooltip for skt
        strg1="socket "
        strg2=self.attribute
        strg3=strg1+strg2
        self.setToolTip(strg3)
        #----end more tjp additions-------

    def _createStyle(self, parent):
        #class SocketItem func _createStyle
        """
         Read the attribute style from the configuration file.
        """
        config = parent.scene().views()[0].config
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(utils._convertDataToColor(config[self.preset]['socket']))

    def boundingRect(self):
        #class SocketItem func boundingRect
        """
         The bounding rect based on the width and height variables.
        """
        #30jan vvv is bbox of sktItem
        height = self.parentItem().attrHeight -4
        width  = self.parentItem().baseWidth + 7

        nodzInst = self.scene().views()[0]
        #14jan notice how he got infor from cfg file
        config = nodzInst.config

        #17dec SIMPLIFIED all gui rect slots begin  x = -7
        x = -7
        y = (self.parentItem().baseHeight - config['node_radius'] +
            (self.parentItem().attrHeight/4) +
             self.parentItem().attrs.index(self.attribute) * self.parentItem().attrHeight )

        rect = QtCore.QRectF(QtCore.QRect(x, y, width, height))
        return rect

    def connect(self, plug_item, connection):
        #class SocketItem func connect
        
        # this cnx a skt to a plug
        # i dont think i want this, 
        # i want a digraph and direction is ALWAYS ONLY plug to skt
        # never skt to plug
        """
         Connect to the given plug item.
         20nov this was neutered by add a=1 and remming rest, that action screwed save, so undo
        """
        numcnxns = len(self.connections)

        #21nov i dont think the orig logic is right
        """
            if self.maxConnections>0 and len(self.connected_slots) >= self.maxConnections:
                # Already connected.
                self.connections[self.maxConnections-1]._remove()
        """
        
        #21nov  new wrapper if  'for create new cnxn'
        #21nov well this dis-allowed a new cnxn in db, but does not prevent bez on screen
        #  so the draw code should not be called
        #14jan i always set maxCnxns to infinite, so test maybe unnecc
        if( numcnxns < self.maxConnections ):
            #then allow a new cnxn
            
            # Populate connection.
            connection.plugItem = plug_item
            connection.socketNode = self.parentItem().name
            connection.socketAttr = self.attribute

            # Add plug to connected slots.
            self.connected_slots.append(plug_item)

            # Add connection.
            if connection not in self.connections:
                self.connections.append(connection)
            
            # Emit signal.
            nodzInst = self.scene().views()[0]
            nodzInst.signal_SocketConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)
            
    def disconnect(self, connection):
        #class SocketItem func disconnect
        """
         Disconnect the given connection from this socket item.
        """
        #print("class socketItem func disconnect")
    
        
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_SocketDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected plugs
        if connection.plugItem in self.connected_slots:
            self.connected_slots.remove(connection.plugItem)
        # Remove connections
        self.connections.remove(connection)
           
class ConnectionItem(QtWidgets.QGraphicsPathItem):
    #class ConnectionItem
    """
     A graphics path representing a connection between two attributes.
    """
    #22nov need source cnxnSide  target cnxnSide, dunno who is plug who is skt,,, ? yes??
    #  well source is ALWAYS plug for me in my app, 
    
    def __init__(self, source_point, target_point, source, target, netname, cnxnSide ):
        #class ConnectionItem func __init__
        """
         Initialize the class.

         :param sourcePoint: Source position of the connection.
         :type  sourcePoint: QPoint.

         :param targetPoint: Target position of the connection
         :type  targetPoint: QPoint.

         :param source: Source item (plug or socket).
         :type  source: class.

         :param target: Target item (plug or socket).
         :type  target: class.

         :param netname: name for the signal 
         :type  netname: string
        """
        
        super(ConnectionItem, self).__init__()
        
        self.setZValue(1)
        
        self.socketNode = None
        self.socketAttr = None
        self.plugNode = None
        self.plugAttr = None
        
        # 11nov  smells funny    does not this already have value?
        #21nov DONE check its really needed  YES it IS necc
        self.netname = netname

        
        self.source_point = source_point
        self.target_point = target_point
        self.source = source
        self.target = target

        #24nov+++ i think target is 'None'
        
        self.plugItem = None
        self.socketItem = None
        
        self.movable_point = None
        
        self.data = tuple()
        
        # Methods.
        self._createStyle()
        
        strg1="signal "
        strg2=self.netname
        strg3=strg1+strg2
        self.setToolTip(strg3)
        
        
    def _createStyle(self):
        #class ConnectionItem func _createStyle
        """
         Read the connection style from the configuration file.
        """
        config = self.source.scene().views()[0].config
        #14dec2021 this vvv is orig code not mine
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

        self._pen = QtGui.QPen(utils._convertDataToColor(config['connection_color']))
        self._pen.setWidth(config['connection_width'])

    def _outputConnectionData(self):
        #class ConnectionItem func _outputConnectionData
        """
         tjp  i think this goofy "{0}.{1}".format(self.socketNode, self.socketAttr)
          ia dam screwy way to build a string given 2 args, whcih are {0].{1}
          with a dot between
          so my current prob is self.socketNode is None
          and                   self.socketAttr is None
        """
        return ("{0}.{1}".format(self.plugNode, self.plugAttr),
                "{0}.{1}".format(self.socketNode, self.socketAttr))
        
    def mousePressEvent(self, event):
        #return True
        
        #class ConnectionItem func mousePressEvent    
        """
         Snap the Connection to the mouse.
         
         TJP what doe sthis func do?
         what is source and target
        """
        #24jan  rtclk del net is ok(deleted)  lfclk net is ok ( nada)

        # this is what is done when a mouse press happens on a cnxn
        # i want a left ctrl press  to delete it
        # i want a left nomod press to NOT delete it
        #print("classCnxnItem mousePress")
        
        # 13nov this looks like a handy universal way to get verything available to a func
        nodzInst = self.scene().views()[0]
        
        # 13nov a high Z value is 'on top' and therefore visible
        #21nov maybe useful to highlight a net later
        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)
        
        nodzInst.drawingConnection = True
            
        self.updatePath()
            
    def mouseMoveEvent(self, event):
        #return True
        
        #class ConnectionItem func mouseMveEvent
        # THIS FUNC IS NEUTERED  it has early return
        #23jan test  
        #  if this func NOT rtnd early, 
        #  and mouseReleaseEvent (next) is NOT rtnd early
        #  then i CAN get trim to happen (dangling noodle)
        #
        #  if this func RTND EARLY and next NOT RTND EARLY
        #  then i CANNOT get trim to happen
        #
        #  if next func IS RTND EARLY
        #  and this func is NOT RTND early
        #  then i CAN get trim to happen
        #
        #  if next IS NOT RTND EARLY
        #  and this IS NOT RTND EARLY
        #  then i CAN get trim to happen
        return 
        """
           Move the Connection with the mouse.
        """
        #23jan --------begin dbug   
            
        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        mbb = utils._createPointerBoundingBox(pointerPos=event.scenePos().toPoint(),
                                              bbSize=config['mouse_bounding_box'])
        # Get nodes in mouse pointer's bounding box.
        targets = self.scene().items(mbb)
        if any(isinstance(target, NodeItem) for target in targets):
            if nodzInst.sourceSlot.parentItem() not in targets:
                for target in targets:
                    if isinstance(target, NodeItem):
                        nodzInst.currentHoveredNode = target
        else:
            nodzInst.currentHoveredNode = None
        if self.movable_point == 'target_point':
            self.target_point = event.pos()
        else:
            self.source_point = event.pos()
        self.updatePath()
    
    def mouseReleaseEvent(self, event):
        #return True
        
        #class ConnectionItem func mouseReleaseEvent
        #24jan make action conditional with button() == 2 (rt btn)
        #  now rtPress dels net leftPress does nothing 
        """
         Create a Connection if possible, otherwise delete it.
        """
        #24jan vvv is printed now, report 1 ( leftbtn )
        #print("class cnxnItem func mouseReleaseEvent  mouse btn was ", event.button())
        #24jan make action conditional with button() == 2 (rt btn)
        if(event.button() == QtCore.Qt.RightButton):
            nodzInst = self.scene().views()[0]
            nodzInst.drawingConnection = False
            slot = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())
            if not isinstance(slot, SlotItem):
                self._remove()
                self.updatePath()
                super(ConnectionItem, self).mouseReleaseEvent(event)
                return
            # (else)
            if self.movable_point == 'target_point':
                if slot.accepts(self.source):
                    # Plug reconnection.
                    self.target = slot
                    self.target_point = slot.center()
                    plug = self.source
                    socket = self.target
                    # Reconnect.
                    socket.connect(plug, self)
                    self.updatePath()
                else:
                    self._remove()
            else:
                if slot.accepts(self.target):
                    # Socket Reconnection
                    self.source = slot
                    self.source_point = slot.center()
                    socket = self.target
                    plug = self.source
                    # Reconnect.
                    plug.connect(socket, self)
                    self.updatePath()
                else:
                    self._remove()
            
    def _remove(self):
        """
         Remove this Connection from the scene.
        """
        #class ConnectionItem func _remove
        
        if self.source is not None:
            self.source.disconnect(self)
        if self.target is not None:
            self.target.disconnect(self)

        scene = self.scene()
        scene.removeItem(self)
        scene.update()

    def updatePath(self):	
        """
            Update the path.
        """
        #class ConnectionItem func updatePath
        
        self.setPen(self._pen)
        
        path = QtGui.QPainterPath()
        path.moveTo(self.source_point)
        
                
        if( isinstance(self.source , PlugItem)):

            #14jan dx clc is chgd by TJP, 
            #  code senses if begx = end x (vert) 
            #   and bows outward from node if so
            # dy,ctrl1 ctrl2 are as orig
            dx = (self.target_point.x() - self.source_point.x()) * 0.5
            
            #25nov i had some nets that were between 2 vertically stacjed nodes
            # and made some code to 'bend' the bez away from the node boundary
            # and i think a larger 'standoff' value is easier to interpret ( was 50 now 100 )
            #18dec i saw no bend for loopback on left side of ioControlNN
            #  and chg from 3 to 10 'fixed' it
            if(self.source.cnxnSide == 'left'):
                if(( dx < 10) and (dx > -10)):
                    dx = -100
            if(self.source.cnxnSide == 'right'):
                if(( dx < 10) and (dx > -10)):
                    dx = 100
            
            dy = self.target_point.y() - self.source_point.y()
            ctrl1 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 0)
            ctrl2 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 1)
            path.cubicTo(ctrl1, ctrl2, self.target_point)

            #25nov added text on bezier, uses netname
            #  is justified towards plug end
            if(self.source.cnxnSide == "right"):
                percent = 0.2
            else:
                percent = 0.35
            txtloc = path.pointAtPercent(percent)
            path.addText(txtloc,QtGui.QFont('monospace',10), self.netname)
        
            self.setPath(path)




"""
was in 'l' load
                #09feb hard code to toolchg  just a test of setting scrollbars
                #BEWARE zoom and PLUS MINUS keys try to track mouse cursor so keep cursor out of view[port fro tests
                # works toolchg
                #self.verticalScrollBar().setValue(710)
                #self.horizontalScrollBar().setValue(3040)
                #sx=sy=0.930
                #self.scale(sx,sy)
                
                #  stepper  78 1450 ng    245 2320 very good
                #self.verticalScrollBar().setValue(245)
                #self.horizontalScrollBar().setValue(2320)
                #sx=sy=0.607
                #self.scale(sx,sy)
                
                # 09feb z offset
                #self.verticalScrollBar().setValue(226)
                #self.horizontalScrollBar().setValue(1040)
                #sx=sy=1.02
                #self.scale(sx,sy)

                # 09feb gap simulator
                self.verticalScrollBar().setValue(700)
                self.horizontalScrollBar().setValue(0)
                sx=sy=1.100
                self.scale(sx,sy)
                #HERE HERE HERE
                


                #09feb i killed all mouse stuff with earlly return
                #  can i Load json5 t
                #  then 'l' to get hard coded mcodes view scrolled into view 
                #  and zoomed to fit?
                # maybe set a flag ( nomousestuff as prefix in all mouse funcx ( lots!)

                ## 09feb mcodes
                #self.verticalScrollBar().setValue(300)
                #self.horizontalScrollBar().setValue(0)
                ##how th f did i get that scaleing sx sy???
                ##  gotta be view w / scene w
                #sx=sy=0.4777255928160439
                #self.scale(sx,sy)
                
                return
"""
""" from 505
        # Drag Item
        # yes this works   Lbtn ON NODE w/o(alt, or shift , or ctrl)
        elif (event.button() == QtCore.Qt.LeftButton and
              #04feb test if 
              # no, alt left prss drag moves whole window not view
              #  maybe an xfce4 thing
              # yes, to defeat it use 
              # windowmanagertweaks accessability keyused tomobe&grabwindows NONE ( was Alt)
              # result: NO modifier AND alt modifier both allow drag node
              #  w/o moving window
              #
              #event.modifiers() == QtCore.Qt.NoModifier and
              event.modifiers() == QtCore.Qt.AltModifier and
              self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is not None):
            self.currentState = 'DRAG_ITEM'
            self.setInteractive(True)
"""
#from 1147
"""
                    return
                    #--------------------end i hope -----------
                    #10feb sel nodes from 'view' file
                    for selnode in nodesToView:
                        #print(selnode)

                    #03feb2022 TODI is _getSelectionBoundingbox
                    #   same/as good as this vvv?  can i call it ^ reduce code length?
                    ctr=0
                    #24jan find bounding box for selected nodes
                    for selnode in nodesToView:
                        #print(selnode)
                        nodeInst = self.scene().nodes[selnode] 
                        tx=nodeInst.x()
                        ty=nodeInst.y()
                        if ctr == 0:
                            minx=tx
                            maxx=tx
                            miny=ty
                            maxy=ty
                        else:
                            if tx < minx:
                                minx = tx
                            if tx > maxx:
                                maxx = tx
                            #print("ty is ", ty, " miny is ", miny )
                            if ty < miny:
                                miny = ty
                            if ty > maxy:
                                maxy = ty

                        #10feb set selected flag fro fitinview later
                        selNode.setSelected(False)

                        #print(tx,ty,minx,miny,maxx,maxy)
                        ctr += 1
                    #wdth = (maxx - minx ) + 200 +150 +300
                    # chk with fakegap.json for width
                    wdth = (maxx-minx) + 350
                    #wdth = (maxx-minx)
                   
                    #05feb use same everywhere ( dummy make a func)
                    #hght = (maxy - miny) + 800
                    #09feb 200 is enuf  else 
                    # TODO find lowest node and real hght
                    #hght = (maxy - miny ) + 200
                    hght = (maxy - miny )+90
                    
                    #10feb vv maybe uselss also minxminymaxxmaxy maybe uselee
                    # maybe set seleted and focus is enf
                    self.setSceneRect(minx, miny, wdth, hght)


                    pp = QtGui.QPainterPath()
                    pp.addRect( QtCore.QRectF(minx, miny, wdth , hght) )
                    self.scene().setSelectionArea(pp)
                    self._focus()
                    
                    # ^^^ not bad ,almost right, the slected nodes are ctrd 
                    #  almost ctrd, and visible, and little if anything is trimmed at right
                    #  as good as it gets  03feb2022
                    
                    #04feb de-sel all after load view
                    # works all 'l'oad  show black borders ( not orange as in selected)
                    for selname in self.scene().selectedItems():
                        selname.setSelected(False)

"""