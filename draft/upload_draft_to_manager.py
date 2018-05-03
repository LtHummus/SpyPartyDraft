import json
import requests


class Uploader:
    def __init__(self):
        with open("config/uploader.json") as f:
            data = json.load(f)
            self.psk = data['psk']
            self.url = data['url']

    # case class DraftInput(roomCode: String, player1: String, player2: String, payload: DraftPayload)

    def upload_room(self, room):
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
            file = open("log/payload.log", "a")
            file.write(json.dumps(payload))
            print 'Upload Failed. Appending payload to log file.'

        







