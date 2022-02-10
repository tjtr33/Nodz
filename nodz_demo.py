#10feb is all working? time for menu?
# cleanup.. 1) rem dbug prints
#10feb setting scrollbars and scale does not work with resized windoq
# but lasoo are then F works
# drag scene works too
# try 
#  clear all selected nodes
#  set selected on nodes from vie file
#  call _focus
# result: perfecto! no minx maxx miny maxy width height needed
#  no set rect needed, very simple & clean :-) :-) :-)
#  works at diff screen and window sizes
#
#09feb made some hardcoded 'views' with 3 data
# the veryscroolabr val the hporsscrollbar val the zoom
# works pretty well
# i think i need to disable any mouse msgs/influences during this
# i see that the rsult can be drawn 'tors' the cursor
#
#09feb fixed bad xmin ymin xmax ymax width height calcs
#  
#08feb new idea
# use scroll bars to locate a view
# use scale to fit the view into the viewport
# so far i find that setting the horz and vert scrollbars will work r& reliably
# but the scale is ... well the scale seems hard to get at
# i read you can calc it from the viewrect w&h in view coords vs scene coords
#  i have not gotten those 2 data yet
#
#07feb2022 back to work
#  zoom and pan are ok ,
#   they work with whole 'L'oaded graphs, and with 'F'ocus views of lassoo'ed areas
#   they DO NOT work after scenerect chgd
#   i need a way to 'l'oad a view w/o using setscenerect
#
#07feb cant script create indiv nodes
#  using idea of load indiv comp  (this breaks the idea, can load mesa7ixx bitfile xxxx unless you have the hdwr)
#         then save show sig
#         then process show sig
# which leaves dig thru docs to build
#   which breaks again on sheer number of permutations
#     given bitfiles and personalities
#  and local non published Mcodes, .py files bash scripts etc that can sets or setp
# conclusion: same as last umpteen attempts at gui designing of hal files:
#  impractical, near impossible ( could you make a widget my my fred.comp?)
#   answer , no you cant, you have to give us a universal decoder
# end result: a display aid is useful and is done here in Nodz4hal
#
#07feb add scripts to create indiv nodes
#  make alist of comps avail to linuxcnc
#  run lcnc in rip  (necc?  no !)
#  open another terminal
#  for thing in list:
#    halcmd loadNNN thing ( how to tell user.rt? up to list! 1 list user 1 list rt)
#    halcmd show sig > thing.signals
#    halcmd unloadNNN     (how t tell if user/rt? up to list! 1 list user 1 list rt)
#    halrun -U
#  ( ^^^ just off top of head )
#ok collect rt list 
#
#06feb studyinf scene and view
#  found how to get node height
#              self.myscene.items()[i].boundingRect().height()
#
#05feb2022 try to understand qgraphicsscene qgraphicsview
# the view is the knothole we look thru at the scene
# the scene is big 
# the view is UPTO as big as the scene or so smallwe dont see anything
#
#05feb2022 lets try loadinga single node and see if it repeats
#  the vismach files are single node
#  yes it repeats  it being 5axisgui.json
#  and asfaras pan goes... 
#  it allows little move of view left or down 
#  becuz it is at top left  posn 500,500, try 10,10 to check yes at 10,10, its fully Y on top left but 1/2 on screen in X
#  so borders hit soon to left and up, but loads to rigth and down
#  why left 1/2 off screen when 10,10?
#
#05feb2022 the 'l'oad views dont pan well
#  most only pan u/d.
#  all have limited motion ( some none )
#
#05feb2022 now i calc the scene rect on 'L'oad ( inside loadGraph() )
#  i rtn the w,h to caller
#  'L'oad seems ok  not perfect
#  lasoo and Focus ng
#  i do _focus wdth hght diff from other funcs()  ng
#   fixed, same calcs for all
#
#05feb2022 mouse pan not right
#  mouse pan is  alt-midl-drag
#  it chgs to black hand cursor on press and back to arrow on release
# BUT the range of drag varies, meaning how far you can drag, that chgs
# case: just L(oaded) and zoomed in so whole graph is no longer vsisble...
#       resultz; can pan to top and to left and to right (seems a lot further than just the rect containg items), and down ( is further than rect containing items
#          so i think i can pan within rect of defaulkt_config wdth hght
# was     "scene_width": 4681,
#        "scene_height": 2000,
# try    "scene_width": 3500,
#       "scene_height": 1500,
# yes the pan range is definitely the deault_cfg wdth hght
# and any static value is not correct
# the values have to be calc'd on load
# consider he values in defualt_cfg to be dummy, temporary expendable values
#
#04feb2022 mouse pan works,,, some
# what i did  3 stansaz weere copied from orig code
#  all for  state == DRAG VIEW
#   in mousePress, mouseMove and mouse Release
# problem
#  if a smallish area is focused, then alt midl drag will pan arround inside viewport
#  BUT a loaded view has limited motion, eg spindle.json
# NB: arow keys can pan also udlr (except on loaded view , a focused view is ok)
#
# DONE chg 'l'oad view so after load, the nodes were DEselected
#  this was minor annoyance requiring hammerin l btn in space to shake off the previous selection
#
# DONE open hypermedia files readonly
#   no, i made the files readonly instead of opening ro
#
#03feb2022 wheel zoom and scroll bars work some
#  the defualt cursor is mickeymouse hand and drag sel rect is crazy
#  i need to test ability to do things i could do yesterday
# g'nite 23:23
# 555 23:54
# orig code has fix for drag view   key word for search  drag_view
#
# begin by remming 2 (newish) lines that chgd cursor
# at bot of class Nodz __init__()
#       self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
#       self.viewport().setCursor(Qt.ArrowCursor)
#now have no drag view 

#04feb2022 TODO minor annoyance  when view loaded all are slected, not expected, so desel all
#
#03feb2022 worked on views 'l'oad view  and 's'ave view
# the load worked ok but in corner cases trimmed right side too much
# it happens when the area calculation ignores any loop back nets
#  on rightmost nodes. Whne these occured the view simply butted the
#  node against the right edge of window and thus hid those cnxns
# this happens with the tools of qt
# one tool crawls thru all the items (including the nets) to build
#  the 'selectedArea'. This is a qt func  itemsBoundingRect()
# another tool is code i wrote to calc the x,y,wdth,hght of the
#  selected nodes, using node names from a list ( the view type json file )
#  this method find rect of top left corner of nodes
#  so will ignore node width nodeheight and any nets to right of node
#  to accomodate, i knew all nodes were 200 wide, so i add 200 to the
#  rect's width. then i add 20 to accomodate right side nets
#  This additional width is ignored by qt when i create a painterpath
#    name 'pp' using x,y,wdth,hght 
#    then call self.scene().setSelectionArea(pp), 
#    then call self._focus()
#  so i use a belt and suspenders
# i use self.setSceneRect(minx, miny, wdth, hght)
# then self.scene().setSelectionArea(pp)
# then self._focus()
#
# this seems to work, needs more testing
# i'd like it simpler ( i'd like to setSelected  but that isnt in qt!!
#  try   selectionModel = self.selectionModel()
#
#02feb TODO add file name 'L'oaded to title bar
#           study code found  for scroll wheel zoom, and arrow key pan lrud
#
#02feb  some views are not ctrd
# this is a qt bug
# if the aspect ration of the focussed items (say 1:5) is 
#  "less" than the viewport (say 540x480 so 4:3)
# then the renedred view is not ctrd
# as the viewport window is resized vertically, 
# subsequent loads of same aspecr will grow more ctrd
# until the viewport windo is "greater" aspect than the AreaToFocus
# I cant fix this w/o resizing viewport tp selArea's aspect
#
# there may be more to this, the single node gv2offset13 saved as a view
# is tall and narrow, but renders ok
# well, it looks tall on screen but  rect is...
# 964.0449164520867  y  444.17146854625616  wide  220.0  high  200.0
#  !only 200 tall cuz i just swag the hght
# so try making rect say, 200, ng 
#
# for one case, i see selarea is ~227  wery narrow
# and if that is ctrd, then theres neg coords inside viewport to left
# so, how big is viewport?
# wait some views of 220ish width load ok
# well the bot 4 mcodes 'l'oads ok
# and the bot 5 mcodes alway wronng ( not ctrd)
#
# it seems dependant on viewport aspect ratio to selectedBbox aspect ratio
# IF ~same then 'l' works (is ctrd)
# if selectedarea aspect is say 300w and 950h
#  and  viewport is ~4:3   then  NOT ctrd
# and
# if viewport chgd to 3:4  then ok (CTRD)
#--------------code to find viewport geometry
#screen = app.primaryScreen()
#print('Screen: %s' % screen.name())
#size = screen.size()
#print('Size: %d x %d' % (size.width(), size.height()))
#rect = screen.availableGeometry()
#print('Available: %d x %d' % (rect.width(), rect.height()))
#------------------------------------------------

#01feb2022 add lL s S save load diferentiations
# use LS to load and saqve graphs
# use ls to load and save views ( just lists of nodesby name )
# ebgin makin L & S diff from l & s
#
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

#09feb catch22 in this file, nodz_main is imported
# i'd like to import this vvv func from insde nodz_main but cant 
#  theres some circular thing happening
# i just want to put the cursor in ctr of viewport before loading a view
# a view is a setting of hscrollbar, vscrollbar, and scale
# BUT the viewport is 'attracted to the mose and shifts towards it
# IF i move the mout outside the viewport then its ok
# IF i put the mouse in ctr of viewport its ok
# IF i put the mouse at left of viewport then NG (etc top bot rt....)
#def getScreenStuff():
#    screen = app.primaryScreen()
#    print('Screen: %s' % screen.name())
#    size = screen.size()
#    print('Size: %d x %d' % (size.width(), size.height()))
#    rect = screen.availableGeometry()
#    print('Available: %d x %d' % (rect.width(), rect.height()))

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
    a=1
    #09feb reduce clutter
    #print('slot on_keyPressed : ', key)
    
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
