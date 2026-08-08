import time
# ==========================================
"""
i2c_lcd.py

I2C 16x2 LCD Driver for PCF8574 Backpack
"""

class LcdApi:
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_DDRAM = 0x80
    LCD_FUNCTION = 0x20
    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x, self.cursor_y = 0, 0
        self.backlight = True
        self.hal_write_command(self.LCD_ON_CTRL)
        self.hal_backlight_on()
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        self.hal_write_command(self.LCD_HOME)
        self.cursor_x, self.cursor_y = 0, 0

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x, self.cursor_y = cursor_x, cursor_y
        addr = cursor_x & 0x3f
        if cursor_y & 1: addr += 0x40
        if cursor_y & 2: addr += self.num_columns
        self.hal_write_command(self.LCD_DDRAM | addr)

    def putchar(self, char):
        if char == '\n':
            self.cursor_y = (self.cursor_y + 1) if self.cursor_y < self.num_lines - 1 else 0
            self.cursor_x = 0
            self.move_to(self.cursor_x, self.cursor_y)
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
            if self.cursor_x >= self.num_columns:
                self.cursor_x = 0
                self.cursor_y = (self.cursor_y + 1) if self.cursor_y < self.num_lines - 1 else 0
                self.move_to(self.cursor_x, self.cursor_y)

    def putstr(self, string):
        for char in string: self.putchar(char)
        
    def hal_backlight_on(self): pass
    def hal_write_command(self, cmd): pass
    def hal_write_data(self, data): pass

class I2cLcd(LcdApi):
    MASK_RS = 0x01
    MASK_E = 0x04
    SHIFT_BACKLIGHT = 3
    SHIFT_DATA = 4

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = True
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        time.sleep_ms(20)
        for cmd in [0x30, 0x30, 0x30, 0x20]:
            self.hal_write_init_nibble(cmd)
            time.sleep_ms(5)
        self.hal_write_command(self.LCD_FUNCTION | self.LCD_FUNCTION_2LINES)
        time.sleep_ms(1)
        super().__init__(num_lines, num_columns)

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0f) << self.SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytearray([byte | self.MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte]))

    def hal_backlight_on(self):
        self.i2c.writeto(self.i2c_addr, bytearray([1 << self.SHIFT_BACKLIGHT]))

    def hal_write_command(self, cmd):
        for val in [(cmd >> 4) & 0x0f, cmd & 0x0f]:
            byte = (self.backlight << self.SHIFT_BACKLIGHT) | (val << self.SHIFT_DATA)
            self.i2c.writeto(self.i2c_addr, bytearray([byte | self.MASK_E]))
            self.i2c.writeto(self.i2c_addr, bytearray([byte]))
        if cmd <= 3: time.sleep_ms(5)

    def hal_write_data(self, data):
        for val in [(data >> 4) & 0x0f, data & 0x0f]:
            byte = self.MASK_RS | (self.backlight << self.SHIFT_BACKLIGHT) | (val << self.SHIFT_DATA)
            self.i2c.writeto(self.i2c_addr, bytearray([byte | self.MASK_E]))
            self.i2c.writeto(self.i2c_addr, bytearray([byte]))

# ====
