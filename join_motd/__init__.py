import os
from datetime import datetime
from typing import List, Optional, Callable, Any, Union

from mcdreforged.api.all import *


class Config(Serializable):
	serverName: str = 'Survival Server'
	mainServerName: str = 'My Server'
	serverList: List[str] = [
		"survival",
		"lobby"
	]
	start_day: Optional[str] = None
	daycount_plugin_ids: List[str] = [
		'mcd_daycount',
		'day_count_reforged',
		'daycount_nbt'
	]


Prefix = '!!joinMOTD'
config: Config
ConfigFilePath = os.path.join('config', 'joinMOTD.json')


def get_day(server: ServerInterface) -> str:
	try:
		startday = datetime.strptime(config.start_day, '%Y-%m-%d')
		now = datetime.now()
		output = now - startday
		return str(output.days)
	except:
		pass
	for pid in config.daycount_plugin_ids:
		api = server.get_plugin_instance(pid)
		if hasattr(api, 'getday') and callable(api.getday):
			return api.getday()
	try:
		import daycount
		return daycount.getday()
	except:
		return '?'


def display_motd(server: ServerInterface, reply: Callable[[Union[str, RTextBase]], Any]):
	messages = []
	for subServerName in config.serverList:
		command = '/server {}'.format(subServerName)
		messages.append(RText('[{}]'.format(subServerName)).h(command).c(RAction.run_command, command))

	reply('§7=======§r Welcome back to §e{}§7 =======§r'.format(config.serverName))
	reply('今天是§e{}§r开服的第§e{}§r天'.format(config.mainServerName, get_day(server)))
	reply('§7-------§r Server List §7-------§r')
	reply(RTextBase.join(' ', messages))


def on_player_joined(server: ServerInterface, player, info):
	display_motd(server, lambda msg: server.tell(player, msg))


def on_load(server: PluginServerInterface, old):
	global config
	config = server.load_config_simple(file_name=ConfigFilePath, in_data_folder=False, target_class=Config)
	server.register_help_message(Prefix, '显示欢迎消息')
	server.register_command(Literal(Prefix).runs(lambda src: display_motd(src.get_server(), src.reply)))
