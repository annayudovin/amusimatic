#defines Marker, Note, Octave, PartialOct, CollapsedOct, Notegrid, LinedNoteGrid, TrackTabbedPanel, NoteScroll, TickSlider, TickLabel, Timeline, TimelineScroll

# <Marker@Widget>:
# #----------------------
# <Note@Widget>:
# <Octave@Widget>:
# <PartialOct@Widget>:
# <CollapsedOct@Widget>:
# <Notegrid@BoxLayout>:
# <LinedNoteGrid@Widget>:
# <TrackTabbedPanel@TabbedPanel>:
# <NoteScroll@ScrollView>:
# #----------------------
# <TickLabel@Label>:
# <Timeline@Widget>:
# <TimelineScroll@ScrollView>:	

import numpy
import math
import os
# from os.path import abspath, dirname, join, exists, sep, expanduser, isfile
# import pathlib
import json

from colorsys import hsv_to_rgb, rgb_to_hsv
from array import array

from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock
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

#from globals import chroma_dict, chroma, scale_steps, diatonic_scales, other_scales, instruments, tick2second, second2tick, bpm2tempo, tempo2bpm, camel_to_snake, snake_to_camel, Log2, isPowerOfTwo, nearestPowerOfTwo, get_document_directory

#from custom import USpinner, DrawerAccordion, DrawerAccordionItem, AutoSizedTabHeader, AutoSizedTabItem, GradientSlider, HSVColorPicker, HSVColorPickerDropDown, HSVTColorPicker, HSVTColorDropDown, HSVTColorMenuBtn, AdjusterBox, SliderAdjuster, VolumeAdjuster
from .custom import AutoSizedTabHeader, AutoSizedTabItem

__all__ = ('Marker', 'Note', 'Octave', 'PartialOct', 'CollapsedOct', 'Notegrid', 'LinedNoteGrid', 'TrackTabbedPanel', 'NoteScroll', 'TickSlider', 'TickLabel', 'Timeline', 'TimelineScroll')

#------------------------------------------------------------------------------------------------------------------------------
class Marker(Widget):
	finished_creating_event = ObjectProperty(None, allownone=True)
	chn_color = ColorProperty([0, 0, 0, 0])
	
	def __init__(self, *args, **kwargs):
		super(Marker, self).__init__()
		
		self.top_level_ref = kwargs.get('top_level_ref', None)
		self.channel = kwargs.get('chnum', -1)			
			
		if 'color' in kwargs:
			self.chn_color = kwargs.get('color')
		elif self.channel != -1:
			self.chn_color = self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.get_channel_color(self.channel)
		else:
			self.chn_color = [0, 0, 0, 1]
			
		self.midinum =  kwargs.get('midinum', -1)
		self.octave = self.midinum // 12 - 1
		self.chroma = self.midinum % 12

		if 'tt_on' in kwargs and 'tt_off' in kwargs:
			self.tt_on = kwargs.get('tt_on')
			self.tt_off = kwargs.get('tt_off')
			self.deltaT = self.tt_off - self.tt_on	
			
		else:
			self.tt_on = 0
			self.tt_off = 0
			self.deltaT = 0		
			# self.finished_creating_event = Clock.schedule_once(self.rescale, 3)
	
	
	def rescale(self, *args):
		#TODO: spacer(?), track index(?)
		#grid_scale = self.top_level_ref.note_scroller.grid_time_scale
		ticks_per_bar = self.top_level_ref.left_panel.voltempo_ctrl.ticks_per_bar.val
		grid_scale = ticks_per_bar/self.top_level_ref.note_scroller.track_tabs.lined_note_grid.bar_length
		
		self.tt_on = int(round((self.pos[0] - self.parent.pos[0]) * grid_scale, 0))
		self.tt_off = int(round((self.pos[0] + self.width - self.parent.pos[0]) * grid_scale, 0))
		self.deltaT = int(round(self.width * grid_scale, 0))
		
		#self.top_level_ref.note_scroller.visual_track_lst[self.top_level_ref.note_scroller.active_track].check_marker_note(self)
		
		#print(f'(rescale) self.pos[0]: {self.pos[0]}, self.parent.pos[0]: {self.parent.pos[0]}, self.width: {self.width}')		
		#print(f'grid_scale: {grid_scale}, tt on: {self.tt_on}, tt off: {self.tt_off}, duration: {self.deltaT}')
		
		
	# TODO: add markers to a structure on creation, remove on deletion
	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			if self.top_level_ref.note_scroller.editable == True:
				if self.top_level_ref.note_scroller.active_channel is not None:
					active_channel = self.top_level_ref.note_scroller.active_channel.cnum - 1
					if self.channel == active_channel:
						#print(f'tt on: {self.tt_on}, tt off: {self.tt_off}, duration: {self.deltaT}')
						self.top_level_ref.note_scroller.visual_track_lst[self.top_level_ref.note_scroller.active_track].remove_marker(self)
						self.parent.remove_widget(self)
						return True
					else:
						return False
				else:
					#print(f'tt on: {self.tt_on}, tt off: {self.tt_off}, duration: {self.deltaT}')
					self.top_level_ref.note_scroller.visual_track_lst[self.top_level_ref.note_scroller.active_track].remove_marker(self)
					self.parent.remove_widget(self)
					return True
			
			else:  # TODO: add 'Selectable' logic
				print(f'selected: channel {self.channel}, tt on: {self.tt_on}, tt off: {self.tt_off}, duration: {self.deltaT}')
				return True
		else:
			return False


#------------------------------------------------------------------------------------------------------------------------------
class Note(Widget):
	note_off_event = ObjectProperty(None, allownone=True)
	font_sz = NumericProperty(0)
	key_pos_x = NumericProperty(0)
	lbl_ctr_x = NumericProperty(0)
	lbl_type = NumericProperty(0)
	
	
	def place_marker(self, mrkr, ticks_per_bar):
		#grid_scale = self.parent.note_scroller_ref.grid_time_scale
		mrkr.height = self.height
		
		# mrkr.width = mrkr.deltaT / grid_scale
		# mrkr.pos[0] = mrkr.tt_on / grid_scale + self.pos[0]
		# mrkr.pos[1] = self.pos[1]
		
		grid_scale = ticks_per_bar/self.parent.note_scroller_ref.track_tabs.lined_note_grid.bar_length
		
		mrkr.width = mrkr.deltaT / grid_scale
		mrkr.pos[0] = mrkr.tt_on / grid_scale + self.pos[0]
		mrkr.pos[1] = self.pos[1]
		
		#presumably already in VisualTrack, no need to add
		self.add_widget(mrkr)
		
		#print(f'(place_marker) tt on: {mrkr.tt_on}, tt off: {mrkr.tt_off}, duration: {mrkr.deltaT}')		
		#print(f'grid_scale: {grid_scale}, mrkr.width: {mrkr.width}, mrkr.pos[0]: {mrkr.pos[0]}, self.pos[0]: {self.pos[0]}')

	
	def on_touch_down(self, touch):
		
		if self.collide_point(*touch.pos):
			if super(Note, self).on_touch_down(touch):
				return True
			
			if self.parent.note_scroller_ref.top_level_ref.note_player is not None:
				if self.parent.note_scroller_ref.active_channel is not None:
					play_channel = self.parent.note_scroller_ref.active_channel.cnum - 1
				else:
					play_channel = 0

				self.parent.note_scroller_ref.top_level_ref.note_player.midi_note_on(self.midinum, channel = play_channel)
				# per kivy docs, on_touch_up event is not certain to come, so schedule the note to terminate after 2 seconds (and unschedule in on_touch_up if it's triggered)
				self.note_off_event = Clock.schedule_once(self.parent.note_scroller_ref.top_level_ref.note_player.midi_last_off, 2)

			if self.parent.note_scroller_ref.editable == True:
				if self.parent.note_scroller_ref.active_channel is not None:
					mrkr = Marker(top_level_ref = self.parent.note_scroller_ref.top_level_ref,
								  color=self.parent.note_scroller_ref.active_channel.chn_color,
								  chnum=self.parent.note_scroller_ref.active_channel.cnum - 1,
								  midinum=self.midinum)
					mrkr.x = touch.x
					mrkr.y = self.y
					mrkr.width = 5
					mrkr.height = self.height
					self.add_widget(mrkr)
					#print(f'active track:{self.parent.note_scroller_ref.active_track}')
					self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].add_marker(mrkr)
					#print(f'visual_track_lst len: {len(self.parent.note_scroller_ref.visual_track_lst)}, active_track: {self.parent.note_scroller_ref.active_track}')
					touch.ud['mrkr'] = mrkr
			# else:
			#print(f'bar:{self.parent.note_scroller_ref.track_tabs.lined_note_grid.bar_length}; beat:{self.parent.note_scroller_ref.track_tabs.lined_note_grid.beat_length}')
			
			return True
	
	def on_touch_move(self, touch):
		if self.collide_point(*touch.pos) or self.collide_point(*touch.opos):
			if self.parent.note_scroller_ref.active_channel is not None:
				active_channel_num = self.parent.note_scroller_ref.active_channel.cnum - 1
			else:
				active_channel_num = -1
			
			if not touch.ud.get('mrkr', None) is None:
				if touch.x > touch.ox:
					touch.ud['mrkr'].width = touch.x - touch.ox
				else:
					touch.ud['mrkr'].width = touch.ox - touch.x
					touch.ud['mrkr'].x = touch.x
				
				for child in self.children:
					if child != touch.ud['mrkr'] and isinstance(child, Marker):
						if touch.ud['mrkr'].x <= child.x <= touch.ud['mrkr'].x + touch.ud[
							'mrkr'].width and child.channel == active_channel_num:
							self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].remove_marker(child)
							self.remove_widget(child)

						elif child.x >= min(touch.ox, touch.x) and child.x <= max(touch.ox,
																				  touch.x) and child.channel == active_channel_num:
							self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].remove_marker(child)
							self.remove_widget(child)
							
						elif child.x + child.width > min(touch.ox, touch.x) and child.x + child.width < max(touch.ox,
																											touch.x) and child.channel == active_channel_num:
							self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].remove_marker(child)
							self.remove_widget(child)
							
			else:
				for child in self.children:
					if isinstance(child, Marker):
						if child.x >= min(touch.ox, touch.x) and child.x <= max(touch.ox,
																				touch.x) and child.channel == active_channel_num:
							self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].remove_marker(child)
							self.remove_widget(child)

						elif child.x + child.width > min(touch.ox, touch.x) and child.x + child.width < max(touch.ox,
																											touch.x) and child.channel == active_channel_num:
							self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].remove_marker(child)
							self.remove_widget(child)

			return True
	
	def on_touch_up(self, touch):
		if self.collide_point(*touch.pos) or self.collide_point(*touch.opos):
			if not touch.ud.get('mrkr', None) is None:
				this_mrkr = touch.ud['mrkr']
				if this_mrkr.width < 2:
					self.remove_widget(this_mrkr)
				else:
					this_mrkr.rescale()
					#print(f'active track:{self.parent.note_scroller_ref.active_track}')
					self.parent.note_scroller_ref.visual_track_lst[self.parent.note_scroller_ref.active_track].add_marker(this_mrkr)
					
			if self.parent.note_scroller_ref.top_level_ref.note_player is not None:
				self.parent.note_scroller_ref.top_level_ref.note_player.midi_last_off()
				if self.note_off_event is not None:
					Clock.unschedule(self.note_off_event)
					

#------------------------------------------------------------------------------------------------------------------------------


class Octave(Widget):
	def get_chroma_note_ref(self, chroma):
		chroma_attr = 'note' + str(chroma)
				
		if hasattr(self, chroma_attr):
			note_ref = getattr(self, chroma_attr)
			return note_ref
		else:
			return None


class PartialOct(Widget):
	def get_chroma_note_ref(self, chroma):
		chroma_attr = 'note' + str(chroma)
				
		if hasattr(self, chroma_attr):
			note_ref = getattr(self, chroma_attr)
			return note_ref
		else:
			return None


class CollapsedOct(Widget):
	def __init__(self, OctaveNumber):
		super(CollapsedOct, self).__init__()
		self.octnum = OctaveNumber


class Notegrid(BoxLayout):
	
	def __init__(self, **kwargs):
		super(Notegrid, self).__init__(**kwargs)
		self.orig_octaves = {}
		self.dirty_octaves = {}
		self.octave_expanded = {}
		
		Clock.schedule_once(self.on_octaves_loaded, 1)
	
		
	def on_octaves_loaded(self, *arg):
		if len(self.children) == 11:
			self.index_octaves()
	
	
	def get_midinum_note_ref(self, midinum):
		octnum = midinum // 12 - 1
		chroma = midinum % 12
		
		if self.octave_expanded[octnum]:
			oct_ref = self.dirty_octaves.get(octnum, None)
			return oct_ref.get_chroma_note_ref(chroma)
		else:
			return None
		
				
	def expand_between_min_max(self, min_midinum, max_midinum):
		min_octnum = min_midinum // 12 - 1
		max_octnum = max_midinum // 12 - 1
		
		#print(f'min octave:{min_octnum}, expanded:{self.octave_expanded[min_octnum]}; max octave:{max_octnum}, expanded:{self.octave_expanded[max_octnum]}')
		
		#if min and max octaves are already expanded, we are done
		if self.octave_expanded[min_octnum] and self.octave_expanded[max_octnum]:
			return
			
		mid_octnum = (max_octnum - min_octnum) // 2
		
		if not self.octave_expanded[min_octnum]:
			if self._can_expand(min_octnum):
				self._expand_octave(min_octnum)
			else:
				for octnum in range(mid_octnum, min_octnum-1, -1):
					if self._can_expand(octnum):
						self._expand_octave(octnum)
				
		if not self.octave_expanded[max_octnum]:
			if self._can_expand(max_octnum):
				self._expand_octave(max_octnum)
			else:
				for octnum in range(mid_octnum, max_octnum+1):
					if self._can_expand(octnum):
						self._expand_octave(octnum)

	
	def index_octaves(self):
		for child in self.children:
			if isinstance(child, Octave) or isinstance(child, PartialOct):
				self.orig_octaves[child.octnum] = child
				self.dirty_octaves[child.octnum] = child
				self.octave_expanded[child.octnum] = True
			else:
				self.octave_expanded[child.octnum] = False


	def can_expand(self, OctaveObjectRef):
		#if already expanded, can't expand [further]
		if isinstance(OctaveObjectRef, Octave) or isinstance(OctaveObjectRef, PartialOct):
			return False
		
		return self._can_expand(OctaveObjectRef.octnum)

	
	def can_collapse(self, OctaveObjectRef):
		if isinstance(OctaveObjectRef, CollapsedOct):
			return False
		
		return self._can_collapse(OctaveObjectRef.octnum)
	
	
	# expand octaves from innermost to outermost
	def expand_octave(self, OctaveObjectRef):
		
		if not self.can_expand(OctaveObjectRef):
			return
		
		self._expand_octave(OctaveObjectRef.octnum)
		
		
	# only collapse topmost and bottommost [expanded] octaves
	def collapse_octave(self, OctaveObjectRef):
		
		if len(self.orig_octaves) < 11:
			self.index_octaves()
		
		if not self.can_collapse(OctaveObjectRef):
			return
			
		self._collapse_octave(OctaveObjectRef.octnum)
		
				
	def _can_expand(self, octnum):
		# when all octaves are collapsed, any one can be expanded
		if not True in list(self.octave_expanded.values()):
			return True
		
		if octnum == -1:
			if self.octave_expanded[0] == True:
				return True
			else:
				return False
		
		if octnum == 9:
			if self.octave_expanded[8] == True:
				return True
			else:
				return False
		
		if self.octave_expanded[octnum - 1] == True or self.octave_expanded[octnum + 1] == True:
			return True
		
		return False

		
	def _expand_octave(self, octnum):
		if octnum == 9:
			new_content_size = self.note_scroller_ref.cont_sz_y + 6
		else:
			new_content_size = self.note_scroller_ref.cont_sz_y + 10
		
		#print(f'NoteGrid before expanding, NoteGrid.height: {self.height}; cont_sz_y:{self.note_scroller_ref.cont_sz_y}; after, should be: {new_content_size}')
		self.dirty_octaves[octnum] = self.orig_octaves[octnum]
		self.octave_expanded[octnum] = True
		
		self._reattach_children(new_content_size)
	
	
	def _can_collapse(self, octnum):
		if octnum == -1 or octnum == 9:
			return True
		
		if self.octave_expanded[octnum - 1] == False or self.octave_expanded[octnum + 1] == False:
			return True
		
		return False	
		
		
	def _collapse_octave(self, octnum):
		if octnum == 9:
			new_content_size = self.note_scroller_ref.cont_sz_y - 6
		else:
			new_content_size = self.note_scroller_ref.cont_sz_y - 10
		
		#print(f'NoteGrid before collapsing, NoteGrid.height: {self.height}; cont_sz_y:{self.note_scroller_ref.cont_sz_y}; after, should be: {new_content_size}')
		self.dirty_octaves[octnum] = CollapsedOct(octnum)
		self.octave_expanded[octnum] = False
		
		self._reattach_children(new_content_size)
		
		
	def _reattach_children(self, new_content_size):
		
		for child in self.children[::-1]:
			self.remove_widget(child)
		
		dict_tuples = sorted(self.dirty_octaves.items(), key=lambda item: item[0], reverse=True)
		
		for item in dict_tuples:
			self.add_widget(item[1])
		
		#print(f'NoteGrid resizing, cont_sz_y:{self.note_scroller_ref.cont_sz_y}; NoteGrid.height: {self.height};  LinedNoteGrid.height: {self.note_scroller_ref.track_tabs.lined_note_grid.height}')
		#print(f'NoteGrid _reattach_children, before content size change, grid_sz_y:{self.note_scroller_ref.grid_sz_y}')
		
		self.note_scroller_ref.cont_sz_y = new_content_size
		
		#print(f'NoteGrid _reattach_children, NoteScroll.cont_sz_y:{self.note_scroller_ref.cont_sz_y}, cont_sz_mult_y:{self.note_scroller_ref.cont_sz_mult_y}; grid_sz_y:{self.note_scroller_ref.grid_sz_y}')
		
		for child in self.children:
			if isinstance(child, Octave):
				child.size_hint = 1, 12 / new_content_size
			elif isinstance(child, PartialOct):
				child.size_hint = 1, 8 / new_content_size
			elif isinstance(child, CollapsedOct):
				child.size_hint = 1, 2 / new_content_size
	
	#print(f'NoteGrid resized, cont_sz_y:{self.note_scroller_ref.cont_sz_y}; NoteGrid.height: {self.height};  LinedNoteGrid.height: {self.note_scroller_ref.track_tabs.lined_note_grid.height}')
	
	

class LinedNoteGrid(Widget):
	bar_length = NumericProperty(0)
	beat_length = NumericProperty(0)
	
	def on_bar_length(self, instance, value):
		if self.note_scroller_ref is not None:
			self.note_scroller_ref.top_level_ref.toolbar_widget.last_bar_num = self.cont_sz_x / self.bar_length

	def redraw_grid_lines(self):
		# remove existing grid lines
		self.grid_lines.canvas.after.remove_group('octave')
		self.grid_lines.canvas.after.remove_group('note')
		self.grid_lines.canvas.after.remove_group('beat')
		self.grid_lines.canvas.after.remove_group('bar')
		
		bottom_collapsed = 0
		for (oct_num, is_expanded) in self.note_grid.octave_expanded.items():
			if not is_expanded:
				bottom_collapsed += 1
			else:
				break
				
		#if all octaves are collapsed, no need to draw any gridlines, we are done
		if bottom_collapsed == 11:
			return
		
		top_collapsed = 0
		for (oct_num, is_expanded) in reversed(self.note_grid.octave_expanded.items()):
			if not is_expanded:
				top_collapsed += 1
			else:
				break
				
		expanded_count = 11 - top_collapsed - bottom_collapsed	
		
		#self.note_scroller_ref.cont_sz_y is the number of notes (or number of notes and collapsed octaves - each collapsed octave 2x note_height)
		note_height = self.note_scroller_ref.cont_sz_mult_y
		visible_notes = expanded_count * 12 if top_collapsed > 0 else (expanded_count - 1) * 12 + 8		
		
		notegrid_y_pos = self.note_grid.oct_1.pos[1]
		grid_btm_pad = bottom_collapsed * 2 * note_height
		grid_bottom = grid_btm_pad + notegrid_y_pos
		grid_top = visible_notes * note_height + grid_bottom
		grid_width = self.width - self.h_pad
		
		tick_steps = self.note_scroller_ref.top_level_ref.time_scroller.time_line.ticker.ticks_minor
		
		# get x-positions of all ticks in TickSlider (4 values per vertex, 2 vertices per tickline)  
		x_divs = self.note_scroller_ref.top_level_ref.time_scroller.time_line.ticker_mesh.vertices[::8]

		# check how close together the minor ticks are -- if too close, only draw major ticks
		if x_divs[1] - x_divs[0] < 8:
			draw_minor = False
		else:
			draw_minor = True
		
		#print(f'note_height:{note_height}, visible_notes:{visible_notes}')
		
		# re-draw horizontal lines
		for i in range(visible_notes + 1):
			with self.grid_lines.canvas.after:
				if i % 12 == 0:
					Color(rgba=[0, 0, 0, .8], group='octave')
					Line(points=[self.h_pad, grid_bottom + i * note_height, grid_width, grid_bottom + i * note_height],
						 width=1, group='octave')
				elif i % 12 == 1:
					Color(rgba=[0, 0, 0, .5], group='note')
					Line(points=[self.h_pad, grid_bottom + i * note_height, grid_width, grid_bottom + i * note_height],
						 width=1, group='note')
				else:
					Line(points=[self.h_pad, grid_bottom + i * note_height, grid_width, grid_bottom + i * note_height],
						 width=1, group='note')
		
		# also set bar_length/beat_length variables
		self.bar_length = math.ceil(x_divs[tick_steps] - x_divs[0])
		self.beat_length = math.ceil(x_divs[1] - x_divs[0])
		
		#print(f'grid_width:{grid_width}, bar_length:{self.bar_length}, beat_length:{self.beat_length}')
		#print(f'cont_sz_x: {self.note_scroller_ref.cont_sz_x}')
		#print(f'cont_sz_mult_x: {self.note_scroller_ref.cont_sz_mult_x}')
		#print(f'int_grid_width: {self.note_scroller_ref.int_grid_width}')
		#print(f'time_line.width: {self.note_scroller_ref.top_level_ref.time_scroller.time_line.width}')
		#print(f'ticker.ticks_major: {self.note_scroller_ref.top_level_ref.time_scroller.time_line.ticker.ticks_major}')
		#print(f'ticker.width: {self.note_scroller_ref.top_level_ref.time_scroller.time_line.ticker.width}')
		
		# re-draw vertical lines
		for idx, x_pos in enumerate(x_divs):
			with self.grid_lines.canvas.after:
				if draw_minor == False:
					if idx % tick_steps == 0:
						Color(rgba=[0, 0, 0, .8], group='bar')
						Line(points=[x_pos, grid_bottom, x_pos, grid_top], width=1, group='bar')
				else:
					# draw lines corresponding to both minor and major ticks
					if idx % tick_steps == 0:
						Color(rgba=[0, 0, 0, .8], group='bar')
						Line(points=[x_pos, grid_bottom, x_pos, grid_top], width=1, group='bar')
					elif idx % tick_steps == 1:
						Color(rgba=[0, 0, 0, .5], group='beat')
						Line(points=[x_pos, grid_bottom, x_pos, grid_top], width=1, group='beat')
					else:
						Line(points=[x_pos, grid_bottom, x_pos, grid_top], width=1, group='beat')

	
	def tab_selected(self, active_track_idx):
		#refresh with current track markers?
		#currently done by class NoteScroll(ScrollView): def on_active_track(self, instance, value):
		pass
	
		
						
class TrackTabbedPanel(TabbedPanel):
	# playable_track_names = ListProperty([''])
	#cur_tab_num = NumericProperty(0)
	
	def __init__(self, **kwargs):
		super(TrackTabbedPanel, self).__init__(**kwargs)
		self.loaded = False
		Clock.schedule_once(self.on_panel_load)
	
	# def on_kv_post(self, instance):
		# self.on_panel_load

		
	def on_panel_load(self, *arg):
		self.on_new_file()
		self.loaded = True

		
	def _add_adder_tab(self):
		#TODO: create naming/renaming control, use it for adder_tab.content; 
		#only on the adder_tab: when change is accepted, delete/re-add adder_tab at the end
		adder_tab = AutoSizedTabItem(text='+', font_size=14)
		#adder_tab.content = 
		self.add_widget(adder_tab)
		adder_tab.active = False
		
		
	def on_new_file(self):
		#delete existing tabs, if any
		self.clear_tabs()		
		
		first_tab = self.ids.get('first_tab')
		first_tab.text = 'Track 1'
		self.add_widget(first_tab)

		self.note_scroller_ref.visual_track_lst.append(self.top_level_ref.toolbar_widget.play_ctrl.create_blank_track())
		
		self._add_adder_tab()

		#self.tab_list[0].active = True

		
	def on_file_open(self, playable_track_names):
		#delete existing tabs
		self.clear_tabs()
		
		total_letters = '..'.join(playable_track_names)
		first_tab = self.ids.get('first_tab')
		
		for name in playable_track_names:
			tab = AutoSizedTabItem(text=name, font_size=14)
			tab.content = first_tab.content
			self.add_widget(tab)
			
			if len(total_letters) > 120:
				tab.shorten = True
				
			tab.active = False
	
		self._add_adder_tab()
		
		#self.tab_list[0].active = True


	def on_current_tab(self, instance, value):
		# tabs are displayed in reverse order, so the first tab is the last in self.tab_list
		if self.loaded and self._current_tab.text != '+':
			self.note_scroller_ref.prev_active_track = self.note_scroller_ref.active_track
			active_track_idx = len(self.tab_list) - self.tab_list.index(self.current_tab) - 1
			self.note_scroller_ref.active_track = active_track_idx
			#print(f'tab #{active_track_idx} activated, previous active tab {self.note_scroller_ref.prev_active_track}')
			
		if self._current_tab.text != '' and  self._current_tab.text != '+':
			self._current_tab.content.tab_selected(active_track_idx)
	
	

# note_scroller
class NoteScroll(ScrollView):
	editable = BooleanProperty(False)
	# lined_note_grid = ObjectProperty(None)
	visual_track_lst = ObjectProperty([])	
	active_track = NumericProperty(0)
	prev_active_track = NumericProperty(-1)
	
	active_channel = ObjectProperty(None, allownone=True)
	scroll_x = NumericProperty(0)
	scroll_y = NumericProperty(0)
	cont_sz_mult_x = BoundedNumericProperty(1, min=1, max=50, errorhandler=lambda x: 1 if x < 1 else 50)
	cont_sz_mult_y = BoundedNumericProperty(8, min=8, max=20, errorhandler=lambda x: 8 if x < 8 else 20)
	cont_sz_y = NumericProperty(128)
	cont_sz_x = NumericProperty(1920)
	#grid_time_scale = NumericProperty(10)

	def clear_all_tracks(self):
		if len(self.visual_track_lst) > 0:
			#self.visual_track_lst[self.active_track].hide_track_markers()
			#del self.visual_track_lst[self.active_track]
			for idx, track in enumerate(self.visual_track_lst):
				track.hide_track_markers()
				del self.visual_track_lst[idx]
			self.visual_track_lst.clear()

		self.prev_active_track = -1
		self.active_track = 0	
		
			
	#channel color changed, check/change existing markers
	def update_channel_color(self, channel_num, color):
		if len(self.visual_track_lst) > 0:
			for v_trk in self.visual_track_lst:
				if v_trk.channels is not None and len(v_trk.channels) > 0:
					if channel_num in v_trk.channels:
						v_trk.channels[channel_num].chn_color = color
			
		
	def on_active_track(self, instance, value):
		if value < len(self.visual_track_lst):
			if self.prev_active_track != -1 and self.prev_active_track < len(self.visual_track_lst):
				self.visual_track_lst[self.prev_active_track].hide_track_markers()
			self.visual_track_lst[value].display_track_markers()

			if self.visual_track_lst[value].voices_timed == False and len(self.visual_track_lst[value].channel_voice_dict) > 0:
				for item in self.visual_track_lst[value].channel_voice_dict.items():
					#print(f"active track idx: {value}, channel_num: {item[0]}, midi_voice_idx: {item[1]}")
					self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.set_instrument_from_track(channel_num=item[0], midi_voice_idx=item[1])

	
	def on_cont_sz_x(self, instance, value):
		self.recalc_grid_width()
	
	def on_cont_sz_mult_x(self, instance, value):
		self.recalc_grid_width()
		
		if instance.hbar is not None:
			self.recalc_lbl_pos(instance)
		else:
			self.lbl_ctr_x = .15 * self.h_pad
			self.key_pos_x = .1 * self.h_pad
		
		return True
	
	
	def on_scroll_x(self, instance, value):
		if self.top_level_ref.time_scroller.scroll_x != value:
			self.top_level_ref.time_scroller.scroll_x = value
			
		#[padding_left, padding_top, padding_right, padding_bottom]
		#self.track_tabs._tab_layout.padding[0]
		self.track_tabs._tab_layout.padding[0] = int(self.int_grid_width * value)
		if value <= .33:
			self.track_tabs.tab_pos = 'top_left'
			self.track_tabs._tab_layout.padding[0] = self.int_grid_width/3 - self.track_tabs._tab_strip.width
			#print(int(self.int_grid_width * value * .5))
			#self.track_tabs._tab_layout.padding[0] = int(self.int_grid_width * value * .5) #str(int(self.int_grid_width * value * .5)) + 'dp'
		elif value <= .66:
			self.track_tabs._tab_layout.padding[0] = 2 #'2dp'
			self.track_tabs._tab_layout.padding[2] = 2			
			self.track_tabs.tab_pos = 'top_mid'
		else:
			self.track_tabs._tab_layout.padding[2] = 50
			self.track_tabs.tab_pos = 'top_right'
			
		self.recalc_lbl_pos(instance)

				
	def recalc_grid_width(self):
		# calculate new container size
		self.int_grid_width = int(self.cont_sz_x * self.cont_sz_mult_x) + 2 * self.h_pad
		self.grid_sz_x = str(self.int_grid_width) + 'sp'
		#self.grid_time_scale = self.cont_sz_x / self.track_tabs.lined_note_grid.bar_length
		
		# set new timeline size
		self.top_level_ref.time_scroller.int_grid_width = self.int_grid_width

		
	def recalc_lbl_pos(self, instance):
		bar_x_pos = instance.hbar[0]
		scrollbar_len = instance.hbar[1]
		margin1 = self.int_grid_width * scrollbar_len * .017
		
		self.lbl_ctr_x = max(self.h_pad * 1.5, ((self.int_grid_width * bar_x_pos) + margin1))
		self.key_pos_x = max(self.h_pad + 2, ((self.int_grid_width * bar_x_pos)))
	
	
	def on_cont_sz_y(self, instance, value):
		#print(f'NoteScroll cont_sz_y changed to: {self.cont_sz_y}, cont_sz_mult_y is: {self.cont_sz_mult_y}, grid_sz_y is: {self.grid_sz_y}')
		#print(f'NoteScroll.grid_sz_y now:{self.grid_sz_y}; TrackTabbedPanel.height:{self.track_tabs.height}; LinedNoteGrid.height: {self.track_tabs.lined_note_grid.height}')
		self.recalc_grid_height()
		self.track_tabs.lined_note_grid.redraw_grid_lines()
		return True
	
	
	def on_cont_sz_mult_y(self, instance, value):
		#print(f'NoteScroll cont_sz_mult_y changed to: {self.cont_sz_mult_y}')
		self.font_sz = max(8, self.cont_sz_mult_y - (self.cont_sz_mult_y % 2) - 2)
		self.recalc_grid_height()
		return True
	
	
	def recalc_grid_height(self):
		# calculate new container size
		self.int_grid_height = int(self.cont_sz_y * self.cont_sz_mult_y) + 2 * self.v_pad + self.tab_strip_height
		self.grid_sz_y = str(self.int_grid_height) + 'sp'
	
	#print(f'in recalc_grid_height, cont_sz_y:{self.cont_sz_y}, cont_sz_mult_y:{self.cont_sz_mult_y}, grid_sz_y:{self.grid_sz_y}')


# set_tempo tempo=120bpm
# tempo = the number of microseconds (0.000001sec) per quarter note (beat = quarter note).
# tempo=120bpm (500000 microseconds per beat) .5 sec/ quarter note, represent in milliseconds on control
# numerator=4 denominator=4 clocks_per_click=24 notated_32nd_notes_per_beat=8
# denominator of the time signature is a negative power of 2 (i.e. 2 represents a quarter-note, 3 represents an eighth-note, etc).
# ignore denominator for now
# set ticks_minor to numerator of time sig
# clocks_per_click is the number of MIDI clocks between metronome clicks.
# number of notated 32nd-notes in a MIDI quarter-note (24 MIDI Clocks) is usually 8		

# 6sp for 1/32nd
# 12sp for 1/16
# 24sp for 1/8
# 48sp for 1/4

#-------------------------------------------------------------------------------------------------


class TickSlider(Slider, TickMarker):
	def _set_ticks(self, *args):
		super(TickSlider, self)._set_ticks(*args)
		
		if self.parent is not None and self.parent.top_level_ref is not None:
			self.parent.ticker_mesh = self._mesh
			self.parent.top_level_ref.note_scroller.track_tabs.lined_note_grid.redraw_grid_lines()
			self.parent.label_ticks()


class TickLabel(Label):
	def __init__(self, **kwargs):
		super(TickLabel, self).__init__(**kwargs)
		
		self.bind(on_texture_size=self.on_texture_size)
	
	def on_texture_size(self, *args):
		if self.texture:
			self.width = self.texture.width
			self.height = self.texture.height
			self.pos[0] = self.pos[0] - self.texture.width * 0.5


class Timeline(Widget):
	# initial values (empty grid)
	# cont_sz_x = 1920 (48sp for 1/4 note)
	# ticks_major = 96 ((actually 192sp), distance between major ticks, in DP (twice numeric value))
	# ticks_minor = 4
	# slide_max = 960
	# sets up the following proportions:
	# 10 measures, with 192sp per measure, each divided into 4 quarter measures, with 48sp per quarter measure
	
	ticker_mesh = ObjectProperty(None, allownone=True) 	#re-exposes ticker._mesh, useful for a variety of purposes

	# TODO: add time to the left once markers are in a structure (update marker position)
	def add_time_left(self):
		#same procedure as add_time_right, but shift all markers one bar to the right afterwards
		pass
	
	def add_time_right(self):
		one_bar = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.bar_length 	#192sp (=96dp * 2)
		
		#self.ticker.max = slide_max = initial value 960dp
		self.ticker.max += self.ticker.ticks_major
		self.top_level_ref.note_scroller.cont_sz_x += one_bar
		
		self.top_level_ref.note_scroller.recalc_grid_width()	
		#print(f'cont_sz_x: {self.top_level_ref.note_scroller.cont_sz_x}; int_grid_width: {self.top_level_ref.note_scroller.int_grid_width}; ticker.max: {self.ticker.max}; ticks_major: {self.ticker.ticks_major}')
	
	def expand_to_num_bars(self, num_bars):
		one_bar = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.bar_length 	#192sp (=96dp * 2)
		
		#self.ticker.max = slide_max = initial value 960dp
		self.ticker.max = num_bars * self.ticker.ticks_major
		self.top_level_ref.note_scroller.cont_sz_x = num_bars * one_bar
		
		self.top_level_ref.note_scroller.recalc_grid_width()	
		#print(f'cont_sz_x: {self.top_level_ref.note_scroller.cont_sz_x}; int_grid_width: {self.top_level_ref.note_scroller.int_grid_width}; ticker.max: {self.ticker.max}; ticks_major: {self.ticker.ticks_major}')
	
	def label_ticks(self, *args):
		steps = self.ticker.ticks_minor
		
		# first, remove all existing labels
		# for child in self.label_holder.children:
		# self.label_holder.remove_widget(child)
		self.label_holder.clear_widgets()
		
		# get x-positions of all ticks in TickSlider
		x_divs = self.ticker._mesh.vertices[::8]  # 4 values per vertex, 2 vertices per tickline
		
		for idx, x_pos in enumerate(x_divs):
			if idx % steps == 0:
				self.label_holder.add_widget(TickLabel(text=str(idx // steps), pos=(x_pos, 16)))
		# elif idx % steps == steps//2:
		# self.label_holder.add_widget(TickLabel(text='1/2', pos=(x_pos,16)))

		
	def player_progress(self, progress_list):
		progress_percent, progress_tt = progress_list
		
		#self.ticker.value = (self.slide_width-self.h_pad)*progress_percent/200.0
		ticks_per_bar = self.top_level_ref.left_panel.voltempo_ctrl.ticks_per_bar.val
		grid_scale = 2 * ticks_per_bar/self.top_level_ref.note_scroller.track_tabs.lined_note_grid.bar_length
		
		self.ticker.value = progress_tt / grid_scale
		
		#parent is TimelineScroll (time_scroller)
		if progress_percent > 0 and progress_percent < 100:
			self.parent.scroll_x = progress_percent/100
		
		if progress_tt == 0:
			self.top_level_ref.toolbar_widget.lbl_play_progress.text = ''
		else:
			self.top_level_ref.toolbar_widget.lbl_play_progress.text = str(round(progress_percent, 2)) + '%'
			
		return 0
	
		
	def user_is_seeking(self, new_pos):
		self.top_level_ref.toolbar_widget.lbl_play_progress.text = str(round(new_pos,2)) + '%'
		self.top_level_ref.toolbar_widget.play_ctrl.seeking(new_pos)
		return 0

		
	def user_done_seeking(self, new_pos):
		self.user_seek = False
		self.top_level_ref.toolbar_widget.lbl_play_progress.text = str(round(new_pos,2)) + '%'
		self.top_level_ref.toolbar_widget.play_ctrl.seek_released(new_pos)
		return 0

		

# time_scroller
class TimelineScroll(ScrollView):
	# cont_sz_x = NumericProperty(1280)
	# int_grid_width = NumericProperty(1280)
	# slide_min = NumericProperty(0)
	# slide_max = NumericProperty(100)
	# ticks_major = NumericProperty(10)
	# ticks_minor = NumericProperty(4)
	# slide_value = NumericProperty(0)
	
	scroll_x = NumericProperty(0)

	def on_scroll_x(self, instance, value):
		#print(f'scroller val: {value}; progress bar val: {self.time_line.ticker.value}')
		if self.top_level_ref.note_scroller.scroll_x != value:
			self.top_level_ref.note_scroller.scroll_x = value

