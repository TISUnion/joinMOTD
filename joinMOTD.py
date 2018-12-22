from daycount import getday

msgstart = '=====Welcome back to TIS====='
servername = 'TIS'
msgend = ''

def onPlayerJoin(server, player):
  msg = ''
  msg += msgstart + '\n'
  msg += '今天是' + servername + '开服的第' + getday() + '天\n'
  msg += msgend
  for line in msg.splitlines():
    server.tell(player, line)