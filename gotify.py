# -*- coding: utf-8 -*-

# https://github.com/flocke/weechat-gotify

try:
	import weechat
except ImportError:
	from sys import exit
	print('This script has to run under WeeChat (https://weechat.org/).')
	exit(1)

from urllib import urlencode
import requests

SCRIPT_NAME = 'gotify'
SCRIPT_AUTHOR = 'flocke'
SCRIPT_VERSION = '0.1.0'
SCRIPT_LICENSE = 'MIT'
SCRIPT_DESC = 'Send highlights and mentions through Gotify'

SETTINGS = {
	'host': (
		'',
		'host for the gotify api'),
	'token': (
		'',
		'app token for the gotify api'),
	'priority': (
		'2',
		'priority of the message'),
	'separator': (
		': ',
		'separator between nick and message in notifications'),
        'timeout': (
                '5',
                'timeout for the message sending in seconds'),
	'notify_on_highlight': (
		'on',
		'push notifications for highlights in buffers (on/off)'),
	'notify_on_privmsg': (
		'on',
		'push notifications for private messages (on/off)'),
	'notify_when': (
		'always',
		'when to push notifications (away/detached/always/never)'),
	'ignore_buffers': (
		'',
		'comma-separated list of buffers to ignore'),
	'ignore_nicks': (
		'',
		'comma-separated list of users to not push notifications from'),
}

def send_message(title, message):
	token = weechat.config_get_plugin('token')
        host = weechat.config_get_plugin('host')

	if token != '' and host != '':
                timeout = float(weechat.config_get_plugin('timeout'))
                priority = int(weechat.config_get_plugin('priority'))

		api = host.rstrip('/') + '/message?token=' + token

                data = {
                    "message": message,
                    "title": title,
                    "priority": priority
                }

                try:
                    resp = requests.post(api, json=data, timeout=timeout)
                except requests.exceptions.Timeout:
                    weechat.prnt("", "{0:s}failed to send notification, the request to the Gotify API timed out".format(weechat.prefix("error")))

def get_sender(tags, prefix):
	# attempt to find sender from tags
	# nicks are always prefixed with 'nick_'
	for tag in tags:
		if tag.startswith('nick_'):
			return tag[5:]

	# fallback method to find sender from prefix
	# nicks in prefixes are prefixed with optional modes (e.g @ for operators)
	# so we have to strip away those first, if they exist
	if prefix.startswith(('~', '&', '@', '%', '+', '-', ' ')):
		return prefix[1:]

	return prefix

def get_buffer_names(buffer):
	buffer_names = []
	buffer_names.append(weechat.buffer_get_string(buffer, 'short_name'))
	buffer_names.append(weechat.buffer_get_string(buffer, 'name'))
	return buffer_names

def should_send(buffer, tags, nick, highlighted):
	if not nick:
		# a nick is required to form a correct message, bail
		return False

	if highlighted:
		if weechat.config_get_plugin('notify_on_highlight') != 'on':
			# notifying on highlights is disabled, bail
			return False
	elif weechat.buffer_get_string(buffer, 'localvar_type') == 'private':
		if weechat.config_get_plugin('notify_on_privmsg') != 'on':
			# notifying on private messages is disabled, bail
			return False
	else:
		# not a highlight or private message, bail
		return False

	notify_when = weechat.config_get_plugin('notify_when')
	if notify_when == 'never':
		# user has opted to not be notified, bail
		return False
	elif notify_when == 'away':
		# user has opted to only be notified when away
		infolist_args = (
			weechat.buffer_get_string(buffer, 'localvar_channel'),
			weechat.buffer_get_string(buffer, 'localvar_server'),
			weechat.buffer_get_string(buffer, 'localvar_nick')
		)

		if not None in infolist_args:
			infolist = weechat.infolist_get('irc_nick', '', ','.join(infolist_args))
			if infolist:
				away_status = weechat.infolist_integer(infolist, 'away')
				if not away_status:
					# user is not away, bail
					return False
	elif notify_when == 'detached':
		# user has opted to only be notified when detached (relays)
		num_relays = weechat.info_get('relay_client_count', 'connected')
		if num_relays != '0':
			# some relay(s) connected, bail
			return False

	if nick == weechat.buffer_get_string(buffer, 'localvar_nick'):
		# the sender was the current user, bail
		return False

	if nick in weechat.config_get_plugin('ignore_nicks').split(','):
		# the sender was on the ignore list, bail
		return False

	for buffer_name in get_buffer_names(buffer):
		if buffer_name in weechat.config_get_plugin('ignore_buffers').split(','):
			# the buffer was on the ignore list, bail
			return False

	return True

def message_callback(data, buffer, date, tags, displayed, highlight, prefix, message):
	nick = get_sender(tags, prefix)

	if should_send(buffer, tags, nick, int(highlight)):
		message = '%s%s%s' % (nick, weechat.config_get_plugin('separator'), message)

		if int(highlight):
			buffer_names = get_buffer_names(buffer)
			send_message(buffer_names[0] or buffer_names[1], message)
		else:
			send_message('Private Message', message)

	return weechat.WEECHAT_RC_OK

# register plugin
weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', '')

# grab all messages in any buffer
weechat.hook_print('', '', '', 1, 'message_callback', '')

# register configuration defaults
for option, value in SETTINGS.items():
	if not weechat.config_is_set_plugin(option):
		weechat.config_set_plugin(option, value[0])

	weechat.config_set_desc_plugin(option, '%s (default: "%s")' % (value[1], value[0]))
