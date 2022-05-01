import mido
from mido import Message, MetaMessage, MidiFile
from mido.messages.messages import SysexData
from mido.messages.checks import check_msgdict, check_value, check_time
from mido.py2 import convert_py2_bytes
from mido.messages.specs import make_msgdict
from mido.messages.specs import (SPEC_BY_TYPE)
from mido.midifiles.meta import (_META_SPEC_BY_TYPE)


__all__ = ('ExtMessage', 'ExtMetaMessage')

		
#-----------------------------------------------------------------------------------------------------	
#---MIDO EXTENSIONS-----------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------
def check_msgdict(msgdict):
	spec = SPEC_BY_TYPE.get(msgdict['type'])
	if spec is None:
		raise ValueError('unknown message type {!r}'.format(msgdict['type']))

	for name, value in msgdict.items():
		if name != 'tt' and name not in spec['attribute_names']:
			raise ValueError(
				'{} message has no attribute {}'.format(spec['type'], name))
		if name != 'tt':
			check_value(name, value)
			

class ExtMessage(Message):

	@classmethod
	def extend(cl, msg):
		msgdict = vars(msg).copy()
		msgdict['tt'] = 0
		return cl(**msgdict)
	
	@classmethod
	def un_extend(cl, msg):
		msgdict = vars(msg).copy()
		del msgdict['tt']
		return cl(**msgdict)
	
	def __init__(self, type, **args):
		msgdict = make_msgdict(type, args)
		if type == 'sysex':
			msgdict['data'] = SysexData(convert_py2_bytes(msgdict['data']))
		check_msgdict(msgdict)
		vars(self).update(msgdict)
	
	#overriding from BaseMessage, to make an exception and allow removal of the new attribute
	#to convert message back to original spec
	def __delattr__(self, name):
		if name != 'tt':
			raise AttributeError('attribute cannot be deleted')
	
	
	#overriding from BaseMessage, we don't want this functionality for the 'Extended' variety 
	def bin(self):
		raise NotImplemented

		
	#overriding from BaseMessage, we don't want this functionality for the 'Extended' variety
	def hex(self, sep=' '):
		raise NotImplemented
		
		
	def _setattr(self, name, value):
		if name == 'type':
			raise AttributeError('type attribute is read only')
		#added------------------
		elif name == 'tt':
			vars(self)['tt'] = value
		#end added--------------
		elif name not in vars(self):
			raise AttributeError('{} message has no '
								 'attribute {}'.format(self.type, name))
		else:
			check_value(name, value)
			if name == 'data':
				vars(self)['data'] = SysexData(value)
			else:
				vars(self)[name] = value

	__setattr__ = _setattr

	
	def __str__(self):
		return super(ExtMessage, self).__str__() + ' tt=' + str(self.tt)
	
	
	
class ExtMetaMessage(MetaMessage):
	
	@classmethod
	def extend(cl, msg):
		msgdict = vars(msg).copy()
		msgdict['tt'] = 0
		return cl(**msgdict)

		
	@classmethod
	def un_extend(cl, msg):
		msgdict = vars(msg).copy()
		del msgdict['tt']
		return cl(**msgdict)
		
		
	def __init__(self, type, **kwargs):
		spec = _META_SPEC_BY_TYPE[type]
		self_vars = vars(self)
		self_vars['type'] = type

		for name in kwargs:
			if name != 'tt' and name not in spec.settable_attributes:
				raise ValueError(
					'{} is not a valid argument for this message type'.format(name))

		for name, value in zip(spec.attributes, spec.defaults):
			self_vars[name] = value
		self_vars['time'] = 0
		self_vars['tt'] = 0
		
		for name, value in kwargs.items():
			# Using setattr here because we want type and value checks.
			self._setattr(name, value)

			
	#overriding from BaseMessage, to make an exception and allow removal of the new attribute
	#to convert message back to original spec
	def __delattr__(self, name):
		if name != 'tt':
			raise AttributeError('attribute cannot be deleted')
			

	def _setattr(self, name, value):
		spec = _META_SPEC_BY_TYPE[self.type]
		self_vars = vars(self)

		if name in spec.settable_attributes:
			if name == 'time':
				check_time(value)
			else:
				spec.check(name, value)
			self_vars[name] = value
		#added------------------
		elif name == 'tt':
			vars(self)['tt'] = value
		#end added--------------
		elif name in self_vars:
			raise AttributeError('{} attribute is read only'.format(name))
		else:
			raise AttributeError(
				'{} message has no attribute {}'.format(self.type, name))

	__setattr__ = _setattr

	
	#overriding from MetaMessage, we don't want this functionality for the 'Extended' variety 
	def bytes(self):
		raise NotImplemented

		
	def __repr__(self):
		spec = _META_SPEC_BY_TYPE[self.type]
		attributes = []
		for name in spec.attributes:
			attributes.append('{}={!r}'.format(name, getattr(self, name)))
		# #added------------------
		# attributes.append('tt=' + str(self.tt))
		# #end added--------------
		attributes = ' '.join(attributes)
		if attributes:
			attributes = (' {}'.format(attributes))

		return '<meta message {}{} time={} tt={}>'.format(self.type, attributes, self.time, self.tt)
		
#-----------------------------------------------------------------------------------------------------	
#---END MIDO EXTENSIONS-------------------------------------------------------------------------------	
#-----------------------------------------------------------------------------------------------------		

	