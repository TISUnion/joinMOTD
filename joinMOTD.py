import json
import os

from mcdreforged.api.all import *

PLUGIN_METADATA = {
	'id': 'join_motd',
	'version': '1.1.0',
	'name': 'Join MOTD Display',
	'author': 'Fallen_Breath',
	'link': 'https://github.com/TISUnion/joinMOTD'
}

Prefix = '!!joinMOTD'
ConfigFilePath = os.path.join('config', 'joinMOTD.json')


def get_day(server: ServerInterface):
	for pid in ('mcd_daycount', 'day_count_reforged', 'daycount_nbt'):
		api = server.get_plugin_instance(pid)
		if hasattr(api, 'getday') and callable(api.getday):
			return api.getday()
	return '?'


def on_player_joined(server: ServerInterface, player, info):
	message = RTextList()
	with open(ConfigFilePath, 'r') as f:
		js = json.load(f)
	server_name = str(js["serverName"])
	main_server_name = str(js["mainServerName"])
	lines = js["serverList"]
	for i in range(len(lines)):
		subServerName = lines[i]
		command = '/server {}'.format(subServerName)
		message.append(RText('[{}]'.format(subServerName)).h(command).c(RAction.run_command, command))
		if i != len(lines) - 1:
			message.append(' ')

	server.tell(player, '§7=======§r Welcome back to §e{}§7 =======§r'.format(server_name))
	server.tell(player, '今天是§e{}§r开服的第§e{}§r天'.format(main_server_name, get_day(server)))
	server.tell(player, '§7-------§r Server List §7-------§r')
	server.tell(player, message)


def on_user_info(server, info):
	if info.content == Prefix:
		on_player_joined(server, info.player, None)


def on_load(server, old):
	server.register_help_message(Prefix, '显示欢迎消息')
	if not os.path.isfile(ConfigFilePath):
		with open(ConfigFilePath, 'r') as f:
			json.dump({
				"serverName": "My Server",
				"mainServerName": "?",
				"serverList": []
			}, f, indent=4)
