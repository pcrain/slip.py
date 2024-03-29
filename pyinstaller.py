#!/usr/bin/python
#Script for generating single-executable file on Windows

import os, PyInstaller.__main__

sep = ";" if os.name == 'nt' else ":"

options = [
  os.path.join('slipdotpy','slip.py'),
  '--noupx',
  '--noconfirm',
  '--noconsole',
  '--windowed',
  '--add-data','{}{}app'.format(os.path.join('slipdotpy','app'),sep),
  '--add-data','{}{}playback-dolphin'.format(os.path.join('slipdotpy','playback-dolphin'),sep),
  '--add-binary','{}{}slippc'.format(os.path.join('slipdotpy','slippc','slippc.exe'),sep),
  '--icon',os.path.join(os.getcwd(),'slipdotpy','app','static','icons','wolfhead.ico'),
  '--name','slipdotpy',
  ]

PyInstaller.__main__.run(options)
