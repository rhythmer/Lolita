import os
import time
from slackclient import SlackClient
import requests
import json

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def mqkv_useage():
	return '''
	If you want to know some certain host's mqkv status,please input like this:
	'show mqkv IP status';
	If you want to change some certain host's mqkv status,please input like this:
	'do switch IP (kafkamaster,redisonly,backuping...)'
	'''
	

def get_mqkv_status(ip):
	url = 'http://' + ip + ':7788/api/v1/status'
	try:
		r = requests.get(url,timeout = 3)
	except requests.exceptions.Timeout:
		return "Timeout,so you'd best to check your IP"
	
	return str(r.json()["data"]["switch"])

def switch_mqkv_status(ip, status):
	url = "http://" + ip + ":7788/api/v1/change/status"
	switch_data = {"switch": status}
	try:
		r = requests.post(url, data=json.dumps(switch_data),timeout = 3)
	except requests.exceptions.Timeout:
		return "Timeout,so you'd best to check your IP"
	if r.status_code == 200:
		return "OK."
	else:
		return str(r.status_code) + " some thing is wrong."

def handle_command(command, channel):

	command_list = command.split()
	for i in command_list:
		i = str(i)

	if  command_list[0] == ":" and command_list[1] == "show" and command_list[2] == "mqkv" and len(command_list) == 5 and  command_list[4] == "status":
		ip = command.split()[3]
		ip_status = get_mqkv_status(ip)
		response = ip_status
	elif command_list[0] == ":" and command_list[1] == "do" and command_list[2] == "switch" and len(command_list) == 5:
		ip = command.split()[3]
		if command_list[4] == "kafkamaster":
			switch_result = switch_mqkv_status(ip, command_list[4])
			response = "Change to " + command_list[4] + " " + switch_result
		elif command_list[4] == "redisonly":
			switch_result = switch_mqkv_status(ip, command_list[4])
			response = "Change to " + command_list[4] + " " + switch_result
		elif command_list[4] == "backuping":
			switch_result = switch_mqkv_status(ip, command_list[4])
			response = "Change to " + command_list[4] + " " + switch_result
		else:
			response = mqkv_useage() 
			
			
	else:
		print command_list
		response = mqkv_useage()
		
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):

    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Lolita connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
