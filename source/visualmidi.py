
import mido
import math
from copy import deepcopy

from mido import Message, MetaMessage, MidiFile
from .globals import *
from .notegrid import Marker
from .midoext import ExtMessage
#from .midoplayer import printMIDOTrackToConsole, printMIDOTrackToText, printListToText, printNestedListToText, ExtMessage, ExtMetaMessage, LoadedTrack, FilePlayer

#__all__ = ('VisualTrack')


#def printMIDOTrackToConsole(track):
#def printMIDOTrackToText(textFilename, track):
#def printListToText(textFilename, list):
#def printNestedListToText(textFilename, list):


	
def calculate_midi_bars(bar_len, song_total_ticks):
	return math.ceil(song_total_ticks/bar_len)

	
class VisualNote:

	def __init__(self, **kwargs):
		self.channel = kwargs.get('channel', -1)
		self.midinum = kwargs.get('midinum', -1)	
		self.tt_on = kwargs.get('tt_on', -1)		
		self.tt_off = kwargs.get('tt_off', -1)
		self.velocity = kwargs.get('velocity', 64)

	def __str__(self):
		return f"channel: {self.channel}; midinum: {self.midinum}; velocity: {self.velocity}; tt_on: {self.tt_on}; tt_off: {self.tt_off}"		
		
		
	def to_midi(self):
		on_msg = Message('note_on', channel=self.channel, note=self.midinum, velocity=self.velocity)
		ext_on_msg = ExtMessage.extend(on_msg)
		ext_on_msg.tt = self.tt_on
		
		off_msg = Message('note_off', channel=self.channel, note=self.midinum, velocity=0)
		ext_off_msg = ExtMessage.extend(off_msg)
		ext_off_msg.tt = self.tt_off

		return ext_on_msg, ext_off_msg

		
		
class VisualChannel:
	def __init__(self, **kwargs):
		self.chn_num = kwargs.get('channel', -1)
		self._color = kwargs.get('color', [0,0,0,0])
		self._midi_voice = 0
		self.note_lst = kwargs.get('notes', [])
		self.marker_lst = kwargs.get('markers', [])
	
	def __str__(self):
		return f"channel: {self.chn_num}; len note_lst: {len(self.note_lst)}"		
		
	def init_color(self, color):
		self._color = color
		
	#when the color of the channel changes, all markers belonging to the channel change color accordingly
	def color_setter(self, value):
		if self._color == value:
			return
		else:
			self._color = value
			for mrkr in self.marker_lst:
				mrkr.chn_color = value
				
	def color_getter(self):
		return self._color

	chn_color = property(color_getter, color_setter)

	
	def has_notes(self):
		if len(self.marker_lst) > 0 or len(self.note_lst) > 0:
			return True			
		return False
	
	
	def msg_lst(self):
		msglist = []
		
		# i = 0
		for note in self.note_lst:
			msglist += [*note.to_midi()]
			# i += 1
			# if i == 10:
				#print(msglist)
		
		msglist.sort(key=lambda msg: (msg.tt, msg.type))
		return msglist
	
	
class VisualTrack:
	#if loading file, order of operations: __init__ finishes (called from midoplayer.py process_all_playable_tracks), then
	#midoplayer.py process_all_playable_tracks verifies note_on and note_off mido messages by calling match_on_offs
	#match_on_offs also creates a VisualNote object for each "verified" note_on and note_off pair, returns a list of those
	#process_all_playable_tracks then calls VisualTrack.add_note_list and passes it list of VisualNotes received from match_on_offs
	#toolbar.py PlayCtrl.open then calls VisualTrack.visualize on each of its list of self.visual_tracks
		
	#kwargs: (top_level_ref=top_level_ref, tick_len=total_ticks, ticks_per_beat=midi_file.ticks_per_beat, time_sig_n=numerator, time_sig_d=denominator, mido_track=track))
	def __init__(self, **kwargs):
		self.track_total_ticks = kwargs.get('tick_len', 0)
		self.ticks_per_beat = kwargs.get('ticks_per_beat', 480)		#default=480	
		self.time_sig_numerator = kwargs.get('time_sig_n', 4)		
		self.time_sig_denominator = kwargs.get('time_sig_d', 4)
		self.top_level_ref = kwargs.get('top_level_ref', None)
		self.single_tempo = True
		self.tempo = 500000			#default
		
		self.channel_voice_dict = {}
		self.voices_timed = False
		
		self.ticks_per_bar = calculate_bar_ticks(self.time_sig_numerator, self.time_sig_denominator, self.ticks_per_beat)
		self.bars = max(10, calculate_midi_bars(self.ticks_per_bar, self.track_total_ticks))

		self.track_name = ''
		self.min_midinum = -1
		self.max_midinum = -1
		self.channels = None
		self.silent_msg_lst = []
		self.note_msg_lst = []
		
		self.dirty = False
				
		if 'mido_track' in kwargs:
			self._mine_mido_track(kwargs.get('mido_track'))

		
	def _get_min_max_midinum(self, mido_track):
		#get max and min midinum (msg.note) from mido_track
		midinum_list = [msg.note for msg in mido_track if msg.type == 'note_on']
		self.min_midinum = min(midinum_list)
		self.max_midinum = max(midinum_list)	
	
	
	def _mine_mido_track(self, mido_track):
		name_msg = next((msg for msg in mido_track if msg.type == 'track_name'), None)
		self.track_name = name_msg.name if name_msg is not None else 'Track'
		self._get_min_max_midinum(mido_track)
		# don't display these, but leave them in the list: msg.type == 'track_name' and msg.type == 'end_of_track'
		self.silent_msg_lst = [msg for msg in mido_track if msg.type != 'note_on' and msg.type != 'note_off']
		self.note_msg_lst = [msg for msg in mido_track if msg.type == 'note_on' or msg.type == 'note_off']		

		self._check_channel_voices()
		
	
	def _check_channel_voices(self):
		self.channel_voice_dict.clear()
		
		if self.silent_msg_lst is None:
			return None

		voice_messages = [msg for msg in self.silent_msg_lst if msg.type == 'program_change']
		
		if len(voice_messages) > 0:	
			#determine if complex handling is necessary:
			chn_lst = [msg.channel for msg in voice_messages]
			
			#more than one program_change message for a channel indicates that channel changes voices during play
			if len(chn_lst) > len(set(chn_lst)):
				#double check			
				for chn_num in chn_lst:
					instrument_lst = [msg.program for msg in voice_messages if msg.channel == chn_num]
					#if multiple program_change messages for the same channel indicate more than one unique instrument, complex case confirmed
					if len(set(instrument_lst)) > 1:
						self.voices_timed = True
						break
				#handle case where a channel changes voices during play (more than one program_change message encountered for channel)		
				for msg in voice_messages:
					self.channel_voice_dict[msg.channel, msg.tt] = msg.program		
						
			else:
				for msg in voice_messages:
					self.channel_voice_dict[msg.channel] = msg.program
					

	def _check_octaves_expanded(self):
		if self.note_grid_ref is None:
			return False

		if self.min_midinum == -1 or self.max_midinum == -1:
			return False
			
		#check if max and min octaves are expanded, if not, expand all prior octaves and max/min octaves
		self.note_grid_ref.expand_between_min_max(self.min_midinum, self.max_midinum)
		return True
		
		
	def _get_midinum_note_ref(self, midinum):
		#note_grid_ref = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
		if self.note_grid_ref is None:
			return None
		return self.note_grid_ref.get_midinum_note_ref(midinum)	

		
	def has_notes(self):	
		if self.channels is not None:
			for channel in self.channels.values():
				if len(channel.marker_lst) > 0 or len(channel.note_lst) > 0:
					return True
					
		return False
			
			
	def set_single_tempo(self, tempo):
		self.single_tempo = True
		self.tempo = tempo
	
	
	def set_avg_tempo(self, tempo_msg_lst):
		self.single_tempo = False
		
		sum = 0
		for msg in tempo_msg_lst:
			sum += msg.tempo
		
		self.tempo = sum/len(tempo_msg_lst)
		
	
	def add_marker(self, marker):
		if self.channels is None:
			self.channels = {}	
	
		if marker.channel in self.channels:
			if not marker in self.channels[marker.channel].marker_lst:
				self.channels[marker.channel].marker_lst.append(marker)
				self.channels[marker.channel].marker_lst.sort(key=lambda mrkr: mrkr.tt_on)
		else:	#add a new channel
			self.channels[marker.channel] = VisualChannel(channel=marker.channel, color=marker.chn_color, markers=[marker])
			
		if not (marker.tt_on == 0 and marker.tt_off == 0):
			note_list = self.channels[marker.channel].note_lst
			note_inst = next((note for note in note_list if note.midinum == marker.midinum and note.tt_on == marker.tt_on and note.tt_off == marker.tt_off), None)
			if note_inst is None:
				note_list.append(VisualNote(channel=marker.channel, midinum=marker.midinum, tt_on=marker.tt_on, tt_off=marker.tt_off))
				note_list.sort(key=lambda note: note.tt_on)
					
		#print(f'added marker channel:{marker.channel} note:{marker.midinum}; marker_lst len:{len(self.channels[marker.channel].marker_lst)}, note_lst len:{len(self.channels[marker.channel].note_lst)}')	
		self.dirty = True


	def remove_marker(self, marker):
		note_list = self.channels[marker.channel].note_lst
		note_inst = next((note for note in note_list if note.midinum == marker.midinum and note.tt_on == marker.tt_on and note.tt_off == marker.tt_off), None)
		
		if note_inst is not None:
			#print(f'marker note found:{note_inst}')
			self.channels[marker.channel].note_lst.remove(note_inst)

		self.channels[marker.channel].marker_lst.remove(marker)
		
		#if the last marker in the channel is removed, remove channel from dictionary
		if not self.channels[marker.channel].has_notes():
			#print(f'channel:{marker.channel} has no notes, deleting from dictionary')
			del self.channels[marker.channel]
			
		#print(f'removed marker channel:{marker.channel} note:{marker.midinum}; marker_lst len:{len(self.channels[marker.channel].marker_lst)}, note_lst len:{len(self.channels[marker.channel].note_lst)}')
		self.dirty = True

	
	def add_tempo_list(self, tempo_messages):
		#TODO: create tempo message markers on overlay
		if len(tempo_messages) == 1:
			self.set_single_tempo(tempo_messages[0].tempo)
		elif len(tempo_messages) == 0:
			pass
		else:
			self.set_avg_tempo(tempo_messages)


	def add_note_list(self, visual_note_lst):
		if self.channels is not None:
			return

		chnDict = {}
		chnNoteLst = []
		for i in range(0,16):
			chnNoteLst = [note for note in visual_note_lst if note.channel == i]
			if len(chnNoteLst) > 0:
				chnNoteLst.sort(key=lambda note: note.tt_on)
				chnDict[i] = VisualChannel(channel=i,notes=deepcopy(chnNoteLst))
				chnNoteLst.clear()

		self.channels = chnDict
		self.dirty = False
		
	
	def make_playable(self):

		# for channel in self.channels.values():
			#print(channel.msg_lst())
			
		if self.has_notes():
			#if len(self.channels) > 1:
			self.note_msg_lst = list(linear_merge([channel.msg_lst() for channel in self.channels.values()], compare_on=lambda x: x.tt))

		#calculate deltaTs (time attribute) on note messages
		now = 0
		for idx, msg in enumerate(self.note_msg_lst):
			delta = msg.tt - now
			self.note_msg_lst[idx].time = delta
			now = msg.tt
			
		self.track_total_ticks = now
		
		#print(f"(make_playable) self.channels: {self.channels}; track note_msg_lst: {self.note_msg_lst}")
		
			
	
	def display_track_markers(self):
		if self.channels is not None:
			for chn_num in self.channels.keys():
				for mrkr in self.channels[chn_num].marker_lst:
					note_ref = self._get_midinum_note_ref(mrkr.midinum)
					note_ref.add_widget(mrkr)
					#print(f'placing marker: channel {mrkr.channel} note {mrkr.midinum} (oct:{note_ref.octnum}, chroma:{note_ref.chroma}), mrkr.width: {mrkr.width}, mrkr.pos[0]: {mrkr.pos[0]}')				
					

	def hide_track_markers(self):
		if self.channels is not None:
			for chn_num in self.channels.keys():
				for mrkr in self.channels[chn_num].marker_lst:
					if mrkr.parent is not None:
						note_ref = mrkr.parent
						note_ref.remove_widget(mrkr)
						#print(f'removing marker: channel {mrkr.channel} note {mrkr.midinum} (oct:{note_ref.octnum}, chroma:{note_ref.chroma}), mrkr.width: {mrkr.width}, mrkr.pos[0]: {mrkr.pos[0]}')			
				
				
	def visualize(self, **kwargs):
		
		if self.top_level_ref is None:
			if 'top_level_ref' in kwargs:
				self.top_level_ref = kwargs.get('top_level_ref')
				self.note_grid_ref = self.top_level_ref.note_scroller.track_tabs.lined_note_grid.note_grid
			else:
				return			
			
		#check if new time values have been passed
		if 'tick_len' in kwargs:
			self.track_total_ticks = kwargs.get('tick_len')
			
		if 'ticks_per_beat' in kwargs:
			self.ticks_per_beat = kwargs.get('ticks_per_beat')
			
		if 'time_sig_n' in kwargs:
			self.time_sig_numerator = kwargs.get('time_sig_n')

		if 'time_sig_d' in kwargs:
			self.time_sig_denominator = kwargs.get('time_sig_d')
		
		#self.ticks_per_bar and self.bars are already calculated in __init__, this code is only executed if new values are passed to visualize
		if 'tick_len' in kwargs and 'ticks_per_beat' in kwargs and 'time_sig_n' in kwargs and 'time_sig_d' in kwargs:
			self.ticks_per_bar = calculate_bar_ticks(self.time_sig_numerator, self.time_sig_denominator, self.ticks_per_beat)
			self.bars = max(10, calculate_midi_bars(self.ticks_per_bar, self.track_total_ticks))
				
		# self.single_tempo = True
		# self.tempo = tempo
		self.top_level_ref.left_panel.tempo_ctrl.set_from_file(tempo=self.tempo, single_tempo=self.single_tempo, \
			tickdiv=self.ticks_per_beat, tsig_n=self.time_sig_numerator, tsig_d=self.time_sig_denominator, ticks_per_bar=self.ticks_per_bar)
		
		if 'mido_track' in kwargs:
			self._mine_mido_track(kwargs.get('mido_track'))
	
		else:
			#check for initialized values
			if self.min_midinum == -1 or self.max_midinum == -1:
				return
			
		if self._check_octaves_expanded() and self.channels is not None:

			#expand grid horizontally to contain all the bars
			self.top_level_ref.time_scroller.time_line.expand_to_num_bars(self.bars)
			
			for chn_num in self.channels.keys():
				self.channels[chn_num].marker_lst.clear()
				self.channels[chn_num].init_color(self.top_level_ref.left_panel.chnl_ctrl.chn_scroll.channel_list.get_channel_color(chn_num))
				
				#for each channel, activate the channel instrument
				if self.voices_timed == False and len(self.channel_voice_dict) > 0:
					self.channels[chn_num]._midi_voice = self.channel_voice_dict.get(chn_num, 0)
				
				#create/place note markers
				for note in self.channels[chn_num].note_lst:
					#print(note.channel, note.midinum, note.tt_on, note.tt_off)
					mrkr = Marker(top_level_ref=self.top_level_ref, chnum=note.channel, \
								  midinum=note.midinum, tt_on=note.tt_on, tt_off=note.tt_off)
					self.channels[chn_num].marker_lst.append(mrkr)
					note_ref = self._get_midinum_note_ref(note.midinum)
					note_ref.place_marker(mrkr, self.ticks_per_bar)
				

	


				
				

				
				
				
				
				
				
				
