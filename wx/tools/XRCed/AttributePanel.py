# Name:         AttributePanel.py
# Purpose:      View components for editing attributes
# Author:       Roman Rolinsky <rolinsky@mema.ucl.ac.be>
# Created:      17.06.2007
# RCS-ID:       $Id$

import string
import wx
import wx.lib.buttons as buttons
from globals import *
import params
import component
import undo
import images


labelSize = (80,-1)

# Panel class is the attribute panel containing class name, XRC ID and
# a notebook with particular pages.

class ScrolledPage(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent)
        self.topSizer = wx.BoxSizer()
        self.SetSizer(self.topSizer)
        self.panel = None

    def Reset(self):
        if self.panel:
            self.panel.Destroy()
            self.panel = None

    def SetPanel(self, panel):
        self.Reset()
        self.panel = panel
        self.topSizer.Add(panel, 0, wx.ALL, 5)
        self.Layout()
        self.SetScrollRate(1, 1)

class Panel(wx.Panel):
    '''Attribute panel main class.'''
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Set common sizes
        params.InitParams(self)

        topSizer = wx.BoxSizer(wx.VERTICAL)
        pinSizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.FlexGridSizer(2, 2, 1, 5)
        self.labelClass = wx.StaticText(self, -1, 'class:')
        self.controlClass = params.ParamText(self, 'class', textWidth=200)
        sizer.AddMany([ (self.labelClass, 0, wx.ALIGN_CENTER_VERTICAL),
                        (self.controlClass, 0, wx.LEFT, 5) ])
        self.labelName = wx.StaticText(self, -1, 'name:')
        self.controlName = params.ParamText(self, 'name', textWidth=200)
        sizer.AddMany([ (self.labelName, 0, wx.ALIGN_CENTER_VERTICAL),
                        (self.controlName, 0, wx.LEFT, 5) ])
        pinSizer.Add(sizer, 0, wx.ALL, 5)
        pinSizer.Add((0, 0), 1)
        self.pinButton = buttons.GenBitmapToggleButton(
            self, bitmap=images.getToolPinBitmap(),
            style=wx.BORDER_NONE)
        self.pinButton.SetBitmapSelected(images.getToolPinDownBitmap())
        self.pinButton.SetToggle(g.conf.panelPinState)
        self.pinButton.SetToolTipString('Sticky page selection')
        # No highlighting please
        self.pinButton.GetBackgroundBrush = lambda dc: None
        pinSizer.Add(self.pinButton)
        topSizer.Add(pinSizer, 0, wx.EXPAND)
        self.sizer = sizer

        self.nb = wx.Notebook(self, -1)
        if wx.Platform == '__WXGTK__':
            # Redefine AddPage on GTK to fix when page added is not shown
            _oldAddPage = wx.Notebook.AddPage
            def _newAddPage(self, page, label):
                _oldAddPage(self, page, label)
                page.Show(True)
            wx.Notebook.AddPage = _newAddPage

        # Create scrolled windows for panels
        self.pageA = ScrolledPage(self.nb)
        self.nb.AddPage(self.pageA, 'Attributes')
        # Style page
        self.pageStyle = ScrolledPage(self.nb)
        self.pageStyle.Hide()
        # Extra style page
        self.pageExStyle = ScrolledPage(self.nb)
        self.pageExStyle.Hide()
        # Window attributes page
        self.pageWA = ScrolledPage(self.nb)
        self.pageWA.Hide()
        # Implicit attributes page
        self.pageIA = ScrolledPage(self.nb)
        self.pageIA.Hide()
        # Code page
        self.pageCode = ScrolledPage(self.nb)
        self.pageCode.Hide()

        topSizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(topSizer)

        self.undo = None        # pending undo object

    def SetData(self, container, comp, node):
        oldLabel = self.nb.GetPageText(self.nb.GetSelection())
        self.nb.SetSelection(0)
        map(self.nb.RemovePage, range(self.nb.GetPageCount()-1, 0, -1))
        
        self.comp = comp
        panels = []
        # Class and name
        if comp.klass != 'root':
            self.labelClass.Show()
            self.controlClass.Show()
            self.controlClass.SetValue(node.getAttribute('class'))
        else:
            self.labelClass.Hide()
            self.controlClass.Hide()
        self.labelName.Show(comp.hasName)
        self.controlName.Show(comp.hasName)
        if comp.hasName:
            self.controlName.SetValue(node.getAttribute('name'))

        self.Layout()           # update after hiding/showing

        attributes = comp.attributes
        panel = AttributePanel(self.pageA, attributes, comp.params, comp.renameDict)
        self.SetValues(panel, node)
        panels.append(panel)
        self.pageA.SetPanel(panel)

        if comp.windowAttributes:
            panel = AttributePanel(self.pageWA, comp.windowAttributes,
                                   rename_dict = params.WARenameDict)
            self.SetValues(panel, node)
            panels.append(panel)
            self.pageWA.SetPanel(panel)
            self.nb.AddPage(self.pageWA, "Look'n'Feel")

        if comp.styles or comp.genericStyles:
            # Create style page
            panel = params.StylePanel(self.pageStyle, comp.styles, comp.genericStyles)
            self.SetStyleValues(panel, comp.getAttribute(node, 'style'))
            panels.append(panel)
            self.pageStyle.SetPanel(panel)
            self.nb.AddPage(self.pageStyle, 'Style')

        if comp.exStyles or comp.genericExStyles:
            # Create extra style page
            panel = params.StylePanel(self.pageExStyle, comp.exStyles + comp.genericExStyles)
            self.SetStyleValues(panel, comp.getAttribute(node, 'exstyle'))
            panels.append(panel)
            self.pageExStyle.SetPanel(panel)
            self.nb.AddPage(self.pageExStyle, 'ExStyle')

        # Additional panel for hidden node
        if container and container.requireImplicit(node) and container.implicitAttributes:
            panel = AttributePanel(self.pageIA, 
                                   container.implicitAttributes, 
                                   container.implicitParams,
                                   container.implicitRenameDict)
            self.SetValues(panel, node.parentNode)
            panels.append(panel)
            self.pageIA.SetPanel(panel)
            self.nb.AddPage(self.pageIA, container.implicitPageName)

        if comp.events:
            # Create code page
            panel = CodePanel(self.pageCode, comp.events)
            self.SetCodeValues(panel, comp.getAttribute(node, 'XRCED_data'))
            panels.append(panel)
            self.pageCode.SetPanel(panel)
            self.nb.AddPage(self.pageCode, 'Code')

        # Select old page if possible and pin is down
        if g.conf.panelPinState:
            for i in range(1, self.nb.GetPageCount()):
                if oldLabel == self.nb.GetPageText(i):
                    self.nb.SetSelection(i)
                    break

        return panels
        
    def Clear(self):
        self.comp = None
        self.nb.SetSelection(0)
        map(self.nb.RemovePage, range(self.nb.GetPageCount()-1, 0, -1))
        self.pageA.Reset()
        self.undo = None

        self.controlClass.SetValue('')
        self.labelName.Show(False)
        self.controlName.Show(False)

        self.Layout()

    def GetActivePanel(self):
        if self.nb.GetSelection() >= 0:
            return self.nb.GetPage(self.nb.GetSelection()).panel
        else:
            return None

    # Set data for a panel
    def SetValues(self, panel, node):
        panel.node = node
        for a,w in panel.controls:
            value = self.comp.getAttribute(node, a)
            w.SetValue(value)

    # Set data for a style panel
    def SetStyleValues(self, panel, style):
        panel.style = style
        styles = map(string.strip, style.split('|')) # to list
        for s,w in panel.controls:
            w.SetValue(s in styles)

    # Set data for a style panel
    def SetCodeValues(self, panel, data):
        if data:
            events = data['events']
            events = map(string.strip, events.split('|')) # to list
            for ev,w in panel.controls:
                w.SetValue(ev in events)
            panel.checkVar.SetValue(bool(data.get('assign_var', '0')))
            

################################################################################

class AttributePanel(wx.Panel):
    '''Particular attribute panel, normally inside a notebook.'''
    def __init__(self, parent, attributes, param_dict={}, rename_dict={}):
        wx.Panel.__init__(self, parent, -1)
        self.controls = []
        sizer = wx.FlexGridSizer(len(attributes), 2, 0, 0)
        for a in attributes:
            # Find good control class
            paramClass = param_dict.get(a, params.paramDict.get(a, params.ParamText))
            sParam = rename_dict.get(a, a)
            control = paramClass(self, sParam)
            if control.isCheck: # checkbox-like control
                label = wx.StaticText(self, -1, control.defaultString)
                sizer.AddMany([ (control, 1, wx.ALIGN_CENTER_VERTICAL),
                                (label, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2) ])
            else:
                if sParam:
                    label = wx.StaticText(self, -1, sParam, size=labelSize)
                    sizer.AddMany([ (label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20),
                                    (control, 0, wx.ALIGN_CENTER_VERTICAL) ])
                else:           # for node-level params
                    sizer.Add(control, 1, wx.LEFT, 20)
            self.controls.append((a, control))
        self.SetSizerAndFit(sizer)

    def GetValues(self):
        '''Generic method used for creating XML and for other operations.'''
        return [(a,c.GetValue()) for a,c in self.controls]
        
    def SetValues(self, values):
        '''Generic method used for undo.'''
        for ac,a2v in zip(self.controls, values):
            a,c = ac
            v = a2v[1]
            c.SetValue(v)

################################################################################

class CodePanel(wx.Panel):
    '''Code generation panel.'''
    def __init__(self, parent, events):
        wx.Panel.__init__(self, parent, -1)
        self.SetFont(g.smallerFont())
        self.node = None
        self.controls = []
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        if events:
            # Events on the left
            sizer = wx.GridSizer(len(events), 1, 0, 5)
            label = wx.StaticText(self, label='Events')
            label.SetFont(g.labelFont())
            sizer.Add(label, 0, wx.LEFT, 20)
            for ev in events:
                control = wx.CheckBox(self, label=ev)
                sizer.Add(control)
                self.controls.append((ev, control))
            topSizer.Add(sizer)
        # Right sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.checkVar = wx.CheckBox(self, label='assign variable')
        sizer.Add(self.checkVar, 0, wx.LEFT, 20)
        topSizer.Add(sizer)
        # Cach all checkbox events
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.SetSizerAndFit(topSizer)

    def GetValues(self):
        checked = []
        for s,check in self.controls:
            if check.IsChecked(): checked.append(s)
        # Encode data to a dictionary and the cPicke it
        data = {}
        if self.checkVar.GetValue(): data['assign_var'] = '1'
        events = '|'.join(checked)
        if events: data['events'] = events
        if data:
            return [('XRCED_data', data)]
        else:
            return []

    def SetValues(self, values):
        print 'SetValues'
        data = values[0][1]
        events = data['events']
        for s,check in self.controls:
            check.SetValue(s in events)
        self.checkVar.SetValue(bool(data.get('assign_var', '0')))

    def OnCheck(self, evt):
        g.Presenter.setApplied(False)

