
import mido
import threading
from time import sleep
from copy import deepcopy

from mido import Message, MetaMessage, MidiFile
from mido.messages.messages import SysexData
from mido.messages.checks import check_msgdict, check_value, check_time
from mido.py2 import convert_py2_bytes
from mido.messages.specs import make_msgdict
from mido.messages.specs import (SPEC_BY_TYPE)
from mido.midifiles.meta import (_META_SPEC_BY_TYPE)

from .globals import linear_merge
from .midoext import ExtMessage, ExtMetaMessage
from .visualmidi import VisualTrack, VisualNote
__all__ = ('TonePlayer', 'FilePlayer')


def printMIDOTrackToConsole(track):

	for i, msg in enumerate(track):
		print(f'idx {i}: '+ str(msg) + '\n')
		
		
def printMIDOTrackToText(textFilename, track):
	
	access_mode = 'w' #Write Only: Creates the file if the file does not exist, otherwise the data is over-written.
	outfile = open(textFilename, access_mode)

	for i, msg in enumerate(track):
		outfile.write(f'idx {i}: '+ str(msg) + '\n')

	outfile.close()
	
	
def printListToText(textFilename, list):
	
	access_mode = 'w' #Write Only: Creates the file if the file does not exist, otherwise the data is over-written.
	outfile = open(textFilename, access_mode)

	for idx, el in enumerate(list):
		outfile.write(f'idx {idx}: '+ str(el) + '\n')

	outfile.close()	

	
	
def printNestedListToText(textFilename, list):
	
	access_mode = 'w' #Write Only: Creates the file if the file does not exist, otherwise the data is over-written.
	outfile = open(textFilename, access_mode)

	for idx, el in enumerate(list):
		for i, e in enumerate(el):
			outfile.write(f'idx {idx}-{i}: '+ str(e) + '\n')

	outfile.close()	



#-----------------------------------------------------------------------------------------------------	
#---BASE CLASS FOR COMMON MIDI CONTROL FUNCTIONALITY--------------------------------------------------
#-----------------------------------------------------------------------------------------------------
class MidiControlBase():
	midi_outport = None
	
	def __init__(self, **kwargs):
		self.volume = kwargs.get('volume', 64)
		
		verbose_open = kwargs.get('verbose', True)
		outport_ref = kwargs.get('outport', None)
		if outport_ref != None:
			self.link_to_outport(outport_ref)
		else:
			self.create_outport(verbose=verbose_open)
			
		channel = kwargs.get('channel', 0)
		instrument_idx = kwargs.get('instrument', 0)
		
		if channel > 0 or instrument_idx > 0:
			self.set_channel_instrument(channel, midi_voice_idx) 
			

	#validates type and range of integer value, returns val (integer value) if valid, or default
	def _check_valid(self, val, default):
		if str(type(val)) != "<class 'int'>" and str(type(val)) != "<class 'float'>":
			return 64
		elif int(val) < 0 or int(val) > 127:
			return 64
		else:
			return int(val)


	def set_volume(self, value):
		self.volume = self._check_valid(value, 64)

		
	def send_out(self, msg):
		if type(self).midi_outport == None:
			return
			
		type(self).midi_outport.send(msg)
	
	
	def set_channel_instrument(self, channel, midi_voice_idx):
		if type(self).midi_outport == None:
			return
			
		midi_voice_idx = self._check_valid(midi_voice_idx, 0)

		if str(type(channel)) != "<class 'int'>":
			channel = 0
		elif channel < 0 or channel > 15:
			channel = 0

		msg = Message('program_change', channel=channel, program=midi_voice_idx)		#'program_change' channel=0 program=75 time=0
		self.send_out(msg)


	def link_to_outport(self, outport_ref):
		type(self).midi_outport = outport_ref
	
	
	def get_outport_ref(self):
		return type(self).midi_outport 

		
	def create_outport(self, verbose=True):
		if type(self).midi_outport != None:
			return
			
		output_devices = []
		output_devices = mido.get_output_names()
		midi_device_name = output_devices[0]
		
		if verbose:
			print('available MIDI devices:')
			for od in output_devices:
				print(od)
			print(f'(selected) default MIDI device: {midi_device_name}')

		type(self).midi_outport = mido.open_output(midi_device_name)
		type(self).midi_outport.reset()

	
	def destroy_outport(self):
		if type(self).midi_outport == None:
			return
			
		type(self).midi_outport.reset()
		type(self).midi_outport.close()
		type(self).midi_outport = None
		
		
	def reset_outport(self):
		if type(self).midi_outport == None:
			return
		type(self).midi_outport.reset()
		

#-----------------------------------------------------------------------------------------------------	
#---TONE PLAYER---------------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------
		
class TonePlayer(MidiControlBase):

	def __init__(self, **kwargs):
		super(TonePlayer, self).__init__(**kwargs)
		self.last_event = []

#self.player.midi_note_on(midinum, volume, 0)
#self.player.midi_note_off(midinum, 0, 0)
	def midi_note_on(self, midi_note_num, volume = -1, channel = -1):
		midi_note_num = self._check_valid(midi_note_num, 64)

		if volume == -1:
			volume = self.volume
		else:
			volume = self._check_valid(volume, self.volume)

		if str(type(channel)) != "<class 'int'>":
			channel = 0
		elif channel < 0 or channel > 15:
			channel = 0

		self.last_event = ['note_on', midi_note_num, volume, channel]
		
		msg = Message('note_on', channel=channel, note=midi_note_num, velocity=volume)
		self.send_out(msg)


	def midi_last_off(self, *args):
		if len(self.last_event) == 0:
			return
			
		if self.last_event[0] == 'note_on':
			msg = Message('note_off', channel=self.last_event[3], note=self.last_event[1], velocity=0)
			self.send_out(msg)
		self.last_event = ['note_off', self.last_event[1], 0, self.last_event[3]]


	def midi_note_off(self, midi_note_num, volume = -1, channel = -1):
		midi_note_num = self._check_valid(midi_note_num, 64)

		if str(type(channel)) != "<class 'int'>":
			channel = 0
		elif channel < 0 or channel > 15:
			channel = 0

		self.last_event = ['note_off', midi_note_num, 0, channel]
		msg = Message('note_off', channel=channel, note=midi_note_num, velocity=0)
		self.send_out(msg)

#-----------------------------------------------------------------------------------------------------	
#---END TONE PLAYER-----------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------
		

#-----------------------------------------------------------------------------------------------------	
#---FILE PLAYER---------------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------

class LoadedTrack():

	def __init__(self, **kwargs):

		if 'track_idx' in kwargs:
			self.track_idx = kwargs.get('track_idx')
		else:
			self.track_idx = False
			
		if 'playable' in kwargs:
			self.playable = kwargs.get('playable')
		else:
			self.playable = False
			
		if 'has_tempo' in kwargs:
			self.has_tempo = kwargs.get('has_tempo')
		else:
			self.has_tempo = False
		
		if 'tick_len' in kwargs:
			self.tick_length = kwargs.get('tick_len')
		else:
			self.tick_length = 0

			
class FilePlayer(MidiControlBase):

	def __init__(self, **kwargs):
		super(FilePlayer, self).__init__(**kwargs)

		self.midi_loaded = False
		self.song_time_length = 0
		self.song_tick_length = 0
		self.ticks_per_beat = 480		#default=480	
		self.tempo = 500000		#default
		
		self.curr_tt = 0
		self.meta_cursor = 0
		
		self.playable_tracks = []

		self.file_play_thread = None
		self._stop = threading.Event()

		if 'callback' in kwargs:
			self.progress_callback = kwargs.get('callback')
		else:
			self.progress_callback = None
		
		#list of tuples with the following structure: track_idx, msg_idx, msg.tt, msg.time
		self.merged_meta_track = []
		
		if 'filename' in kwargs:
			self.load_from_file(kwargs.get('filename'), kwargs.get('visual_track_lst', None))			

		
#-----------------------------------------------------------------------------------------------------
		
	def second2tick(self, seconds):
		scale = self.tempo * 1e-6 / self.ticks_per_beat
		return int(seconds / scale)

		
	def tick2second(self, ticks):
		#scale = tempo * 1e-6 / ticks_per_beat
		scale = self.tempo / 1000000
		return ticks * scale / self.ticks_per_beat


	#tempo/ticks_per_beat = microseconds
	#1e-6 * micro_deltaT(deltaT) will give deltaT in seconds
	#or micro_deltaT(deltaT) / 1000000 will give deltaT in seconds
	def micro_deltaT(self, deltaT):
		return deltaT * self.tempo / self.ticks_per_beat
		
		
#---FILE PROCESSING HELPERS-------------------------------------------------------------------------------------		

	def _extend_msg(self, msg, tt):	
		if msg.is_meta:
			ext_msg = ExtMetaMessage.extend(msg)
		else:
			ext_msg = ExtMessage.extend(msg)
			
		ext_msg.tt = tt
		return ext_msg

		
	def _un_extend_msg(self, msg):	
		if msg.is_meta:
			un_ext_msg = ExtMetaMessage.un_extend(msg)
		else:
			un_ext_msg = ExtMessage.un_extend(msg)
				
		return un_ext_msg
				

	#adds time in total ticks as a new message attribute tt to all non-meta messages
	#(helps facilitate progress tracking)
	def _addUpTrackTicks(self, playable_track):	
		currTick = 0
		
		for idx, msg in enumerate(playable_track):
			currTick += msg.time 
			
			# if msg.is_meta:
				# ext_msg = ExtMetaMessage.extend(msg)
			# else:
				# ext_msg = ExtMessage.extend(msg)
				
			# ext_msg.tt = currTick
			
			playable_track[idx] = self._extend_msg(msg, currTick)

		return playable_track
		
		
		
	#converts "note silent" (Note_On velocity=0) messages into explicit Note_Off messages 
	#returns updated track
	def _buffer_silent_2_note_off(self, playable_track):
		
		#check if the track has explicit Note_Off messages rather than Note_On velocity=0
		silentCount = len([msg for msg in playable_track if msg.type == 'note_on' and msg.velocity == 0])
		offCount = len([msg for msg in playable_track if msg.type == 'note_off'])
		
		#if there's something to convert, do so
		if offCount == 0 or silentCount > 0:
			#loop through the track and substitute note_on silent messages to note_off with the same attributes when necessary
			for idx, msg in enumerate(playable_track):
				if msg.type == 'note_on' and msg.velocity == 0:
					playable_track[idx] = ExtMessage.extend(Message('note_off', channel=msg.channel, note=msg.note, velocity=msg.velocity, time=msg.time))
					playable_track[idx].tt = msg.tt

		return playable_track

		
	def _on_off_counts_match(self, track):
		numOns = len([msg for msg in track if msg.type == 'note_on'])
		numOffs = len([msg for msg in track if msg.type == 'note_off'])

		if numOns != numOffs:
			print(f'note on count:{numOns}, note off count:{numOffs}')
			return False
		return True
	
	
	def _find_note_msg_idx(self, track, type, channel, note, tt):
		#type should be note_on or note_off only, otherwise mido will error out
		try:	
			idx, _msg = next((idx, msg) for (idx, msg) in enumerate(track) if msg.type == type \
										and msg.channel == channel and msg.note == note and msg.tt == tt)
		except StopIteration:
			return -1
		return idx
		
				
	#check for AND fix same-note/channel-double-note_on problem, if not detected, track is returned unchanged
	def match_on_offs(self, track):
		visual_note_list = []
		activeNotesDict = {}
		
		#noteMsgs = ([msg for msg in track if msg.type == 'note_on' or msg.type == 'note_off'])

		for idx, msg in enumerate(track): #noteMsgs:
			if msg.type == 'note_on':
				#try fetching from dictionary to see if the same note is passed on the same channel before being turned off
				existing_msg_idxs = activeNotesDict.get((msg.channel, msg.note), [])
				if len(existing_msg_idxs) == 0:	#all is well
					activeNotesDict[(msg.channel, msg.note)] = [idx]
				else:		#found problem, handle when a note_off comes up
					existing_msg_idxs.append(idx)
					existing_msg_idxs.sort()
					activeNotesDict[(msg.channel, msg.note)] = existing_msg_idxs	
					
			elif msg.type == 'note_off':
				idx_on_lst = activeNotesDict.get((msg.channel, msg.note), [])
				#if there is at least one note_on that this note_off message turns off, remove the first idx
				
				if len(idx_on_lst) == 0:	#problem - we have an off message without a prior on, ignore?
					pass
					
				elif len(idx_on_lst) == 1: #if this was the ONLY note_on index in the list (the ideal case), moving on
					del activeNotesDict[(msg.channel, msg.note)]
					visual_note_list.append(VisualNote(channel=msg.channel, midinum=msg.note, velocity=track[idx_on_lst[0]].velocity, \
														tt_on=track[idx_on_lst[0]].tt, tt_off=msg.tt))
					
				#-------------------------------------------------------------------------------------
				#---normal error checking logic up to this point, if all is well, we never get here
				#-------------------------------------------------------------------------------------
				elif len(idx_on_lst) > 1:	#problem: note_on at least twice on same channel/note, w/o note_off between them
											#see if the note_off we have fits the bill
					#track is processed in order, so tt of everything in dictionary is LESS THAN msg.tt
					#so, safe to assume tt_on < msg.tt and next_tt_on <= msg.tt								
					idx_on = idx_on_lst.pop(0)	#remove the first note_on tt from the list, leave the second in place
					tt_on = track[idx_on].tt
					next_idx_on = idx_on_lst[0]
					next_tt_on = track[next_idx_on].tt
					this_off_idx = idx
					
					#track is processed in order, and we already found the second note_on (which is the problem), therefore
					#current note_off can only be on the same tick as the second note_on, or later
					if next_tt_on == msg.tt: #current note_off happened ON SAME TICK AS as the second note_on 
						#REMOVE note_off msg from its current track position (msg is a pointer to it, so we can re-insert later)				
						del track[this_off_idx]
						
					#the current note_off happened LATER than the second note_on. (at least one example in the wild)
					#We'll turn this into something that can be fixed by user in the visual interface by 
					#"inventing" a note_off (so that a marker can be created for the first note_on)
					else: #next_tt_on < msg.tt
						#turn msg into an independent copy of current note_off, instead of a pointer to it (we are creating/inserting a duplicate)
						msg = deepcopy(track[this_off_idx])
						msg.tt = next_tt_on
						visual_note_list.append(VisualNote(channel=msg.channel, midinum=msg.note, velocity=track[next_idx_on].velocity, \
															tt_on=next_tt_on, tt_off=track[this_off_idx+1].tt))
						this_off_idx += 1	#we'll insert an extra message, so current note_off's position will move up by one
						#both notes will be terminated, we can delete this dictionary entry (but not if we didn't create an extra note_off)
						del activeNotesDict[(msg.channel, msg.note)]
						
					#find index of the next note_on in dictionary using tt 
					next_on_idx = self._find_note_msg_idx(track, 'note_on', msg.channel, msg.note, next_tt_on)	

					#re-insert the note_off before the second note_on in the track
					track.insert(next_on_idx, msg) #next element's index is incremented by one
							
					#recalculate message times, based on tt between this_off_idx and next_on_idx+1
					for idx_cursor in range(next_on_idx, this_off_idx+2):
						track[idx_cursor].time = track[idx_cursor].tt - track[idx_cursor-1].tt
						
					visual_note_list.append(VisualNote(channel=msg.channel, midinum=msg.note, velocity=track[idx_on].velocity, tt_on=tt_on, tt_off=next_tt_on))
					
		return track, visual_note_list
		
		
	# def _on_offs_match(self, track):
		# activeNotesDict = {}
		
		# noteMsgs = ([msg for msg in track if msg.type == 'note_on' or msg.type == 'note_off'])

		# for idx, msg in enumerate(noteMsgs):
			# if msg.type == 'note_on':
				# #the same note is passed on the same channel before being turned off
				# if activeNotesDict.get((msg.channel, msg.note), -1) > -1:
					#print(f'double-on (note {msg.note}) detected at idx {idx}')
					# return False
				# else:
					# activeNotesDict[(msg.channel, msg.note)] = idx
				
			# elif msg.type == 'note_off':
				# #a note_off message appears before its corresponding note_on
				# if activeNotesDict.get((msg.channel, msg.note), -1) == -1:
					#print(f'off before on (note {msg.note}) detected at idx {idx}')
					# return False
				# else:
					# del activeNotesDict[(msg.channel, msg.note)]
				
		# return True
	
	

	#this is for "fixing" midis where note_off messages follow the next note_on that happens on the same tick (makes note duration less obvious)
	def _untangle_note_off_pairs(self, track):
		try:	
			idx, noWaitOff = next((idx, deepcopy(msg)) for (idx, msg) in enumerate(track) if msg.type == 'note_off' and msg.time == 0 and idx > 0)
			found_before = idx
		except StopIteration:
			return track
			
		while True:
			prev_idx = idx-1
			prev_msg = deepcopy(track[prev_idx])
			
			if prev_msg.time > 0 and prev_msg.tt == noWaitOff.tt: #prev_msg.type == 'note_on' and prev_msg.note != noWaitOff.note 
				prev_msg.time = noWaitOff.time
				noWaitOff.time = track[prev_idx].time
				
				track[prev_idx] = noWaitOff 
				track[idx] = prev_msg
			try:	
				idx, noWaitOff = next((idx, deepcopy(msg)) for (idx, msg) in enumerate(track) if msg.type == 'note_off' and msg.time == 0 and idx > found_before)
				found_before = idx
			except StopIteration:
				break
	
		return track
		

	# #sorted structure: [[(0, 2, 0, 0), (0, 3, 320, 320), (0, 4, 640, 320), ...], [...], [...], ...]
	# #tuple scturcture: track_idx, msg_idx, msg.tt, msg.time, 
	# def _linear_meta_merge(self, sortedlists):
		# # Create a list of tuples containing each iterator and its first value
		# iterlist = [[i,next(i)] for i in [iter(j) for j in sortedlists]]
			
		# # Perform an initial sort of each iterator's first value
		# # we are sorting on message.tt, which is the [2] in each tuple (#track_idx, msg_idx, msg.tt, msg.time)
		# iterlist.sort(key=lambda x: x[1][2])

		# # Helper function to move the larger first item to its proper position
		# def reorder(iterlist, i): 
			# if i == len(iterlist) or iterlist[0][1][2] < iterlist[i][1][2]:
				# iterlist.insert(i-1,iterlist.pop(0))
			# else:
				# reorder(iterlist,i+1)

		# while True:
			# if len(iterlist):
				# # Reorder the list if the 1st element has grown larger than the 2nd
				# if len(iterlist) > 1 and iterlist[0][1][2] > iterlist[1][1][2]:
					# reorder(iterlist, 1)

				# yield iterlist[0][1]

				# # try to pull the next value from the current iterator
				# try:
					# iterlist[0][1] = next(iterlist[0][0])
				# except StopIteration:
					# del iterlist[0]
			# else:
				# break


	#sorted structure: [[(0, 2, 0, 0), (0, 3, 320, 320), (0, 4, 640, 320), ...], [...], [...], ...]
	#tuple scturcture: track_idx, msg_idx, msg.tt, msg.time, 
	def _linear_meta_merge(self, sortedlists, compare_on=lambda x: x):
		# Create a list of tuples containing each iterator and its first value
		iterlist = [[i,next(i)] for i in [iter(j) for j in sortedlists]]
			
		# Perform an initial sort of each iterator's first value
		# we are sorting on message.tt, which is the [2] in each tuple (#track_idx, msg_idx, msg.tt, msg.time)
		iterlist.sort(key=lambda x: compare_on(x[1]))

		# Helper function to move the larger first item to its proper position
		def reorder(iterlist, i): 
			if i == len(iterlist) or compare_on(iterlist[0][1]) < compare_on(iterlist[i][1]):
				iterlist.insert(i-1,iterlist.pop(0))
			else:
				reorder(iterlist,i+1)

		while True:
			if len(iterlist):
				# Reorder the list if the 1st element has grown larger than the 2nd
				if len(iterlist) > 1 and compare_on(iterlist[0][1]) > compare_on(iterlist[1][1]):
					reorder(iterlist, 1)

				yield iterlist[0][1]

				# try to pull the next value from the current iterator
				try:
					iterlist[0][1] = next(iterlist[0][0])
				except StopIteration:
					del iterlist[0]
			else:
				break

				
	def _calc_new_deltaTs(self):
		now = 0
		for idx, addr in enumerate(self.merged_meta_track):
			delta = addr[2] - now
			self.merged_meta_track[idx] = (addr[0],addr[1],addr[2],delta) 
			now = addr[2]	
		
			
	def process_all_playable_tracks(self, midi_file, visual_track_lst=None):
		total_ticks = 0
		found_notes = False
		found_tempo = False
		tempo_track_cnt = 0
		tempo_track_idx = 0
		tempo_msgs_cnt = 0
		numerator=0 
		denominator=0

		track_info_list = []
		list_of_track_msgs = []
		list_of_tempo_msgs = []
		
		self.playable_tracks.clear()
		self.merged_meta_track.clear()
		
		for idx, track in enumerate(midi_file.tracks):
			#find a note_on message
			n_msg = next((msg for msg in track if msg.type == 'note_on'), None)
			found_notes = n_msg is not None
			
			#find a tempo message:
			t_msg = next((msg for msg in track if msg.type == 'set_tempo'), None)
			found_tempo = t_msg is not None
			
			#find a time message (this is only for visualization, player doesn't care):
			sig_msg = next((msg for msg in track if msg.type == 'time_signature'), None)
			if sig_msg is not None:
				numerator=sig_msg.numerator 
				denominator=sig_msg.denominator
			else:
				numerator=denominator=4
			
			if found_notes or found_tempo:

				#add total ticks (.tt) attribute to all messages			
				track = self._addUpTrackTicks(track)
				total_ticks = track[-1].tt + track[-1].time		
				
				if found_notes:
					track = self._buffer_silent_2_note_off(track)

					if self._on_off_counts_match(track):
						track = self._untangle_note_off_pairs(track)
						
					
					#this is a playable track, send to visualizer
					#TODO: figure out object ownership
					if visual_track_lst is not None:
						visual_track_lst.append(VisualTrack(tick_len=total_ticks, ticks_per_beat=midi_file.ticks_per_beat, 
															time_sig_n=numerator, time_sig_d=denominator, 
															mido_track=track))
						
					track, visual_note_lst = self.match_on_offs(track)

					if visual_track_lst is not None:
						visual_track_lst[-1].add_note_list(visual_note_lst)
						
			
				#remove all meta messages besides tempo from playable tracks, to simplify play			
				#track = [msg for msg in track if msg.type == 'set_tempo' or msg.is_meta == False]
				
				track_info = LoadedTrack(track_idx=len(self.playable_tracks), \
										 tick_len=total_ticks, playable=found_notes, has_tempo=found_tempo)		#mido_track=track, 

				if found_tempo:
					self.tempo = t_msg.tempo
					list_of_tempo_msgs.extend(list(msg for msg in track if msg.type == 'set_tempo'))
					tempo_msgs_cnt = len(list_of_tempo_msgs)
					tempo_track_cnt += 1
					tempo_track_idx = len(track_info_list)
				
				self.playable_tracks.append(track)
				track_info_list.append(track_info)
		#---done looping through tracks - got all track info		
		
		#add list of tempos to every visual_track in the list (if any), for use in UI
		if visual_track_lst is not None:
			for visual_track in visual_track_lst:
				visual_track.add_tempo_list(list_of_tempo_msgs)
						
						
		#---if there's only a single tempo message on a non-playable track, we don't need a separate 'tempo track'		
		if tempo_track_cnt == 1 and tempo_msgs_cnt == 1 and track_info_list[tempo_track_idx].playable == False:
			del track_info_list[tempo_track_idx]
			del self.playable_tracks[tempo_track_idx]
		
		#set song length in total ticks
		self.song_tick_length = max(list(trk.tick_length for trk in track_info_list))
		#done with this list, release memory
		track_info_list.clear()
			
		for track_idx, playable_track in enumerate(self.playable_tracks):
			#create meta track for each playable track
			#tuple structure: track_idx, msg_idx, msg.tt, msg.time
			list_of_track_msgs.append(list((track_idx, i, msg.tt, msg.time) for (i, msg) in enumerate(playable_track) if msg.type == 'set_tempo' or msg.is_meta == False))
			
		if len(self.playable_tracks) > 1:
			#if multiple playable tracks exist, create a 'merged' meta track to control playback order
			self.merged_meta_track = list(linear_merge(list_of_track_msgs, compare_on=lambda x: x[2]))
			#update time in merged_meta_track to deltaT with previous message in merged_meta_track
			self._calc_new_deltaTs()
		else:
			#if only one playable track exists, no need to merge anything, and existing deltaTs are correct
			self.merged_meta_track.extend(list_of_track_msgs[0])

		#print(self.merged_meta_track)
		self.meta_cursor = 0
		self.curr_tt = 0
		

	def process_editor_tracks(self, editor_track_lst):
		tick_len = 0
		list_of_track_msgs = []

		self.playable_tracks.clear()
		self.merged_meta_track.clear()
		
		for track_idx, editor_track in enumerate(editor_track_lst):
			editor_track.make_playable()
			tick_len = max(tick_len, editor_track.track_total_ticks)
			self.playable_tracks.append(editor_track.note_msg_lst)
			#create meta track for each playable track
			#tuple structure: track_idx, msg_idx, msg.tt, msg.time
			list_of_track_msgs.append(list((track_idx, i, msg.tt, msg.time) for (i, msg) in enumerate(editor_track.note_msg_lst)))
			
		if len(editor_track_lst) > 1:
			#if multiple playable tracks exist, create a 'merged' meta track to control playback order
			self.merged_meta_track = list(linear_merge(list_of_track_msgs, compare_on=lambda x: x[2]))
			#update time in merged_meta_track to deltaT with previous message in merged_meta_track
			self._calc_new_deltaTs()
		else:
			#if only one playable track exists, no need to merge anything, and existing deltaTs are correct
			self.merged_meta_track.extend(list_of_track_msgs[0])
			
		#print(f"(process_editor_tracks) merged_meta_track len: {len(self.merged_meta_track)}; playable_tracks len: {len(self.playable_tracks)}")
		#print(self.merged_meta_track)
		
		self.song_tick_length = tick_len
		self.meta_cursor = 0
		self.curr_tt = 0

		
#---END FILE PROCESSING HELPERS-------------------------------------------------------------------------------------		
		
	def load_from_file(self, filename, visual_track_lst=None, callback=None):
		self.progress_callback = callback	
		midi_file = MidiFile(filename, clip=True)
		self.song_time_length = midi_file.length	
		self.ticks_per_beat = midi_file.ticks_per_beat	
		
		self.process_all_playable_tracks(midi_file, visual_track_lst)
		#print(f'loaded {filename}, visual_track_lst: {visual_track_lst}, len:{len(visual_track_lst)}')
		#print(f'(load_from_file) currently running thread count: {threading.active_count()}, midi_outport:{type(self).midi_outport}')
		self.midi_loaded = True
			
	
	def load_from_editor(self, editor_track_lst, callback=None):
		self.progress_callback = callback	
		#midi_file = MidiFile()	#MidiFile('empty.mid', clip=True)
		#self.song_time_length = midi_file.length	
		#self.ticks_per_beat = midi_file.ticks_per_beat	
		
		#print(f"(load_from_editor) track list: {editor_track_lst}, len: {len(editor_track_lst)}, marker_lst len:{len(editor_track_lst[0].channels[0].marker_lst)}")
		self.process_editor_tracks(editor_track_lst)
		self.midi_loaded = True
	
	
	def unload_all(self):
		self.midi_loaded = False
		self.song_time_length = 0
		self.song_tick_length = 0
		self.ticks_per_beat = 480		#default=480	
		self.tempo = 500000		#default
		
		self.curr_tt = 0
		self.meta_cursor = 0
		
		self.playable_tracks.clear()
		self.merged_meta_track.clear()
		
		self.file_play_thread = None
		self._stop = threading.Event()

	
	def _reset_to_start(self):
		self.meta_cursor = 0
		self.curr_tt = 0


	def get_duration(self):
		if not self.midi_loaded:
			return 0
			
		return self.song_time_length

		
	def get_duration_tix(self):
		if not self.midi_loaded:
			return 0
			
		return self.song_tick_length	
	
			
	def _progress_percent_idx_lst(self):
		if not self.midi_loaded:
			return [0, 0]

		return [round(100.0*float(self.curr_tt)/float(self.song_tick_length), 2), self.curr_tt]
			
		
	#position is given in percent		
	def get_position(self):
		if not self.midi_loaded:
			return 0
			
		return round(100.0*float(self.curr_tt)/float(self.song_tick_length), 2)


	#position is given in percent
	def set_position(self, percent):
		if not self.midi_loaded:
			return 0

		ticks_goal = int(percent * float(self.song_tick_length) / 100.0)

		try:
			#"addr" tuple structure: track_idx, msg_idx, msg.tt, msg.time	
			after_idx, addr = next((idx, address) for (idx, address) in enumerate(self.merged_meta_track) if address[2] >= ticks_goal)
		except StopIteration:
			after_idx = len(self.merged_meta_track)
			addr = self.merged_meta_track[-1]

		self.meta_cursor = after_idx

		
	def toggle_pause(self):
		#print(f'(toggle_pause) currently running thread count: {threading.active_count()}, midi_loaded: {self.midi_loaded}, midi_outport:{type(self).midi_outport}')
		if self._stop.is_set():
			#paused
			self._stop.clear()
			self.file_play_thread = threading.Thread(target=self._play_loaded_midi, kwargs={"start_idx":self.meta_cursor})
			self.file_play_thread.start()

		else:
			#playing
			self._stop.set()
			
	
	def stop(self):
		self._stop.set()
		self._reset_to_start()

	
	def interrupt(self):
		self._stop.set()
	
	
	def start(self):
		self.play()
		
	
	def play(self):
		#print(f'(play) currently running thread count: {threading.active_count()}, midi_loaded: {self.midi_loaded}, midi_outport:{type(self).midi_outport}')
		if not self.midi_loaded:
			return
			
		if type(self).midi_outport == None:
			return
		
		self._stop.clear()
		self.file_play_thread = threading.Thread(target=self._play_loaded_midi, kwargs={"start_idx":self.meta_cursor})
		self.file_play_thread.start()

		
	def _play_loaded_midi(self, **kwargs):
		if 'start_idx' in kwargs:
			start_idx = kwargs.get('start_idx')
		else:
			start_idx = 0
		
		def paced_notes():
			for idx, address in enumerate(self.merged_meta_track[start_idx:]):

				self.meta_cursor = idx + start_idx
				#address scturcture: track_idx, msg_idx, msg.tt, msg.newDeltaT
				self.curr_tt = address[2]
				msg = self.playable_tracks[address[0]][address[1]]

				is_stopped = self._stop.wait(1e-6 * self.micro_deltaT(address[3]))
				
				if is_stopped:
					type(self).midi_outport.reset()
					return
					
				if msg.is_meta:
					if msg.type == 'set_tempo':
						self.tempo = msg.tempo
					continue
				else:
					yield msg

		try:
			for msg in paced_notes():
				self.send_out(msg)
				
				if self.progress_callback != None:
					self.progress_callback(self._progress_percent_idx_lst())
					
			#check paced_notes() exit conditions
			if len(self.merged_meta_track)-1 == self.meta_cursor:
				#once all notes have been played (song is done) signal progress of 100%
				if self.progress_callback != None:
					self.progress_callback([100, self.song_tick_length])
					
		finally:
			type(self).midi_outport.reset()

#-----------------------------------------------------------------------------------------------------	
#---END FILE PLAYER-----------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------
			

#---test--------------	
def main():

	def print_progress(data):
		print(f'print_progress({data})')

	#midi_player = FilePlayer(filename = 'WuJi.mid')#, callback = print_progress)	
	#midi_player = FilePlayer(filename = 'fuguette.mid')#, callback = print_progress)
	midi_player = FilePlayer(filename = 'minuet.mid')#, callback = print_progress)
	#midi_player = FilePlayer(filename = 'moonlight.mid') #mismatched pairs found
	#midi_player = FilePlayer(filename = 'allaturk.mid') #mismatched pairs found
	#midi_player = FilePlayer(filename = 'fugue.mid')#, callback = print_progress)
	#printListToText('fuguette_merged.txt', midi_player.merged_meta_track)
	#printMIDOTrackToText('WuJi_track.txt', midi_player.playable_tracks[0])	
	midi_player.play()
	


if __name__ == '__main__':
	main()	
	#midi_player = FilePlayer(filename = 'WuJi.mid')
	
	
	
	