#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import util
from simplesto import demjson
from Entities import User, Bucket, Item, decode_auth
from simplesto.twitter_oauth_handler import OAuthClient, OAuthHandler, OAuthAccessToken
	
class UsersHandler(webapp.RequestHandler):
							
	def get(self):
		jsonp = self.request.get('jsoncallback', default_value=None)
		client = OAuthClient('twitter', self)
		auth_cookie = client.get_cookie()
		if not auth_cookie:
			return 
			
		AuthToken = OAuthAccessToken.get_by_key_name(auth_cookie)
		if not AuthToken:
			return 
		
		query = User.all()
		query.filter('user_name =', AuthToken.specifier)
		query.filter('user_domain =', AuthToken.service )
		u = query.get()
		if not u:
			return
			
		self.response.out.write(u.to_json(jsonp))
			
def main():
    application = webapp.WSGIApplication([
		('/api/user',UsersHandler),
		('/api/user/',UsersHandler),		
		], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

"""
/api/bucket/[auth]/[bucket_name]
"""