from google.appengine.ext import db
import random
import string
from simplesto import demjson

class User(db.Model):
	api_key = db.StringProperty(required=True)
	user_name = db.StringProperty(required=True)
	user_domain = db.StringProperty(required=True)
	real_name = db.StringProperty()
	email = db.EmailProperty()
	url = db.LinkProperty()
	cre_date = db.DateTimeProperty(auto_now_add=True)
	upd_date = db.DateTimeProperty(auto_now=True)
	
	@classmethod
	def get_by_user_key(cls, user_name, api_key, user_domain='twitter'):
		if not (user_name and api_key):
			return False
		query = User.all()
		query.filter('user_name =', user_name)
		query.filter('api_key =', api_key)
		query.filter('user_domain =', user_domain)
		u = query.get()
		if not u:
			return None
		else:
			return u

	@classmethod
	def new_api_key(cls):
		bucket_secret = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(8))
		return bucket_secret
		
	def to_dict(self):
		response = {
			"user_name": self.user_name,
			"user_domain": self.user_domain,
			"real_name": self.real_name,
			"email": self.email,
			"url": self.url,
			"cre_date": self.cre_date.isoformat(),
			"upd_date": self.upd_date.isoformat(),
			"secret": "%dx%s" % (self.key().id(), self.api_key)
		}
		return response

	def to_json(self, jsonp=None):
		ret = demjson.encode(self.to_dict())
		if jsonp:
			ret = "%s(%s)" % (jsonp, ret)
		return ret
	
class Bucket(db.Model):
	secret = db.StringProperty()
	cre_date = db.DateTimeProperty(auto_now_add=True)
	upd_date = db.DateTimeProperty(auto_now=True)
	is_public = db.BooleanProperty(default=False)
	description = db.TextProperty()
	
	def to_dict(self):
		response = {
			"name": self.key().name(),
			"auth_token": self.xkey(),
			"is_public": self.is_public,
			"description": self.description,
			"upd_date": self.upd_date.isoformat()
		}
		return response
	def to_json(self, jsonp=None):
		ret = demjson.encode(self.to_dict())
		if jsonp:
			ret = "%s(%s)" % (jsonp, ret)
		return ret
		
	def xkey(self):
		return "%dx%s" % (self.key().parent().id(), self.secret)
		
	@classmethod
	def new_secret(cls):
		bucket_secret = ''.join(random.choice(string.ascii_letters + string.digits) for i in xrange(8))
		return bucket_secret
		
	def put(self):
		if not self.secret:
			self.secret = Bucket.new_secret()
		return db.Model.put(self)
		
	@classmethod
	def get_by_auth_name(cls, auth_token, bucket_name):
		parent_id, secret = decode_auth(auth_token)
		b = cls.get_by_key_name(bucket_name, parent=db.Key.from_path('User', parent_id) )
		if b and (b.secret == secret):
			return b
		else:
			return None
		
class Item(db.Model):
	application = db.StringProperty() #usually the application creating the item.
	cre_date = db.DateTimeProperty(auto_now_add=True)
	upd_date = db.DateTimeProperty(auto_now=True)	
	exp_date = db.DateTimeProperty()
	datatype = db.StringProperty()
	content = db.TextProperty()
	
	def to_dict(self):
		bucket = self.parent()
		response = {
			"name": self.key().name(),
			"application": self.application,
			"cre_date": self.cre_date.isoformat(),
			"upd_date": self.upd_date.isoformat(),
			"datatype": self.datatype,
			"content": self.content
		}
		if self.exp_date:
			response['exp_date'] = self.exp_date.isoformat()
		return response
	
	def to_json(self, jsonp=None):
		ret = demjson.encode(self.to_dict())
		if jsonp:
			ret = "%s(%s)" % (jsonp, ret)
		return ret	

def decode_auth(token):
	parent_id, x, secret = token.partition('x')
	return int(parent_id), secret