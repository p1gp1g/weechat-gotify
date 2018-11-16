# weechat-gotify

A [WeeChat](https://weechat.org/) plugin that sends highlights and/or private message notifications through [Gotify](https://github.com/gotify/).

### Options

The plugin allows you to set a few options through the normal WeeChat settings system.  
You'll find all of them under _`plugins.var.python.gotify`_, and all of them have helpful descriptions.

To set them use _`/set plugins.var.python.gotify.foo bar`_ or through the [iset.pl](https://weechat.org/scripts/source/iset.pl.html) plugin.

- `host`
	- host for the gotify api (default: "")
- `token`
	- app token for the gotify api (default: "")
- `priority`
	- priority of the message (default: 2)
- `timeout`
	- timeout for the message sending in seconds (>= 1) (default: 30)
- `separator`
	- separator between nick and message in notifications (default: ": ")
- `notify_on_highlight`
	- push notifications for highlights in buffers (on/off) (default: "on")
- `notify_on_privmsg`
	- push notifications for private messages (on/off) (default: "on")
- `notify_when`
	- when to push notifications (away/detached/always/never) (default: "always")
- `ignore_buffers`
	- comma-separated list of buffers to ignore (default: "")
- `ignore_nicks`
	- comma-separated list of users to not push notifications from (default: "")

