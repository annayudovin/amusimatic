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
# from kivy.core.window import Window

# local modules:
from source.midoplayer import TonePlayer, FilePlayer
from source.globals import *
from source.notegrid import Marker, Note, Octave, PartialOct, CollapsedOct, Notegrid, LinedNoteGrid, TrackTabbedPanel, NoteScroll, TickSlider, TickLabel, Timeline, TimelineScroll
from source.toolbar import Toolbar, SectionDropDown, FileDropDown, PlayCtrl
from source.dialogs import LoadDialog, SaveDialog, SettingsDialog
from source.custom import  USpinner, DrawerAccordion, DrawerAccordionItem, AutoSizedTabHeader, AutoSizedTabItem, GradientSlider, HSVColorPicker, HSVColorPickerDropDown, HSVTColorPicker, HSVTColorDropDown, HSVTColorMenuBtn, AdjusterBox, SliderAdjuster, VolumeAdjuster
from source.controlpanel import TempoTab, ChannelColor, ChannelCheck, ChannelDropDown, Channel, ChannelList, ChannelListDropDown, ChannelCtrlTab, ScaleNameSelector, IntervalStrSelector, ScalePicker, ScalePickerDropDown, RootNoteSelector, ScaleDisplay, SharpsHighlight, HighlightCtrlTab


class LeftTabbedPanel(TabbedPanel):
	# track_names = ListProperty([''])
	cur_tab_num = NumericProperty(0)
	
	def on_current_tab(self, instance, value):
		if self._current_tab.text != '':
			self._current_tab.content.tab_selected()
	
	
	def activate_tab_num(self, num=1):
		# tabs are displayed in reverse order, so the first tab is the last in self.tab_list
		self.switch_to(self.tab_list[-num], do_scroll=True)
		self.cur_tab_num = len(self.tab_list) - self.tab_list.index(self.current_tab)
		
			
	def reset_all_tabs(self):
		for tab in self.tab_list:
			if tab.text != '':
				tab.content.reset()
			
			

class ContainerLayout(GridLayout):
	toolbar_widget = ObjectProperty(None)
	note_scroller = ObjectProperty(None)
	left_panel = ObjectProperty(None)
	time_scroller = ObjectProperty(None)
	note_player = ObjectProperty(None)
	midi_player = ObjectProperty(None)
	
	# top_corner = ObjectProperty(None)
	# bottom_corner = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(ContainerLayout, self).__init__(**kwargs)
		
		self.note_player = TonePlayer() #verbose=False)
		self.midi_player = FilePlayer(outport=self.note_player.get_outport_ref())
	# Clock.schedule_once(self.on_tabs_loaded, 1)


# def on_tabs_loaded(self, *arg):
# pass


if __name__ == '__main__':
	class AmusimaticApp(App):
		kv_directory = 'source'
		
		def build(self):
			baseContainer = ContainerLayout()
			return baseContainer

	AmusimaticApp().run()
