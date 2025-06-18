import collections
import json
import os
import random
import threading
from datetime import datetime
from typing import List, Optional, Callable, Any, Union, Dict

from mcdreforged.api.all import *


class ServerInfo(Serializable):
	name: str
	display: Optional[str] = None
	description: Optional[str] = None
	category: str = ''

	@classmethod
	def from_object(cls, obj) -> 'ServerInfo':
		if isinstance(obj, cls):
			return obj
		return ServerInfo(name=str(obj))


class Config(Serializable):
	serverName: str = 'Survival Server'
	commonJsonDataPath: Optional[str] = None
	mainServerName: str = 'My Server'
	serverList: List[Union[str, ServerInfo]] = [
		'survival',
		'lobby',
		ServerInfo(name='creative1', description='CMP Server#1', category='CMP'),
		ServerInfo(name='creative2', description='CMP Server#2', category='CMP'),
	]
	start_day: Optional[str] = None
	daycount_plugin_ids: List[str] = [
		'mcd_daycount',
		'day_count_reforged',
		'daycount_nbt'
	]
	auto_reload_interval: Optional[float] = None


Prefix = '!!joinMOTD'
config: Config
ConfigFilePath = os.path.join('config', 'joinMOTD.json')
UnloadFlag = threading.Event()


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
	reply('§7=======§r Welcome back to §e{}§7 =======§r'.format(config.serverName))
	reply('今天是§e{}§r开服的第§e{}§r天'.format(config.mainServerName, get_day(server)))
	reply('§7-------§r Server List §7-------§r')

	server_dict: Dict[str, List[ServerInfo]] = collections.defaultdict(list)
	for entry in config.serverList:
		info = ServerInfo.from_object(entry)
		server_dict[info.category].append(info)
	for category, server_list in server_dict.items():
		header = RText('{}: '.format(category) if len(category) > 0 else '')
		messages = []
		for info in server_list:
			command = '/server {}'.format(info.name)
			hover_text = command
			if info.description is not None:
				hover_text = info.description + '\n' + hover_text
			display_text = info.display or info.name
			messages.append(RText('[{}]'.format(display_text)).h(hover_text).c(RAction.run_command, command))
		reply(header + RTextBase.join(' ', messages))


def on_player_joined(server: ServerInterface, player, info):
	display_motd(server, lambda msg: server.tell(player, msg))


def on_load(server: PluginServerInterface, old):
	load_config(server, echo_in_console=True)
	server.register_help_message(Prefix, '显示欢迎消息')
	server.register_command(Literal(Prefix).runs(lambda src: display_motd(src.get_server(), src.reply)))

	def is_auto_reload_enabled() -> bool:
		return config.auto_reload_interval is not None and config.auto_reload_interval

	def get_auto_reload_interval() -> float:
		return max(1.0, config.auto_reload_interval + random.random() * 0.2 - 0.1)  # +- 0.1s jitter

	if is_auto_reload_enabled():
		@new_thread('JoinMOTDAutoReload')
		def auto_reload():
			server.logger.debug('AutoReload thread start')
			while is_auto_reload_enabled() and UnloadFlag.wait(get_auto_reload_interval()) is False:
				server.logger.debug('Reloading config')
				load_config(server, echo_in_console=False)
			server.logger.debug('AutoReload thread end')

		auto_reload()


def on_unload(server: PluginServerInterface):
	UnloadFlag.set()


def load_config(server: PluginServerInterface, echo_in_console: bool):
	new_config = server.load_config_simple(file_name=ConfigFilePath, in_data_folder=False, target_class=Config, echo_in_console=echo_in_console)
	common_json_path = new_config.commonJsonDataPath
	if common_json_path is not None:
		server.logger.debug('Loading common config from {!r}'.format(common_json_path))
		try:
			with open(common_json_path, 'r', encoding='utf8') as f:
				common_config_json = json.load(f)

			new_config_json = new_config.serialize()
			new_config_json.update(common_config_json)
			new_config = Config.deserialize(new_config_json)
		except Exception as e:
			server.logger.error('Load common config json from {!r} failed: {}'.format(common_json_path, e))

	global config
	config = new_config
