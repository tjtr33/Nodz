![Screenshot](Nodz-lcnc.png)

Nodz is a very user friendly python library to create nodes based graphs. It can be connected to anything you want as long as it understands python. Nodz does not hold any data other than its own graphics and attributes types as it is used by the graphics.
Nods provides you with a very simple way to read your graph, it outputs connections as strings ('Node1.attribute1', 'node2.attribute5')

Nodz is partially customizable via a configuration file that let you change colors and the shape of nodes.

EDIT: 10Jan2022 Tjtr33
changes made for use with Linuxcnc Hal components ( like nodes )
I am not a professional software developer. Apologies for not
understanding the program as delivered, not understanding Python,
and not understanding GIT.
Please look at the 3 json files SaveMe01... SaveMe02... SaveMe03...
run the app 'python nodz_demo.py' 
( I use python 2.7 and will update code to 3 soon )
Load these files to see how Nodz works with LinuxCNC informations.

The file creation flow:
The LinuxCNC hal files are loaded into LinuxCNC.
Then a command is issued to collect all the nodes and connections.
 halcmd show sig > mysystem.signals
The file mysystem.signals is processed into json for Nodes.
The tool to convert mysystem.signals into mysystem.json is
not uploaded yet ( I suppose that will be a new git repo... )

For the meantime you can see and play with the supplied json files.

Enjoy, tjtr33




***If you find any errors/bugs/flaws or anything bad, feel free to let me know so I can fix it for the next persons that would like to download nodz.***
EDIT: tjtr33 i suppose you can contact me thru github, i dunno 

***PLEASE MAKE SURE TO CREATE 1 PULL REQUEST PER ISSUE ! THIS IS EASIER AND CLEANER TO PROCESS***

Nodz in under the [MIT license](LICENSE.txt).

[WATCH DEMO HERE](https://vimeo.com/219933604)
EDIT: tjtr33  a new video is coming




###
## Requirement
The following needs to be installed!
- pip
- pipenv




###
## Installation
- `git clone`
- `cd location`
- `pipenv install`
- enjoy! :)




###
## Configuration file

Nodz comes with a default [configuration file](default_config.json), it is specified what can be removed and what can't be.
If this file stays in the default location, it is auto loaded BUT you still need to apply it to Nodz (look at [nodz_demo.py](nodz_demo.py) lines 5/6)
Be careful when editing it, if you are missing a "**,**" it will error. So don't screw up. :smile:




###
## Features

Nodz comes by default with few features, you can toggle the grid visibility and the auto snap mode + some hotkeys. Hotkeys are at the moment based on Autodesk Maya because I developped this library for my personnal use in this specific software but I'm planning on adding that part in the configuration file so everyone can set different hotkeys.

```python
nodz.gridVisToggle = True
nodz.gridSnapToggle = False
```

```
del : delete the selected nodes
f   : zoom focus on selected items, all the items if nothing is selected
s   : snap the selected node on the grid

```




###
## API

Nodz has a very simple API of 12 methods.
For more information on each method, please read [nodz_main.py](nodz_main.py) as it has all the documentation required.

Initialize
```python
def loadConfig(filePath=defautConfigPath)
def initialize()
```
Nodes
```python
def createNode(name, preset, position, alternate)
def deleteNode(node)
def editNode(node, newName)
```
Attributes
```python
def createAttribute(node, name, index, preset, plug, socket, dataType, plugMaxConnections, socketMaxConnections)
def deleteAttribute(node, index)
def editAttribute( node, index, newName, newIndex)
```
Connections
```python
def createConnection(sourceNode, sourceAttr, targetNode, targetAttr)
```
Graph
```python
def saveGraph(filePath)
def loadGraph(filePath)
def evaluateGraph()
def clearGraph()
```

###
## Signals

Nodz also offers you some signals, most of them can feel redundant considering the design of the library but I'm sure some of you will find a use for it. It's better to have them just in case than not having them.
**They are absolutly not mandatory in order for nodz to work.**

Nodes
```python
signal_NodeCreated(nodeName)
signal_NodeDeleted([nodeNames])
signal_NodeEdited(oldName, newName)
signal_NodeSelected([nodeNames])
signal_NodeMoved(nodeName, nodePos)
signal_NodeDoubleClicked(nodeName)
```
Attributes
```Python
signal_AttrCreated(nodeName, attrIndex)
signal_AttrDeleted(nodeName, attrIndex)
signal_AttrEdited(nodeName, oldIndex, newIndex)
```
Connections
```python
signal_PlugConnected(srcNodeName, plugAttribute, dstNodeName, socketAttribue)
signal_PlugDisconnected(srcNodeName, plugAttribute, dstNodeName, socketAttribue)
signal_SocketConnected(srcNodeName, plugAttribute, dstNodeName, socketAttribue)
signal_SocketDisconnected(srcNodeName, plugAttribute, dstNodeName, socketAttribue)
```
Graph
```python
signal_GraphSaved()
signal_GraphLoaded()
signal_GraphCleared()
```
View
```Python
signal_KeyPressed(key)
signal_Dropped(drop position)
```

