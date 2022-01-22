#22jan2022 1537 stop on the L S rect stuff
# go work on Convert halcmdshowpon  to json
#
#22jan cntd look at why F doesnt fit selected nodes into a window that 'just' envelopes those nodes
# 1) the action of manually selecting (^shiftMetaLeftPress in space)
#  all then F(ocus) does NOT work always
# 2) the action od deselectall ( l clk in space )
#  then F does NOT work ( code sez if none selected then select all then Focus)
#am i printing the rect of slected or the rect the nodes will be placed into?
#slot on_nodeSelected 
# a new run, load, then F   is FIT and topleft test rect dragged shows ~0 ~-150
#   NOT on all saved scenes!  usually not :-(
#
# beware QrectF is x,y,width,height  NOLT x1,y1,x2,y2
#  this can be seen with any tiny rect, last 2 nums are tiny, 1st 2 depend on loc
#
# the initial load goes into world defined by cfg file ( 0,0,3800,2000 )
# so any element in neg space ( neg X for xmpl ) are not seen ( they are off-screen )
# i think author never expected ned positions
# --- if some nodes are neg x, then lasso all, then F, then some nodes ar eoff screen 
#  --   i must drag whole scene so no nodes are neg
#  --   AND all must fit inside cfg files width/height
# --- manual sel all F is better than auto sel all F
#
# i think a good idea to justify all ( move to positive x and y )
#   i had a file x.json where all were pos, but min was > 1000
#   so i made y.json subrtacting 1000 from evert x position
#    with y.json ... L then F worked 
#    ( had extra space on rt  becuz cfg had 5700 width
#      max x posn was 4381... so 4381+200widgetwidth+100bendybezier=4681
#      so try 4681 in cfg file
#      yes that workls but very much mashed up onto left edge
# Can i begin by making all pos?
#  key P positive... using ... file or dict?
# 
# i think a good idea to save width height in json file NOT in cfg file
#
#21jan 
# re:  the saved view is not what was active when Save issued
#  it is at least left shifted
#
#i need to look at the rect used 'itemsarea'
# i think i need to see the x y posn
# so i can compare 'items area to what i see on screen
# myabe begin with top left  of itemmarea and 
# be able to meta rt clk get xy posn of mouse
#
# if i carefully adjust whole graph so it saves and loads (with sleAll Focus)
#  then i see the rect is...  near 400 right shifted of 0
#  while leftmost node is at left edge ( where i thought 0 would be )
#  bit where i expect 0 is really 371!
#  NB: i also have cfg.jso chgd to width4000 ( was 2000)
#  hmmm retired at width2000 and scene was WAY right shifted  huge blank area to left
#('itemsArea is ', PyQt5.QtCore.QRectF(371.0, 308.0, 3594.0, 1254.0))
#
# at width 4000 or gretaer (tested up to 5000) the leftmst node is left edge
#  AND rightmodt is right edge, so > 4000 not usedfull
#  and <4000 moves all nodes towards right, leaving empty space on left
#
# why 4000?   becuz actual itemArea is ~3600 plus inherent 400 error?
#  so its some way other value for other graphs?
#
# theres something with visible...
# if some nodes off screen, and i select all and focus
#   then all is not seen
# if all is visible on screen, say really small up and left on screen
#   then slecte all, focus  will zoom to all
#
#if i am close to ctr and zoomed WAY in,
# (like zoomed in till theres only grey space on screen )
# then ^shiftMetaLeftClkInSpace selectall, Focus works
#
# if not on screne ctr, but on some node ctr zoomed way in ( but can clk on space)
# then selectAll Focus 'works', the zoomed view is ALL but ctrd on clk spot
#  not all nodes are seen
#20jan 2300  
# idea: the views... 
#  if i had a list of the components in the view
#  and the unzoomed layout was 'pleasant'
# then i select the nodes in the list
#   and do a F(ocus) command
# well its a good idea, but Focus deosnt work well
#  same general problem as zoom and pan
#
#15jan 10am i saw that ctrl shift l press on node ( near ShowMe)
# was no reliable in getting scite o open SaveMe file from startup
# now Noon it seems to always work !?!?
#
#14jan almost done restoring and cleaning
#  after that get the editing func back ?? ctrl l dblclk on node??
#14jan reduce comments, try to better understand signals and slots
# 14jan i restored all orig slots and .connects
#       in case i trampled on something handy
#
#14jan ctrl shift l clk on a node 
#  will toggle teh node's select state
#  not clean! sometime takes 2 ctl shift l clk before node outline goes orange
#  also the node will become sel'd but wont de-sel w further ctl shift l press-es
#   ( node toggles on but wont not off )
#
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
    print('slot on_nodeCreated : ', nodeName)

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
