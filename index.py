'''
All relevant import statements.
'''
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox
)

from PyQt6.QtGui     import (
    QPixmap,
    QIcon
)

import requests
import sys
import os
import subprocess
import asyncio
import websockets
import random

'''
Cinderella loader's PyQt6 application.
'''

app = QApplication([])


'''
Cinderella loader's window. Contains all visual elements
pertaining to the loader's functionality.
'''

# window object
cin_window     = QMainWindow()

# widget objects
win_widget     = QWidget()
win_layout     = QVBoxLayout(win_widget)
win_license_tb = QLineEdit()
win_game_t_cb  = QCheckBox()
win_load_b     = QPushButton()
win_status_l   = QLabel()

win_license_tb.setPlaceholderText('Enter your license?')
win_game_t_cb.setText('Hood-based Game')
win_load_b.setText('Load Cinderella')
win_status_l.setText('<b>Status:</b> ')

# gateway
status = '<b>Status:</b>'
fail_c = f'{status} <font color="#ff584d">{{}}</font>'
pass_c = f'{status} <font color="#52ff60">{{}}</font>'
idle_c = f'{status} <font color="#b5a2d6">{{}}</font>'

def go_cinderella():
    # status update
    win_status_l.setText(idle_c.format('Cleaning up...'))

    # resolve current path
    dir = os.path.dirname(os.path.abspath(__file__))

    try:
        # go through all files near loader
        for fn in os.listdir(dir):
            # sanitize file's name
            lfn = fn.lower()

            # if it's similar to a generated name
            if lfn.endswith('.exe') and len(lfn) == 19:
                # remove old cinderella loader
                os.remove(lfn)
    except Exception:
        # no need for anything more
        pass

    # get license from text-box
    license = win_license_tb.text() or None
    
    # open license file
    with open(os.path.join(dir, 'license.txt'), 'a+') as f:
        # get content
        txt = f.read()

        # if file's empty (no license stored)
        if txt == '':
            # if they entered one in the text-box
            if license:
                # store license
                f.write(license)
            else:
                # status update
                win_status_l.setText(fail_c.format('No license available, enter one.'))

                #return
        else:
            # set locally to whatever's stored
            license = txt

    try:
        # status update
        win_status_l.setText(idle_c.format('Downloading latest source...'))

        # fetch loader's executable
        resp = requests.get('https://github.com/kagehana/cinderella/raw/refs/heads/main/loader.exe', stream = True)
        
        # generate random string for executable's file name
        abc    = 'bcdfghjklmnpqrstvwxyz'
        result = []

        for i in range(15): # 10 syllables = 20 characters
            result.append(random.choice(abc))

        # build new path to executable
        exe = os.path.join(dir, f'{''.join(result)}.exe')

        # throw if request failed
        resp.raise_for_status()

        # open executable
        with open(exe, 'wb') as f:
            # iterate through fetched chunks
            for chunk in resp.iter_content(chunk_size = 10000):
                # write executable's binary
                f.write(chunk)
        
        # status update
        win_status_l.setText(pass_c.format('Loading <b>Cinderella</b>...'))
        
        # open loader's executable as a process
        subprocess.Popen(
            # provide context
            [exe, '--license', f'"{license}"', '--hb', 1 if win_game_t_cb.isChecked() else 0],
            # no console, we only want a gui
            creationflags = subprocess.CREATE_NO_WINDOW,
            # no std output
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        # status update
        win_status_l.setText(fail_c.format('Failed to load.'))

win_load_b.pressed.connect(go_cinderella)

# widget addition
win_layout.addWidget(win_license_tb)
win_layout.addWidget(win_game_t_cb)
win_layout.addWidget(win_load_b)
win_layout.addWidget(win_status_l)

# window initialization
cin_window.adjustSize()
cin_window.setCentralWidget(win_widget)
cin_window.setWindowTitle('Cinderella')
cin_window.setMinimumSize(250, 118)
cin_window.setFixedSize(cin_window.size())
cin_window.setWindowIcon(QIcon('cinderella.png'))
cin_window.show()

'''
Cinderella loader's locally hosted websocket. Used
for communication between Cinderella subsidiaries.
'''
async def handle_conn(ws, path):
    try:
        # listen to msgs
        async for msg in ws:
            # if cinderella executed
            if msg == 'cinderella::finished':
                # exit loader
                sys.exit()
    except Exception:
        # client disconnect
        pass

async def open_ws():
    # open websocket connection
    async with websockets.serve(handle_conn, 'localhost', 6969):
        # run til' otherwise is directed
        asyncio.Future()




####################
asyncio.run(open_ws)
sys.exit(app.exec())
####################
