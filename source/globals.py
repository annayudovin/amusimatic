#defines chroma_dict, chroma, scale_steps, diatonic_scales, other_scales, instruments, bpm2tempo, tempo2bpm, camel_to_snake, snake_to_camel, Log2, isPowerOfTwo, nearestPowerOfTwo, get_document_directory

import math

__all__ = ('chroma_dict', 'chroma', 'scale_steps', 'diatonic_scales', 'other_scales', 'instruments', 'bpm2tempo', 'tempo2bpm', 'camel_to_snake', 'snake_to_camel', 'Log2', 'isPowerOfTwo', 'nearestPowerOfTwo', 'get_document_directory', 'linear_merge')

# -------------------------------
# ---global dictionaries---

# chroma_dict = {'C':'C', 'C♯ / D♭':'C#', 'D':'D', 'D♯ / E♭':'D#', 'E':'E', 'F':'F', 'F♯ / G♭':'F#', 'G':'G', 'G♯ / A♭':'G#', 'A':'A', 'A♯ / B♭':'A#', 'B':'B'}
chroma_dict = {'': '', 'C': 'C', 'C[size=18][sub]#[/sub][/size] / D[i][size=16][sub]b[/sub][/size][/i]': 'C#', 'D': 'D',
			   'D[size=18][sub]#[/sub][/size] / E[i][size=16][sub]b[/sub][/size][/i]': 'D#', 'E': 'E', 'F': 'F',
			   'F[size=18][sub]#[/sub][/size] / G[i][size=16][sub]b[/sub][/size][/i]': 'F#', 'G': 'G',
			   'G[size=18][sub]#[/sub][/size] / A[i][size=16][sub]b[/sub][/size][/i]': 'G#', 'A': 'A',
			   'A[size=18][sub]#[/sub][/size] / B[i][size=16][sub]b[/sub][/size][/i]': 'A#', 'B': 'B'}
chroma = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')  # tuple, immutable

scale_steps = {'': 0, 'H': 1, 'W': 2, '3H': 3, '2W': 4, '4H': 4}

diatonic_scales = {'': '', 'MAJOR': 'W-W-H-W-W-W-H', 'MINOR [NATURAL]': 'W-H-W-W-H-W-W',
				   'AEOLIAN / MINOR [N]': 'W-H-W-W-H-W-W', 'DORIAN': 'W-H-W-W-W-H-W', 'IONIAN / MAJOR': 'W-W-H-W-W-W-H',
				   'LOCRIAN': 'H-W-W-H-W-W-W', 'LYDIAN': 'W-W-W-H-W-W-H', 'MIXOLYDIAN': 'W-W-H-W-W-H-W',
				   'PHRYGIAN': 'H-W-W-W-H-W-W'}

other_scales = {'': '', 'ACOUSTIC': 'W-W-W-H-W-H-W', 'ALTERED SCALE': 'H-W-H-W-W-W-W', 'AUGMENTED': '3H-H-3H-H-3H-H',
				'BEBOP DOMINANT': 'W-W-H-W-W-H-H-H', 'BLUES': '3H-W-H-H-3H-W', 'DOUBLE HARMONIC': 'H-3H-H-W-H-3H-H',
				'ENIGMATIC': 'H-3H-W-W-W-H-H', 'FLAMENCO MODE': 'H-3H-H-W-H-3H-H', 'GYPSY': 'W-H-3H-H-H-W-W',
				'HALF DIMINISHED': 'W-H-W-H-W-W-W', 'HARMONIC MAJOR': 'W-W-H-W-H-3H-H',
				'HARMONIC MINOR': 'W-H-W-W-H-3H-H', 'HIRAJOSHI': '2W-W-H-2W-H', 'HUNGARIAN "GYPSY"': 'W-H-3H-H-H-3H-H',
				'HUNGARIAN MINOR': 'W-H-3H-H-H-3H-H', 'HUNGARIAN MAJOR': '3H-H-W-H-W-H-W', 'IN': 'H-2W-W-H-2W',
				'INSEN': 'H-2W-W-3H-W', 'IWATO': 'H-2W-H-2W-W', 'SUPER LOCRIAN': 'H-W-H-W-W-W-W',
				'MAJOR LOCRIAN': 'W-W-H-H-W-W-W', 'LYDIAN AUGMENTED': 'W-W-W-W-H-W-H',
				'PHRYGIAN DOMINANT': 'H-3H-H-W-H-W-W', 'MAJOR BEBOP [7]': 'W-W-H-W-H-W-H',
				'MAJOR BEBOP [8]': 'W-W-H-W-H-H-W-H', 'MELODIC MINOR [ASC]': 'W-H-W-W-W-W-H',
				'MELODIC MINOR [DESC]': 'W-W-H-W-W-H-W', 'MAJOR PENTATONIC': 'W-W-3H-W-3H',
				'MINOR PENTATONIC': '3H-W-W-3H-W', 'NEAPOLITAN MAJOR': 'H-W-W-W-W-W-H',
				'NEAPOLITAN MINOR': 'H-W-W-W-H-3H-H', 'OCTATONIC [W-H]': 'W-H-W-H-W-H-W-H',
				'OCTATONIC [H-W]': 'H-W-H-W-H-W-H', 'PERSIAN': 'H-3H-H-H-W-3H-H', 'PROMETHEUS': 'W-W-W-3H-H-W',
				'SCALE OF HARMONICS': '3H-H-H-W-W-3H', 'TRITONE': 'H-3H-W-H-3H-W',
				'TWO-SEMITONE TRITONE': 'H-H-4H-H-H-4H', 'UKRAINIAN DORIAN': 'W-H-3H-H-W-H-W',
				'WHOLE TONE': 'W-W-W-W-W-W', 'YO': '3H-W-W-3H-W'}


# -------------------------------

instruments = ["Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honkytonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavi", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics", "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2", "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensemble 1", "String Ensemble 2", "SynthStrings 1", "SynthStrings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "SynthBrass 1", "SynthBrass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)", "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bag Pipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"]

#-------------------------------

# def tick2second(tick, ticks_per_beat, tempo):
	# scale = tempo * 1e-6 / ticks_per_beat
	# return tick * scale


# def second2tick(second, ticks_per_beat, tempo):
	# scale = tempo * 1e-6 / ticks_per_beat
	# return second / scale


def bpm2tempo(bpm):
	return int(round((60 * 1000000) / bpm))


def tempo2bpm(tempo):
	return (60 * 1000000) / tempo

#-------------------------------
def camel_to_snake(name):
	return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')


def snake_to_camel(name):
	return ''.join(word.title() for word in name.split('_'))

#-------------------------------
# Functions to check if x is power of 2
def Log2(x):
	return (math.log10(x) / math.log10(2))


def isPowerOfTwo(n):
	return (math.ceil(Log2(n)) == math.floor(Log2(n)))


# returns nearest LOWER PowerOfTwo
def nearestPowerOfTwo(n):
	# neither of these are powers of 2, but we need them
	if n == 0 or n == 1:
		return n
	if isPowerOfTwo(n):
		return n
	p2 = 2
	while p2 < n / 2:
		p2 *= 2
	
	return p2

	
#-------------------------------
def get_document_directory():
	user_data_dir = App.get_running_app().user_data_dir
	nested_dirs = user_data_dir.split('\\')
	
	if 'Users' in nested_dirs:
		idx = nested_dirs.index('Users')
		doc_dir = '\\'.join(nested_dirs[:idx + 2]) + '\\Documents'
	else:
		doc_dir = user_data_dir
	
	print(f'user_data_dir: {user_data_dir},  doc_dir: {doc_dir}')
	return doc_dir

#-------------------------------

def linear_merge(sortedlists, compare_on=lambda x: x):
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
				
#-------------------------------