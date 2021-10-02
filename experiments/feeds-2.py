

import lem


_ns_microformats = lem.id_prefix (prefix = "https://w3id.org/lem/2021a/schemas/microformats", separator = "/")

_ns_ciprian = lem.id_prefix (prefix = "https://w3id.org/people/ciprian.craciun", separator = "/")
_ns_ciprian_resources = lem.id_prefix (prefix = "https://w3id.org/people/ciprian.craciun/2021", separator = "/")
_ns_ciprian_random = lem.id_tag_random (authority = "ciprian.craciun@gmail.com")




_bundle = lem.bundle ()




_ciprian = _bundle.entity_with_facet (
		id = _ns_ciprian ("self"),
		facet = _ns_microformats ("h-card"),
		properties = {
				"name" : "Ciprian Dorin Craciun",
			})

_ciprian.attachment (
		id = _ns_ciprian ("self", "avatar"),
		schema = _ns_microformats ("h-card", "logo"),
		url = "https://scratchpad.volution.ro/ciprian/c602db805b4e93c9014126062432311b/avatar.jpg")




_feed = _bundle.entity_with_facet (
		id = _ns_ciprian_resources ("830529eb"),
		facet = _ns_microformats ("h-feed"),
		properties = {
				"name" : "Ciprian's unpublished ideas",
			})

_bundle.link (
		id = _ns_ciprian_resources ("830529eb", "author"),
		schema = _ns_microformats ("h-feed", "author"),
		entities = {
				"feed" : _feed,
				"author" : _ciprian,
			})




def _article (*, id, title, updated = None, feeds = []) :
	
	_url_base = "https://scratchpad.volution.ro/ciprian/992c7f2944456f18cdde77f683f49aa7/"
	
	_post = _bundle.entity_with_facet (
			id = _ns_ciprian_resources (id),
			facet = _ns_microformats ("h-entry"),
			properties = {
					"name" : title,
					"url" : _url_base + id,
					"updated" : updated,
				})
	
	_post.attachment (
			id = _ns_ciprian_resources (id, "content", "html"),
			schema = _ns_microformats ("h-entry", "content", "html"),
			url = _url_base + id + ".html")
	
	_post.attachment (
			id = _ns_ciprian_resources (id, "content", "text"),
			schema = _ns_microformats ("h-entry", "content", "text"),
			url = _url_base + id + ".txt")
	
	_bundle.link (
			id = _ns_ciprian_resources (id, "author"),
			schema = _ns_microformats ("h-entry", "author"),
			entities = {
					"entry" : _post,
					"author" : _ciprian,
				})
	
	for _feed in feeds :
		_bundle.link (
				id = _ns_ciprian_random (),
				schema = _ns_microformats ("h-feed", "entry"),
				entities = {
						"feed" : _feed,
						"entry" : _post,
					})


_article (id = "19817cd9", title = "Data as code", updated = "2021-09-11", feeds = [_feed])
_article (id = "1ab930b7", title = "Entities, links, data", updated = "2021-09-11", feeds = [_feed])
_article (id = "4a56cfca", title = "The `...` symlinks trick for \"local aliasing\"", updated = "2021-09-11", feeds = [_feed])
_article (id = "58cdcdcd", title = "Regarding a common HTML rendering for markup languages", updated = "2021-09-13", feeds = [_feed])
_article (id = "6697ebb3", title = "Using file-systems for structured-data editors", updated = "2021-09-11", feeds = [_feed])


_bundle._print_json ()

