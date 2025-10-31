import asyncio
from bleak import BleakClient, BleakScanner
import tkinter as tk

# === CONFIGURATION ===
ESP32_NAME = "TorlaserESP32"  # BLE device name
UART_RX_CHAR_UUID = "4bcbf75e-adec-4630-9086-490f413ff514"

mouse_x, mouse_y = 0, 0
client = None
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
SEND_INTERVAL_MS = 50  # ms


def on_mouse_move(event):
    global mouse_x, mouse_y
    mouse_x = max(0, min(event.x, WINDOW_WIDTH))
    mouse_y = max(0, min(event.y, WINDOW_HEIGHT))


async def find_esp32():
    print("Scanning for ESP32...")
    devices = await BleakScanner.discover(timeout=5)
    for d in devices:
        print(f" - {d.name} [{d.address}]")
        if d.name and ESP32_NAME in d.name:
            print(f"Found ESP32: {d.name} ({d.address})")
            return d
    return None


async def send_mouse_data():
    global client
    while True:
        if client and client.is_connected:
            msg = f"{mouse_x},{mouse_y}".encode("utf-8")
            try:
                await client.write_gatt_char(UART_RX_CHAR_UUID, msg)
            except Exception as e:
                print("BLE write error:", e)
        await asyncio.sleep(SEND_INTERVAL_MS / 1000)


async def main():
    global client
    device = await find_esp32()
    if not device:
        print("ESP32 not found. Make sure it's advertising.")
        return

    client = BleakClient(device)
    try:
        await client.connect()
        if client.is_connected:
            print("Connected to ESP32!")
        else:
            print("Failed to connect.")
            return
    except Exception as e:
        print("Connection error:", e)
        return

    # Start Tkinter GUI
    root = tk.Tk()
    root.title("ESP32 Mouse Controller")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="lightgray")
    tk.Label(canvas, width = 2, height = WINDOW_HEIGHT, bg = "black", anchor = 'center')
    canvas.pack()
    canvas.bind("<Motion>", on_mouse_move)

    # Start sending mouse data
    asyncio.create_task(send_mouse_data())

    while True:
        root.update()
        await asyncio.sleep(0.01)


if __name__ == "__main__":
    asyncio.run(main())
