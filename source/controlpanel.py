#defines TempoTab, ChannelColor, ChannelCheck, ChannelDropDown, Channel, ChannelList, ChannelListDropDown, ChannelCtrlTab, ScaleNameSelector, IntervalStrSelector, ScalePicker, ScalePickerDropDown, RootNoteSelector, ScaleDisplay, SharpsHighlight, HighlightCtrlTab
		
# #--------------Volume/Tempo Controls Tab --------	
# <TimeSig@Widget>
# <ShortestNote@Widget>
# <TempoTab@Widget>
# #--------------Channel Controls Tab -------------
# <ChannelColor@Widget>	
# <ChannelCheck@Widget>:
# <ChannelDropDown@DropDown>:
# <Channel@Widget>:
# <ChannelList@BoxLayout>:
# <ChannelScroll@ScrollView>:		
# <ChannelListDropDown@DropDown>:
# <ChannelCtrlTab@BoxLayout>:
# #--------------Highlight Controls Tab -----------
# <ScaleNameSelector@Widget>:
# <IntervalStrSelector@Widget>:
# <ScalePicker@Widget>:
# <ScalePickerDropDown@DropDown>:
# <RootNoteSelector@Widget>:
# <ScaleDisplay@Widget>:
# <ScaleHLightList@Widget>:
# <ScaleHLightScroll@ScrollView>:
# <SharpsHighlight@Widget>:	
# <HighlightCtrlTab@BoxLayout>:

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

from kivy.garden.tickmarker import TickMarker
from kivy.uix.behaviors import ToggleButtonBehavior, ButtonBehavior
from kivy.properties import AliasProperty, BooleanProperty, BoundedNumericProperty, ColorProperty, ConfigParserProperty, \
	DictProperty, ListProperty, NumericProperty, ObjectProperty, OptionProperty, ReferenceListProperty, StringProperty, \
	VariableListProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Line, Rectangle, BorderImage, Canvas


from .globals import *
from .custom import DrawerAccordion, DrawerAccordionItem, HSVColorPicker, HSVColorPickerDropDown, HSVTColorMenuBtn
from .notegrid import Marker, Note, Octave, PartialOct, CollapsedOct, Notegrid, LinedNoteGrid, TrackTabbedPanel, NoteScroll, TickSlider, TickLabel, Timeline, TimelineScroll


__all__ = ('TempoTab', 'ChannelColor', 'ChannelCheck', 'ChannelDropDown', 'Channel', 'ChannelList', 'ChannelListDropDown', 'ChannelCtrlTab', 'ScaleNameSelector', 'IntervalStrSelector', 'ScalePicker', 'ScalePickerDropDown', 'RootNoteSelector', 'ScaleDisplay', 'SharpsHighlight', 'HighlightCtrlTab')
#------------------------------------------------------------------------------------------------------------------------------
#--------------Volume/Tempo Controls Tab -------------------------------------------------------------------------------------------

class TempoTab(Widget):
	
	def __init__(self, **kwargs):
		super(TempoTab, self).__init__(**kwargs)
		self.reset()
		
	
	def reset(self):
		self.global_vol_init = 0
		
		self.tempo_init = 500000			#default
		self.bpm_init = 120					#tempo2bpm(500000)
		self.tickdiv_init = 480				#default
		self.time_sig_init_numerator = 4		#default
		self.time_sig_init_denominator = 4		#default
		self.shortest_note_init = 32			#default

		if hasattr(self, 'tempo_ctrl') and self.tempo_ctrl is not None:
			self.tempo_ctrl.displ_only = False
		
			if hasattr(self, 'tab_selected') and hasattr(self, 'recalc_time_scale'):
				self.tab_selected()
				self.recalc_time_scale()

				
	def tab_selected(self):
		#refresh with default values
		
		if self.global_vol.val != 0:
			self.global_vol.val = self.global_vol_init
		if self.global_vol.absolute_selected == True:
			self.global_vol.absolute_selected = False
		
		if self.bpm_init != self.tempo_ctrl.val:
			self.tempo_ctrl.val = self.bpm_init
		
		if self.tickdiv_init != self.tickdiv_ctrl.val:
			self.tickdiv_ctrl.val = self.tickdiv_init

		if self.time_sig_init_numerator != self.time_sig_ctrl.numerator.val:
			self.time_sig_ctrl.numerator.val = self.time_sig_init_numerator
		
		if self.time_sig_init_denominator != self.time_sig_ctrl.denominator.val:
			self.time_sig_ctrl.denominator.val = self.time_sig_init_denominator
		
		if self.shortest_note_init != self.shortest_note.denominator.val:
			self.shortest_note.denominator.val = self.shortest_note_init


	def set_from_file(self, tempo=500000, single_tempo=True, tickdiv=480, tsig_n=4, tsig_d=4, ticks_per_bar=1920):
		self.tickdiv_ctrl.val = self.tickdiv_init = tickdiv
		self.time_sig_ctrl.numerator.val = self.time_sig_init_numerator = tsig_n
		self.time_sig_ctrl.denominator.val = self.time_sig_init_denominator = tsig_d
		self.tpb_ctrl.val = ticks_per_bar
		
		self.tempo_init = tempo
		self.tempo_ctrl.val = self.bpm_init = tempo2bpm(tempo)
		if not single_tempo:
			self.tempo_ctrl.displ_only = True
	
	def adjust_volume(self):
		# TODO: check if file is loaded, update volume of all tracks in file		
		if self.global_vol_init != self.global_vol.val:
			self.global_vol_init = self.global_vol.val
			self.ctrl_tabpanel_ref.top_level_ref.note_player.set_volume(self.global_vol.val)

	def recalc_time_scale(self):
		self.tpb_ctrl.val = calculate_bar_ticks(self.time_sig_ctrl.numerator.val, self.time_sig_ctrl.denominator.val, self.tickdiv_ctrl.val)	
						
						
	def adjust_timing(self):
		pass


# TODO: implement tickdiv math


class TimeSig(Widget):

	def check_numerator():
		self.parent.recalc_time_scale()

	def check_denominator():
		self.parent.recalc_time_scale()

#----class TimeSig--------
# parent = TempoTab
# class TimeSig(BoxLayout):				
# numerator = ObjectProperty(None)

# def notify(self, notifier, value):
# if notifier != self.numerator:
# return

# bpm = value
# shortest_disp = self.parent.shortest_note.denominator.val
# initial_LCM = numpy.lcm(bpm, shortest_disp)
# GCD = math.gcd(shortest_disp, bpm)

# if isPowerOfTwo(bpm):
# divs = numpy.lcm(bpm, shortest_disp) #initial_LCM
# shortest_disp = math.gcd(48, divs)
# else:

# if shortest_disp > 2 and initial_LCM > 16:
# divs = numpy.lcm(bpm//GCD, max(2, GCD))
# shortest_disp = initial_LCM//divs
# else:
# divs = numpy.lcm(bpm//GCD, shortest_disp)
# #shortest_disp not updated in this case

# self.parent.shortest_note.denominator.val = int(shortest_disp)
# self.parent.shortest_note.denominator.step = int(Log2(shortest_disp))

# if isPowerOfTwo(divs) or (divs % 3 == 0 and isPowerOfTwo(divs//3) and divs < 33):
# self.ctrl_tabpanel_ref.top_level_ref.time_scroller.ticks_minor = int(divs)
#print(f'beats-per-measure: {bpm}, initial shortest displayed: {self.parent.shortest_note.denominator.val}, initial_LCM: {initial_LCM}, initial_GCD: {GCD}, divs: {divs}, shortest displayed note: {shortest_disp}')


#----class ShortestNote--------
# parent = TempoTab
# TempoTab.parent = LeftTabbedPanel.TabbedPanelItem
# class ShortestNote(BoxLayout):				
# denominator = ObjectProperty(None)

# def notify(self, notifier, value):
# divs = self.parent.time_sig.numerator.val

# if isPowerOfTwo(divs) or (divs % 3 == 0 and isPowerOfTwo(divs//3) and numpy.lcm(divs, value) < 33):
# self.ctrl_tabpanel_ref.top_level_ref.time_scroller.ticks_minor = int(numpy.lcm(divs, value))

#print(f'shortest note divisor: {self.denominator.val}')
# self.ctrl_tabpanel_ref.top_level_ref.time_scroller.ticks_minor = int(LCM)




#------------------------------------------------------------------------------------------------------------------------------
#--------------Channel Controls Tab -------------------------------------------------------------------------------------------

class ChannelDropDown(DropDown):
	hidden = BooleanProperty(False)
	muted = BooleanProperty(False)
	caller = ObjectProperty(None)
	instruments_list = ListProperty()
	
	def __init__(self, **kwargs):
		self.instruments_list = instruments
		super(ChannelDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None
	
	def on_muted(self, instance, value):
		if self.caller.muted != value:
			self.caller.muted = value
		
		if self.chk_mute.active != value:
			self.chk_mute.active = value
	
	def on_hidden(self, instance, value):
		if self.caller.hidden != value:
			self.caller.hidden = value
		
		if self.chk_hide.active != value:
			self.chk_hide.active = value

	def instrument_selected(self, name):
		self.caller.midi_voice_idx = self.instruments_list.index(name)
		return True


class ChannelCheck(Widget):
	active = BooleanProperty(False)
	
	def on_active(self, instance, value):
		if self.chk_box.active != value:
			self.chk_box.active = value


class ChannelColor(Widget):
	chn_color = ObjectProperty(None)
	btn_color = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(ChannelColor, self).__init__(**kwargs)
		self.dropdown = HSVColorPickerDropDown(caller=self)
	
	def edit(self):
		self.dropdown.sample_color = self.chn_color
		self.dropdown.open(self.parent)
	
	def on_chn_color(self, instance, value):
		if not hasattr(self, 'owner') or not hasattr(self.owner, 'chn_color'):
			return
		
		# owner is channel (self.parent.parent is dropdown (self.parent is DropDown's internal GridLayout))
		if self.owner.chn_color != value:
			self.owner.chn_color = value
			
			if self.owner.hidden:
				hidden_value = sum([value[:3], [.05]], [])
				self.owner.btn_color = hidden_value
			else:
				self.owner.chn_color = value
				
			#propagate notification of channel color change, so existing markers can all be checked/changed
			self.owner.ctrl_tabpanel_ref.top_level_ref.note_scroller.update_channel_color(self.owner.cnum-1, value)


class Channel(ToggleButtonBehavior, Widget):
	cnum = NumericProperty(0)
	deleted = BooleanProperty(False)
	muted = BooleanProperty(False)
	hidden = BooleanProperty(False)
	midi_voice_idx = NumericProperty(0)
	
	def _get_active(self):
		return self.state == 'down'
	
	def _set_active(self, value):
		self.state = 'down' if value else 'normal'
	
	active = AliasProperty(
		_get_active, _set_active, bind=('state',), cache=True)
	

	def __init__(self, **kwargs):
		self.fbind('state', self._on_state)
		super(Channel, self).__init__(group='channels', **kwargs)
		self.dropdown = ChannelDropDown(caller=self)
	

	def edit(self):
		self.dropdown.width = self.width
		self.dropdown.chn_color = self.chn_color
		self.dropdown.midi_voice_idx = self.midi_voice_idx
		self.dropdown.open(self)
	

	def remove(self):
		self.parent.remove_channel(self)
	

	def on_cnum(self, instance, value):
		if value > 0:
			# _channel_dict[value] = self
			self.parent.channel_dict[value] = self
	

	def on_touch_up(self, touch):
		if not touch.ud.get('mrkr', None) is None:
			del touch.ud['mrkr']
	

	def _on_state(self, instance, value):
		if self.state == 'down':
			self.bcolor = [.3, .3, .3, 1]  # active
			self.parent.active_channel = self #parent is ChannelList
			self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel = self
			self._activate_midi_voice()
			self._release_group(self)
		#print(self.size)
		else:
			self.bcolor = [.1, .1, .1, 1]
			if self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel == self:
				self.parent.active_channel = None
				self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel = None
				top_channel = self.parent.first_visible_channel() #parent is ChannelList
				if top_channel != None:
					top_channel._activate_midi_voice()


	def on_group(self, *largs):
		super(Channel, self).on_group(*largs)
		if self.active:
			self._release_group(self)
	

	def on_muted(self, instance, value):
		if self.dropdown.muted != value:
			self.dropdown.muted = value
	

	def on_hidden(self, instance, value):
		if self.dropdown.hidden != value:
			self.dropdown.hidden = value


	def on_midi_voice_idx(self, instance, value):
		if self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel == self:
			self._activate_midi_voice(midi_voice = value)
		elif self.cnum == 1 and self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel == None:
			self._activate_midi_voice(midi_voice = value)
		else:
			return True


	def _activate_midi_voice(self, play_channel=-1, midi_voice=-1):
		if play_channel == -1: 
			play_channel = self.cnum - 1

		if midi_voice == -1:
			midi_voice = self.midi_voice_idx

		if self.ctrl_tabpanel_ref.top_level_ref.note_player is not None:
			self.ctrl_tabpanel_ref.top_level_ref.note_player.set_channel_instrument(channel=play_channel, midi_voice_idx=midi_voice)
		return True


class ChannelList(BoxLayout):
	def __init__(self, **kwargs):
		super(ChannelList, self).__init__(**kwargs)
		self.channel_dict = {}
		self.active_channel = None
	
	
	def get_channel_color(self, channel_num):
		return self.channel_dict[channel_num+1].chn_color
	
	
	def reset_all_instruments(self):
		for item in self.channel_dict.items():
			item[1].midi_voice_idx = 0

	
	def set_instrument_from_track(self, channel_num=-1, midi_voice_idx=-1):
		if str(type(channel_num)) == "<class 'int'>" and str(type(midi_voice_idx)) == "<class 'int'>":
			if channel_num > -1 and midi_voice_idx > -1:
				#midi_voice_idx assignment triggers an event, so only set value if it's actually being changed
				if self.channel_dict[channel_num+1].midi_voice_idx != midi_voice_idx:
					self.channel_dict[channel_num+1].midi_voice_idx = midi_voice_idx
		
		
	def first_visible_channel(self):
		if self.show_count > 0:
			# widgets are displayed in reverse order, so the first child is the last visible channel - we want the first
			for child in reversed(self.children):
				if isinstance(child, Channel) and child.hidden == False:
					return child
		
		return None
	
	
	def remove_channel(self, ChannelObjectRef):
		if self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel == ChannelObjectRef:
			self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel = None

		if self.active_channel == ChannelObjectRef:
			self.active_channel = None
			
		self.show_count -= 1
		# ChannelObjectRef.deleted = False
		ChannelObjectRef.deleted = True
		self.remove_widget(ChannelObjectRef)
	
	# technically only necessary after the show_count increases
	def adjust_height(self):
		self.height = 28 * self.show_count + 2 * (self.show_count - 1) + 6
	
	def prune_list(self):
		dict_tuples = sorted(self.channel_dict.items(), key=lambda item: item[0])
		self.show_count = 0
		
		# to get order right, clear the list first
		for item in dict_tuples:
			self.remove_widget(item[1])
		
		for item in dict_tuples:
			if not item[1].deleted:
				self.add_widget(item[1])
				self.show_count += 1
		
		# fix the scroll container height (in case more items are showing now)
		self.adjust_height()
	
	# called from the dropdown
	def clear_checks(self):
		for item in self.channel_dict.items():
			item[1].muted = False
			item[1].hidden = False
	
	# called from the dropdown
	def show_all(self):
		if self.show_count < 16:
			for item in self.channel_dict.items():
				item[1].deleted = False
		
		self.prune_list()
	
	# called from the dropdown
	def remove_hidden(self):
		for item in self.channel_dict.items():
			if item[1].hidden:
				item[1].deleted = True
		
		self.prune_list()
	
	# called from the dropdown
	# adds channels not marked as hidden to the currently visible list
	def show_unhidden(self):
		# if every channel is already showing, nothing to do here
		if self.show_count == 16:
			return
		
		for item in self.channel_dict.items():
			if not item[1].hidden:
				item[1].deleted = False
		
		self.prune_list()
	
	# called from the dropdown
	def remove_muted(self):
		for item in self.channel_dict.items():
			if item[1].muted:
				item[1].deleted = True
		
		self.prune_list()
	
	# called from the dropdown
	# adds channels not marked as hidden to the currently visible list
	def show_unmuted(self):
		# if every channel is already showing, nothing to do here
		if self.show_count == 16:
			return
		
		for item in self.channel_dict.items():
			if not item[1].muted:
				item[1].deleted = False
		
		self.prune_list()
	
	# called from the dropdown
	def just_one(self):
		for item in self.channel_dict.items():
			if item[1].cnum == 1:
				item[1].deleted = False
			else:
				item[1].deleted = True
		
		self.prune_list()


# class ChannelScroll(ScrollView):
# channel_list = ObjectProperty(None)

class ChannelListDropDown(DropDown):
	caller = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(ChannelListDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None


# def on_select(self, value):
# self.caller=ChannelScroll
# self.caller.channel_list...


class ChannelCtrlTab(BoxLayout):
	auto_select = BooleanProperty(False)
	
	def reset(self):
		pass
		
		
	def tab_selected(self):
		pass
		#print('channel tab')


# def switch_editable(self, ToggleButtonObject, toggleState):
# if toggleState == 'down':
# ToggleButtonObject.text = 'Editable'
# self.ctrl_tabpanel_ref.top_level_ref.note_scroller.editable = True
# else:
# ToggleButtonObject.text = 'Selectable'
# self.ctrl_tabpanel_ref.top_level_ref.note_scroller.editable = False
# if self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel is not None:
# self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel._set_active(False)
# self.ctrl_tabpanel_ref.top_level_ref.note_scroller.active_channel = None


#------------------------------------------------------------------------------------------------------------------------------
#--------------Highlight Controls Tab -----------------------------------------------------------------------------------------

class RootNoteSelector(Widget):
	root_color = ListProperty([1, 1, 1, 0])
	root_note = StringProperty('')
	root_val_list = ListProperty()
	bottom_pad = NumericProperty(0)
	
	def _get_sample_color(self):
		return self.root_color
	
	def _set_sample_color(self, value):
		self.root_color = value
	
	sample_color = AliasProperty(_get_sample_color, _set_sample_color)
	
	__events__ = ('on_resized_up', 'on_resized_down')
	
	def __init__(self, **kwargs):
		self.root_val_list = chroma_dict.keys()
		super(RootNoteSelector, self).__init__()
		
		Clock.schedule_once(self.on_selector_loaded, 1)
	
	def on_selector_loaded(self, *arg):
		# some bug creates two instances of HSVTColorMenuBtn on top of each other on __init__, only one is color_picker_menu_btn
		# removing both at the start seems to be the most expedient solution
		for child in self.children:
			if isinstance(child, HSVTColorMenuBtn):
				self.remove_widget(child)
	
	def set_root_note(self, text):
		self.root_note = chroma_dict[text]
	
	def reset(self):
		self.root_note_spnr.text = ''
		self.root_note = ''
	
	def color_magic(self, state):
		if state == 'down':
			self.bottom_pad = 45
			self.color_picker_menu_btn.sample_color = self.root_color
			self.add_widget(self.color_picker_menu_btn)
			self.dispatch('on_resized_up')
		else:
			self.bottom_pad = 0
			self.remove_widget(self.color_picker_menu_btn)
			self.dispatch('on_resized_down')
	
	def on_resized_up(self):
		pass
	
	def on_resized_down(self):
		pass


class IntervalStrSelector(Widget):
	scale_steps_list = ListProperty()
	interval_str = StringProperty('')
	intervals_list = ListProperty(['', '', '', '', '', '', '', '', ''])
	
	def __init__(self, **kwargs):
		self.intervals_list = [''] * 9
		self.scale_steps_list = scale_steps.keys()
		self.clean_interval_str = ''
		super(IntervalStrSelector, self).__init__(**kwargs)
	
	def on_interval_str(self, instance, value):
		if self.interval_str == '-'.join(self.intervals_list).rstrip('-'):
			return True
		else:
			intervals = self.interval_str.split('-')
			self.intervals_list = intervals + [''] * (9 - len(intervals))
	
	# currently not used
	def rm_between(self, interval_str):
		while '--' in interval_str:
			interval_str = interval_str.replace('--', '-')
		return interval_str
	
	# currently not used
	def validate_i_str(self):
		self.clean_interval_str = self.rm_between(self.interval_str.strip('-'))
		
		# redefine interval str and list from clean version
		if self.clean_interval_str in diatonic_scales.values() or self.clean_interval_str in other_scales.values():
			self.intervals_list = self.clean_interval_str.split('-') + [''] * (8 - self.clean_interval_str.count('-'))
			self.interval_str = self.clean_interval_str
	
	def update_interval_str(self, spinnr_inst, u_text):
		self.intervals_list[spinnr_inst.pos_num] = u_text
		self.interval_str = '-'.join(self.intervals_list).rstrip('-')


class ScaleNameSelector(Widget):
	diatonic_scales_list = ListProperty()
	other_scales_list = ListProperty()
	final_name = StringProperty('')
	
	def __init__(self, **kwargs):
		self.diatonic_scales_list = diatonic_scales.keys()
		self.other_scales_list = other_scales.keys()
		super(ScaleNameSelector, self).__init__(**kwargs)
	
	def scale_selected(self, type, name):
		#print(f'ScaleNameSelector(scale_namer) on_user_text->scale_selected(): type={type}, name={name}')
		#print(f'ScaleNameSelector(scale_namer) on_user_text->scale_selected(): other_scales.user_text={self.other_scales_spnr.user_text}, other_scales.text={self.other_scales_spnr.text}')
		#print(f'ScaleNameSelector(scale_namer) on_user_text->scale_selected(): self.diatonic_spnr={self.diatonic_spnr.user_text}, diatonic_spnr.text={self.diatonic_spnr.text}')
		
		if type == 'diatonic':
			if name != '':
				self.diatonic_spnr.text = self.diatonic_spnr.user_text
				self.other_scales_spnr.text = ''
				self.interval_str = diatonic_scales[name]
			else:
				self.interval_str = ''
		else:
			if name != '':
				self.other_scales_spnr.text = self.other_scales_spnr.user_text
				self.diatonic_spnr.text = ''
				self.interval_str = other_scales[name]
			else:
				self.interval_str = ''
		
		self.final_name = name
		
		#print(f'ScaleNameSelector(scale_namer) on_user_text->scale_selected(): final_name={self.final_name}, interval_str={self.interval_str}')
		return True


class ScalePicker(Widget):
	interval_str = StringProperty('')
	scale_name = StringProperty('')
	
	def init_vals(self, interval_s, s_name):
		
		if s_name == 'USER DEFINED' or s_name == '':
			self.scale_namer.diatonic_spnr.text = ''
			self.scale_namer.other_scales_spnr.text = ''
		
		elif s_name in diatonic_scales.keys():
			self.scale_namer.diatonic_spnr.text = s_name
			self.scale_namer.other_scales_spnr.text = ''
		
		elif s_name in other_scales.keys():
			self.scale_namer.other_scales_spnr.text = s_name
			self.scale_namer.diatonic_spnr.text = ''
		
		self.scale_namer.interval_str = interval_s
		
		self.string_definer.intervals_list = interval_s.split('-') + [''] * (8 - interval_s.count('-'))
		self.string_definer.interval_str = interval_s
	
	def intervals_to_scale(self, interval_s):
		# #from self.string_definer to self.scale_namer
		
		self.scale_namer.diatonic_spnr.text = ''
		self.scale_namer.other_scales_spnr.text = ''
		self.scale_namer.interval_str = ''
		
		# reverse recognition: if interval_str is found in a dictionary, name it
		if interval_s in diatonic_scales.values():
			l = [k for (k, v) in diatonic_scales.items() if v == interval_s]
			self.scale_namer.diatonic_spnr.text = l[0]
			self.scale_name = l[0]
		elif interval_s in other_scales.values():
			l = [k for (k, v) in other_scales.items() if v == interval_s]
			self.scale_namer.other_scales_spnr.text = l[0]
			self.scale_name = l[0]
		else:
			self.scale_name = 'USER DEFINED'
		
		self.interval_str = interval_s
		return True
	
	def scale_to_intervals(self, final_name, interval_s):
		# from self.scale_namer to self.string_definer
		
		if final_name != '':
			self.scale_name = final_name
		else:
			self.scale_name = 'USER DEFINED'
		
		self.interval_str = interval_s
		
		self.string_definer.intervals_list = interval_s.split('-') + [''] * (8 - interval_s.count('-'))
		self.string_definer.interval_str = interval_s
		
		return True
	
	def clear_rejected(self):
		self.scale_namer.diatonic_spnr.text = ''
		self.scale_namer.other_scales_spnr.text = ''
		self.scale_namer.interval_str = ''
		self.string_definer.intervals_list = [''] * 9
		self.string_definer.interval_str = ''
	
	def accept_selections(self):
		#print(f'ScalePicker scale_name: {self.scale_name}, interval_str: {self.interval_str}')
		self.dropdown_ref.select((self.scale_name, self.interval_str))


class ScalePickerDropDown(DropDown):
	caller = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(ScalePickerDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None
	
	def on_select(self, value):
		self.caller.scale_name = value[0]
		self.caller.interval_str = value[1]
	
	def on_dismiss(self, *args):
		self.scale_picker.clear_rejected()
	
	def init_vals(self, interval_s, s_name):
		self.scale_picker.init_vals(interval_s, s_name)


class ScaleDisplay(Widget):
	scale_color = ListProperty([1, 1, 1, 0])
	scale_chroma_list = ListProperty([])
	xpander = NumericProperty(0)
	
	def _get_sample_color(self):
		return self.scale_color
	
	def _set_sample_color(self, value):
		self.scale_color = value
	
	sample_color = AliasProperty(
		_get_sample_color, _set_sample_color, bind=('scale_color',))
	
	__events__ = ('on_resized_up', 'on_resized_down')
	
	def __init__(self, **kwargs):
		super(ScaleDisplay, self).__init__(**kwargs)
		self.dropdown = ScalePickerDropDown(caller=self)
		
		Clock.schedule_once(self.on_scale_display_loaded, 1)
	
	def on_scale_display_loaded(self, *arg):
		self.scale_color = self.init_color
		self.root_color = self.init_color
	
	def edit(self):
		#print(f'ScaleDisplay scale_name: {self.scale_name}, interval_str: {self.interval_str}')
		self.dropdown.init_vals(self.interval_str, self.scale_name)
		self.dropdown.open(self.name_disp)
	
	def shrink(self):
		# user de-selected option to set root note color separately, so reset current root color to current scale color
		self.root_color = self.scale_color
		self.xpander = 0
		self.root_separate = False
		self.dispatch('on_resized_down')
	
	def expand(self):
		self.root_color = self.scale_color  # initialize control's color with current scale color
		self.xpander = 45
		self.root_separate = True
		self.dispatch('on_resized_up')
	
	def on_resized_up(self):
		pass
	
	def on_resized_down(self):
		pass
	
	def reset(self):
		if self.h_light_on == True:
			#self.apply_hlight_chk.state = 'normal'
			self.apply('normal')
		
		self.scale_color = self.init_color
		self.root_color = self.init_color
		self.root_select.reset()
		self.scale_name = ''
		self.interval_str = ''
		self.scale_chroma_list.clear()
	
	def build_scale(self):
		self.scale_chroma_list.clear()
		idx = 0
		
		if self.root_note != '' and self.interval_str != '':
			# ----build list of pitches (as chroma idx) that make up the scale
			scale_intervals = self.interval_str.split('-')
			
			# get chroma index of the root note
			idx = chroma.index(self.root_note)
			self.scale_chroma_list.append(idx)
			
			# build the pitch class collection - root_note's idx is now the starting point
			# scale_steps={'':0, 'H':1, 'W':2, '3H':3, '2W':4, '4H':4}
			for si in scale_intervals:
				idx = (idx + scale_steps[si]) % 12
				self.scale_chroma_list.append(idx)
			
			# remove the last note if it's root to avoid duplicates (this is necessary because some scales end on a non-root note)
			if self.scale_chroma_list[0] == self.scale_chroma_list[-1]:
				self.scale_chroma_list = self.scale_chroma_list[:-1]
	
	#print(f'root_note: {self.root_note}({idx}) scale_name: {self.scale_name}  interval_str: {self.interval_str} scale_color: {self.scale_color}, root_color: {self.root_color}')
	#print(self.scale_chroma_list)
	
	def apply(self, state):
		# highlighting is turned on when (state == 'down') == True
		self.h_light_on = (state == 'down')
		
		#print(f'self.root_note:{self.root_note}; self.interval_str: {self.interval_str}; self.scale_color: {self.scale_color}; self.init_color: {self.init_color}')
		
		# validate user input -- apply highlighting only if we have meaningful directions
		if self.root_note != '' and self.interval_str != '' and self.scale_color[3] != 0:
			
			if self.root_separate and (self.root_color == self.init_color or self.root_color == self.scale_color):
				self.root_separate = False
			
			self.build_scale()
			
			if self.h_light_order != 0:
				# group_name = 'h_light' + str(self.h_light_order)
				color_attr = 'hl' + str(self.h_light_order) + '_color'
			else:
				# group_name = 'h_light1'
				color_attr = 'hl1_color'
			
			note_grid_ref = self.ctrl_tabpanel_ref.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
			root_chroma = self.scale_chroma_list[0] if self.root_separate else -1
			
			for child in note_grid_ref.children:
				if not isinstance(child, CollapsedOct):
					for note_ref in child.note_stack.children:
						# get color object pointer, in case we need to change it
						# color_ref = note_ref.canvas.get_group(group_name)[0]
						
						if self.h_light_on:  # apply highlighting
							if note_ref.chroma in self.scale_chroma_list:  # this note belongs to our scale
								if note_ref.chroma == root_chroma:  # when separate root color is not applied, root_chroma is -1 (and ours start at 0)
									# color_ref.rgba = self.root_color
									if hasattr(note_ref, color_attr):
										setattr(note_ref, color_attr, self.root_color)
								else:
									# color_ref.rgba = self.scale_color
									if hasattr(note_ref, color_attr):
										setattr(note_ref, color_attr, self.scale_color)
						else:  # remove highlighting - reset all highlight group to transparent
							# color_ref.rgba = [0,0,0,0]
							if hasattr(note_ref, color_attr):
								setattr(note_ref, color_attr, [0, 0, 0, 0])
		
		
		else:  # not enough information to act on, set highlighting to off if user set to 'on'
			if self.h_light_on:
				#self.apply_hlight_chk.state = 'normal'
				self.h_light_on = False
				
				# if self.root_note == '' :
				#print(f'self.root_note:{self.root_note} (not definded)')
				# if self.interval_str == '' :
				#print(f'self.interval_str: {self.interval_str}; (not defined)')
				# if self.scale_color == self.init_color:
				#print(f'self.scale_color {self.scale_color} == self.init_color {self.init_color}')
				return

#class HLightAccordion(DrawerAccordion):
class SharpsHighlight(Widget):
	current_transp = BoundedNumericProperty(30, min=0, max=100, errorhandler=lambda x: 0 if x < 0 else 100)
	sharps_on = BooleanProperty(True)

	def accept(self):
		if self.sharps_on:
			self.set_sharps_alpha(self.current_transp / 100)


	def reset(self):
		self.current_transp = 30

		if self.sharps_on:
			self.set_sharps_alpha(self.current_transp / 100)


	def on_current_transp(self, instance, value):
		self.transp_slider.value = 100 - int(value)
		return True

	# highlight sharps (independently of keyboard switch)
	# highlighting is turned on when (state == 'down') == True
	def highlight_sharps(self, state):
		self.sharps_on = (state == 'down')
		
		if self.sharps_on:
			self.set_sharps_alpha(self.current_transp / 100)
		else:
			self.set_sharps_alpha(0)


	def set_sharps_alpha(self, value):
		note_grid_ref = self.ctrl_tabpanel_ref.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
		for child in note_grid_ref.children:
				if not isinstance(child, CollapsedOct):
					for gchild in child.note_stack.children:
						gchild.sharps_alpha = value



class HighlightCtrlTab(BoxLayout):
	def tab_selected(self):
		pass
		
	def reset(self):
		pass
		
