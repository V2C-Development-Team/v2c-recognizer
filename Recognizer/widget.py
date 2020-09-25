import tkinter as tk
import asyncio
import websockets
import json

# Sends string to websocket
async def send(command):
    uri = "ws://127.0.0.1:2585/v1/messages"
    async with websockets.connect(uri) as websocket:
        await websocket.send(command)

# Initializing program
# Registering recognizer with dispatcher
register = {
    "action": "REGISTER_LISTENER",
    "app": "widget",
    "eavesdrop": False,
}

deregister = {
    "action": "DEREGISTER_LISTENER",
    "app": "widget"
}

asyncio.get_event_loop().run_until_complete(send(json.dumps(register)))

# Widget
widget = tk.Tk()
widget.geometry("400x240")
widget.lift()
widget.call('wm', 'attributes', '.', '-topmost', True)

def sendCommand():
    result = txtCommand.get("1.0", "end")
    payload = {
        "action": "DISPATCH_COMMAND",
        "command": result.strip(),
        "recipient": "desktop"
    }
    asyncio.get_event_loop().run_until_complete(send(json.dumps(payload)))

txtCommand=tk.Text(widget, height=1)
txtCommand.pack()
btnSend=tk.Button(widget, height=1, width=10, text="Send", command=sendCommand)
btnSend.pack()
widget.mainloop()

asyncio.get_event_loop().run_until_complete(send(json.dumps(deregister)))