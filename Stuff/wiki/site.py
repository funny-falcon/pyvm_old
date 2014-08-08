#
# para-wiki: the ridiculously simple wiki engine.
#
# This code is in the public domain. Written by Stelios Xanthakis
#
# For few pages/hits. Everything is loaded in memory.
# No databases.
# Runs with SimpleHTTPServer. No CGI.
# With a stackless VM, you can run a wiki server with just 3 OS threads.
#
# This is good for people who have a non-root, unix account with quotas.
# If you run this server at some other port the sysadmin shouldn't mind.
#
# Dependancies: web.py and markdown.py 
#
#
# Todo: 
#	-source shows orig.
#	-relative URLS
#	-convert to static
#
import web
import sys
import md5
from markdown import Markdown
from binascii import hexlify
from threading import Lock
from time import time

from cms import Pages, Stylesheet, Passwd, Limits, HOST
from cms import REDIRECT_FILE, REDIRECT_DIR

def wrt (*args):
	for i in args:
		sys.stderr.write (repr (i))
	sys.stderr.write ('\n')
	sys.stderr.flush ()


PAGES = {}

class page:
	def __init__ (self, name):
		self.name = name
		PAGES [name] = self
		self.text = None
		try:
			text = open (name + '.txt').read ()
		except:
			text = ''
		self.update (text, md5.new (text).hexdigest ())
		self.commit ()
		self.last_edit = time()
		L = Lock ()
		self.acquire, self.release = L.acquire, L.release
	def commit (self):
		self.html = self.cache
		self.sig_head = self.sig_cache
	def web_commit (self):
		self.acquire ()
		try:
			self.commit ()
			file (self.name + '.txt', 'w+').write (self.text)
		finally:
			self.release ()
	def update (self, text, sig):
		if text == self.text:
			return
		self.cache = Markdown (text)
		self.text = text
		self.sig_cache = sig
		file (self.name + '.txt2', 'w+').write (text)
	def modified (self):
		return self.sig_cache != self.sig_head

for i in Pages:
	page (i)

PAGEre = "|".join (PAGES.keys ())

urls = (
	'/','view',
	'/edit/(' + PAGEre + ').html', 'edit',
	'/update/(' + PAGEre + ')/(.+)', 'cache',
	'/cache/(' + PAGEre + ').html', 'cache',
	'/commit/(' + PAGEre + ').html', 'commit',
	'/source/(' + PAGEre + ').html', 'source',
	'/special/(.+)', '_site',
	'/(' + PAGEre + ').html', 'view'
)

class Stats:
	NR = 0
	start_time = time()

def fmt_time (t):
	min, sec = divmod (t, 60)
	hour, min = divmod (min, 60)
	return '%i:%i:%i' %(hour, min, sec)

def site_html_start ():
	print "<html>"
	print '<head> <style type="text/css">' + Stylesheet + '</style></head> '
	print "<body>"

class site:
	def Footer (self, P):
		print "<br><hr><small>"
		def sup (name, href, active, ext=".html"):
			if active:
				print ".<sup><a href=%s%s>%s</a></sup>" %(href, ext, name)
			else:
				print ".<sup>"+name+"</sup>"
		sup ('root', '/', 1, '')
		for i in 'head', 'cache', 'source', 'edit':
			if i == 'head': j = P.name
			else: j = i + '/' + P.name
			sup (i, '/'+j, self.dom != i)
		if self.dom == 'cache':
			sup ('commit', '/commit/'+P.name, P.modified ())
		print "</small></body></html>"

	def GET (self, name='main'):
		Stats.NR += 1
		P = PAGES [name]
		web.header ('Content-Type', 'text/html')
		site_html_start ()
		self.custom_GET (P)
		self.Footer (P)

class view(site):
	dom = 'head'
	def custom_GET (self, P):
		print P.html

class edit(site):
	dom = 'edit'
	def custom_GET (self, P):
		P.acquire ()
		try:
			now = time()
			last_edit, name, sig_cache, text = P.last_edit, P.name, P.sig_cache, P.text
			P.last_edit = now
		finally:
			P.release ()
		diff = fmt_time (int (now - last_edit))
		print "Last time somebody requested edit of this page was %s ago"%diff
		print '<br><form action="/update/%s/%s" method=post>' % (
				name, sig_cache)
		print ('<p><textarea name=text rows=20 cols=80>' + text +
			'</textarea><br><input type=submit></p></form>')

class cache(site):
	dom = 'cache'
	def custom_GET (self, P):
		print P.cache
	def POST (self, name, sig):
		text = web.input ().text
		MD5 = md5.new (text).hexdigest ()
		if MD5 == sig:
			self.GET (name)
			return
		P = PAGES [name]
		P.acquire ()
		if sig != P.sig_cache:
			P.release ()
			site_html_start ()
			print "<h1>CAN'T UPDATE: THE PAGE HAS BEEN MODIFIED !</h1></body></html>"
			return
		try:
			P.update (text, MD5)
		finally:
			P.release ()
		self.GET (name)

class source:
	def GET (self, name='main'):
		web.header ('Content-Type', 'text/plain')
		print PAGES [name].text

class commit:
	def GET (self, name=''):
		try:
			if web.input ().passwd == Passwd:
				PAGES [name].web_commit ()
				web.redirect ('/cache/%s.html' % name)
				return
		except:
			pass
		print '<html>'
		print '<form action="/commit/%s.html" method=get>' % name
		print 'Enter password to commit: <input name=passwd type=text>'
		print '</form>'
		print '</html>'

class _site:
	def GET (self, name):
		if name == 'Index.html':
			self.GET_Index ()
		elif name == 'stats.html':
			self.GET_stats ()
		elif name == 'site.py':
			self.GET_sitepy ()
		else:
			web.notfound ()

	def GET_sitepy (self):
		web.header ('Content-Type', 'text/plain')
		print open ('site.py').read ()


	def GET_stats (self):
		web.header ('Content-Type', 'text/plain')
		print "%i requests served" %Stats.NR
		print "server uptime %s" %fmt_time (int (time() - Stats.start_time))
		try:
			import pyvm_extra
			pyvm_extra.thread_status ()
		except:
			pass

	def GET_Index (self):
		web.header ('Content-Type', 'text/html')
		print "<html><body><ul>"
		for i in sorted (PAGES.keys ()):
			print '<li><a href=/%s.html>%s</a>' %(i, i)
			if not PAGES [i].text:
				print "(empty)"
			if PAGES [i].modified ():
				print "(modified<blink>!</blink>)"
		print "</ul></body></html>"

tothewiki=r"""<html><head>
<meta http-equiv=refresh content="2;url=%s">
</head><body>redirecting to %s...
let's hope it works!</body></html>
"""

#
# __main__ -- this is an application
#

port = int (sys.argv [1])
ADDR = "http://"+HOST+":"+str(port)+"/"
file (REDIRECT_DIR+REDIRECT_FILE, 'w').write (tothewiki % (ADDR, ADDR))
web.run (urls)
