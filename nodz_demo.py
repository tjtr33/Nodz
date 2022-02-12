#12feb2022 this file is clean
#11feb added cmd M/m for menu
# DONE re: menu   use a text file brought up by m or M keys
#
#11feb DONE hints for cnxn source candidate
#   a valid src will have hint > or < depending on cnxnside
#11feb DONE deselected all nodes after 'l' load view
#11feb DONE in doEditSaveMe() there is a personal choice of editor 'scite'
#      so, added a line in default_config.json'
#      now user can specify his favorite text editor
# 
#11feb TODO outside of this app, 
#  the hal-edm suite uses M198 for
#    how long arcing is allowed.
#    and how long sparkout takes
#  these use counts ( likely thread periods)
#  the unit of measure shout be decimal seconds ( allowing mS maybe uS )
#
#10feb2022 
# TODO add file name 'L'oaded to title bar

# TODO  the 'calcscale()' code is repeated 2x
#  it can become a func

# TODO 10feb2022  the code for 'C'onvert is too large, 
#   should be factored

# TODO can s/S be used for either save graph or view
# simply let user decide extant
# and process accoring to extent (.graph vs .view possibly)

#TODO why am i using loadGraph() in the save func?
        
#TODO is _getSelectionBoundingbox used? 
#  can this func replace redundant code?	    
#  look for duplicated code in saveGraph(
#  and in saveGraph

# TODO in saveGraph
# i moved the node name inside the noderect
#  is this 12 necc? (looks suspiciously like text ht )

# TODO allow for 'io' pins

# TODO svg output of whole scene, 
#   may be useful w/o needing this app, just for viewing

# TODO moving slot up/down via index not implemented
#   in loadGraph()

# TODO in loadGraph  set some visual hint about data type

# TODO in NodeScene
# should this vvv be here?, all alone, in a bunch by itself?
#    signal_NodeMoved = QtCore.Signal(str, object)

# TODO in _createStyle   is nodeCenter() useful?

# TODO in connect() is socket_item.parent used?

# TODO in connect() is this used? correct thinking?

# TODO make dlogs to aid in editing  SwapDotSide, restack slots
#   add alternate fqfn and media type

#TODO in createNode
#instead of fudging the posn
#  maybe the test 'if not position' is wrong
#  maybe if is none ??

#07feb re making a gui for creating hal files...
#  i CAN script creating new nodes ( from show sig or even man/code )
# but not all, and many unwieldly large (eg motion)
#  using idea of load indiv comp  (this breaks the idea, can load mesa7ixx bitfile xxxx unless you have the hdwr)
#         then save show sig
#         then process show sig to create a grfx node fo Nodz
# which leaves, dig thru docs to build
#   which breaks again on sheer number of permutations
#     given bitfiles and personalities
#  and local non published Mcodes, .py files bash scripts etc that can sets or setp
# conclusion: same as last umpteen attempts at gui designing of hal files:
#  impractical, near impossible ( could you make a widget my my fred.comp?)
#   answer , no you cant, you have to give us a universal decoder
# end result: a display aid is useful and is done here in Nodz4hal

#10feb2022 vvv maybe useful to get rect size exact
#  right now i use a fixed number for node height when setting rect
#  the rect is really the origins of the node,
#  so it does not include the region of the lowest node,
#  only indicating the top left of lowest node
#  IF the lowest node was found ( during the discovery of teh rect x y w h)
#   then finding the actual height of this lowest node
#   will allow calcing the actual rect height
#
#  found how to get node height
#              self.myscene.items()[i].boundingRect().height()
#

# TODO the default_config.json still has width & height
# is this used? is it a problem? can it be removed?

# DONE open hypermedia files readonly
#   no, i made the files readonly instead of opening ro
# except for menu.ts, leave that for user to annotate as he likes

# see this SO answer for using json in and out
#  https://stackoverflow.com/questions/27745500/how-to-save-a-list-to-a-file-and-read-it-as-a-list-type


#-------------------end top comments -------------------------#

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
    #24jan reduce clutter
    a=1
    #print('slot on_nodeSelected : ', nodesName)

@QtCore.Slot(str, object)
def on_nodeMoved(nodeName, nodePos):
    print('slot on_nodeMoved  {0} moved to {1}'.format(nodeName, nodePos))

@QtCore.Slot(str)
def on_nodeDoubleClick(nodeName):
    print('slot on_nodeDoubleClick on node : {0}'.format(nodeName))

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
    
@QtCore.Slot(str, str, str, str)
def on_connected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
    #22jan2022 reduce clutter
    a=1
    #print('slot on_connected src: "{0}" at "{1}" to dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))

@QtCore.Slot(str, str, str, str)
def on_disconnected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
    print('slot on_disconnected src: "{0}" at "{1}" from dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))

# Graph
@QtCore.Slot()
def on_graphSaved():
    print('slot on_graphSaved !')

@QtCore.Slot()
def on_graphLoaded():
    #10feb2022 remove clutter
    a=1
    #print('slot on_graphLoaded !')

@QtCore.Slot()
def on_graphCleared():
    #10feb2022 remove clutter
    a=1
    #print('slot on_graphCleared !')

@QtCore.Slot()
def on_graphEvaluated():
    print('slot on_graphEvaluated !')
    
# Other
@QtCore.Slot(object)
def on_keyPressed(key):
    #24jan reduce clutter
    a=1
    #print('slot on_keyPressed : ', key)
    


#04jan2022 these vvv connect SIGNAL to SLOT ( SLOTS ar ethe @Qtblah things above)
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

######################################################################
# Test API
######################################################################
#21nov   all the info needed to construct the scene is in the SaveMe json file

# Graph
nodz.clearGraph()

if app:
    # command line stand alone test... run our own event loop
    app.exec_()
