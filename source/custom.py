#defines USpinner, DrawerAccordion, DrawerAccordionItem, AutoSizedTabHeader, AutoSizedTabItem, GradientSlider, HSVColorPicker, HSVColorPickerDropDown, HSVTColorPicker, HSVTColorDropDown, HSVTColorMenuBtn, AdjusterBox, SliderAdjuster, VolumeAdjuster


# <AdjusterBox@Widget>:
# <SliderAdjuster@Widget>
# <VolumeAdjuster@Widget>
# #-------------CUSTOM COLOR PICKERS--------
# <-GradientSlider@Slider>:
# <HSVColorPicker@Widget>:	
# <HSVColorPickerDropDown@DropDown>:
# <HSVTColorPicker@Widget>:	
# <HSVTColorMenuHdr@Widget>:			
# <HSVTColorMenuBtn@Widget>:
# <HSVTColorDropDown@DropDown>:
# #------------------------------------------
# <SpinnerOption@Button>:
# #------------------------------------------
# <-AccordionItem>:
# <HLightAccordion@DrawerAccordion>:


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

__all__ = ('USpinner', 'DrawerAccordion', 'DrawerAccordionItem', 'AutoSizedTabHeader', 'AutoSizedTabItem', 'GradientSlider', 'HSVColorPicker', 'HSVColorPickerDropDown', 'HSVTColorPicker', 'HSVTColorDropDown', 'HSVTColorMenuBtn', 'AdjusterBox', 'SliderAdjuster', 'VolumeAdjuster')

#------------------------------------------------------------------------------------------------------------------------------

class USpinner(Spinner):
	user_text = StringProperty('')
	user_updated = BooleanProperty(False)
	
	def __init__(self, **kwargs):
		self._selection_started = False
		super(USpinner, self).__init__(**kwargs)
	
	def on_user_updated(self, instance, data):
		if self.user_updated == True:
			if self.user_text != self.text:
				self.user_text = self.text
	
	def _on_dropdown_select(self, instance, data, *largs):
		self._selection_started = False
		self.user_updated = True
		super(USpinner, self)._on_dropdown_select(instance, data, *largs)
		self.user_text = data
	
	def on_release(self, *args):
		self._selection_started = True
		self.user_updated = False
	
	def _close_dropdown(self, *largs):
		self._selection_started = False
	
	def on_text(self, *args):
		if self._selection_started == True:
			self._selection_started = False
			self.user_updated = True
		else:
			self.user_updated = False

#------------------------------------------------------------------------------------------------------------------------------


class DrawerAccordion(Accordion):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def _do_layout(self, dt):
		children = self.children
		if children:
			all_collapsed = all(x.collapse for x in children)
		else:
			all_collapsed = False

		min_space = self.min_space
		min_space_total = len(children) * self.min_space
		w, h = self.size
		x, y = self.pos

		display_space = self.height - min_space_total

		if display_space <= 0:
			Logger.warning('Accordion: not enough space '
						   'for displaying all children')
			Logger.warning('Accordion: need %dpx, got %dpx' % (
				min_space_total, min_space_total + display_space))
			Logger.warning('Accordion: layout aborted.')
			return


		children = reversed(children)

		for child in children:
			child_space = min_space
			child_space += display_space * (1-child.collapse_alpha) #when child is collapsed, collapse_alpha=1.0 (when selected, 0.0)

			child._min_space = min_space
			child.x = x
			child.y = y + min_space_total - min_space + display_space * child.collapse_alpha
			child.orientation = self.orientation
			child.content_size = w, display_space
			child.width = w
			child.height = child_space

			y -= child_space


class DrawerAccordionItem(AccordionItem):
	def on_touch_down(self, touch):
		if not self.collide_point(*touch.pos):
			return
		if self.disabled:
			return True

		if self.collapse:
			self.collapse = False
			return True
		elif self.container_title.collide_point(*touch.pos):
			self.collapse = True

		return super(AccordionItem, self).on_touch_down(touch)

		
#------------------------------------------------------------------------------------------------------------------------------		

class AutoSizedTabHeader(TabbedPanelHeader):
	shorten = BooleanProperty(False)
	
	def _get_active(self):
		return self.state == 'down'
	
	def _set_active(self, value):
		self.state = 'down' if value else 'normal'
	
	active = AliasProperty(
		_get_active, _set_active, bind=('state',), cache=True)
	
	def __init__(self, **kwargs):
		super(AutoSizedTabHeader, self).__init__(**kwargs)
		self.full_text = self.text
		self.shorten = False
		
		self.size_hint_x = None
		self.bind(on_texture_size=self.on_texture_size)
	
	def on_texture_size(self, *args):
		if self.texture:
			self.width = self.texture.width + 12
	
	def on_shorten(self, instance, value):
		# print(f'on_shorten, value:{value}; shorten:{self.shorten}; state:{self.state}; text:{self.text};')
		if self.text == '':
			return
		
		if not hasattr(self, 'full_text'):
			return
		else:
			# print(f'on_shorten, text:{self.text}; full_text:{self.full_text}')
			if self.full_text == '':
				self.full_text = self.text
			# print(f'on_shorten, set full_text=text (full_text:{self.full_text})')
			elif self.text != self.full_text[0] and self.text != self.full_text:
				self.full_text = self.text
			# print(f'on_shorten, set full_text=text (full_text:{self.full_text})')
			
			if self.shorten == True:
				if self.active == False:
					# print(f'on_shorten, shorten is True & active is False, text:{self.text}; full_text:{self.full_text}; setting text=text[0]')
					self.text = self.text[0]
			elif self.text == self.full_text[0]:
				self.text = self.full_text
			# print(f'on_shorten, shorten is False, text:{self.text}; full_text:{self.full_text}; setting text=full_text')
	
	def on_active(self, instance, value):
		# print(f'on_active, value:{value}; active:{self.active}; state:{self.state}; text:{self.text}; full_text:{self.full_text}; shorten:{self.shorten}')
		if self.text == '':
			return
		
		if self.shorten == False:
			return
		
		if self.full_text == '':
			return
		
		if self.active == True:
			self.text = self.full_text
		# print(f'on_active, set self.text to full_text ({self.full_text})')
		else:
			self.text = self.text[0]
		# print(f'on_active, set self.text to text[0] ({self.text[0]})')


class AutoSizedTabItem(TabbedPanelItem, AutoSizedTabHeader):
	pass


#------------------------------------------------------------------------------------------------------------------------------		
#--------------------CUSTOM COLOR PICKERS--------------------------------------------------------------------------------------		

		
class GradientSlider(Slider):
	# overrides
	background_horizontal = ObjectProperty(None,
										   allownone=True)  # StringProperty('atlas://data/images/defaulttheme/sliderh_background')
	background_disabled_horizontal = ObjectProperty(None,
													allownone=True)  # StringProperty('atlas://data/images/defaulttheme/sliderh_background_disabled')
	background_vertical = ObjectProperty(None,
										 allownone=True)  # StringProperty('atlas://data/images/defaulttheme/sliderv_background')
	background_disabled_vertical = ObjectProperty(None,
												  allownone=True)  # StringProperty('atlas://data/images/defaulttheme/sliderv_background_disabled')
	cursor_image = ObjectProperty(None,
								  allownone=True)  # StringProperty('atlas://data/images/defaulttheme/slider_cursor')
	cursor_disabled_image = ObjectProperty(None,
										   allownone=True)  # StringProperty('atlas://data/images/defaulttheme/slider_cursor_disabled')
	
	# set existing
	padding = NumericProperty('8sp')
	background_width = NumericProperty('15sp')
	value_track_color = ColorProperty([1, 1, 1, .1])
	value_track_width = NumericProperty('10dp')
	
	# create new
	color_property = OptionProperty('hue', options=('hue', 'value', 'saturation', 'transparency'))
	sample_hue = BoundedNumericProperty(1, min=1, max=360, errorhandler=lambda x: 1 if x < 1 else 360)
	sample_rgb = ListProperty([0, 0, 0, 1])
	texture = ObjectProperty(None, allownone=True)
	texture_width = NumericProperty(360)
	
	def get_double_padding(self):
		if self.padding:
			tup = self.to_widget(self.padding, 0)
			return int(2 * tup[0])
		else:
			return 10
	
	double_padding = AliasProperty(get_double_padding, None)
	
	def __init__(self, **kwargs):
		self.texture = None
		self.texture_height = 20
		self.texture_width = 360
		self.create_gradient_texture()
		super(GradientSlider, self).__init__(**kwargs)
	
	def on_texture_width(self, *args):
		if self.color_property:
			self.create_gradient_texture()
	
	def on_color_property(self, *args):
		if self.color_property:
			self.create_gradient_texture()
	
	def on_sample_hue(self, *args):
		if self.color_property:
			self.create_gradient_texture()
	
	def on_sample_rgb(self, *args):
		if self.color_property:
			self.create_gradient_texture()
	
	def create_gradient_texture(self):
		self.texture_width = width = math.ceil(self.texture_width)
		self.texture = Texture.create(size=(self.texture_width, self.texture_height))
		
		rgb = self.sample_rgb
		hue = self.sample_hue
		
		# create the first line of pixels (fill self.texture_width) and flatten array to one dimension (ravel)
		# since color goes from (0,0,0) to (1,1,1), multiply each value in buffer by 255
		switchr = {'HUE': numpy.multiply(numpy.ravel([hsv_to_rgb(x / float(width), 1, 1) for x in range(width)]), 255),
				   'SATURATION': numpy.multiply(
					   numpy.ravel([hsv_to_rgb(float(hue) / 360.0, x / float(width), 1) for x in range(width)]), 255),
				   'VALUE': numpy.multiply(numpy.ravel([hsv_to_rgb(0, 0, x / float(width)) for x in range(width)]),
										   255),
				   'TRANSPARENCY': numpy.multiply(numpy.ravel([(.6 + x * (rgb[0] - .6) / width,
																.6 + x * (rgb[1] - .6) / width,
																.6 + x * (rgb[2] - .6) / width) for x in range(width)]),
												  255)}
		
		buffer = switchr.get(self.color_property.upper())
		# convert buffer to a simple list of integers and repeat the first line of pixels (self.texture_height) times
		buffer = list(buffer.astype(int)) * self.texture_height
		arr = array('B', buffer)  # array('B', [1, 2, 3...])
		
		self.texture.blit_buffer(arr, colorfmt='rgb', bufferfmt='ubyte')


class HSVColorPicker(Widget):
	sample_color = ListProperty([0, 0, 0, 1])
	display_color = ListProperty([0, 0, 0, 1])
	
	text_mode = OptionProperty('full', options=('abbreviated', 'full'))
	current_h = BoundedNumericProperty(1, min=1, max=360,
									   errorhandler=lambda x: 1 if x < 1 else 360)  # NumericProperty(0)
	current_v = BoundedNumericProperty(0, min=0, max=100,
									   errorhandler=lambda x: 0 if x < 0 else 100)  # NumericProperty(0)
	current_s = BoundedNumericProperty(0, min=0, max=100,
									   errorhandler=lambda x: 0 if x < 0 else 100)  # NumericProperty(0)
	
	# def __init__(self,**kwargs):
	# super(HSVColorPicker, self).__init__(**kwargs)
	
	def on_sample_color(self, instance, value):
		if not (hasattr(self, 'h_slider') or hasattr(self, 's_slider') or hasattr(self, 'v_slider')) \
				or self.h_slider == None or self.s_slider == None or self.v_slider == None:
			return False
		
		# set button background
		self.display_color = self.sample_color
		self.set_color_rgb(value[0], value[1], value[2])
		
		return True
	
	def reset_sample(self, rgba_color):
		self.sample_color = rgba_color
	
	def set_color_rgb(self, r, g, b):
		hsv = rgb_to_hsv(r, g, b)
		
		# the following also updates self.current_h self.current_s self.current_v (triggers events)
		self.h_slider.value = self.s_slider.sample_hue = math.ceil(round(hsv[0], 3) * 360)  # math.ceil(hsv[0] * 360)
		self.s_slider.value = int(hsv[1] * 100)
		self.v_slider.value = int(hsv[2] * 100)
	
	def set_color_hsv(self, h, s, v):
		if h > 1 or s > 1 or v > 1:
			hsv = [round(h / 360, 3), round(s / 100, 3), round(v / 100, 3)]
		else:
			hsv = [round(float(h), 3), round(float(s), 3), round(float(v), 3)]
		
		# the following also updates self.current_h self.current_s self.current_v (triggers events)
		self.h_slider.value = self.s_slider.sample_hue = math.ceil(hsv[0] * 360)
		self.s_slider.value = int(hsv[1] * 100)
		self.v_slider.value = int(hsv[2] * 100)
	
	def on_current_h(self, instance, value):
		self.update_color()
	
	# return True
	
	def on_current_s(self, instance, value):
		self.update_color()
	
	# return True
	
	def on_current_v(self, instance, value):
		self.update_color()
	
	# return True
	
	def update_color(self):
		lst = list(hsv_to_rgb(self.current_h / 360, self.current_s / 100, self.current_v / 100))
		lst.extend([1])
		self.display_color = [round(x, 3) for x in lst]  # round the color values to 3 decimals just to be neat
	
	def accept(self):
		self.sample_color = self.display_color
		self.dropdown_ref.select(self.sample_color)
	
	def clear_rejected(self):
		if self.sample_color != self.display_color:
			self.set_color_rgb(self.sample_color[0], self.sample_color[1], self.sample_color[2])


class HSVColorPickerDropDown(DropDown):
	caller = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(HSVColorPickerDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None
	
	def on_select(self, value):
		self.caller.chn_color = value
	
	def on_dismiss(self, *args):
		# if the selected sample_color is not accepted by user, reset HSVColorPicker's sample color to current channel's for next call
		self.color_picker.clear_rejected()


class HSVTColorPicker(Widget):
	sample_color = ListProperty([0, 0, 0, 1])
	display_color = ListProperty([0, 0, 0, 1])
	
	text_mode = OptionProperty('full', options=('abbreviated', 'full'))
	current_h = BoundedNumericProperty(1, min=1, max=360, errorhandler=lambda x: 1 if x < 1 else 360)
	current_v = BoundedNumericProperty(0, min=0, max=100, errorhandler=lambda x: 0 if x < 0 else 100)
	current_s = BoundedNumericProperty(0, min=0, max=100, errorhandler=lambda x: 0 if x < 0 else 100)
	current_t = BoundedNumericProperty(0, min=0, max=100, errorhandler=lambda x: 0 if x < 0 else 100)
	
	def on_sample_color(self, instance, value):
		if not (hasattr(self, 'h_slider') or hasattr(self, 's_slider') or hasattr(self, 'v_slider')) \
				or self.h_slider == None or self.s_slider == None or self.v_slider == None:
			return False
		
		# set button background
		self.display_color = self.sample_color
		self.set_color_rgba(value[0], value[1], value[2], value[3])
		
		return True
	
	def reset_sample(self, rgba_color):
		self.sample_color = rgba_color
	
	def set_color_rgba(self, r, g, b, a):
		hsv = rgb_to_hsv(r, g, b)
		
		# the following also updates self.current_h self.current_s self.current_v (triggers events)
		self.h_slider.value = self.s_slider.sample_hue = math.ceil(round(hsv[0], 3) * 360)
		self.s_slider.value = int(hsv[1] * 100)
		self.v_slider.value = int(hsv[2] * 100)
		self.t_slider.value = int(a * 100)
	
	def set_color_hsv(self, h, s, v):
		if h > 1 or s > 1 or v > 1:
			hsv = [round(h / 360, 3), round(s / 100, 3), round(v / 100, 3)]
		else:
			hsv = [round(float(h), 3), round(float(s), 3), round(float(v), 3)]
		
		# the following also updates self.current_h self.current_s self.current_v (triggers events)
		self.h_slider.value = self.s_slider.sample_hue = math.ceil(hsv[0] * 360)
		self.s_slider.value = int(hsv[1] * 100)
		self.v_slider.value = int(hsv[2] * 100)
		self.t_slider.value = 100
	
	def on_current_h(self, instance, value):
		self.update_color()
	
	def on_current_s(self, instance, value):
		self.update_color()
	
	def on_current_v(self, instance, value):
		self.update_color()
	
	def on_current_t(self, instance, value):
		self.update_color()
	
	def update_color(self):
		lst = list(hsv_to_rgb(self.current_h / 360, self.current_s / 100, self.current_v / 100))
		lst.extend([self.current_t / 100])
		self.display_color = [round(x, 3) for x in lst]  # round the color values to 3 decimals just to be neat
	
	def accept(self):
		self.sample_color = self.display_color
		self.dropdown_ref.select(self.sample_color)
	
	def clear_rejected(self):
		if self.sample_color != self.display_color:
			self.set_color_rgba(self.sample_color[0], self.sample_color[1], self.sample_color[2], self.sample_color[3])
	
	def print_sizes(self):
		print('widget size, pos', self.to_window(*self.size), self.to_window(*self.pos))
		print('t_slider size, pos', self.to_window(*self.t_slider.size),
			  self.to_window(*self.t_slider.pos))
		print('t_lbl size, pos', self.to_window(*self.ids.get("t_display").size),
			  self.to_window(*self.ids.get("t_display")))
		print('h_slider size, pos', self.to_window(*self.h_slider.size),
			  self.to_window(*self.h_slider.pos))
		print('h_lbl size, pos', self.to_window(*self.ids.get("h_display").size),
			  self.to_window(*self.ids.get("h_display").pos))
		print('s_slider size, pos', self.to_window(*self.s_slider.size),
			  self.to_window(*self.s_slider.pos))
		print('s_lbl size, pos', self.to_window(*self.ids.get("s_display").size),
			  self.to_window(*self.ids.get("s_display").pos))
		print('v_slider size, pos', self.to_window(*self.v_slider.size),
			  self.to_window(*self.v_slider.pos))
		print('v_lbl size, pos', self.to_window(*self.ids.get("v_display").size),
			  self.to_window(*self.ids.get("v_display").pos))
		print('color_btn size, pos',
			  self.to_window(*self.ids.get("select_button").size),
			  self.to_window(*self.ids.get("select_button").pos))
		print('separator size, pos', self.to_window(*self.separator.size),
			  self.to_window(*self.ids.separator.pos))


class HSVTColorDropDown(DropDown):
	caller = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(HSVTColorDropDown, self).__init__(**kwargs)
		self.caller = kwargs.get('caller') if 'caller' in kwargs else None
	
	def on_select(self, value):
		if self.caller is not None:
			if self.caller.parent is not None:
				if hasattr(self.caller.parent, "sample_color"):
					self.caller.parent.sample_color = value
				elif hasattr(self.caller, "sample_color"):
					self.caller.sample_color = value
			elif hasattr(self.caller, "sample_color"):
				self.caller.sample_color = value
		else:
			return value
	
	def open(self, widget):
		# propagate changes to color_picker
		self.color_picker.sample_color = self.sample_color
		super(HSVTColorDropDown, self).open(widget)
	
	def on_dismiss(self, *args):
		# if the selected sample_color is not accepted by user, reset HSVTColorPicker's sample color
		self.color_picker.clear_rejected()


class HSVTColorMenuBtn(Widget):
	
	def __init__(self, **kwargs):
		super(HSVTColorMenuBtn, self).__init__(**kwargs)
		self.dropdown = HSVTColorDropDown(caller=self)
	
	def edit(self):
		# print(f'self.dropdown.sample_color:{self.dropdown.sample_color}  (HSVTColorMenuBtn)self.sample_color:{self.sample_color}')
		self.dropdown.sample_color = self.sample_color
		self.dropdown.open(self)

#------------------------------------------------------------------------------------------------------------------------------		
#--------------------OTHER-----------------------------------------------------------------------------------------------------


class AdjusterBox(Widget):
	val = NumericProperty(0)
	
	def decrement(self):
		if self.power_of_2:
			if self.step > self.min:
				self.step -= 1
				self.val = 2 ** self.step
				if self.parent is not None and hasattr(self.parent, 'notify'):
					self.parent.notify(self, self.val)
		else:
			if self.val > self.min:
				self.val -= self.step
				if self.parent is not None and hasattr(self.parent, 'notify'):
					self.parent.notify(self, self.val)
	
	def increment(self):
		if self.power_of_2:
			if self.step < self.max:
				self.step += 1
				self.val = 2 ** self.step
				if self.parent is not None and hasattr(self.parent, 'notify'):
					self.parent.notify(self, self.val)
		else:
			if self.val < self.max:
				self.val += self.step
				if self.parent is not None and hasattr(self.parent, 'notify'):
					self.parent.notify(self, self.val)


class SliderAdjuster(Widget):
	val = NumericProperty(0)
	
	def on_adjuster_val(self, instance, value):
		# print('on_adjuster_val ', value)
		self.val = int(value)
		self.slider.value = int(value)
		return False
	
	def on_slider_value(self, instance, value):
		# print('on_slider_value ', value)
		self.val = int(value)
		self.adjuster_box.val = int(value)
		return False


# def on_kv_post(self, instance):
# Clock.schedule_once(self.show_sizes, 10)

# def show_sizes(self, *arg):
# print(f'{self.ids.get("title").text}')
# print(f'self:{self.size}, {self.pos}, {self.to_window(*self.pos, True)}')
# print(f'title:{self.to_window(*self.ids.get("title").size, True)}, {self.to_window(*self.ids.get("title").pos, True)}')
# print(f'adjuster_box:{self.to_window(*self.ids.get("adjuster_box").size, True)}, {self.to_window(*self.ids.get("adjuster_box").pos, True)}')
# print(f'slider:{self.to_window(*self.ids.get("slider").size, True)}, {self.to_window(*self.ids.get("slider").pos, True)}')


class VolumeAdjuster(Widget):
	absolute_selected = BooleanProperty(False)
	val = NumericProperty(0)
	
	def on_adjuster_val(self, instance, value):
		self.val = value
		return False
		
	
	def on_absolute_selected(self, instance, value):
		if value == True:
			self.adj_type_label.text = 'ABSOLUTE'
			self.vol_adjuster.val = 64
		else:
			self.adj_type_label.text = 'RELATIVE'
			self.vol_adjuster.val = 0
		return False



		