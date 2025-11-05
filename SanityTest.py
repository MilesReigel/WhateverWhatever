import asyncio
from bleak import BleakClient, BleakScanner
import tkinter as tk
import random as r

# Config
ESP32_NAME = "TorlaserESP32-test"  # BLE device name
SERVICE_UUID = "4bcbf75c-adec-4630-9086-490f413ff514"
UART_RX_CHAR_UUID = "4bcbf75d-adec-4630-9086-490f413ff514"
mouse_x, mouse_y = 0, 0
programOn = True
client = None
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
SEND_INTERVAL_MS = 50

async def tkinterUI(loop, send_queue):
    global programOn

    #Notification Function for auto mode
    def AutoRunOnOff():
        if AutoRunTF.get():
            print("Auto Mode Enabled")
        else: 
            print("Auto Mode Disabled")

    #Exit Function
    def annihilation():
        global programOn
        programOn = False
        print("Terminating Program")
        root.destroy()
    
    # Event Handlers/ UI
    def on_mouse_move(event):
        global mouse_x, mouse_y
        mouse_x = max(0, min(event.x, WINDOW_WIDTH))
        mouse_y = max(0, min(event.y, WINDOW_HEIGHT))
    
    #Tkinter GUI
    root = tk.Tk()
    root.title("ESP32 Mouse Controller")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="lightgray")
    canvas.pack()
    AutoRunTF = tk.BooleanVar()
    tk.Checkbutton(canvas, font = ("Times New Roman", 10), text = "Auto Mode", bd = 3, variable = AutoRunTF, command = AutoRunOnOff).place(relx = .5, rely = .5, anchor = 'center')
    tk.Button(canvas, font = ("Times New Roman", 10), text = "Exit", command = annihilation, fg = "red").place(relx = .5, anchor = 'n')
    positionLabel = tk.Label(canvas, font = ("Times New Roman", 7), text = f"X:{mouse_x}, Y:{mouse_y}", bg = "lightgray", fg = "red")
    positionLabel.place(anchor = 'nw')
    canvas.create_line(0, WINDOW_HEIGHT/2, WINDOW_WIDTH, WINDOW_HEIGHT/2, activewidth = 3)
    canvas.create_line(WINDOW_WIDTH/2, 0, WINDOW_WIDTH/2, WINDOW_HEIGHT, activewidth = 3)
    canvas.bind("<Motion>", on_mouse_move)
    root.protocol("WM_DELETE_WINDOW", annihilation)

    #Update GUI loop
    async def tk_loop():
        global programOn, mouse_x, mouse_y
        while programOn:
            try:
                root.update()
                positionLabel['text'] = f"X:{mouse_x}, Y:{WINDOW_HEIGHT - mouse_y}"
                if not AutoRunTF.get():
                    await send_queue.put((mouse_x, mouse_y))
                await asyncio.sleep(0.01)
            except tk.TclError:
                break
    
    #Auto Run Function
    async def autoRunFunction():
        global mouse_x, mouse_y
        while programOn:
            if AutoRunTF.get():
                mouse_x = r.randint(0, WINDOW_WIDTH)
                mouse_y = r.randint(0, WINDOW_WIDTH)
                await send_queue.put((mouse_x, mouse_y))
            await asyncio.sleep(2.5)
    
    return root, [tk_loop(), autoRunFunction()]

#Connection to ESP32
async def BTConnection_ESP32():
    print("Scanning for ESP32...")
    devices = await BleakScanner.discover()
    target = next((d for d in devices if ESP32_NAME in (d.name or "")), None)
    if not target:
        raise Exception(f"ESP32 named '{ESP32_NAME}' not found")
    client = BleakClient(target.address)
    await client.connect()
    print("Connected to ESP32")
    return client

#Tx function
async def send_mouse_data(client, send_queue):
    while programOn and client.is_connected:
        try:
            x, y = await send_queue.get()
            msg = f"{x},{y}".encode("utf-8")
            print(f"Sending {x},{y}")
            await client.write_gatt_char(UART_RX_CHAR_UUID, msg)
        except Exception as e:
            print("BLE write error: ", e)
        await asyncio.sleep(SEND_INTERVAL_MS / 1000)

#Main Loop
async def main():
    global client
    send_queue = asyncio.Queue()
    try:
        client = await BTConnection_ESP32()
    except Exception as e:
        print("Connection error: ", e)
        return
    
    root, tasks = await tkinterUI(asyncio.get_event_loop(), send_queue)
    #Sends Queue Data to Tx function
    await asyncio.gather(*tasks, send_mouse_data(client, send_queue))

    if client and client.is_connected:
        await client.disconnect()
        print("Disconnected")

#Calls Main Loop to run
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Program Exited")