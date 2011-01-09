#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users

import os
import sys
import random
import string

from simplesto import demjson
from Entities import User, Bucket, Item
	
def myauth():
	user = users.get_current_user()
	
	if not user:
		return False
	
	query = User.all()
	query.filter('user_name =', user.nickname())
	query.filter('user_domain =', 'google' )
	u = query.get()

	if not u:
		u = User(
			api_key=User.new_api_key(),
			user_name=user.nickname(), 
			user_domain='google',
			email = user.email()
			)
		u.put()
	return u
	
class MainHandler(webapp.RequestHandler): 
		
	def get(self):
		u = myauth()
		if u:
			path = os.path.join(os.path.dirname(__file__), 'templates/user.html')
			self.response.out.write(template.render(path, {
				"user":u,
				"logout_url": users.create_logout_url("/")
				}))
		else:
			path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
			self.response.out.write(template.render(path, {'login_url': users.create_login_url("/") }))

class guiHandler(webapp.RequestHandler):
	def get(self, secret=None, bucket_name=None):
		if bucket_name:			
			path = os.path.join(os.path.dirname(__file__), 'templates/items.html')
			self.response.out.write(template.render(path,{
				'bucket_name': bucket_name,
				'secret':secret
				}))
		else:
			u = myauth()
			if u:
				path = os.path.join(os.path.dirname(__file__), 'templates/buckets.html')
				self.response.out.write(template.render(path,{
				'secret':u.secret
				}))	
			else:
				# Let the user they should login.
				pass
def main():
    application = webapp.WSGIApplication([
		('/',MainHandler),
		('/gui/bucket/', guiHandler),
		('/gui/bucket/(.*)/', guiHandler),
		('/gui/bucket/(.*)/(.*)/item', guiHandler),
		], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()

"""
/api/buckets/
	GET: lists all buckets
	POST: creates a new bucket
	
/api/buckets/key
	GET: display bucket properties
	POST: updates bucket information
	
/api/buckets/key/items
	GET: list all items (pagination?)
	POST: create new item
	
/api/buckets/key/items/key
	GET: get full item data
	POST: update item data
"""