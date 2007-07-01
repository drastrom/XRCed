# Name:         XMLTree.py
# Purpose:      XMLTree class
# Author:       Roman Rolinsky <rolinsky@femagsoft.com>
# Created:      31.05.2007
# RCS-ID:       $Id$

from globals import *
from model import Model
from component import Manager, Component
import images

class XMLTree(wx.TreeCtrl):
    def __init__(self, parent):
        style = wx.TR_HAS_BUTTONS | wx.TR_MULTIPLE | wx.TR_EDIT_LABELS | wx.TR_HIDE_ROOT
        wx.TreeCtrl.__init__(self, parent, style=style)

        # Color scheme
        self.SetBackgroundColour(wx.Colour(224, 248, 224))
        self.COLOUR_COMMENT  = wx.Colour(0, 0, 255)
        self.COLOUR_REF      = wx.Colour(0, 0, 128)
        self.COLOUR_HIDDEN   = wx.Colour(128, 128, 128)
        self.COLOUR_HL       = wx.Colour(255, 0, 0)
        self.COLOUR_DT       = wx.Colour(0, 64, 0)

        # Comments use italic font
        self.fontComment = wx.FFont(self.GetFont().GetPointSize(),
                                    self.GetFont().GetFamily(),
                                    wx.FONTFLAG_ITALIC)

        # Create image list
        il = wx.ImageList(16, 16, True)
        # 0 is the default image index
        il.Add(images.getTreeDefaultImage().Scale(16,16).ConvertToBitmap())
        # 1 is root
        self.rootImage = il.Add(images.getTreeRootImage().Scale(16,16).ConvertToBitmap())
        # Loop through registered components which have images
        for component in Manager.components.values():
            for im in component.images:
                im.Id = il.Add(im.Scale(16,16).ConvertToBitmap())
        self.il = il
        self.SetImageList(il)

        self.root = self.AddRoot('XML tree', self.rootImage)
        self.SetItemHasChildren(self.root)
#        self.Expand(self.root)

    def Clear(self):
        '''Clear everything except the root item.'''
        self.UnselectAll()
        self.DeleteChildren(self.root)
#        self.Expand(self.root)

    # Add tree item for given parent item if node is DOM element node with
    # object/object_ref tag. xxxParent is parent xxx object
    def AddNode(self, parent, node):
        # Append tree item
        className = node.getAttribute('class')
        try:
            comp = Manager.components[className]
        except:
            # Try to create some generic component on-the-fly
            attributes = []
            for n in node.childNodes:
                if n.nodeType == node.ELEMENT_NODE and not n.tagName in attributes:
                    attributes.append(n.tagName)
            comp = Component(className, 'unknown', attributes)
            Manager.register(comp)
            wx.LogWarning('Unknown component class "%s", registered as generic' % className)
        item = self.AppendItem(parent, className, image=comp.getTreeImageId(node),
                               data=wx.TreeItemData(node))
        # Different color for comments and references
        if className == 'comment':
            self.SetItemTextColour(item, self.COLOUR_COMMENT)
            self.SetItemFont(item, self.fontComment)
#        elif treeObj.ref:
#            self.SetItemTextColour(item, self.COLOUR_REF)
#        elif treeObj.hasStyle and treeObj.params.get('hidden', False):
#            self.SetItemTextColour(item, self.COLOUR_HIDDEN)
        # Try to find children objects
        for n in filter(is_object, node.childNodes):
            self.AddNode(item, comp.getTreeNode(n))

    def Flush(self):
        '''Update all items after changes in model.'''
        self.Clear()
        # (first node is test node)
        for n in filter(is_object, Model.mainNode.childNodes[1:]):
            self.AddNode(self.root, n)

    def ExpandAll(self, item):
        if self.ItemHasChildren(item):
            if not self.IsExpanded(item):
                self.Expand(item)
            i, cookie = self.GetFirstChild(item)
            children = []
            while i.IsOk():
                children.append(i)
                i, cookie = self.GetNextChild(item, cookie)
            map(self.ExpandAll, children)

    def CollapseAll(self, item):
        if self.ItemHasChildren(item):
            i, cookie = self.GetFirstChild(item)
            children = []
            while i.IsOk():
                children.append(i)
                i, cookie = self.GetNextChild(item, cookie)
            map(self.CollapseAll, children)
            if item != self.root:
                self.Collapse(item)

    # Override to use same form as InsertItem
    def InsertItemBefore(self, parent, next, label, image=-1, data=None):
        prev = self.GetPrevSibling(next)
        if prev:
            return self.InsertItem(parent, prev, label, image, data=data)
        else:
            return self.PrependItem(parent, label, image, data=data)

    # Fix for broken

    def ItemHasChildren(self, item):
        return self.GetChildrenCount(item)

