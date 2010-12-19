#!/usr/bin/env python
import urllib
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from simplesto import demjson
from Entities import User, Bucket, Item, decode_auth
	
class ItemsHandler(webapp.RequestHandler):
							
	def get(self, auth_token=None, bucket_name=None, item_name=None):
		method = self.request.get('method')
		
		if method == 'post':
			self.post(auth_token, bucket_name, item_name)
			return
			
		if method == 'delete':
			self.delete(auth_token, bucket_name, item_name)
			return
		
		jsonp = self.request.get('jsoncallback')
		user_id, secret = decode_auth(auth_token)
		bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
		
		bucket = Bucket.get_by_key_name(bucket_name, parent=db.Key.from_path('User', user_id))
		if not bucket:
			return
		if not bucket.is_public and bucket.secret != secret:
			return
			
		if not item_name:
			query = Item.all().ancestor(bucket)
			items = [ item.to_dict() for item in query ]
			json = demjson.encode(items)
			if jsonp:
				json = "%s(%s)" % (jsonp, json)
			self.response.out.write(json)
		else:
			item_name = urllib.unquote(item_name.encode('ascii')).decode('utf-8')
			item = Item.get_by_key_name(item_name, parent=bucket)
			if not item:
				return
			self.response.out.write( item.to_json(jsonp) )
		
	def post(self, auth_token=None, bucket_name=None, item_name=None):
		jsonp = self.request.get('jsoncallback')
		user_id, secret = decode_auth(auth_token)
		bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
		bucket = Bucket.get_by_key_name(bucket_name, parent=db.Key.from_path('User', user_id))
		
		application = self.request.get('application', default_value='')
		datatype = self.request.get('datatype', default_value='')
		content = self.request.get('content', default_value='')
		exp_date = self.request.get('exp_date', default_value=None)		
				
		if not bucket:
			return
		if bucket.secret != secret:
			return
			
		if not item_name:
			item_name = self.request.get('name')
		else:
			item_name = urllib.unquote(item_name.encode('ascii')).decode('utf-8')
			
		i = Item.get_by_key_name(item_name, parent=bucket)
		if i:
			upd = False 
			if application:
				i.application = application
				upd = True
			if datatype:
				i.datatype = datatype
				upd = True
			if content:
				i.content = content
				upd = True
			if exp_date:
				i.exp_date = exp_date
				upd = True
			if upd:
				i.put()	
		else:
			i = Item(
				key_name = item_name,
				parent = bucket,
				content = content,
				datatype = datatype,
				application = application,
				exp_date = exp_date
			)
			i.put()
		self.response.out.write(i.to_json(jsonp))
		
	def delete(self, auth_token=None, bucket_name=None, item_name=None):
		jsonp = self.request.get('jsoncallback')
		user_id, secret = decode_auth(auth_token)
		bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
		item_name = urllib.unquote(item_name.encode('ascii')).decode('utf-8')
		bucket = Bucket.get_by_key_name(bucket_name, parent=db.Key.from_path('User', user_id))

		if not bucket or bucket.secret != secret:
			return
			
		i = Item.get_by_key_name(item_name, parent=bucket)
		if i:
			i.delete()
			json = demjson.encode({'response': 'item deleted'})
			if jsonp:
				json = "%s(%s)" % (jsonp, json)
			self.response.out.write(json)
			return

def main():
    application = webapp.WSGIApplication([
		('/api/bucket/(.*)/(.*)/item/(.*)',ItemsHandler),
		('/api/bucket/(.*)/(.*)/item',ItemsHandler),	
		], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

"""
/api/bucket/[auth]/[bucket_name]
"""