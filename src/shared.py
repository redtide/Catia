#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Common/Shared code
# Copyright (C) 2010-2020 Filipe Coelho <falktx@falktx.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the COPYING file

# ---------------------------------------------------------------------------------------------------------------------
# Imports (Global)

import os
import sys
from codecs import open as codecopen
from unicodedata import normalize

from PyQt5.QtCore import pyqtSignal, qWarning, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

# ---------------------------------------------------------------------------------------------------------------------
# Set Platform

if sys.platform == "darwin":
    HAIKU   = False
    LINUX   = False
    MACOS   = True
    WINDOWS = False
elif "haiku" in sys.platform:
    HAIKU   = True
    LINUX   = False
    MACOS   = False
    WINDOWS = False
elif "linux" in sys.platform:
    HAIKU   = False
    LINUX   = True
    MACOS   = False
    WINDOWS = False
elif sys.platform in ("win32", "win64", "cygwin"):
    WINDIR  = os.getenv("WINDIR")
    HAIKU   = False
    LINUX   = False
    MACOS   = False
    WINDOWS = True
else:
    HAIKU   = False
    LINUX   = False
    MACOS   = False
    WINDOWS = False

# ---------------------------------------------------------------------------------------------------------------------
# Try Import Signal

try:
    from signal import signal, SIGINT, SIGTERM, SIGUSR1, SIGUSR2
    haveSignal = True
except:
    haveSignal = False

# ---------------------------------------------------------------------------------------------------------------------
# Safe exception hook, needed for PyQt5

def sys_excepthook(typ, value, tback):
    return sys.__excepthook__(typ, value, tback)

sys.excepthook = sys_excepthook

# ---------------------------------------------------------------------------------------------------------------------
# Set Version

VERSION = "0.9.0"

# ---------------------------------------------------------------------------------------------------------------------
# Set Debug mode

DEBUG = bool("-d" in sys.argv or "-debug" in sys.argv or "--debug" in sys.argv)

# ---------------------------------------------------------------------------------------------------------------------
# Global variables

global gGui
gGui = None

# ---------------------------------------------------------------------------------------------------------------------
# Set TMP

TMP = os.getenv("TMP")

if TMP is None:
    if WINDOWS:
        qWarning("TMP variable not set")
        TMP = os.path.join(WINDIR, "temp")
    else:
        TMP = "/tmp"

# ---------------------------------------------------------------------------------------------------------------------
# Set HOME

HOME = os.getenv("HOME")

if HOME is None:
    HOME = os.path.expanduser("~")

    if not WINDOWS:
        qWarning("HOME variable not set")

if not os.path.exists(HOME):
    qWarning("HOME does not exist")
    HOME = TMP

# ---------------------------------------------------------------------------------------------------------------------
# Set PATH

PATH = os.getenv("PATH")

if PATH is None:
    qWarning("PATH variable not set")

    if MACOS:
        PATH = ("/opt/local/bin", "/usr/local/bin", "/usr/bin", "/bin")
    elif WINDOWS:
        PATH = (os.path.join(WINDIR, "system32"), WINDIR)
    else:
        PATH = ("/usr/local/bin", "/usr/bin", "/bin")

else:
    PATH = PATH.split(os.pathsep)

# ---------------------------------------------------------------------------------------------------------------------
# Remove/convert non-ascii chars from a string

def asciiString(string):
    return normalize("NFKD", string).encode("ascii", "ignore").decode("utf-8")

# ---------------------------------------------------------------------------------------------------------------------
# Convert a ctypes c_char_p into a python string

def cString(value):
    if not value:
        return ""
    if isinstance(value, str):
        return value
    return value.decode("utf-8", errors="ignore")

# ---------------------------------------------------------------------------------------------------------------------
# Get Icon from user theme, using our own as backup (Oxygen)

def getIcon(icon, size=16):
    return QIcon.fromTheme(icon, QIcon(":/%ix%i/%s.svgz" % (size, size, icon)))

# ---------------------------------------------------------------------------------------------------------------------
# Signal handler

def setUpSignals(self_):
    global gGui

    if gGui is None:
        gGui = self_

    if not haveSignal:
        return

    signal(SIGINT,  signalHandler)
    signal(SIGTERM, signalHandler)
    signal(SIGUSR1, signalHandler)
    signal(SIGUSR2, signalHandler)

    gGui.SIGTERM.connect(closeWindowHandler)
    gGui.SIGUSR2.connect(showWindowHandler)

def signalHandler(sig, frame):
    global gGui

    if gGui is None:
        return

    if sig in (SIGINT, SIGTERM):
        gGui.SIGTERM.emit()
    elif sig == SIGUSR1:
        gGui.SIGUSR1.emit()
    elif sig == SIGUSR2:
        gGui.SIGUSR2.emit()

def closeWindowHandler():
    global gGui

    if gGui is None:
        return

    gGui.hide()
    gGui.close()
    QApplication.instance().quit()

    gGui = None

def showWindowHandler():
    global gGui

    if gGui is None:
        return

    if gGui.isMaximized():
        gGui.showMaximized()
    else:
        gGui.showNormal()

# ---------------------------------------------------------------------------------------------------------------------
# Safer QSettings class, which does not throw if type mismatches

class QSafeSettings(QSettings):
    def value(self, key, defaultValue, valueType):
        if not isinstance(defaultValue, valueType):
            print("QSafeSettings.value() - defaultValue type mismatch for key", key)

        try:
            return QSettings.value(self, key, defaultValue, valueType)
        except:
            return defaultValue

# ---------------------------------------------------------------------------------------------------------------------
