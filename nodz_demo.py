#30jan all files cleaned up ( old/bad comments removed)
#  TODO logic cleanup
#  TODO add save & load views
#       L S are load save scene
#       l s are load save view ( a list of nodes to zoom to )
#30jan t get new json graph load to fill viewport...
# load  fname
# select all
# focus
# zooms and ctrs any graph
# DONE
# i didnt have to calc bounds , there's a cmd that does that
#   itemsArea = self.scene().itemsBoundingRect()        
#   self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)
# this rect is used instead of the default width height from defau;t_config.json
#
#29jan  FIXED (workaround) 
# after save, the nets are not cnxd to nodes
#  a tiny drag/move of a node will recnx all
#  maybe do a ??? after a save?
#  hack/ workaround
#     after   self.saveGraph(workingFile)
#     exec    self.loadGraph(workingFile)
# works, but is hack
# TODO remove hack, make err happen, untill i understand WHAT is not happening
# DONE stripping the code out of loadGraph and making it a func is more troble than its worth
#  just use loadGraph as is   to fix torn off nets
#
#28jan DONE & WORKS begin convert to python 3
#  22:29  runs with  python3 nodzdemo.py
#  just indents checked, no print errs seen
#
#24jan2022 22:37 V(iew) from a list of node names works ok
# TODO save the list   i am thinking L S are scene Load Save
# TODO load the list   and l s are list load save ( views)
#
# see this SO answer for using json in and out
#  https://stackoverflow.com/questions/27745500/how-to-save-a-list-to-a-file-and-read-it-as-a-list-type
#
#24jan2022 hypermedia
#  i can still get editor w ^shift left clk on node
#  phew! ability still there, i hadnet edited in the hypermedia infos  for fname and datattype
#  NB to get hypermedia  just dbl clk on ShowMe
#  NB to get editor  use ^ShiftLeftClick on node ( use the yellow bar else you clkd on a slot not node )
#
#24jan2022
# YAY now using RTPRESS will del net so normal dragging zoomed out is ok
# normal LFPRESS will NOT del nets
# chg made in class ConnectionItem func mouseReleaseEvent
# ...
#       #24jan make action conditional with button() == 2 (rt btn)
#	if(event.button() == QtCore.Qt.RightButton):
#...
#
#  TODO CLEANUP
#
#20jan 2300  
# idea: the views... 
#  if i had a list of the components in the view
#  and the unzoomed layout was 'pleasant'
# then i select the nodes in the list
#   and do a F(ocus) command


#14jan orig import from Qt , i use from PyQt5
from PyQt5 import QtCore, QtWidgets
import nodz_main

try:
    app = QtWidgets.QApplication([])
except:
    # authors note:  I guess we're running somewhere that already has a QApp created
    app = None

nodz = nodz_main.Nodz(None)
nodz.initialize()
nodz.show()

# 06nov2021  heavy handed global aliasing  found on web as 'cure' for pyqt5
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtCore.Property = QtCore.pyqtProperty

######################################################################
# Test signals
######################################################################
#-------------15jan begin restore slots for nodes
#15jan chg all slot prints to identify better what did the print
@QtCore.Slot(str)
def on_nodeCreated(nodeName):
    #24jan reduce clutter
    a=1
    #print('slot on_nodeCreated : ', nodeName)

@QtCore.Slot(str)
def on_nodeDeleted(nodeName):
    print('slot on_nodeDeleted : ', nodeName)

@QtCore.Slot(str, str)
def on_nodeEdited(nodeName, newName):
    print('slot on_nodeEdited : {0}, new name : {1}'.format(nodeName, newName))

@QtCore.Slot(str)
def on_nodeSelected(nodesName):
    a=1
    # 22jan2022 dummied up to reduce visual clutter
    #print('slot on_nodeSelected : ', nodesName)

@QtCore.Slot(str, object)
def on_nodeMoved(nodeName, nodePos):
    print('slot on_nodeMoved  {0} moved to {1}'.format(nodeName, nodePos))

@QtCore.Slot(str)
def on_nodeDoubleClick(nodeName):
    print('slot on_nodeDoubleClick on node : {0}'.format(nodeName))
#-------------15jan end restore slots for nodes

#-------------15jan beg restore slots for attrs ( all were missing)
# Attrs
@QtCore.Slot(str, int)
def on_attrCreated(nodeName, attrId):
    #22jan2022 reduce clutter
    a=1
    #print('slot on_attrCreated : {0} at index : {1}'.format(nodeName, attrId))

@QtCore.Slot(str, int)
def on_attrDeleted(nodeName, attrId):
    print('slot on_attrDeleted : {0} at old index : {1}'.format(nodeName, attrId))

@QtCore.Slot(str, int, int)
def on_attrEdited(nodeName, oldId, newId):
    print('slot on_attrEdited : {0} at old index : {1}, new index : {2}'.format(nodeName, oldId, newId))
    
#-------------15jan end restore slots for attrs

#-------------15jan beg restore slots for cnxns
@QtCore.Slot(str, str, str, str)
def on_connected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
    #22jan2022 reduce clutter
    a=1
    #print('slot on_connected src: "{0}" at "{1}" to dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))

@QtCore.Slot(str, str, str, str)
def on_disconnected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
    print('slot on_disconnected src: "{0}" at "{1}" from dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))
#-------------15jan beg restore slots for cnxns

#-------------15jan beg restore slots for graph
# Graph
@QtCore.Slot()
def on_graphSaved():
    print('slot on_graphSaved !')

@QtCore.Slot()
def on_graphLoaded():
    print('slot on_graphLoaded !')

@QtCore.Slot()
def on_graphCleared():
    print('slot on_graphCleared !')

@QtCore.Slot()
def on_graphEvaluated():
    print('slot on_graphEvaluated !')
    
#-------------15jan end restore slots for graph

#-------------15jan end restore slots for other
# Other
@QtCore.Slot(object)
def on_keyPressed(key):
    print('slot on_keyPressed : ', key)
    
#-------------15jan end restore slots for other


#04jan2022 these vvv connect SIGNAL to SLOT ( SLOTS ar ethe @Qtblah things above)
#14jan restore all old .connect s----------------------beg
nodz.signal_NodeCreated.connect(on_nodeCreated)
nodz.signal_NodeDeleted.connect(on_nodeDeleted)
nodz.signal_NodeEdited.connect(on_nodeEdited)
nodz.signal_NodeSelected.connect(on_nodeSelected)
nodz.signal_NodeMoved.connect(on_nodeMoved)
nodz.signal_NodeDoubleClicked.connect(on_nodeDoubleClick)

nodz.signal_AttrCreated.connect(on_attrCreated)
nodz.signal_AttrDeleted.connect(on_attrDeleted)
nodz.signal_AttrEdited.connect(on_attrEdited)

nodz.signal_PlugConnected.connect(on_connected)
nodz.signal_SocketConnected.connect(on_connected)
nodz.signal_PlugDisconnected.connect(on_disconnected)
nodz.signal_SocketDisconnected.connect(on_disconnected)

nodz.signal_GraphSaved.connect(on_graphSaved)
nodz.signal_GraphLoaded.connect(on_graphLoaded)
nodz.signal_GraphCleared.connect(on_graphCleared)
nodz.signal_GraphEvaluated.connect(on_graphEvaluated)

nodz.signal_KeyPressed.connect(on_keyPressed)
#14jan restore all old .connect s----------------------end

######################################################################
# Test API
######################################################################
#21nov   all the info needed to construct the scene is in the SaveMe json file

# Graph

nodz.clearGraph()

if app:
    # command line stand alone test... run our own event loop
    app.exec_()
