# Name:         xrced.py
# Purpose:      XRC editor, main module
# Author:       Roman Rolinsky <rolinsky@mema.ucl.ac.be>
# Created:      20.08.2001
# RCS-ID:       $Id$

"""

xrced -- Simple resource editor for XRC format used by wxWidgets/wxPython
         GUI toolkit.

Usage:

    xrced [ -h ] [ -v ] [ XRC-file ]

Options:

    -h          output short usage info and exit

    -v          output version info and exit
"""

import os
from optparse import OptionParser
from globals import *
import params
from presenter import Presenter
from listener import Listener
from component import Manager
import view
import undo
import plugin

class App(wx.App):
    def OnInit(self):
        # Check version
        if wx.VERSION[:3] < MinWxVersion:
            wx.LogWarning('''\
This version of XRCed may not work correctly on your version of wxWidgets. \
Please upgrade wxWidgets to %d.%d.%d or higher.''' % MinWxVersion)

        g.undoMan = undo.UndoManager()
        Manager.init()

        parser = OptionParser(prog=progname, version=version,
                              usage='%prog [options] [XRC file]')
        #parser.add_option('-v', '--verbose', help='print verbose messages to stdout')
        parser.add_option('-d', '--debug', action='store_true',
                          help='add Debug command to Help menu')
        parser.add_option('-m', '--meta', action='store_true',
                          help='add support for meta components')

        # Process command-line arguments
        (options, args) = parser.parse_args()
        print options
        if options.debug:
            set_debug(True)
        if options.meta:
            # Register meta-components
            import meta
            
#            if wx.Platform != '__WXMAC__': # macs have some extra parameters
#                print >> sys.stderr, 'Unknown option'
#                usage()
#                sys.exit(1)

        self.SetAppName(progname)

        self.ReadConfig()
        
        # Add handlers
        wx.FileSystem.AddHandler(wx.MemoryFSHandler())
        self.toolArtProvider = view.ToolArtProvider()
        wx.ArtProvider.Push(self.toolArtProvider)

        # Load standard plugins
        plugin.load_plugins(os.path.join(g.basePath, 'plugins'))

        # Setup MVP
        view.create_view()
        Presenter.init()
        Listener.Install(view.frame, view.tree, view.panel,
                         view.toolFrame, view.testWin)

        if len(args) > 1:
            Presenter.open(sys.argv[1])
        view.frame.Show()
        if not g.conf.embedPanel:
            view.frame.miniFrame.Show()
        if g.conf.showToolPanel:
            view.toolFrame.Show()

        # Create main frame
#        frame = Frame(pos, size)
        # Mac does not set the correct size
#        if wx.Platform == '__WXMAC__':
#            frame.SetClientSize(size)
#        frame.Show(True)
        
        # Load plugins
#        plugins = os.getenv('XRCEDPATH')

        return True

    def OnExit(self):
        self.WriteConfig()

    def ReadConfig(self):
        # Settings
        conf = g.conf = wx.Config(style = wx.CONFIG_USE_LOCAL_FILE)
        conf.localconf = None
        conf.autoRefresh = conf.ReadInt('autorefresh', True)
        conf.pos = wx.Point(conf.ReadInt('x', -1), conf.ReadInt('y', -1))
        conf.size = wx.Size(conf.ReadInt('width', 800), conf.ReadInt('height', 600))
        conf.embedPanel = conf.ReadInt('embedPanel', True)
        conf.showToolPanel = conf.ReadInt('showToolPanel', True)
        conf.sashPos = conf.ReadInt('sashPos', 200)

        # read recently used files
        g.fileHistory = wx.FileHistory()
        g.fileHistory.Load(conf)

        conf.panelPos = wx.Point(conf.ReadInt('panelX', -1), 
                                 conf.ReadInt('panelY', -1))
        conf.panelSize = wx.Size(conf.ReadInt('panelWidth', 200),
                                 conf.ReadInt('panelHeight', 200))
        conf.sashPos = conf.ReadInt('sashPos', 200)
        
        conf.toolPanelPos = wx.Point(conf.ReadInt('toolPanelX', -1), 
                                     conf.ReadInt('toolPanelY', -1))
        
        # Preferences
#        conf.allowExec = conf.Read('Prefs/allowExec', 'ask')
#        p = 'Prefs/sizeritem_defaults_panel'
#        import xxx
#        if conf.HasEntry(p):
            ##sys.modules['xxx'].xxxSizerItem.defaults_panel = ReadDictFromString(conf.Read(p))
#            xxx.xxxSizerItem.defaults_panel = ReadDictFromString(conf.Read(p))
#        p = 'Prefs/sizeritem_defaults_control'
#        if conf.HasEntry(p):
            ##sys.modules['xxx'].xxxSizerItem.defaults_control = ReadDictFromString(conf.Read(p))
#            xxx.xxxSizerItem.defaults_control = ReadDictFromString(conf.Read(p))
            
    def WriteConfig(self):
        
        # Write config
        conf = g.conf
        conf.WriteInt('autorefresh', conf.autoRefresh)
        conf.WriteInt('x', conf.pos.x)
        conf.WriteInt('y', conf.pos.y)
        conf.WriteInt('width', conf.size.x)
        conf.WriteInt('height', conf.size.y)
        conf.WriteInt('embedPanel', conf.embedPanel)
        conf.WriteInt('showTools', conf.showToolPanel)
        if not conf.embedPanel:
            conf.WriteInt('panelX', conf.panelPos.x)
            conf.WriteInt('panelY', conf.panelPos.y)
        conf.WriteInt('sashPos', conf.sashPos)
        conf.WriteInt('panelWidth', conf.panelSize.x)
        conf.WriteInt('panelHeight', conf.panelSize.y)
        conf.WriteInt('showToolPanel', conf.showToolPanel)
        conf.WriteInt('toolPanelX', conf.toolPanelPos.x)
        conf.WriteInt('toolPanelY', conf.toolPanelPos.y)
        g.fileHistory.Save(conf)
        # Preferences
        conf.DeleteGroup('Prefs')
#        conf.Write('Prefs/allowExec', conf.allowExec)
#        import xxx
        ##v = sys.modules['xxx'].xxxSizerItem.defaults_panel
#        v = xxx.xxxSizerItem.defaults_panel
#        if v: conf.Write('Prefs/sizeritem_defaults_panel', DictToString(v))
        ###v = sys.modules['xxx'].xxxSizerItem.defaults_control
#        v = xxx.xxxSizerItem.defaults_control
#        if v: conf.Write('Prefs/sizeritem_defaults_control', DictToString(v))
        
        conf.Flush()

        
    


def main():
    app = App(0, useBestVisual=False)
    #app.SetAssertMode(wx.PYAPP_ASSERT_LOG)
    app.MainLoop()

if __name__ == '__main__':
    main()
