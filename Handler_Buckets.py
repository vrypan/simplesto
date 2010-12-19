#!/usr/bin/env python
import urllib
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from simplesto import demjson
from Entities import User, Bucket, Item, decode_auth
	
class BucketsHandler(webapp.RequestHandler):
							
	def get(self, auth_token=None, bucket_name=None):
			
		user_id, secret = decode_auth(auth_token)
		jsonp = self.request.get('jsoncallback')
		method = self.request.get('method')
		if method == 'post':
			return self.post(auth_token, bucket_name)
		if method == 'delete':
			return self.delete(auth_token, bucket_name)
		
		if not bucket_name:
			# /bucket/<userid>x<api_key>
			# /bucket/123xAB18c
			# list user buckets
			user = User.get_by_id(user_id)
			if not user:
				return
			if user.api_key != secret:
				return
			query = Bucket.all().ancestor(user)
			
			buckets = [ bucket.to_dict() for bucket in query ]
			json = demjson.encode(buckets)
			if jsonp:
				json = "%s(%s)" % (jsonp, json)
			self.response.out.write(json)
		else:
			bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
			# /bucket/<userid>x<api_key>/<bucket_name>
			# /bucket/123xAB18c/notes
			# get bucket details
			bucket = Bucket.get_by_key_name(bucket_name, parent=db.Key.from_path('User', user_id))
			if bucket and bucket.secret != secret:
				return
			self.response.out.write(bucket.to_json(jsonp))
		
	def post(self, auth_token=None, bucket_name=None):
		user_id, secret = decode_auth(auth_token)
		jsonp = self.request.get('jsoncallback')
		
		if not bucket_name:
			# /bucket/<userid>x<api_key>
			# /bucket/123xAB18c
			# create new bucket
			user = User.get_by_id(user_id)
			if not user:
				return
			if user.api_key != secret:
				return
			bucket_name = self.request.get('name')
			description = self.request.get('description', default_value='')
			is_public = self.request.get('is_public', default_value='0')
			b = Bucket.get_by_key_name(bucket_name, parent=user)
			if b:
				b.description = description
				b.is_public = is_public.upper() in ('TRUE','YES', '1' )
			else:
				b = Bucket(
					key_name = bucket_name, 
					parent=user,
					description = description,
					is_public = is_public.upper() in ('TRUE','YES', '1' ),
					)
			b.put()
			self.response.out.write(Bucket.get(b.key()).to_json(jsonp))
		else:
			# /bucket/<userid>x<bucket_secret>/<bucket_name>
			# /bucket/123xAB18c/mybucket
			# update bucket properties
			bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
			description = self.request.get('description', default_value='')
			is_public = self.request.get('is_public', default_value='undef')
			
			b = Bucket.get_by_auth_name(auth_token, bucket_name)
			if not b:
				return
			upd = False
			if description:
				b.description = description
				upd = True
			if is_public != 'undef':
				b.is_public = is_public.upper() in ('TRUE','YES', '1' )
				upd = True
			if upd:
				b.put()
			self.response.out.write(Bucket.get(b.key()).to_json(jsonp))
			
	def delete(self, auth_token=None, bucket_name=None):
		user_id, secret = decode_auth(auth_token)
		jsonp = self.request.get('jsoncallback')
		
		if not bucket_name:
			return;
		else:
			bucket_name = urllib.unquote(bucket_name.encode('ascii')).decode('utf-8')
			
		user = User.get_by_id(user_id)
		if not user:
			return
		if user.api_key != secret:
			return
		b = Bucket.get_by_key_name(bucket_name, parent=user)
		if not b:
			return
		else:
			b.delete()
			json = demjson.encode({'response': 'bucket deleted'})
			if jsonp:
				json = "%s(%s)" % (jsonp, json)
			self.response.out.write(json)
			return 
			
def main():
    application = webapp.WSGIApplication([
		('/api/bucket/(.*)/(.*)',BucketsHandler),
		('/api/bucket/(.*)',BucketsHandler),		
		], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

"""
/api/bucket/[auth]/[bucket_name]
"""