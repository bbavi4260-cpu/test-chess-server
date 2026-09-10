import json

from server import app, GAMES, ROOMS


def test_custom_room_flow():
    GAMES.clear()
    ROOMS.clear()
    client = app.test_client()

    response = client.post("/v1/custom-room", json={"timeControl": "10+0", "rated": False})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    assert payload["success"] is True
    room_code = payload["roomCode"]
    game_id = payload["gameId"]
    assert room_code in ROOMS
    assert game_id in GAMES

    for path in (f"/v1/rooms/{room_code}", f"/v1/room/{room_code}",
                 f"/v1/custom-room/{room_code}",
                 f"/v1/games/rooms/{room_code}"):
        joined = client.post(path, json={"username": "second-player"})
        assert joined.status_code == 200, (path, joined.get_data(as_text=True))
        assert joined.get_json()["game_id"] == game_id

    status = client.get(f"/v1/game/{game_id}")
    assert status.status_code == 200
    assert status.get_json()["status"] == "active"

    missing = client.get("/v1/custom-room/DOESNOTEXIST")
    assert missing.status_code == 404
    assert missing.get_json()["code"] == 404


def test_query_code_alias():
    client = app.test_client()
    created = client.post("/v1/rooms", json={}).get_json()
    response = client.get(f"/v1/rooms?roomCode={created['roomCode']}")
    assert response.status_code == 200
    assert response.get_json()["roomCode"] == created["roomCode"]


if __name__ == "__main__":
    test_custom_room_flow()
    test_query_code_alias()
    print(json.dumps({"custom_room_tests": "passed"}))
