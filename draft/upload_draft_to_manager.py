import json
import requests
import datetime


class Uploader:
    def __init__(self):
        with open("config/uploader.json") as f:
            data = json.load(f)
            self.psk = data['psk']
            self.url = data['url']
            self.enabled = data['enabled']

    # case class DraftInput(roomCode: String, player1: String, player2: String, payload: DraftPayload)

    def upload_room(self, room):
        if not self.enabled:
            print "Uploading disabled, but would upload here"
            return

        payload = {
            'room_code': room.id,
            'player_1': room.player_list[0].lower(),
            'player_2': room.player_list[1].lower(),
            'payload': room.serialize()
        }

        try:
            request = requests.post(self.url, json=payload, headers={"Authentication": self.psk})
            print request.status_code
            # if(request.status_code != OK) then handle it or log it ?
        except: 
            logFile = open("log/payload.log", "a")
            logFile.write(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y\n"))
            logFile.write(json.dumps(payload))
            logFile.write('\n***********************\n')
            print "Upload Failed. Appending payload to log."







