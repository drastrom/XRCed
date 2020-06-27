# Name:         globals.py
# Purpose:      XRC editor, global variables
# Author:       Roman Rolinsky <rolinsky@mema.ucl.ac.be>
# Created:      02.12.2002
# RCS-ID:       $Id$

from __future__ import print_function
import os,sys
import wx
import wx.xrc as xrc

import logging
logging.basicConfig()
logger = logging.getLogger('xrced')

# Global constants

progname = 'xrced'
ProgName = 'XRCed'
version = '0.2.1-0'
# Minimal wxWidgets version
MinWxVersion = (2,8,0)
if wx.VERSION[:3] < MinWxVersion:
    print('''\
******************************* WARNING **************************************
  This version of XRCed may not work correctly on your version of wxWidgets.
  Please upgrade wxWidgets to %d.%d.%d or higher.
******************************************************************************''' % MinWxVersion)

# Can be changed to set other default encoding different
defaultEncoding = 'utf-8'
# you comment above and can uncomment this:
#defaultEncoding = wx.GetDefaultPyEncoding()

# Constant to define standart window name for tested component
STD_NAME = '_XRCED_T_W'
TEST_FILE = 'test.xrc'

# Global id constants
class ID:
    SHIFT = 1000                        # shift ids of replace commands
    MENU = wx.NewId()
    EXPAND = wx.NewId()
    COLLAPSE = wx.NewId()
    COLLAPSE_ALL = wx.NewId()
    PASTE_SIBLING = wx.NewId()
    PASTE = wx.NewId()
    TOOL_PASTE = wx.NewId()
    INSERT = wx.NewId()
    APPEND = wx.NewId()
    SIBLING = wx.NewId()
    REPLACE = wx.NewId()
    SUBCLASS = wx.NewId()
    REF = wx.NewId()
    COMMENT = wx.NewId()

# Constants
AUTO_REFRESH_POLICY_SELECTION = 0
AUTO_REFRESH_POLICY_FOCUS = 1

# Global variables

_debug = False                  # default debug flag
def set_debug(v):
    global _debug
    _debug = v
    logger.setLevel(logging.DEBUG)
def get_debug():
    return _debug

_verbose = False                # default debug flag
def set_verbose(v):
    global _verbose
    _verbose = v
def get_verbose():
    return _verbose

def TRACE(msg, *args):
    if _debug and _verbose: print('TRACE: ' + (msg % args), file=sys.stderr)

class Globals:
    undoMan = None
    conf = None
    useMeta = False              # use meta-components
    _CFuncPtr = None             # _CFuncPtr from ctypes
    lastActiveFrame = None
    
    def _makeFonts(self):
        self._sysFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._labelFont = wx.Font(self._sysFont.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self._modernFont = wx.Font(self._sysFont.GetPointSize(), wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self._smallerFont = wx.Font(self._sysFont.GetPointSize()-1, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        
    def sysFont(self):
        if not hasattr(self, "_sysFont"): self._makeFonts()
        return self._sysFont
    def labelFont(self):
        if not hasattr(self, "_labelFont"): self._makeFonts()
        return self._labelFont
    def modernFont(self):
        if not hasattr(self, "_modernFont"): self._makeFonts()
        return self._modernFont
    def smallerFont(self):
        if not hasattr(self, "_smallerFont"): self._makeFonts()
        return self._smallerFont
    

g = Globals()

# Set application path for loading resources
if __name__ == '__main__':
    g.basePath = os.path.dirname(sys.argv[0])
else:
    g.basePath = os.path.dirname(__file__)
g.basePath = os.path.abspath(g.basePath)

# Data object used for clipboard
class MyDataObject(wx.DataObjectSimple):
    def __init__(self, data=''):
        wx.DataObjectSimple.__init__(self, wx.DataFormat('XRCed_DND'))
        self.data = data.encode("utf-8")
    def GetDataSize(self):
        return len(self.data)
    def GetDataHere(self, buf):
        buf[:] = self.data  # returns a string  
        return True
    def GetData(self):
        return self.data.decode("utf-8")
    def SetData(self, data):
        self.data = data.tobytes()
        return True

# Test for object elements (!!! move somewhere?)
def is_element(node):
    return node.nodeType == node.ELEMENT_NODE and \
        node.tagName in ['object', 'object_ref', 'component']

def is_object(node):
    return is_element(node) or node.nodeType == node.COMMENT_NODE

# Exception class
class TestWinError(Exception): pass
