import random, os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def get_random_color(max):
    return (
        random.randint(0, max), random.randint(0, max), random.randint(0, max)
    )


def get_valid_code(request):
    img = Image.new('RGB', (270, 40), color=get_random_color(150))
    draw = ImageDraw.Draw(img)
    song = ImageFont.truetype('statics/fonts/STZHONGS.TTF', size=28)
    valid_code_str = ''
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low = chr(random.randint(97, 122))
        random_up = chr(random.randint(65, 90))
        random_char = random.choice([random_low, random_num, random_up])
        draw.text((i * 50 + 20, 5), random_char, get_random_color(255), font=song)
        valid_code_str += random_char
    request.session['valid_code'] = valid_code_str
    f = BytesIO()
    img.save(f, 'png')
    data = f.getvalue()
    return data



