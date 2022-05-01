#defines Toolbar, SectionDropDown, FileDropDown, PlayCtrl

# <Toolbar@BoxLayout>:
# <SectionDropDown@DropDown>:
# <ZoomCtrl@Widget>:
# <GridControl@GridLayout>:
# <FileDropDown@DropDown>:

import numpy
import math
import os
# from os.path import abspath, dirname, join, exists, sep, expanduser, isfile
# import pathlib
import json

from colorsys import hsv_to_rgb, rgb_to_hsv
from array import array
from plyer import filechooser as NativeFilechooser

from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.config import Config, ConfigParser
from kivy.uix.popup import Popup
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import StripLayout, TabbedPanel, TabbedPanelContent, TabbedPanelHeader, TabbedPanelItem, \
	TabbedPanelStrip
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.colorpicker import ColorWheel
# noinspection PyUnresolvedReferences
from kivy.garden.tickmarker import TickMarker
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior
from kivy.properties import AliasProperty, BooleanProperty, BoundedNumericProperty, ColorProperty, ConfigParserProperty, \
	DictProperty, ListProperty, NumericProperty, ObjectProperty, OptionProperty, ReferenceListProperty, StringProperty, \
	VariableListProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, Rectangle, BorderImage, Canvas

import threading
from mido import Message, MidiFile

from .midoplayer import FilePlayer
from .visualmidi import VisualTrack
from .notegrid import CollapsedOct
from .custom import AdjusterBox, SliderAdjuster, VolumeAdjuster

__all__ = ('Toolbar', 'SectionDropDown', 'FileDropDown')

# toolbar_widget
class Toolbar(BoxLayout):
	cont_sz_mult_x = BoundedNumericProperty(1, min=1, max=100, errorhandler=lambda x: 1 if x < 1 else 100)
	cont_sz_mult_y = BoundedNumericProperty(8, min=8, max=20, errorhandler=lambda x: 8 if x < 8 else 20)
	
	last_bar_num = NumericProperty(0)
	
	#play_ctrl = ObjectProperty(None)
	
	
	def windows_new_file(self):
		self.play_ctrl.new()
		#TODO: add dirty check, ask if user wants to save first
	
	def windows_open_file(self):
		appdir = os.path.abspath(App.get_running_app().directory) 	#default for open_file, even w/o path= arg
		
		pathlist = NativeFilechooser.open_file(title="Open MIDI file", path=appdir, filters=[("*.mid")], on_selection=self.open_file_callback)
		
		
	def open_file_callback(self, pathlist):
		if pathlist == []:
			return
			
		fullpath = pathlist[0]

		self.play_ctrl.open(fullpath)

		
	def windows_save_file(self):
		pathlist = NativeFilechooser.save_file(title="Save MIDI file", filters=[("*.mid")], on_selection=self.save_file_callback)

		
	def save_file_callback(self, pathlist):
		if pathlist == []:
			return
			
		fullpath = pathlist[0]	
		
		if not fullpath.endswith('.mid') :
			fullpath = fullpath + '.mid'

		dirs = fullpath.split('\\')
		directory = '\\'.join(dirs[:-1])
		filename = dirs[-1]
		
		print(f'TODO: {filename} saved in {directory}')

	
	def switch_editable(self, ToggleButtonObject, toggleState):
		currently_active = self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.active_channel
		top_channel = self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.first_visible_channel()
		auto_select = self.top_level_ref.left_panel.chnl_ctrl.auto_select
		
		if toggleState == 'down':
			ToggleButtonObject.text = 'EDITABLE'
			self.top_level_ref.note_scroller.editable = True
			
			if currently_active == None and auto_select == True and top_channel != None:
				top_channel._set_active(True)
				self.top_level_ref.note_scroller.active_channel = top_channel
				
			if len(self.top_level_ref.note_scroller.visual_track_lst) == 0:
				self.top_level_ref.note_scroller.visual_track_lst.append(self.play_ctrl.create_blank_track())
			
		else:
			ToggleButtonObject.text = 'SELECTABLE'
			self.top_level_ref.note_scroller.editable = False
			if self.top_level_ref.note_scroller.active_channel is not None:
				self.top_level_ref.note_scroller.active_channel._set_active(False)
				self.top_level_ref.note_scroller.active_channel = None
				

	
	# show/hide keyboard and sharps highlighting
	def switch_keyboard(self, ToggleButtonObject, toggleState):
		#note_grid_ref = self.parent.parent.note_scroller.track_tabs.lined_note_grid.note_grid
		note_grid_ref = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
		
		#sets button state to toggleState and applies currently selected level of 'sharps highlighting' (default is 30%)
		self.top_level_ref.left_panel.hlight_ctrl.hightlight_accordion.sharps_ctrl.sharps_btn.state = toggleState
		
		if toggleState == 'down':
			
			for child in note_grid_ref.children:
				if not isinstance(child, CollapsedOct):
					for gchild in child.note_stack.children:
						gchild.keybrd_alpha = 1

		else:
			for child in note_grid_ref.children:
				if not isinstance(child, CollapsedOct):
					for gchild in child.note_stack.children:
						gchild.keybrd_alpha = 0

						
	def zoom_in(self, *args):
		#print(f'toolbar cont_sz_mult_y will increment to: {self.cont_sz_mult_y+1}')
		self.cont_sz_mult_x += 1
		self.cont_sz_mult_y += 1
	
	
	def zoom_out(self, *args):
		#print(f'toolbar cont_sz_mult_y will decrement to: {self.cont_sz_mult_y-1}')
		self.cont_sz_mult_x -= 1
		self.cont_sz_mult_y -= 1

		
	def test_func(self, *args):
		note_grid_ref = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
		
		# note_grid_ref.expand_between_min_max(64, 84)
		
		# note_ref = note_grid_ref.get_midinum_note_ref(84)
		# if note_ref is not None:
			#print(f'chroma:{note_ref.chroma} midinum:{note_ref.midinum} octave:{note_ref.midinum // 12 - 1}')
		#print(note_grid_ref.oct_1.pos, note_grid_ref.pos, note_grid_ref.to_window(*note_grid_ref.pos) ,note_grid_ref.oct_1.to_window(*note_grid_ref.oct_1.pos))
		#print(note_grid_ref.octave_expanded, note_grid_ref.octave_expanded.items())
		
		
class FileDropDown(DropDown):
	caller = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(FileDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None


class SectionDropDown(DropDown):
	caller = ObjectProperty(None)
	last_bar_num = NumericProperty(0)
	
	def __init__(self, **kwargs):
		super(SectionDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None
		self.section_start = 1
		self.section_end = self.caller.parent.last_bar_num
	
	def open(self, widget):
		self.last_bar_num = self.caller.parent.last_bar_num
		
		if self.section_start > 1 or (self.section_end > self.section_start and self.section_end < self.last_bar_num):
			self.start_bar.val = self.section_start
			self.end_bar.val = self.section_end
		else:
			self.start_bar.val = 1
			self.end_bar.val = self.last_bar_num
		
		super(SectionDropDown, self).open(widget)
	
	# def on_dismiss(self, *args):
	# #if the selected section is not accepted by user, reset slider values to min/max
	# self.section_start = 1
	# self.section_end = self.last_bar_num
	
	def on_select(self, value):
		self.section_start = value[0]
		self.section_end = value[1]

		

class PlayCtrl(Widget):

	def __init__(self, **kwargs):
		super(PlayCtrl, self).__init__(**kwargs)
		self.state = ''
		self._cached_state = ''
		self.progress = 0.0
		self.midi_player = None
		self.visual_tracks_ref = None
		Clock.schedule_once(self._refresh)

	@mainthread
	def update_progress(self, progress_list):
		self.progress = progress_list[0]
		self.top_level_ref.time_scroller.time_line.player_progress(progress_list)
		
		if self.progress == 100.0:
			self._change_state('stop') 
			

	def seeking(self, new_pos):
		self._change_state('seek', position=new_pos)
		return 0
		
	
	def seek_released(self, new_pos):
		self._change_state(self._cached_state, position=new_pos)
		return 0

		
	def _refresh(self, *arg):
		#print(f'(_refresh) player state: {self.state}, visual_track_lst: {self.visual_tracks_ref}, midi_player:{self.top_level_ref.midi_player}')
		if self.state != '' and self.state != 'initial':
			self.midi_player.interrupt()
			self.midi_player.reset_outport()
			
		if self.visual_tracks_ref is None:
			self.visual_tracks_ref = self.top_level_ref.note_scroller.visual_track_lst
		
		#removes all markers from existing tracks AND removes ALL TRACKS
		self.top_level_ref.note_scroller.clear_all_tracks()

		#self._change_state('initial')	
		
		if self.midi_player == None:
			if self.top_level_ref.midi_player is not None:
				self.midi_player = self.top_level_ref.midi_player
			elif self.top_level_ref.note_player is not None:
				self.midi_player = FilePlayer(outport=self.top_level_ref.note_player.get_outport_ref())
			else:	
				self.note_player = TonePlayer() 
				self.midi_player = FilePlayer(outport=self.note_player.get_outport_ref())
				self.top_level_ref.note_player = self.note_player
				self.top_level_ref.midi_player = self.midi_player
				
				
	def create_blank_track(self):	
		ticks_per_bar = self.top_level_ref.left_panel.voltempo_ctrl.ticks_per_bar.val
		num_bars = self.top_level_ref.note_scroller.cont_sz_x / self.top_level_ref.note_scroller.track_tabs.lined_note_grid.bar_length

		return VisualTrack(top_level_ref = self.top_level_ref, tick_len=num_bars*ticks_per_bar)		

	
	def new(self):
		self._refresh()
		self.top_level_ref.note_scroller.track_tabs.on_new_file()
		self.midi_player.unload_all()
		self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.reset_all_instruments()
		

	def open(self, fullpath):
		self._refresh()
		self.midi_player.load_from_file(filename=fullpath, visual_track_lst=self.visual_tracks_ref, callback=self.update_progress)
		
		track_name_lst = []
		
		for v_trk in self.visual_tracks_ref:
			v_trk.visualize(top_level_ref=self.top_level_ref) 
			track_name_lst.append(v_trk.track_name)
		
		if len(self.visual_tracks_ref) > 1:
			for v_trk in self.visual_tracks_ref[1:]:
				v_trk.hide_track_markers()
		
		#set channel instruments from file tracks (in reverse order, so first tab's track assignments take precedence)
		for v_trk in reversed(self.visual_tracks_ref):
			if v_trk.voices_timed == False and len(v_trk.channel_voice_dict) > 0:
				for item in v_trk.channel_voice_dict.items():
					#print(f"track_name: {v_trk.track_name}, channel_num: {item[0]}, midi_voice_idx: {item[1]}")
					self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.set_instrument_from_track(channel_num=item[0], midi_voice_idx=item[1])

		self.top_level_ref.note_scroller.track_tabs.on_file_open(track_name_lst)	
		self._change_state('initial')	

			
	def play(self):
		dirty_track_present = False
		
		for v_trk in self.visual_tracks_ref:
			if v_trk.dirty:
				dirty_track_present = True
				break
		
		print(f"midi_loaded: {self.midi_player.midi_loaded}, dirty_track: {dirty_track_present}")
		#if not self.midi_player.midi_loaded or dirty_track_present:
		if dirty_track_present:
			self._change_state('initial')		
			self.midi_player.load_from_editor(editor_track_lst=self.visual_tracks_ref, callback=self.update_progress)
	
		self._change_state('play') 
		
		
	def pause(self):
		self._change_state('pause') 
		
		
	def stop(self):
		self._change_state('stop') 
		
		
	def _change_state(self, next_state, **kwargs):
		#print(f"current player UI state: {self.state }, next state: {next_state}")

		if next_state == 'initial':
			if self.state != '':
				self._cached_state = ''
				self.midi_player.stop()
				
			self.state = 'initial'				
			self.update_progress([0,0])
			return
		
		if next_state == 'seek':
			if self.state == '':
				return
				
			if self.midi_player != None:
				self.midi_player.interrupt()

				if self.state != 'seek':
					#print(f'caching state {self.state}')				
					self._cached_state = self.state
					
					#print(f'changing state to {next_state}')
					self.state = next_state
				return
		
		if next_state == 'play':
			if self.state == '':
				return
				
			if self.state == 'play':
				return
			if self.state == 'pause':
				self.state = next_state			
				self.midi_player.toggle_pause()
				return
			if self.state == 'seek':
				self.state = next_state
				new_position = kwargs.get('position', -1)
				if new_position >= 0:
					self.midi_player.set_position(new_position)
				self.midi_player.play()
				return
			self.state = next_state
			self.midi_player.play()
			return
				
		#pressing pause while already paused in playback will 'un-pause', i.e. resume playback
		if next_state == 'pause':
			if self.state == '':
				return
				
			if self.state == 'seek':
				self.state = next_state
				new_position = kwargs.get('position', -1)
				if new_position >= 0:
					self.midi_player.set_position(new_position)
				return
				
			if self.state == 'play' or self.state == 'pause':
				self.state = 'pause' if self.state == 'play' else 'play'	
				self.midi_player.toggle_pause()
				return
	
		if next_state == 'stop':
			if self.state == '':
				return
				
			self.state = next_state
			self._cached_state = ''
			self.midi_player.stop()
			self.update_progress([0,0])
			return
		