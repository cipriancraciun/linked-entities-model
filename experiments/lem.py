

import json as py_json
import secrets as py_secrets
import sys as py_sys
import time as py_time




class Base (object) :
	
	def _print (self, _stream = None, /) :
		if _stream is None :
			_stream = py_sys.stdout
		print (self, file = _stream)
	
	def _print_json (self, _stream = None, /) :
		if _stream is None :
			_stream = py_sys.stdout
		_json = self._json ()
		py_json.dump (
				_json, _stream,
				ensure_ascii = True,
				indent = 2,
				separators = (",", " : "),
				sort_keys = False,
			)




class Id (Base) :
	
	def __init__ (self, _id) :
		self._id = _id
	
	def _id_raw (self) :
		return self._id
	
	def _json (self) :
		return self._id
	
	def __repr__ (self) :
		return "<id {}>".format (self._id)


def id (_id) :
	if isinstance (_id, Id) :
		pass
	elif isinstance (_id, str) :
		_id = Id (_id)
	elif isinstance (_id, (Entity, Link, Facet, Attachment)) :
		_id = _id._id
		_id = id (_id)
	elif callable (_id) :
		_id = _id ()
		_id = id (_id)
	else :
		raise Exception ("[c5e36136]", _id)
	return _id




class IdPrefixGenerator (Base) :
	
	def __init__ (self, _prefix, _separator) :
		self._prefix = _prefix
		self._separator = _separator
	
	def __call__ (self, *_elements) :
		_id = self._prefix + self._separator + self._separator.join (_elements)
		_id = Id (_id)
		return _id


class IdRandomGenerator (Base) :
	
	def __init__ (self, _format, _length) :
		self._format = _format
		self._length = _length
	
	def __call__ (self) :
		_token = py_secrets.token_hex (self._length)
		_id = self._format.format (_token)
		_id = Id (_id)
		return _id


def id_prefix (*, prefix, separator = "/") :
	return IdPrefixGenerator (prefix, separator)

def id_random (*, format, length = 16) :
	return IdRandomGenerator (format, length)

def id_tag_random (*, authority, length = 8) :
	_date = py_time.gmtime ()
	_date = py_time.strftime ("%Y-%m-%d", _date)
	_prefix = "tag:{},{}:id:".format (authority, _date)
	_generator = IdRandomGenerator (_prefix + "{}", length)
	return _generator




class Bundle (Base) :
	
	def __init__ (self) :
		self._records = []
	
	def entity (self, **_arguments) :
		return entity (bundle = self, **_arguments)
	
	def entity_with_facet (self, **_arguments) :
		return entity_with_facet (bundle = self, **_arguments)
	
	def link (self, **_arguments) :
		return link (bundle = self, **_arguments)
	
	def link_with_facet (self, **_arguments) :
		return link_with_facet (bundle = self, **_arguments)
	
	def facet (self, **_arguments) :
		return facet (bundle = self, **_arguments)
	
	def attachment (self, **_arguments) :
		return attachment (bundle = self, **_arguments)
	
	def _discover (self, _callback) :
		for _record in self._records :
			_callback (_record)
	
	@staticmethod
	def _include (_bundle, _record) :
		if _bundle is not None :
			_bundle._records.append (_record)
		return _bundle
	
	def _json (self) :
		_records = []
		recurse (self, lambda _record : _records.append (_record._json ()))
		_json = {
				"$schema" : "https://w3id.org/lem/2021a/schemas/records",
				"$records" : _records,
			}
		return _json


def bundle () :
	return Bundle ()




class Entity (Base) :
	
	def __init__ (self, _id, _bundle) :
		self._id = id (_id)
		self._bundle = Bundle._include (_bundle, self)
		self._facets = []
		self._links = []
		self._attachments = []
	
	def facet (self, *, schema, properties) :
		return Facet (self._id, schema, properties, self, self._bundle)
	
	def attachment (self, *, id, schema, url) :
		return Attachment (id, self._id, schema, url, self, self._bundle)
	
	def _discover (self, _callback) :
		_callback (self)
		for _facet in self._facets :
			_callback (_facet)
		for _link in self._links :
			_callback (_link)
		for _attachment in self._attachments :
			_callback (_attachment)
	
	def _type_raw (self) :
		return "entity"
	
	def _id_raw (self) :
		return self._id._id_raw ()
	
	def __repr__ (self) :
		return "<entity (id {})>".format (self._id_raw ())
	
	def _json (self) :
		_json = {
				"$type" : self._type_raw (),
				"$id" : self._id._json (),
			}
		return _json


def entity (*, id, bundle = None) :
	return Entity (id, bundle)

def entity_with_facet (*, id, facet, properties, bundle = None) :
	_entity = entity (id = id, bundle = bundle)
	_entity.facet (schema = facet, properties = properties)
	return _entity




class Link (Base) :
	
	def __init__ (self, _id, _schema, _entities, _bundle) :
		self._id = id (_id)
		self._schema = id (_schema)
		self._owners = []
		self._entities = _data_process (_entities, None, lambda _data, _path : id (_data))
		for _owner in self._owners :
			_owner._links.append (self)
		self._bundle = Bundle._include (_bundle, self)
		self._facets = []
		self._links = []
		self._attachments = []
	
	def facet (self, *, schema, properties) :
		return Facet (self._id, schema, properties, self, self._bundle)
	
	def attachment (self, *, id, schema, url) :
		return Attachment (id, self._id, schema, url, self, self._bundle)
	
	def _discover (self, _callback) :
		for _owner in self._owners :
			_callback (_owner)
		_callback (self)
		for _facet in self._facets :
			_callback (_facet)
		for _link in self._links :
			_callback (_link)
		for _attachment in self._attachments :
			_callback (_attachment)
	
	def _type_raw (self) :
		return "link"
	
	def _id_raw (self) :
		return self._id._id_raw ()
	
	def _schema_raw (self) :
		return self._schema._id_raw ()
	
	def __repr__ (self) :
		return "<link (id {}) (schema {}) (entities {})>".format (self._id_raw (), self._schema_raw (), self._entities)
	
	def _json (self) :
		_json = {
				"$type" : self._type_raw (),
				"$id" : self._id._json (),
				"$schema" : self._schema._json (),
				"$entities" : self._entities_json (),
			}
		return _json
	
	def _entities_json (self) :
		_json = _data_process (self._entities, None, lambda _data, _path : _data._json ())
		return _json


def link (*, id, schema, entities, bundle = None) :
	return Link (id, schema, entities, bundle)

def link_with_facet (*, id, schema, facet, entities, properties, bundle = None) :
	_link = link (id = id, schema = schema, entities = entities, bundle = bundle)
	_link.facet (schema = facet, properties = properties)
	return _link




class Facet (Base) :
	
	def __init__ (self, _id, _schema, _properties, _owner, _bundle) :
		self._id = id (_id)
		self._schema = id (_schema)
		self._properties = _data_process (_properties, None, None)
		self._owner = _owner
		if self._owner is not None :
			self._owner._facets.append (self)
		self._bundle = Bundle._include (_bundle, self)
	
	def _discover (self, _callback) :
		if self._owner is not None :
			_callback (self._owner)
		_callback (self)
	
	def _type_raw (self) :
		return "facet"
	
	def _id_raw (self) :
		return self._id._id_raw ()
	
	def _schema_raw (self) :
		return self._schema._id_raw ()
	
	def __repr__ (self) :
		return "<facet (id {}) (schema {}) (properties {})>".format (self._id_raw (), self._schema_raw (), self._properties)
	
	def _json (self) :
		_json = {
				"$type" : self._type_raw (),
				"$id" : self._id._json (),
				"$schema" : self._schema._json (),
				"$properties" : self._properties_json (),
			}
		return _json
	
	def _properties_json (self) :
		# FIXME
		return self._properties


def facet (*, id, schema, properties, bundle = None) :
	return Facet (id, schema, properties, None, bundle)




class Attachment (Base) :
	
	def __init__ (self, _id, _entity, _schema, _url, _owner, _bundle) :
		self._id = id (_id)
		self._entity = id (_entity)
		self._schema = id (_schema)
		self._url = id (_url)
		self._owner = _owner
		if self._owner is not None :
			self._owner._attachments.append (self)
		self._bundle = Bundle._include (_bundle, self)
	
	def _discover (self, _callback) :
		if self._owner is not None :
			_callback (self._owner)
		_callback (self)
	
	def _type_raw (self) :
		return "attachment"
	
	def _id_raw (self) :
		return self._id._id_raw ()
	
	def _entity_raw (self) :
		return self._entity._id_raw ()
	
	def _schema_raw (self) :
		return self._schema._id_raw ()
	
	def __repr__ (self) :
		return "<attachment (id {}) (entity {}) (schema {}) (url {})>".format (self._id_raw (), self._entity_raw (), self._schema_raw (), self._url)
	
	def _json (self) :
		_json = {
				"$type" : self._type_raw (),
				"$id" : self._id._json (),
				"$entity" : self._entity._json (),
				"$schema" : self._schema._json (),
				"$url" : self._url._json (),
			}
		return _json


def attachment (*, id, entity, schema, url, bundle = None) :
	return Attachment (id, entity, schema, url, None, bundle)




def recurse (_root, _callback) :
	
	_discovered = set ()
	_queue = list ()
	
	def _callback_0 (_record) :
		_type = _record._type_raw ()
		_id = _record._id_raw ()
		if (_type, _id) in _discovered :
			return
		_discovered.add ((_type, _id))
		_queue.append (_record)
	
	_discover_0 (_root, _callback_0)
	
	while len (_queue) > 0 :
		_record = _queue.pop (0)
		_callback (_record)
		_discover_0 (_record, _callback_0)


def _discover_0 (_record, _callback) :
	if isinstance (_record, (Entity, Facet, Link, Attachment)) :
		_record._discover (_callback)
	elif isinstance (_record, Bundle) :
		_record._discover (_callback)
	elif isinstance (_record, (list, tuple)) :
		for _record in _record :
			_discover_0 (_record, _callback)
	else :
		raise Exception ("[9f37dd14]", _record)




def _data_process (_data, _validator, _translator) :
	if _validator is None :
		_validator = lambda _data, _path : True
	if _translator is None :
		_translator = lambda _data, _path : _data
	return _data_process_0 ((), _data, _validator, _translator)


def _data_process_0 (_path, _data, _validator, _translator) :
	
	if _data is None or isinstance (_data, (bool, int, float, str)) :
		_data = _translator (_data, _path)
		if not _validator (_data, _path) :
			raise Exception ("[7f8ae5d1]", _path, _data)
		
	elif isinstance (_data, list) :
		_data = [_data_process_0 (_path + (_index,), _data, _validator, _tranlator) for _index, _data in enumerate (_data)]
		
	elif isinstance (_data, dict) :
		_data = {_index : _data_process_0 (_path + (_index,), _data, _validator, _translator) for _index, _data in _data.items ()}
		
	else :
		_data = _translator (_data, _path)
		if not _validator (_data, _path) :
			raise Exception ("[4f24c0f9]", _path, _data)
	
	return _data

