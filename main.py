import mouse as GHUB
import win32api

GHUB.mouse_open() # initialize mouse
time.sleep(1)

def enabled():
  return win32api.GetKeyState(0x02) in (-127, -128) # 0x02 is right click. See https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

x, y = 1, 1 # sample coordinates to move the mouse to

# Example usage
while enabled():
  mouse.mouse_move(0, x, y, 0) # move mouse to specified coords above.
