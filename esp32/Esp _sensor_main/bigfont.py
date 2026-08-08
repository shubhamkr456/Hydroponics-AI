DIGITS = {
    '0': [1,1,1, 1,0,1, 1,0,1, 1,0,1, 1,1,1],
    '1': [0,1,0, 1,1,0, 0,1,0, 0,1,0, 1,1,1],
    '2': [1,1,1, 0,0,1, 1,1,1, 1,0,0, 1,1,1],
    '3': [1,1,1, 0,0,1, 1,1,1, 0,0,1, 1,1,1],
    '4': [1,0,1, 1,0,1, 1,1,1, 0,0,1, 0,0,1],
    '5': [1,1,1, 1,0,0, 1,1,1, 0,0,1, 1,1,1],
    '6': [1,1,1, 1,0,0, 1,1,1, 1,0,1, 1,1,1],
    '7': [1,1,1, 0,0,1, 0,1,0, 0,1,0, 0,1,0],
    '8': [1,1,1, 1,0,1, 1,1,1, 1,0,1, 1,1,1],
    '9': [1,1,1, 1,0,1, 1,1,1, 0,0,1, 1,1,1],
    ' ': [0,0,0, 0,0,0, 0,0,0, 0,0,0, 0,0,0]
}


def draw_big_char(oled, char, x, y, scale):
    if char == '.': 
        oled.fill_rect(x, y + 4*scale, scale, scale, 1)
        return scale + 2 
    if char not in DIGITS: return 0
    grid = DIGITS[char]
    for row in range(5):
        for col in range(3):
            if grid[row * 3 + col]:
                oled.fill_rect(x + col * scale, y + row * scale, scale, scale, 1)
    return (3 * scale) + 2

def draw_big_text_right(oled, text, y, scale, right_edge=128):
    total_w = 0
    for c in text:
        total_w += (scale + 2) if c == '.' else ((3 * scale) + 2)
    curr_x = right_edge - total_w 
    for c in text:
        curr_x += draw_big_char(oled, c, curr_x, y, scale)

def draw_label(oled, text, x, y):
    width = (len(text) * 8) + 4
    oled.fill_rect(x, y-2, width, 12, 1) 
    oled.text(text, x+2, y, 0)           
