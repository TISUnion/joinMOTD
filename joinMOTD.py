# -*- coding: utf-8 -*-
import os

PLUGIN_METADATA = {
	'id': 'join_motd',
	'version': '1.0.0',
	'name': 'Join MOTD Display',
	'author': 'Fallen_Breath',
	'link': 'https://github.com/TISUnion/joinMOTD'
}

from daycount import getday
import json

PluginName = 'joinMOTD'
Prefix = '!!joinMOTD'
ConfigFileFolder = 'config/'
ConfigFilePath = ConfigFileFolder + PluginName + '.json'


def tellMessage(server, player, msg):
	for line in msg.splitlines():
		server.tell(player, line)


def getJumpCommand(subserverName):
	return '{"text":"[' + subserverName + ']",\
"clickEvent":{"action":"run_command",\
"value":"/server ' + subserverName + '"}}'


def on_player_joined(server, player, info):
	cmd = 'tellraw ' + player + ' {"text":"","extra":['
	with open(ConfigFilePath, 'r') as f:
		js = json.load(f)
		serverName = str(js["serverName"])
		mainServerName = str(js["mainServerName"])
		lines = js["serverList"]

		for i in range(len(lines)):
			name = lines[i].replace('\n', '').replace('\r', '')
			cmd = cmd + getJumpCommand(name)
			if i != len(lines) - 1:
				cmd = cmd + ',{"text":" "},'
	cmd = cmd + ']}'

	# print all stuffs
	msg = '''
§7=======§r Welcome back to §e{}§7 =======§r
今天是§e{}§r开服的第§e{}§r天
§7-------§r Server List §7-------§r
'''.strip().format(serverName, mainServerName, getday())
	tellMessage(server, player, msg)
	server.execute(cmd)


def on_user_info(server, info):
	if info.content == Prefix:
		on_player_joined(server, info.player, info)


def on_load(server, old):
	server.register_help_message(Prefix, '显示欢迎消息')
	if not os.path.isfile(ConfigFilePath):
		with open(ConfigFilePath, 'r') as f:
			json.dump({
				"serverName": "My Server",
				"mainServerName": "?",
				"serverList": []
			}, f, indent=4)

