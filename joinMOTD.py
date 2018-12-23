from daycount import getday

msgstart = '=====Welcome back to TIS====='
servername = 'TIS'
msgend = ''

def onPlayerJoin(server, player):
  msg = ''
  msg += msgstart + '\n'
  msg += '今天是' + servername + '开服的第' + getday() + '天\n'
  for line in msg.splitlines():
    server.tell(player, line)
  server.execute('tellraw ' + player + '{"text":"点击此处进入创造服","clickEvent":{"action":"run_command","vlaue"："/server creative"}}')
  server.execute('tellraw ' + player + '{"text":"点击此处列出任务列表","clickEvent":{"action":"run_command","vlaue"："!!task list"}}')
