# -*- coding: utf-8 -*-
import copy
import sys


sys.path.append('plugins/')
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

def onPlayerJoin(server, player):
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


def onServerInfo(server, info):
  if info.content == Prefix and info.isPlayer:
    onPlayerJoin(server, info.player)


def on_info(server, info):
  info2 = copy.deepcopy(info)
  info2.isPlayer = info2.is_player
  onServerInfo(server, info2)


def on_player_joined(server, playername):
  onPlayerJoin(server, playername)


def on_load(server, old):
  server.add_help_message(Prefix, '显示欢迎消息')
