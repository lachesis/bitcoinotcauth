__module_name__ = "otcgpgauth" 
__module_version__ = "0.5" 
__module_description__ = "Perform GPG authentication steps on #bitcoin-otc."
__module_author__ = "Eric Swanson <eswanson@alloscomp.com>"

import xchat,re,subprocess
import urllib2,urllib

def __pastebin(data):
	# Make the request to the Pastebin API
	resp = urllib2.urlopen('http://pastebin.com/api_public.php', urllib.urlencode({ 'paste_code' : str(data), 'paste_expire_date': '10M' }))
	pburl = resp.read()

	# Check the response; return url if it's correct
	if not pburl.startswith('http://pastebin.com/'):
		raise RuntimeError, pburl
	return pburl

def __clearsign(challenge_string):
	p = subprocess.Popen(['gpg','--no-tty','--clearsign'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
	o,e = p.communicate(challenge_string)
	return o

def acceptGribbleMessages(word,word_eol,event):
	if word[0] == 'gribble':
		m = re.match(r'(?i)^Request successful for user .*?\. Your challenge string is: ([a-f0-9]*)$',word[1])
		if m:
			# Print what gribble said
			xchat.emit_print(event,word[0],word[1]+' ')
			
			cs = m.group(1)
			#xchat.emit_print(event,'otc-gpg',"Challenge: {0}".format(cs))
			resp = __clearsign(cs) # Sign the string
			if not resp:
				xchat.emit_print(event,'otc-gpg',"Error: empty response from gpg!")
			xchat.emit_print(event,'otc-gpg',resp)
			
			# Pastebin the resp
			url = __pastebin(data=resp)
			xchat.emit_print(event,'otc-gpg',"Uploaded to {0}".format(url))
			
			# Tell gribble
			xchat.command('msg gribble ;;gpg verify {0}'.format(url))
			
			return xchat.EAT_XCHAT
		
	return xchat.EAT_NONE
	
def startAuth(*args,**kwargs):
	xchat.command('msg gribble ;;gpg auth {0}'.format(xchat.get_info('nick')))
	return xchat.EAT_XCHAT

# Hook private messages so we can answer gribble's request for auth
for event in [ "Private Message", "Private Message to Dialog" ]:
    xchat.hook_print(event, acceptGribbleMessages, event)

# Hook the command '/gauth' to send the phrase to start auth
xchat.hook_command('gauth',startAuth)

def unload_cb(userdata): print "Plugin '#bitcoin-otc gpg auth' unloaded"
xchat.hook_unload(unload_cb) 

print "Plugin '#bitcoin-otc gpg auth' loaded"

