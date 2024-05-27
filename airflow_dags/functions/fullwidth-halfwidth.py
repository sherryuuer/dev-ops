import re

def fullwidth_to_halfwidth(text):
    def convert_char(match):
        char = match.group(0)
        code_point = ord(char)
        if 0xFF01 <= code_point <= 0xFF5E:
            # Convert full-width character to half-width character
            return chr(code_point - 0xFEE0)
        elif code_point == 0x3000:
            # Convert full-width space to half-width space
            return chr(0x0020)
        return char
    
    # Regular expression to match full-width characters
    fullwidth_re = re.compile(r'[\uFF01-\uFF5E\u3000]')
    
    # Use sub method with convert_char function to replace full-width characters
    halfwidth_text = fullwidth_re.sub(convert_char, text)
    return halfwidth_text

# Example usage
fullwidth_text = "Ｈｅｌｌｏ，　Ｗｏｒｌｄ！"
halfwidth_text = fullwidth_to_halfwidth(fullwidth_text)
print(halfwidth_text)
