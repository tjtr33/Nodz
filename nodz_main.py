import os
import re
import json
#19dec for running KiCad on project file
#import subprocess
import sys

from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg
from PyQt5 import QtGui, QtCore, QtWidgets, QtSvg
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QPushButton, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import *

#from PyQt5.QtCore import *
#from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *


import nodz_utils as utils

#27nov TODO  use a better file name
#05dec this value is initial, it can be chgd by a node's 'alternate'
#  if a node with an alternate file name is dbl clicked
#  then that file is loadGraph'd
#  the var 'filePath is set to node.alternate BEFORE loading
# so, a SAVE (S) cmd  will overwrite the new node.alternate file., not the parent file
# 
# there is a new helper node named GetBackHomeLoretta
# with no attributes, only a node.alternate
# that can be used to return to parent by putting parents filePath string in that var
#
#09jan TODO maybe chg to workingFile
# or get it from a file picker when L is pressed
#filePath = "./SaveMe"
#09jan2022 chg from global filePath to workingFile  bein null$ , use fpicker
workingFile = ""

#09jan2022 zoom infactor outFactor no longger used
#zoomScale = 1
#inFactor = 1.03
#outFactor = 1 / 1.03

# 06nov2021  heavy handed global aliasing
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtCore.Property = QtCore.pyqtProperty

defaultConfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'default_config.json')


#class Nodz(QtWidgets.QGraphicsView):
class Nodz(QtWidgets.QGraphicsView):
    """
     The main view for the node graph representation.

     The node view implements a state pattern to control all the
     different user interactions.

    """
    # 08nov2021 these Signals played hell with PyQt5 so there are aliases to calls that are PyQt5 safe
    #08jan2022 these lines vvv create signals
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
    #08jan try to make  a new sgl
    signal_PlugSelected = QtCore.Signal(object)

    signal_GraphSaved = QtCore.Signal()
    signal_GraphLoaded = QtCore.Signal()
    signal_GraphCleared = QtCore.Signal()
    signal_GraphEvaluated = QtCore.Signal()

    signal_KeyPressed = QtCore.Signal(object)
    signal_Dropped = QtCore.Signal()

    def __init__(self, parent, configPath=defaultConfigPath):
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

    #09jan2022 a fsaver dlog found on web for pyqt5
    # does not do saveGraph (yet) just prints chosenFile to console
    # note saveGraph gets fname passed
    def getFileNameForSave(self,suggestedFname):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        #fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        fileName, _ = QFileDialog.getSaveFileName(self,"Save Graph to File",suggestedFname,"All Files (*);;Text Files (*.txt)", options=options)
	#svDlg.getSaveFileName(this, caption, preferredName, filter);

	#09jan2022 return filename if null or not, just return it
	return fileName
	    
    #17dec  found on web vvv but if here it belongs to class Nodz
    # and my use case is down in slot/plug/socket
    # 
    # 1st try to make po[up appear
    # and be able to get rid of popup

    def getFileNameForOpen(self):
	#09jan2022 uses global  workingFile
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Graph File to Load",workingFile,"All Files (*);;Text Files (*.txt)", options=options)
        #files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        #if fileName:
        #    print(fileName)    
	return fileName    
    #def doit(self,wide,high):
    #18dec MyPopup gets self, so it can find img filename in self.alternate

    def doSch(self,proFile):
        strg1="kicad "
        strg2=proFile
        strg3=strg1+strg2
        os.system(strg3)
        #subprocess.run(strg3)

    def doTxt(self,txtFile):
	#19dec using just "nano fname" 
	#  would run nano in termnl that ran python nodz_demo.py
	#  and that was a mess when nano exited
	# so try openng a new terminal to run nanao from
	strg1="xfce4-terminal -H --command \"nano "
        strg2=txtFile
	strg3="\""
        strg4=strg1+strg2+strg3
        os.system(strg4)
	
    #19dec  this vvv removes need for local ecad pgm
    # just make an svg of the schematic and mark attr <dataType = "svg">
    def doSVG(self,svgFile):
	self.svgWidget = QtSvg.QSvgWidget(svgFile)
	self.svgWidget.show()
	    
    def doMan(self,manItem):
	strg1="xfce4-terminal -H --command \"man "
        strg2=manItem
	strg3="\""
        strg4=strg1+strg2+strg3
        os.system(strg4)
	"""
	
	#08jan2022 stuid test to see what these values are
	strg1="QtCore.Qt.ControlModifier is  "
        strg2=(str(QtCore.Qt.ControlModifier))
	strg3=strg1+strg2
	print(strg3)
	strg1="QtCore.Qt.ShiftModifier is  "
        strg2=(str(QtCore.Qt.ShiftModifier))
	strg3=strg1+strg2
	print(strg3)
	strg1="QtCore.Qt.MetaModifier is  "
        strg2=(str(QtCore.Qt.MetaModifier))
	strg3=strg1+strg2
	print(strg3)
        """
	
    def doUrl(self,url):
	strg1="firefox-esr "
	#19dec spcl invocation of chromium to stop it bitching about keyring
        #strg1="chromium --password-store=basic "
        strg2=url
        strg3=strg1+strg2
        os.system(strg3)
    
    def doImg(self,imgFname):
        self.w = MyPopup(imgFname)
        #17dec the popup wndo size is set by  setPixmap in class mypopup
        #17dec TODO this fx should get image fname
        # the class should NOT set img pixmap sizes HERE HERE HERE
        self.w.show()

    def doEditSaveMe(self,txtFile):
	#09jan2022   works and single wndo to close :-)
	strg1="scite "
        strg2=txtFile
        strg3=strg1+strg2
        os.system(strg3)

    def mousePressEvent(self, event):
        """
         Initialize tablet zoom, drag canvas and the selection.
        """
	#class Nodz func mousePressEvenet
        #ok rmvd 15dec try add popup dlg m 1st get bg sensitive to clk
        
	#08jan2022 this vv prints the object clkd on
        print(self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform()))
	#08jan these vvv turn itemAt into english
	clkontype = (type(self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform())))
	#print("clkontype = >>",clkontype,"<<")
	if clkontype == NodeItem:
	    print("Node clkd")
	if clkontype == PlugItem:
	    print("PlugItem")
	if clkontype == SocketItem:
	    print("SocketItem")
	if clkontype == ConnectionItem:
	    print("ConnectionItem")
	


	#08jan try to notice clk and modifier
        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.NoModifier):
	    print("l btn press and NO mod")
	
	
        # 09nov  AltRtBtn  this is stolen by XFCE4 and it resizes the window vertically
        # DONT USE ALT RT BTN!
        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.AltModifier):
            self.currentState = 'ZOOM_VIEW'
            self.initMousePos = event.pos()
            self.zoomInitialPos = event.pos()
            self.initMouse = QtGui.QCursor.pos()
            self.setInteractive(False)

        # Drag view
        # 09nov alt midBtn  is stolen by xfce4 gui  , it hides wndo and expose below
        # so JUST DONT USE ALT RT BTN
	#08jan2022
	# note  this elif id empty, is also empty on04jan vrsn, and drag cnxn works there
        elif (event.button() == QtCore.Qt.MiddleButton and
              event.modifiers() == QtCore.Qt.AltModifier):
        
            """
            dangerous  inhibit it  ok now just shows other window beneath
                self.currentState = 'DRAG_VIEW'
                self.prevPos = event.pos()
                self.setCursor(QtCore.Qt.ClosedHandCursor)
                self.setInteractive(False)
            """

        # Rubber band  BEGIN
        # aka lasoo  , have to start in empty space, 
        #  but does not need to end in empty space, does not  need to lasoo anything
        #elif (event.button() == QtCore.Qt.LeftButton and
        #      event.modifiers() == QtCore.Qt.NoModifier and
        #      self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
	
	#05jan chgs to ctrl shidt left press
	# now can lassoo group
	# and ingle clk in space deselects all
        #elif (event.button() == QtCore.Qt.LeftButton and
        #      event.modifiers() == QtCore.Qt.ControlModifier and
	#      event.modifiers() == QtCore.Qt.ShiftModifier and
        #      self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):

        #05jan chg to just shift left press ANYWHEE in space
	# got select ALL
	# and ingle clk in space deselects all
        #elif (event.button() == QtCore.Qt.LeftButton and
	#      event.modifiers() == QtCore.Qt.ShiftModifier and
        #      self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
		      
        #05jan chg to just ctrl left press ANYWHEE in space
	# got ctrl left press in space selects ALL
	# and left press anywhere in space DEselects All
	#
	# and control shift left press rubberband selects group
	#
	# and further shift left press adds indiv nodes
	
        #08jan2022 here vv i chgd fron NoModifier to ControlModifier
	# and i lost ability to drag a net frpm a plu
	#elif (event.button() == QtCore.Qt.LeftButton and
	#      event.modifiers() == QtCore.Qt.ControlModifier and
        #      self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
	
	# 08jan this vvv is for select ALL
	# click in space with correct modifier
	# 08jan 2022 i can make it works with Shift Control and Meta
	#  leaving it with Control for now

        #08jan2022 got shift control meta working in all combos
	#       and self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
	# the last constraint means 'clicked in space'
	# so we enter selection mode IF we ctrl chift meta clk in space
	#  further code will ignore the posn where clk occured
	#  and will effectively lasoo everything
        elif ((event.button() == QtCore.Qt.LeftButton ) and 
	      (event.modifiers() & QtCore.Qt.ShiftModifier ) and
	      (event.modifiers() & QtCore.Qt.MetaModifier ) and
	      (event.modifiers() & QtCore.Qt.ControlModifier ) and
	      (self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform()) is None)):
	    print("l btn and SHIFTCONTROLMETA---------------****")
	    #print(self.scene().itemAt(self.mapToScene(event.pos()),QtGui.QTransform()))
            self.currentState = 'SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Drag Item
        # yes this works   Lbtn ON NODE w/o(alt, or shift , or ctrl)
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.NoModifier and
              self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is not None):
            self.currentState = 'DRAG_ITEM'
            self.setInteractive(True)


        # Add selection
	#04jan2022 2146
	# this is CTL SHIFT LBTN PRESS ( other code handle release)
	#  it sets up a STATE  'ADD_SELECTION'
	# MAYBE i can add a new keybtncombo for AddAll
        elif (event.button() == QtCore.Qt.LeftButton and
              QtCore.Qt.Key_Shift in self.pressedKeys and
              QtCore.Qt.Key_Control in self.pressedKeys):
            self.currentState = 'ADD_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Subtract selection
        # 20nov this means Ctl Lbtn   but i see no subtract action
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ControlModifier):
            self.currentState = 'SUBTRACT_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Toggle selection
        #20nov  this works,  ON ONE NODE shiftmodifier is just damn shift
        # and shift Lbtn toggles the hilite of a node when ptr on node
	#04jan can i hack this with a modifier to do select/deselect ALL?
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ShiftModifier):
            self.currentState = 'TOGGLE_SELECTION'
	    
	    #04jan2022 
	    # the event here is  Shift LeftBtn
	    #
	    #  ng   tried w/o vvv and include  the trple quoted below
            self._initRubberband(event.pos())
	    # 04jan i get a rubberbox from 0 0 to the mouse
	    #   not enveloping all widgets
	    #  well IF the mouse if to right and nelow all THEN all nodes selected
	    #
	    
	    """
	    p=QPoint()
            p.setX(0)
            p.setY(0)
	    self._initRubberband(p)
	    """
	    
            self.setInteractive(False)
	    """
            # if after this ^^^ i shift then left btn clck below and right of all
	    # then everything is selected
	    # i think i can make a select All this way
	    # if i use 0,0 ( seems to be top left of canvas)
	    # AND if i knew the bounding box or width.height of canvas
	    # AHAH in the config file is
	    #     "scene_width": 2000,
            #     "scene_height": 2000,
	    # 0,0,2000,2000 should work... NO NOT ENUF -10000 -10000 10000 10000
	    # work where?  i think the start corner is done her4e but the end corner is done in release code
	    """
        else:
            self.currentState = 'DEFAULT'

        super(Nodz, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
         Update tablet zoom, canvas dragging and selection.
        """
	#09jan2022 wth does zoom do in mouseMove???
        # Zoom.
        if self.currentState == 'ZOOM_VIEW':
            offset = self.zoomInitialPos.x() - event.pos().x()

            if offset > self.previousMouseOffset:
                self.previousMouseOffset = offset
                self.zoomDirection = -1
	        #09jan2022 i dont see zoomIncr used		
                #self.zoomIncr -= 1

            elif offset == self.previousMouseOffset:
                self.previousMouseOffset = offset
                if self.zoomDirection == -1:
                    self.zoomDirection = -1
                else:
                    self.zoomDirection = 1

            else:
                self.previousMouseOffset = offset
                self.zoomDirection = 1
	        
	    #09jan2022 the zoom is not as expected
	    # inside Qt  there are numbers
	    # outside in pyqt5 there is the idea of scale
	    # the outsideScale can affect the inside mumbers
	    # bit notas expected
	    # id inside number begins as 15
	    # and outside scale is set to 1
	    # then inside is 16   ok
	    # but if outside scale is set to 2/3
	    # then inside number is 10   ok
	    # now, if outside scale is left at 2/3 and the scale func is called again
	    # then inside number becomes 0.6666...
	    # and if scale called again, inside# is 0.444444 etc
	    # so the outside scale didnt change
	    # it was just called again
	    # SO what is the inside number 15 when 1st loaded?

            #09jan2022 i found to restore the scale to orig on S.O.
	    #  To reset the index you must reset the transformation:
            #  {your_graphicsview}.setTransform(QtGui.QTransform())
            #
	    # maybe a key R restore size?
	    # am i getting close to needing menus?


            # Perform zoom and re-center on initial click position.
            #27nov TODO does this work? "zoom on initl clk posn? ...   re-center on initl clkposn?
            #27nov i think zoom is pretty sucky, needs a "zoom all", "zoom selected"
            pBefore = self.mapToScene(self.initMousePos)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)

	    #09jan2022 i dont see why scene scale is affected by mouseMove
            #  	    so i rem it
            #self.scale(zoomScale, zoomScale)
	    
	    # what is self here?  class Nodz(QtWidgets.QGraphicsView):
	    #  PySide2.QtWidgets.QGraphicsView.scale(sx, sy)
	    
            pAfter = self.mapToScene(self.initMousePos)
            diff = pAfter - pBefore

            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            self.translate(diff.x(), diff.y())

        # Drag canvas.
        elif self.currentState == 'DRAG_VIEW':
            offset = self.prevPos - event.pos()
            self.prevPos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())

        # RuberBand selection.
        elif (self.currentState == 'SELECTION' or
              self.currentState == 'ADD_SELECTION' or
              self.currentState == 'SUBTRACT_SELECTION' or
              self.currentState == 'TOGGLE_SELECTION'):
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

        super(Nodz, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
         Apply tablet zoom, dragging and selection.
        """
        # Zoom the View.
        if self.currentState == '.ZOOM_VIEW':
            # 20nov  zoom has nothing to do with mouseRelease, test by rem-ing this code
            #27nov  recheck, i dunno what ^^^ means
	    #09jan2022 this code has been neutered for a loooong time
	    # dunno what it will do if uncommented
	    # 09jan2022 TODO test what happens when uncommented
            """
            self.offset = 0
            self.zoomDirection = 0
            #09jan2022 i dont see zoomIncr used		
            #self.zoomIncr = 0
            self.setInteractive(True)
            """
        # Drag View.
        elif self.currentState == 'DRAG_VIEW':
            """
            #20nov there is no drag view that i can see using mouse
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setInteractive(True)
            """
        # Selection.
	# if state - SELECTION then mouseReleas will choose ALL
	#05jan2022 why was i in SELECTION state
        elif self.currentState == 'SELECTION':
	    
            #20nov i can lassoo and can move the group that was lassooed
	    #09jan 2022  TODO can i zoom the slected? YES
            #        can I save the selected? NO
	    #        can I turn slected into a macro-widget? DO SAVE SEL 1st
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())
            painterPath = self._releaseRubberband()
	    	    
            self.setInteractive(True)
	    
	    # 09jan2022 found   itemsArea = self.scene().itemsBoundingRect()
	    # cool it works, i didnt like my hard numbered kludge
	    ppath = QPainterPath()
            #ppath.addRect(-10000, -10000, 20000, 20000)
	    ppath.addRect(self.scene().itemsBoundingRect())
            self.scene().setSelectionArea(ppath)

        # Add Selection.
        # 27nov  what does add selection mean?? duplicate/copy? 
        elif self.currentState == 'ADD_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            #20nov this reads like lassoo, all items lassooed get hilihghted
            # but the print doesnt occure   so   its not a lasoo here	    #print("add selection  lassoo-ed")
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(True)

        # Subtract Selection.
        # 27nov what does subtract mean? delete?
	# 08 jan  i think it means de-selected
        elif self.currentState == 'SUBTRACT_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(False)

        # Toggle Selection
        # 27nov what does toggle mean? visibility?
	#08jan i think it means toggle selected-ness of item(s)
        elif self.currentState == 'TOGGLE_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                if item.isSelected():
                    item.setSelected(False)
                else:
                    item.setSelected(True)

        self.currentState = 'DEFAULT'

        super(Nodz, self).mouseReleaseEvent(event)
     
    def keyPressEvent(self, event):
        """
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
	
        #05dec use global  keyword with filePath
	#09jan2022 rename global filePath to workingFile
	global workingFile
	        
	#09jan2022  whats this vvv mean??
	#  is it concatenating a command?
	# useful?  not afaict   the list is just tossed later
        if event.key() not in self.pressedKeys:
            self.pressedKeys.append(event.key())

        #09jan2022 ERASE vvv works  del or b/s
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace):
            self._deleteSelectedNodes()

        #09jan2022 ZOOM IN works  either keypad or shift'='
        if event.key() == QtCore.Qt.Key_Plus:
	    #09jan2022 no more global inFactor, use constant, only 1 place
	    self.scale(1.03,1.03)
            self.currentState = 'DEFAULT'

        #09jan2022 ZOOM OUT works  either keypad or '-'
        if event.key() == QtCore.Qt.Key_Minus:
	    #09jan2022 no more global outFactor   use a constant , only 1 place
	    self.scale(0.970873786408,0.970873786408)
            self.currentState = 'DEFAULT'

        #09jan2022
	# R  RESIZE  restore full size   not very useful
	# I DID find i can restore the original scale ( or unscaled scene )
	#  on Stack Overflow
        # To reset the index you must reset the transformation:
        #  {your_graphicsview}.setTransform(QtGui.QTransform())
        # so self.setTransform(QtGui.QTransform())  should work
	# try it in key 'R'  for resize
        # WORKS  but not very useful, becuz that size doesnt fit on screem (usually, or you have a 2node graph ;-/
        if event.key() == QtCore.Qt.Key_R:
            self.setTransform(QtGui.QTransform())
		
	################# SAVE FILE #################

	#09jan2022 if i want to save ctr and scale
	# short story:   not what i imagined
	#
	# they must be known
	# what are the vars to use now?
	# well for scale there is no var
	#  the view size is chgd by using object.scale(xscale,yscale)
	#  so I know the scaling factor but I might have applied it N times already
	#  so I could track the scaling factor, timesUP and timesDown
	#  but i dont so far

        ################### SAVE #######################
        if event.key() == QtCore.Qt.Key_S:
            if event.modifiers() == QtCore.Qt.NoModifier:
		workingFile = self.getFileNameForSave(workingFile)
		#09jan2022 if fname from dlog has value, then save
		if workingFile:
		    self.saveGraph(workingFile)
	    elif event.modifiers() == QtCore.Qt.ControlModifier:
		######## SAVE AS FILE #########
		filetoSaveAs = self.getFileNameForSave()
		#09jan2022 if fname from dlog has value, then save
		if filetoSaveAs:
		    self.saveGraph(filetoSaveAs)

        ################# LOAD ############################
        if event.key() == QtCore.Qt.Key_L:
	    #09jan2022 use dialog to get file to load
	    fileNameToOpen = self.getFileNameForOpen()
	    if fileNameToOpen:
                self.loadGraph(fileNameToOpen)

        ################## FOCUS ###############################
        #27nov  ctrs the selection on screen
	#09jan2022 hmmm if a single node is seleected, F will zoom it to full window
	#09jan2022 WEEEEE if a groupl is slected, then F will zoom the group to full window
	#09jan2 even a 'sparse' group can be zoomed with F
        if event.key() == QtCore.Qt.Key_F:
            self._focus()

        ################ EMIT KeyPressed SIGNAL ################
        # Emit signal.
        self.signal_KeyPressed.emit(event.key())
    ################### end key press func ########################

    def keyReleaseEvent(self, event):
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
        """
         Initialize the rubber band at the given position.
        """
        self.rubberBandStart = position
        self.origin = position
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()

    def _releaseRubberband(self):
        """
         Hide the rubber band and return the path.
         20nov is this the bez? YES bez is a QPainterPath
        """
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self.rubberband.geometry())
        painterPath.addPolygon(rect)
        self.rubberband.hide()
        
        return painterPath

    def _focus(self):
        """
         Center on selected nodes or all of them if no active selection.
        """
	#09jan2022 the 'focus on all if none selected'   works  sortof  not ctrd horz by a  lot
        #09jan2022 the focus on selected when some selected works ok
        if self.scene().selectedItems():
            itemsArea = self._getSelectionBoundingbox()
            self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)
        else:
	    #10jan2022  if nothing is selected , then Focus on ALL
	    bbox=self.sceneRect()
	    self.fitInView(bbox, QtCore.Qt.KeepAspectRatio)

    def _getSelectionBoundingbox(self):
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

    #05dec    filePath is nfg from config file  default_config.json
    def loadConfig(self, somecfgpath):
        """
         Set a specific configuration for this instance of Nodz.

         :type  somecfg: str.
         :param somecfgpath: The path to the config file that you want to use
        """
        self.config = utils._loadConfig(somecfgpath)

    def initialize(self):
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
        # 03nov2021 ena Horz scrolbars self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # 03nov2021  ena Vert scrollbars self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        # Setup scene.
        scene = NodeScene(self)
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

    #05dec nodes have an 'alternate' property
    # I use alternate for multimeda add'l info about node
    # manpages, svgPix, web urls, textfiles &more can be accessed
    # the top of a node with such xtra info has 'ShowMe'.
    #  just clk on that text and the dataType attribute will determine the viewer
    #  and the viewer will open a filename in 'alternate'
    
    def createNode(self, name='default', preset='node_default', position=None, alternate=""):
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
		# i _think_
                position = self.mapToScene(self.viewport().rect().center())

            # Set node position.
            self.scene().addItem(nodeItem)
            nodeItem.setPos(position - nodeItem.nodeCenter)

            # Emit signal.
            self.signal_NodeCreated.emit(name)

            return nodeItem

    def deleteNode(self, node):
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

    #23nov a node can have a single connection point (a 'dot') and thus a single cnxnSide
    #09jan2022 nodes dont have dots anymore, they have connection side = left or right
    #  there is nothing visible to where the bezier comes from or goes to
    #  but user can see where it is by dragging out from a plug
    #   the user will notice a bit of the netname appear on mousepress
    #  and the acceptable sockets will highlight when the bezier nears them
    def createAttribute(self, node, cnxnSide='default', name='default', netname='defaultnetname', index=-1, preset='attr_default', plug=True, socket=True, dataType=None, plugMaxConnections=-1, socketMaxConnections=1):	    
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


    # GRAPH
    #def saveGraph(self, xfilePath):
    #05dec remove file[path from calls, use globale filePath
    #09jan2022 may chg to have file passed , an fqfn
    #09jan2022 fqfn is fully qualified file name  a full fspec  with full path
    def saveGraph(self,fqfn):
        """
         Get all the current graph infos and store them in a .json file
         at the given location.

         :type  filePath: str.
         :param filePath: The path where you want to save your graph at.

        """
        
	#09jan2022 use passed filewithpath instead ( allows save and saveas
        ##05dec use global  keyword with filePath
        #global filePath
        
        #27nov  the save goes into a JSON file, man readable, and easily edited/hacked
        # if you want to chg netname, easy, 
        #  want to chg order of slots to untangle? easy
        #  want to flip the port/dot/pin to untangle nets? easy
        # TODO make dlogs to aid in editing
        #
        
        # 07nov2021  create an empty dictionary ( list of key:value pairs)
        # 09nov all data should be accessable from the dict
        #  hahaha  it IS accessable, but canbe tricky to formulate the description of the extracter
        #   eg  dict[nodename][attrname][propertyname]  <<< NOT how its done
        data = dict()
        #27dec data is a dict, has 2 entries 'NODES' and 'CONNECTIONS'
	# the dict is private to this
        
	#02jan2022 1043 this vv missing   is in dec19 good code
	data['NODES'] = dict()
	
        nodes = self.scene().nodes.keys()
	
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
            #utils._saveData(filePath, data=data)
	    utils._saveData(fqfn, data=data)
        except:
            print('Invalid path : {0}'.format(fqfn))
            print('Save aborted !')
            return False
        
        
        # Emit signal.
        self.signal_GraphSaved.emit()
        
    #09jan chg save to use fqfn not global filePath
    #05dec if filePath really is global, no need to pass it??
    #def loadGraph(self, xfilePath):
    #05dec remove file[path from calls, use globale filePath
    #09jan2022 chgd so a fsel appears before calling loadGraph
    #  the fsel stores fname slected into global filePath
    #09jan2022 add param for fqfn to be loaded, dont use global 'filePath'
    def loadGraph(self,fqfn):
        """
         Get all the stored info from the .json file at the given location
         and recreate the graph as saved.

         :type  filePath: str.
         :param filePath: The path where you want to load your graph from.
        """	
	#09jan2022 dont use global, use passed fname
        ##05dec use global  keyword with filePath
        #global filePath
        
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
	# it has NO sense of dir, other than an assumption of order = 1)plug 1)skt
	#
	#print(str(data))
	# any None pin will come from halcmd show sig>fname.signals
	#   NOT from a SaveMe file that has none or has existing entries removed
	# so the file suite here is nodz_demo/main/uti  is NOT hwre to look for None/none
	# is 'workingFile' what i want?
	
        self.clearGraph()
        
        # Apply nodes data.
        nodesData = data['NODES']
        #03dec2021  is nodesData available outside of this func? outside of this class?
        
        nodesName = nodesData.keys()
        	
        #26nov this vvv loop will go thru all nodes ( widgets/comps )
        for name in nodesName:
            preset = nodesData[name]['preset']
            position = nodesData[name]['position']
            position = QtCore.QPointF(position[0], position[1])
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
        
        # 12nov this vvv is a spcl method for scene(s)  (Not a dict update )
        self.scene().update()

        #05dec the dbug print of filePath is ok in this func loadGraph at top and at bot
        #05dec filePath is a unique name so it will have to be the passed val bfilePath
    
        # Emit signal.
        self.signal_GraphLoaded.emit()
        
    def createConnection(self, sourceNode, sourceAttr, targetNode, targetAttr, netname, cnxnSide):
        #14dec2021 this method has no mention of mouse clk posn
        # so it is NOT the code used to drag a new bez from plug to skt
        
        plug = self.scene().nodes[sourceNode].plugs[sourceAttr]
	"""
	strg1="...targetNode is "
	strg2=str(targetNode)
	strg3=strg1+strg2
	print(strg3)
	
	strg1="...targetAttr is "
	strg2=str(targetAttr)
	strg3=strg1+strg2
	print(strg3)
	"""
	# vvv KeyError: 'gv2offset13-0.0'
	#  that node doesnt exist yet ( my swag why it fails )
	# no  chging SaveMe gv2offset13.0.0.ena
	#                to gv2offset13.0.0-ena 
	#  ( all others in hat node used - inside pin name)
	# ^^^ stopped the error
	# yeah it stopped the error
	#  but why no error before? did i suddenlu chg a - to a . recently
	# and
	# why cant i have a dor in the attribute name?
	# tests say i can
	# BUT it chgs where the string gets broken!
	# the complaint was KeyError: 'gv2offset13-0.0'
	# which made node name gv2offset13-0.0
	#        and pin  name ena
	# vs
	#            node name gv2offset13-0
	#            pin  name 0.ena
	#
	#the strg given to the code is "gv2offset13-0.0.ena"
	# i prev used split which yields node gv2offset13-0  pin 0.ena
	# and i now use rplit which gives node gv2offset13.0  pin ena
	#which is better?
	# nodename with sequence or axis tag?
	#   gv2offset13-0.0  parport.0  or2.0  axis.z
	#   ena              pin-01-in  in0    enable
	# or node name w/o
	#   gv2offset13-0   parport     or2    axis
	#   0.ena           0.pin-01-in 0.in0  z.enable
	# to my eye , keep the ndx/tag with the nodename
	#is that what i have here on nodz_demo suite?
	#  yes node is gv2offset13-0.0   pins have no 0. prefix
	#is that what i have in test5.py ( halcmd show pin TO json)
	#  yes nodes can end in .LETTER or .DIGIT
	#   and no pins begin with LETTER.  nor DIGIT.
	#this code body does noy use split()
	# this code body DOES use rsplit()

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

#17dec trying to get a popup wndo
class MyPopup(QWidget):
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
    #21nov TODO should this vvv be here?, all alonem in a bunch by itself?
    signal_NodeMoved = QtCore.Signal(str, object)

    def __init__(self, parent):
        """
         Initialize the class.
        """
        super(NodeScene, self).__init__(parent)

        # General.
        self.gridSize = parent.config['grid_size']

        # Nodes storage.
        self.nodes = dict()

    def dragEnterEvent(self, event):
        """
         Make the dragging of nodes into the scene possible.
        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dragMoveEvent(self, event):
        """
         Make the dragging of nodes into the scene possible.
        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dropEvent(self, event):
        """
         Create a node from the dropped item.
        """
        # Emit signal.
        self.signal_Dropped.emit(event.scenePos())

        event.accept()

    # class NodeScene drawBackground
    def drawBackground(self, painter, rect):
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
    #16dec2021 what kindf of obj is a nodeitem?
    
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

        # Reduce node height.
        if self.attrCount > 0:
            self.attrCount -= 1

        # Remove attribute from node.
        if name in self.attrs:
            self.attrs.remove(name)

        # 12nov this updates values for keys in the NODE dict
        self.update()

    def _remove(self):
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
        # is bounding Rect for Node not Slot!
        """
         The bounding rect based on the width and height variables.
        """
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
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)

        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self.name).width() + 14
        text_height = metrics.boundingRect(self.name).height() + 14
        margin = (text_width - self.baseWidth) * 0.5
        textRect = QtCore.QRect(-margin,
                                -text_height,
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

#04jan2022 i can l btn dbl clk on a node and get the ShowMe action
# chg to allow ctrl l dbl clk for editing node
# DONE 1st just print a msg saying event noticed
# Done next get node name so later editig possible
#next open an editor on the SaveMe/test2 file scrolled to the node to edit
#
#notes:
# if (event.button() == QtCore.Qt.LeftButton and
#      event.modifiers() == QtCore.Qt.NoModifier and
#      event.modifiers() == QtCore.Qt.AltModifier):
#      event.modifiers() == QtCore.Qt.ControlModifier):
#      event.modifiers() == QtCore.Qt.ShiftModifier):

# why was this called? who called it?
# can i qualify it with modifiers AFTER getting here 
#  or is the action already filtered and modifiers after not allowed/effective
#
    def mouseDoubleClickEvent(self, event):
	#04jan2022 this vv correctly sense the ctrl left dbl clk on a node
	# the return is used to stop further processing
	# i get 
	#  msgs 1  on_nodeDoubleClick(nodeName):
	#           ^^^ this from my code in here
	#       2  Ctl Mid Btn DblClk
	#           ^^^ this is from my code in here
        # and msg  ('node selected : ', [u'hal_manualtoolchange'])
        #           ^^^ this is from nodz_demo 
        #             	              on_nodeDoubleClick(nodeName):
	#

        #09jan2022 try usin 'workingFile' when editing nodes
        global workingFile
	
	#print(self.name)
	nodeClicked=self.name
	if event.button() == Qt.LeftButton and event.modifiers() & Qt.ControlModifier:
	    nodeclkd=self.name
            strg1=("ctrl left dbl click on node ")
	    strg2=nodeClicked;
	    strg3=strg1+strg2
	    print(strg3)
	    
            # dont do anything yet just see if it opens
            #09jan2022 i need to know where the file that drew the scene is
            #  just saying 'SaveMe' deosnt work now that files are in logical project folders
            # so try to make a 'lastGraphFileLoaded'	    
	    # is 'workingFile' what i want?
	    #YES   stop for tonoght HERE HERE HERE
	    #self.scene().views()[0].doEditSaveMe("SaveMe")
	    self.scene().views()[0].doEditSaveMe(workingFile)
	    
	    return
	
        """
         Emit a signal.
        """

	#03jan2022 this vvv should inherited all actions in orig event handler
	# i think ...  but i see no print in console, so its not treu !?!? :-/
        super(NodeItem, self).mouseDoubleClickEvent(event)
	
	#09jan2022 chg from global filePath to workingFile
	# BUT i dont see workingFile OR filePath used in this func
	#   mouseDoubleClickEvent. nope not used  so rem it out
        ##global filePath
	#global workingFile
        
	
        if(self.alternate != "" ):

            # TODO handle door and circuit/code/thing
            # what if door AND a circuit?
            # like on SaveMe , ArduinoSPindleControl
            #   has a door AND can have a circuit
            
            key1 = 'ENTER'
            key2 = 'EXIT'
            if((key1 in self.attrsData) or (key2 in self.attrsData)):
                #print(self.alternate)
                #17dec this vvv makes global happy
		#
		#09jan dont use global, use self.alternate
                #filePath = self.alternate
                #self.scene().views()[0].loadGraph()
		self.scene().views()[0].loadGraph(self.alternate)
            else:
                #17dec we know self.alternate != ""
                # and we already handled RNTER and EXIT
                # so must be thing/code/circuit
            
                # check for ShowMe
                key = 'ShowMe'
                if(key in self.attrsData):
                    if(self.attrsData['ShowMe']['dataType'] == "<type 'thing'>"):
                        #print('its a thing, need a jpg & viewer')
                        # 17dec TODO should pass the fname to doit()
                        # 18dec doit & MyPopup cane get img fname from self
                        picFile=self.alternate
                        self.scene().views()[0].doImg(picFile)
            
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'code'>"):
                        #print('its code, need a text viewer')
                        txtFile=self.alternate
                        self.scene().views()[0].doTxt(txtFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'circuit'>"):
                        #print('its a circuit , need a schematic viewer')
                        proFile=self.alternate
                        self.scene().views()[0].doSch(proFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'manpage'>"):
                        #print('its a manpage, need a man page viewer')
                        manKey=self.alternate
                        self.scene().views()[0].doMan(manKey)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'svg'>"):
                        #print('its an svg file, need an svg viewer')
                        svgFile=self.alternate
                        self.scene().views()[0].doSVG(svgFile)
                    elif(self.attrsData['ShowMe']['dataType'] == "<type 'url'>"):
                        #print('its an url, need a browser')
                        url=self.alternate
                        self.scene().views()[0].doUrl(url)
                else:
                    print('its a not thing,text.circuit , yet alternate is not empty, why am i here?')
        else:
	    # 08jan print(self.name)
            self.scene().parent().signal_NodeDoubleClicked.emit(self.name)

    def mouseMoveEvent(self, event):
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
        # this mouseRelaseEvent is for class NodeItem
        
        # Emit node moved signal.
        self.scene().signal_NodeMoved.emit(self.name, self.pos())
        
        super(NodeItem, self).mouseReleaseEvent(event)

    def hoverLeaveEvent(self, event):
        nodzInst = self.scene().views()[0]

        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)

        super(NodeItem, self).hoverLeaveEvent(event)

#13nov  a horz field in a widget is a 'slot'
#  and a slot can be a plug or a socket, (or both [untested]  or neither [ a param?] ) based on properties of the slot
class SlotItem(QtWidgets.QGraphicsItem):

    """
     The base class for graphics item representing attributes hook.
    """

    def __init__(self, parent, cnxnSide, attribute, netname, preset, index, dataType, maxConnections):
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
	#08jan hover show obj as node plug socket or signal
	#  hover never reports slot
        strg1="slot "
        strg2=self.attribute
        strg3=strg1+strg2
        self.setToolTip(strg3)

        #07jan connect CANT
	# TypeError: connect() takes exactly 3 arguments (2 given)
        # so strike it out
        #self.connect(self.handleSlotClick)    
	#07jan -- end new event handler for plugite,s


    #07jan useless becuz i cant connect it vvv so strijke it out
    #def handleSlotClick(self):
    #	print("handleSlotClick rescted")
	
    def accepts(self, slot_item):
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
        #17dec in slotItem method mousePress
        """
         class SocketItem  Start the connection process.
        """
	
	## 08jan vvv prints empty dict
	#print(event.button().__dict__)
	##08jan vvv useless, prints list of internal funcs, not poperties/attributes
	#print(dir(event.button()))
	
	#09jan NG show me that a mouse event occured
	# these 3 vvv DO work, i get the msg in console
	if (event.button() == QtCore.Qt.LeftButton):
	    print("top of slotitem mousepressevent  left btn pressed")
	
	if (event.button() == QtCore.Qt.MiddleButton):
	    print("top of slotitem mousepressevent  middle btn pressed")

	if (event.button() == QtCore.Qt.RightButton):
	    print("top of slotitem mousepressevent  right btn pressed")
	
	
	#08jan i dont see this printed on startup, i think useless
        if (event.button() == QtCore.Qt.LeftButton):
            if( not hasattr(self, 'netname') ):
		#08jan
		print("netname set to - char")
                self.netname = "-"
	    
	    #08jan make same
	    #08jan these vvv work, but i DEDUCE the skt/plug  from netname
	    #       i get the clk info from the SLOT
            if(self.netname == '-'):
                strg1="in SlotItem, left mousePress on skt"
                print(strg1)
            else:
                strg1="in SlotItem, left mousePress on plug"
                print(strg1)
            
            if ( self.netname != '-' ):
		#08jan  this is class SlotItem func mousePressEvent
		# is this where drag bez begins? YES
                self.newConnection = ConnectionItem(self.center(), self.mapToScene(event.pos()), self, None, self.netname, self.cnxnSide )
                
                self.connections.append(self.newConnection)
                self.scene().addItem(self.newConnection)
                nodzInst = self.scene().views()[0]
                nodzInst.drawingConnection = True
                nodzInst.sourceSlot = self
                nodzInst.currentDataType = self.dataType
            
            else:
		#08jan else pass the event along... to parent = Node?
		# need to study this signal slot stuff
                super(SlotItem, self).mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        #14dec class SlotItem method mouseMove
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
            # TODO fix 
            print("in mouseReleaseEvent in class SlotItem, mouse was released")
            
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
        #16dec class SlotItem method shape()
        #16dec this code is not called in this program 
        # BUT it IS called, must be that 'shape()' is some basic method
        # and the code here overloads it ( i guess)
        
        # 16dec WOH the shape of the slot is a circle!!!
        #DAMN thats why i get no response clicking in the horz rect
        # DONE i want the slot shape to be a rect!
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

        #17dec socket sensitive rects were too far left tiny amt
        #  tiny amt was 1/2 circle (old idea n longer used)
        #  old way... a circle was the slot, now is  a rect
        if(self.netname == "-"):
            xpos = xpos + 7
            #17dec vvv i made 100 and no diffm rt end seems shy of node border by ~7
            #TODO  test/see  why large value makes no diff
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
        #17dec the 'center' should be 'cnxnpoint'
        # and that will be left edge ctr or rt edge ctr
        # depending on cnxnSide
        # who calls this fx?
        #center = QtCore.QPointF(rect.x() + rect.width() * 0.5, rect.y() + rect.height() * 0.5)
        if(self.cnxnSide == "left"):
            center = QtCore.QPointF(rect.x(), rect.y() + rect.height() * 0.5)
        else:
            center = QtCore.QPointF(rect.x() + rect.width() , rect.y() + rect.height() * 0.5)

        return self.mapToScene(center)

class PlugItem(SlotItem):
    """
     A graphics item representing an attribute out hook.
    """
    def __init__(self, parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections):
        
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
        
        #19nov force the parent into the struct
        #27nov TODO  is this needed? used?
        socket_item.parent = socket_item.parentItem().name
        
        # Populate connection.
        connection.socketItem = socket_item
        
        connection.plugNode = self.parentItem().name
        
        connection.plugAttr = self.attribute
        
        # Add socket to connected slots.
        if socket_item in self.connected_slots:
            self.connected_slots.remove(socket_item)
        
        self.connected_slots.append(socket_item)
        
        # Add connection.
        #20nov this vvv looks like it ensures no duplicate cnxns 
        #  ( like on top of itselfm which you woukd not see )
        if connection not in self.connections:
            self.connections.append(connection)
        
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)
        
    def disconnect(self, connection):
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
	
    #08jan  func not in older code vvv
    # 08 THIS was cause of loss of ability to drag bez from plug to slot
    #def mousePressEvent(self, event):
    #    #17dec in PlugItem method mousePress
    #    """
    #     class PlugItem
    #    """
    #
    #    #if (event.button() == QtCore.Qt.LeftButton):
    #	#    strg1="inPlugItem mousePressEvent modifiers ignored"
    #	#    print(strg1)    
    #
    #    if (event.button() == QtCore.Qt.LeftButton
    #          and event.modifiers() == QtCore.Qt.ShiftModifier):
    #	this does not agree with prev line     strg1="inPlugItem mousePressEvent NO modifiers"
    #	    print(strg1)    
    #	    
	
class SocketItem(SlotItem):
    """
     A graphics item representing an attribute in hook.
    """
    
    def __init__(self, parent, cnxnSide, attribute, netname, index, preset, dataType, maxConnections):

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

        #ok 07jan 2022 plugitem doesnt have these 3 lines
        self.cnxnSide=cnxnSide
        self.parent=parent
        self.index= index

        #fixed 17dec2021 i never stored netname,cnxnSide,parent, index
        self.netname=netname

        #ok 07jan2022 the order of methods and netname reversed from plugitem code        
        # Methods.
        self._createStyle(parent)

        
        #14dec2021 add tooltip for skt
	#06jan 
	# note the kbd modifiers can be accessed during hover
	#PySide2.QtGui.QHoverEvent(type, pos, oldPos[, modifiers=Qt.NoModifier])
	
        strg1="socket "
        strg2=self.attribute
        strg3=strg1+strg2
        self.setToolTip(strg3)

    def _createStyle(self, parent):
        """
         Read the attribute style from the configuration file.
        """
        config = parent.scene().views()[0].config
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(utils._convertDataToColor(config[self.preset]['socket']))

    def boundingRect(self):
        """
         The bounding rect based on the width and height variables.
        """
        
        #width = height = self.parentItem().attrHeight / 2.0
        #17dec text runs outside of gui box, and theres space between gui boxes
        # still outside, its the text baseline thats ng
        #height = self.parentItem().attrHeight / 2.0
        height = self.parentItem().attrHeight -4
        
        #17dec FIXED sensitive area is shy of rt edge of node by ~7
        width  = self.parentItem().baseWidth + 7

        nodzInst = self.scene().views()[0]
        config = nodzInst.config

        #17dec SIMPLIFIED all gui rect slots begin  x -7
        x = -7

        y = (self.parentItem().baseHeight - config['node_radius'] +
            (self.parentItem().attrHeight/4) +
             self.parentItem().attrs.index(self.attribute) * self.parentItem().attrHeight )

        rect = QtCore.QRectF(QtCore.QRect(x, y, width, height))
        return rect

    def connect(self, plug_item, connection):
        #14dec2021 class SktItem method connect
        # this cnx a skt to a plug
        # i dont hink i want this, 
        # i want digraph and direction is plug to skt
        # never skt to plug
        """
         Connect to the given plug item.
         20nov this was neutered by add a=1 and remming rest, that action screwed save, so undo
        """
        #14dec i dont see this vvv printed when i clk on a dot
        # i never see this printed after load ( lots during loadgraph)
        #print("in class SocketItem method connect")
        numcnxns = len(self.connections)
        
        #21nov i dont think the orig logic is right\
        """
            if self.maxConnections>0 and len(self.connected_slots) >= self.maxConnections:
                # Already connected.
                self.connections[self.maxConnections-1]._remove()
        """
        
        #21nov  new wrapper if  'for create new cnxn'
        #21nov well this dis-allowed a new cnxn in db, but does not prevent bez on screen
        #  so the draw code should not be called
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
        """
         Disconnect the given connection from this socket item.
        """
        
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_SocketDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected plugs
        if connection.plugItem in self.connected_slots:
            self.connected_slots.remove(connection.plugItem)
        # Remove connections
        self.connections.remove(connection)
           
class ConnectionItem(QtWidgets.QGraphicsPathItem):
    """
     A graphics path representing a connection between two attributes.
    """
    #22nov add dtPosn passed to ConnectionItem  init    #22nov need source cnxnSide  target cnxnSide, dunno who is plug who is skt,,, ? yes??
    #  well source is ALWAYS plug for me in my app, 
    #
    
    def __init__(self, source_point, target_point, source, target, netname, cnxnSide ):
        
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
        
        #14dec2021 have cnxnItem accept hover events
        # vvv not necc if tooltips used vvv see below
        #self.setAcceptHoverEvents(True)
        
        #14dec2021 try to make tooltip for cnxnItrm
        #cool that works ( its a bit slow to appear )
        #14dec2021 i think i could have a dict for tooltips
        #   key=netname  value="somemere detailed desc of netname"
        #   maybe the desc is in the node structure, the json
        #   maybe in json seperate from NODES and CONNECTIONS, 
        #     maybe a new list/dict  SIGNAL_DESC
        strg1="signal "
        strg2=self.netname
        strg3=strg1+strg2
        self.setToolTip(strg3)
        
        
    def _createStyle(self):
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
        #14dec class CnxnItem method mousePress
        """
         Snap the Connection to the mouse.
         
         TJP what doe sthis func do?
         what is source and target
        """
        # 13nov this looks like a handy universal way to get verything available to a func
        nodzInst = self.scene().views()[0]
        
        # 13nov a high Z value is 'on top' and therefore visible
        #21nov maybe useful to highlight a net later
        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)
        
        nodzInst.drawingConnection = True
        
        if(hasattr(self.target,'disconnect')):
            
            # 13nov code here vvv is exec'd WHILE dragging the new bez cnxn
            d_to_target = (event.pos() - self.target_point).manhattanLength()
            d_to_source = (event.pos() - self.source_point).manhattanLength()
            
            if d_to_target < d_to_source:
            
                self.target_point = event.pos()
                self.movable_point = 'target_point'
                self.target.disconnect(self)
                self.target = None
                nodzInst.sourceSlot = self.source
            else:
                self.source_point = event.pos()
                self.movable_point = 'source_point'
                self.source.disconnect(self)
                
                self.source = None
                nodzInst.sourceSlot = self.target
                
        self.updatePath()
            
    def mouseMoveEvent(self, event):
      #15dec class CnxnItem method mouseMoveEvent
      """
       Move the Connection with the mouse.
      """
      if (event.button() == QtCore.Qt.RightButton):	
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
        """
         Create a Connection if possible, otherwise delete it.
        """	
        #21nov this mouseReleaseEvenet is for class CnxnItem
        nodzInst = self.scene().views()[0]
        nodzInst.drawingConnection = False

        slot = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

        if not isinstance(slot, SlotItem):
            self._remove()
            self.updatePath()
            super(ConnectionItem, self).mouseReleaseEvent(event)
            return

        if self.movable_point == 'target_point':
            
            #21nov accepts()  can reject the cnxn if numcnxnx=s > maxConnections
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
        if self.source is not None:
            self.source.disconnect(self)
        if self.target is not None:
            self.target.disconnect(self)

        scene = self.scene()
        scene.removeItem(self)
        #12nov scene.update() is NOT a dict update
        scene.update()

    def updatePath(self):	
        """
            Update the path.
        """
        
        #22nov this class is ConnectionItem  so self is a ConnectionItem, wit cnxnSide and netname
        
        #25nov a ConnectionItem is a list pair in SaveMe 
        #  the pair has a sourceNode sourceAttr   which is a Node with a Plug
        #           and a targetNode targetAttr   which is a Node with a Socket
        
        #12nov the bez text is fuzzy
        #   tried some web ideas to make netname more legible---none worked
        self.setPen(self._pen)
        
        path = QtGui.QPainterPath()
        path.moveTo(self.source_point)
        
                
        if( isinstance(self.source , PlugItem)):
            
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
            
            #22nov i dont see Y getting probs when dy = 0
            # (maybe later)
            dy = self.target_point.y() - self.source_point.y()
            ctrl1 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 0)
            ctrl2 = QtCore.QPointF(self.source_point.x() + dx, self.source_point.y() + dy * 1)
            path.cubicTo(ctrl1, ctrl2, self.target_point)

            #25nov make text on bezier left justified on cnxnSide == 'right'
            #           an  right justified on cnxnSide == left
            if(self.source.cnxnSide == "right"):
                percent = 0.2
            else:
                percent = 0.35
            txtloc = path.pointAtPercent(percent)
            
            path.addText(txtloc,QtGui.QFont('monospace',10), self.netname)
        
            self.setPath(path)
