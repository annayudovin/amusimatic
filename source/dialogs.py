#defines LoadDialog, SaveDialog, SettingsDialog
# <LoadDialog@Popup>:
# <SaveDialog@Popup>:
# <SettingsDialog@Popup>:

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

from .globals import camel_to_snake, snake_to_camel

__all__ = ('LoadDialog', 'SaveDialog', 'SettingsDialog')

#------------------------------------------------------------------------------------------------------------------------------
#keep/use for iOS?
# class LoadDialog(Popup):
	# # def __init__(self, *args, **kwargs):
	# # super(LoadDialog, self).__init__(*args, **kwargs)
	# def __init__(self, **kwargs):
		# super().__init__()
		
		# appname = App.get_running_app().name
		# appdir = os.path.abspath(App.get_running_app().directory)
		# user_data_dir = App.get_running_app().user_data_dir
		# # print(f'appname: {appname}, path1: {appdir}, path2: {user_data_dir}')
		
		# self.initialpath = appdir
	
	# def load(self, filename):
		# # with open(os.path.join(path, filename[0])) as f:
		# # print(f.read())
		# print(f'selected: {filename}')
	
	# def selected(self, filename):
		# print(f'selected: {filename}')

class LoadDialog:
	pass
#------------------------------------------------------------------------------------------------------------------------------
#keep/use for iOS?
# class SaveDialog(Popup):
	# def save(self, filename):
		# # with open(os.path.join(path, filename), 'w') as stream:
		# # stream.write(self.text_input.text)
		# print(f'selected: {filename[0]}')
	
	# def selected(self, filename):
		# print(f'selected: {filename[0]}')

class SaveDialog:
	pass
	
#------------------------------------------------------------------------------------------------------------------------------
class SettingsDialog(Popup):
	# def __init__(self, *args, **kwargs):
	# super(SettingsDialog, self).__init__(*args, **kwargs)
	def __init__(self, **kwargs):
		super().__init__()
		self.caller = kwargs.get('caller')
		self.title = kwargs.get('title')  # 'SubjectXSettings'
		
		appname = App.get_running_app().name
		# nameroot = appname + '_' + self.title.lower().replace('settings', '')
		nameroot = appname
		
		self.jsonfname = kwargs.get('json_filename') if 'json_filename' in kwargs else nameroot + '.json'
		self.inifname = kwargs.get('ini_filename') if 'ini_filename' in kwargs else nameroot + '.ini'
		
		# self.caller is Toolbar, self.caller.top_level_ref is ContainerLayout
		# print(f'base container: {self.caller.top_level_ref}, title: {self.title}, json: {self.jsonfname}, ini: {self.inifname}')
		
		self.config = ConfigParser.get_configparser(name=self.title)
		if self.config == None:
			self.config = ConfigParser(name=self.title)
			
			# read the panel json definition, find corresponding objects/properties and set default values from initial app defs
			self.default_config_vals = None
			self.get_app_json_defaults()
		# setattr(self.config, 'default_config_vals', self.default_config_vals)
		
		# for item in self.default_config_vals.items():
		# if item[0] != '':
		# self.config.setdefaults(item[0],item[1])
		
		# #read ini file - if it doesn't exist, it will be created on first config change
		# self.config.read(self.inifname)
	
	# else:
	# self.default_config_vals = getattr(self.config, 'default_config_vals')
	
	# #create old values dictionary to roll back un-approved changes
	# self.old_config_vals = {sect: {k: v for k, v in self.config.items(sect)} for sect in self.config.sections()}
	
	# def reify_settings(self):
	# #recreate old values dictionary to roll back future un-approved changes
	# self.old_config_vals = {sect: {k: v for k, v in self.config.items(sect)} for sect in self.config.sections()}
	
	# for section in self.config.sections():
	# target_ref = self.caller.ids.get(camel_to_snake(section), None)
	
	# if target_ref is not None:
	# for k, v in self.config.items(section):
	# setattr(target_ref, k, v)
	
	# def save_settings(self, owner):
	# self.reify_settings()
	# owner.dismiss()
	
	# def undo_changes(self, owner):
	# for section in self.config.sections():
	# old_keys = self.old_config_vals[section]
	# for k, v in self.config.items(section):
	# if v != old_keys[k]:
	# self.config.set(section, k, old_keys[k])
	# self.config.write()
	# owner.dismiss()
	
	# def restore_defaults(self, owner):
	# for section in self.config.sections():
	# default_keys = self.default_config_vals[section]
	# for k, v in self.config.items(section):
	# if v != default_keys[k]:
	# self.config.set(section, k, default_keys[k])
	# self.config.write()
	# self.reify_settings()
	# owner.dismiss()
	
	# per kivy.config.py: no underscores ('_') are allowed in the section name!!!
	def get_app_json_defaults(self):
		
		def convert_el(dt, string):
			el0 = f"{{dt.get({repr(string)}, '')}}"
			el = eval('f"{}"'.format(el0))
			return el
		
		with open(self.jsonfname) as f:
			data = json.load(f)
		
		self.default_config_vals = {}
		
		for d in data:
			sect = convert_el(d, 'section')
			prop = convert_el(d, 'key')
			ref = self.caller.ids.get(camel_to_snake(sect), None)
			
			if ref is not None and hasattr(ref, prop):
				val = getattr(ref, prop)
				if sect in self.default_config_vals.keys():
					self.default_config_vals[sect].update({prop: val})
				else:
					self.default_config_vals[sect] = {prop: val}
		
		print(f'self.default_config_vals: {self.default_config_vals}')


# def on_open(self):

# setpanel = SettingsWithNoMenu()
# setpanel.add_json_panel(self.title, self.config, self.jsonfname)

# placeholder_ref = self.ids.get('placeholder', None)
# if placeholder_ref is not None:
# setpanel.size = placeholder_ref.size
# setpanel.pos = placeholder_ref.pos
# placeholder_ref.add_widget(setpanel)

# self.reify_settings()

