from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import os

from plot_frame import PlotFrame

"""
This file mainly handles the UI and overall program state
"""

infobox_text = """
This was coded using PyQt5 and PyQtGraph in Python, by kangalioo.

The manipulation percentage is calculated by counting the number of
notes that were hit out of order. This is not optimal, but I think it
works well enough.

For session time calculation a session is defined to end when one play
is more than 20 minutes apart from the next play. Therefore a 15min
pause between playing would still count as one session, a 25 min pause
however would not.

Also, if you have any more plot ideas - scatter plot, bar chart,
whatever - I would be thrilled if you sent them to me, over
Discord/Reddit
""".strip() # strip() to remove leading and trailing newlines

# Like QScrollArea, but without scroll wheel scrolling :p
# I did this to prevent simultaneous scrolling and panning when hovering
# a plot while scrolling, which was annoying af.
class ScrollArea(QScrollArea):
	def wheelEvent(self, event):
		pass

# Fields: etterna_xml, canvas, button_load_xml, button_load_replays, window
class Application():
	etterna_xml = None
	replays_dir = None
	
	def __init__(self):
		# Construct app, root widget and layout 
		app = QApplication(["Kangalioo's Etterna stats analyzer"])
		self.app = app
		app.setStyle("Fusion")
		
		window = QMainWindow()
		self.window = window
		root = QWidget()
		layout = QVBoxLayout(root)
		self.layout = layout
		scroll = ScrollArea(window)
		scroll.setWidget(root)
		scroll.setWidgetResizable(True)
		window.setCentralWidget(scroll)
		
		self.setup_ui(layout)
		
		# Start
		w, h = 1600, 2500
		#w, h = 1280, 720
		root.setMinimumSize(1000, h)
		window.resize(w, h)
		window.show()
		app.exec_()
	
	def setup_ui(self, layout):
		# Add infobox
		toolbar = QToolBar()
		infobar = QLabel("This is the infobox. Press on a scatter point to see information about the score")
		infobar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		infobar.setAlignment(Qt.AlignCenter)
		self.infobar = infobar
		toolbar.addWidget(infobar)
		self.window.addToolBar(Qt.BottomToolBarArea, toolbar)
		
		# Button row. Next three sections are the three buttons
		button_row_widget = QWidget()
		button_row = QHBoxLayout(button_row_widget)
		layout.addWidget(button_row_widget)
		
		button = QPushButton("Reload Etterna.xml")
		self.button_load_xml = button
		button_row.addWidget(button)
		button.clicked.connect(self.try_choose_etterna_xml)
		
		button = QPushButton("Load Replays")
		button.setToolTip("Replay data is required for the manipulation chart")
		self.button_load_replays = button
		button_row.addWidget(button)
		button.clicked.connect(self.try_choose_replays)
		
		button = QPushButton("About this program")
		button_row.addWidget(button)
		button.clicked.connect(self.display_info_box)
		
		# REMEMBER
		self.try_find_etterna_xml()
		#self.try_find_replays()
		if self.etterna_xml == None: self.try_choose_etterna_xml()
		
		# Add plot frame
		self.plot_frame = PlotFrame(self.etterna_xml, infobar)
		layout.addWidget(self.plot_frame)
		
		self.refresh_graphs()
	
	def refresh_graphs(self):
		self.plot_frame.draw(self.replays_dir)
	
	def display_info_box(self):
		msgbox = QMessageBox()
		msgbox.setText(infobox_text)
		msgbox.exec_()
	
	def mark_currently_loaded(self, button):
		current_text = button.text()
		if not current_text.endswith(" [currently loaded]"):
			button.setText(current_text + " [currently loaded]")
	
	def try_find_etterna_xml(self):
		path_maybe = "/home/kangalioo/.etterna/Save/LocalProfiles/00000000/Etterna.xml"
		if os.path.exists(path_maybe): self.etterna_xml = path_maybe
	
	def try_find_replays(self):
		path_maybe = "/home/kangalioo/.etterna/Save/ReplaysV2"
		if os.path.exists(path_maybe): self.replays_dir = path_maybe
	
	def try_choose_etterna_xml(self):
		self.try_find_etterna_xml()
		if self.etterna_xml is None:
			result = QFileDialog.getOpenFileName(filter="Etterna XML files(*.xml)")
			path = result[0] # getOpenFileName returns tuple of path and filetype
			
			if path == "": return # User cancelled the file chooser
			
			print(f"[UI] User selected Etterna.xml: {path}")
			self.mark_currently_loaded(self.button_load_xml)
			self.etterna_xml = path
		
		self.refresh_graphs()
	
	def try_choose_replays(self):
		self.try_find_replays()
		if self.replays_dir is None:
			path = QFileDialog.getExistingDirectory(None, "Select ReplaysV2 folder")
			
			if path == "": return # User cancelled the chooser
			
			print(f"[UI] User selected ReplaysV2: {path}")
			self.mark_currently_loaded(self.button_load_replays)
			self.replays_dir = path
		
		self.refresh_graphs()

application = Application()
