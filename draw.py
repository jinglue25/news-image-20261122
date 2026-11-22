"""Draw an original, typeset newspaper using only Pillow geometry and fonts."""
from pathlib import Path
import hashlib
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PAPER, INK, RED, TEAL = '#f8f4ec', '#191919', '#b3261e', '#2e6f6a'
im = Image.new('RGB', (1024, 1024), PAPER)
d = ImageDraw.Draw(im)
FONT = Path('/usr/share/fonts/truetype/noto')
blocks = []


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ('NotoSans-CondensedBold.ttf' if bold else 'NotoSans-Condensed.ttf')), size)


def wrap(text, f, width):
    lines = []
    for word in text.split():
        trial = (lines[-1] + ' ' + word) if lines else word
        if lines and d.textbbox((0, 0), trial, font=f)[2] > width:
            lines.append(word)
        elif lines:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


def textblock(name, text, box, size, bold=False, color=INK, leading=None, center=False):
    x, y, right, bottom = box
    f = font(size, bold)
    lines = wrap(text, f, right - x)
    step = leading or size + 4
    for i, line in enumerate(lines):
        bounds = d.textbbox((0, 0), line, font=f)
        xx = x + ((right - x - (bounds[2] - bounds[0])) / 2 if center else 0)
        # Position the visible glyph bounds, rather than the font ascender.
        pos = (xx - bounds[0], y + i * step - bounds[1])
        actual = d.textbbox(pos, line, font=f)
        assert actual[0] >= x and actual[1] >= y and actual[2] <= right and actual[3] <= bottom, (name, line, actual, box)
        d.text(pos, line, font=f, fill=color)
        blocks.append((name, actual, box))
    return y + (len(lines) - 1) * step + size


def spaced(text, box, size=17, tracking=3):
    f = font(size, True)
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (box[0] + box[2] - total) / 2
    for c, width in zip(text, widths):
        bounds = d.textbbox((x, box[1]), c, font=f)
        assert bounds[0] >= box[0] and bounds[2] <= box[2] and bounds[3] <= box[3]
        blocks.append(('subline', bounds, box))
        d.text((x, box[1]), c, font=f, fill=INK)
        x += width + tracking


def icon(kind, x, y, s):
    def pts(coords):
        return [(x + a * s, y + b * s) for a, b in coords]
    def line(coords, width=3, fill=TEAL):
        d.line(pts(coords), fill=fill, width=width, joint='curve')
    def ellipse(box, fill=None, width=3):
        a, b, c, e = box
        d.ellipse((x+a*s, y+b*s, x+c*s, y+e*s), outline=TEAL, fill=fill, width=width)
    if kind == 'globe':
        ellipse((.04,.08,.85,.89), width=4)
        ellipse((.25,.08,.64,.89))
        line([(.08,.36),(.81,.36)])
        line([(.08,.61),(.81,.61)])
        line([(.445,.09),(.445,.88)])
        # Original leaf, with a paper gap separating it from the globe.
        d.polygon(pts([(.49,.62),(.63,.30),(.96,.23),(.93,.56),(.73,.74)]), fill=PAPER)
        d.polygon(pts([(.57,.60),(.67,.36),(.94,.28),(.89,.54),(.73,.66)]), fill=TEAL)
        line([(.56,.77),(.78,.48)], width=4)
    elif kind == 'gavel':
        line([(.39,.39),(.79,.79)], width=7)
        d.polygon(pts([(.14,.39),(.44,.09),(.62,.27),(.32,.57)]), fill=TEAL)
        line([(.12,.86),(.86,.86)], width=6)
        line([(.24,.77),(.74,.77)], width=5)
    elif kind == 'bat':
        d.polygon(pts([(.12,.68),(.47,.22),(.65,.36),(.30,.83)]), fill=TEAL)
        line([(.54,.28),(.73,.04)], width=5)
        ellipse((.64,.62,.94,.92), fill=TEAL, width=1)
        line([(.70,.66),(.85,.85)], width=2, fill=PAPER)
    elif kind == 'stumps':
        for a in (.25,.5,.75):
            line([(a,.25),(a,.90)], width=5)
        line([(.18,.19),(.48,.19)], width=4)
        line([(.52,.19),(.82,.19)], width=4)
        line([(.13,.93),(.88,.93)], width=2)
    elif kind == 'bolt':
        d.polygon(pts([(.48,.04),(.15,.55),(.46,.55),(.34,.96),(.86,.37),(.55,.37),(.74,.04)]), fill=TEAL)


textblock('masthead', 'SUNDAY 22 NOVEMBER 2026', (30, 30, 994, 88), 64, True, center=True)
d.rectangle((32, 106, 992, 111), fill=RED)
spaced('FIVE STORIES FROM AROUND THE WORLD', (32, 122, 992, 150))

textblock('COP31 kicker', 'CLIMATE · ANTALYA, TURKEY', (36, 173, 790, 194), 16, True, RED)
end = textblock('COP31 headline', 'COP31 draft lands in the early hours — still no fossil-fuel exit', (36, 205, 810, 292), 36, True, leading=42)
textblock('COP31 body', 'A third draft deal was published in Antalya in the early hours of Sunday, and delegates meet on Sunday morning to approve it. The text still has no fossil-fuel phase-out and no $120bn adaptation finance goal.', (36, end + 14, 808, 388), 19, leading=26)
icon('globe', 839, 211, 143)
d.line((32, 405, 992, 405), fill=INK, width=2)

stories = [
    ('DIPLOMACY · JOHANNESBURG, SOUTH AFRICA', 'G20 closes with no American at the table', 'President Ramaphosa banged the gavel to close the summit on Sunday. With the US boycotting, no American official was there to take the presidency — the handover waits until Monday.', 'gavel'),
    ('CRICKET · WELLINGTON, NEW ZEALAND', "Pant's 128 puts India 261 ahead", "Rishabh Pant smashed 128 off 153 balls as India reached 629 for 6 at lunch on day four. It is India's highest Test total in New Zealand, and makes Pant the first Indian wicketkeeper with Test hundreds in all four SENA countries.", 'bat'),
    ('CRICKET · PERTH, AUSTRALIA', "Head's 69-ball hundred wins the Ashes opener in two days", 'Travis Head blasted 123 off 83 balls as Australia chased 205 to beat England by eight wickets. Mitchell Starc took ten wickets in the match; Australia lead the series 1–0.', 'stumps'),
    ('WAR · UKRAINE', 'Rolling blackouts return across Ukraine', 'Hourly power cuts of up to 2.5 queues are in force in several regions on Sunday after Russian strikes on the grid. Odesa and Rivne are the worst hit.', 'bolt'),
]
d.line((512, 424, 512, 965), fill='#c5bdb0', width=1)
d.line((32, 691, 992, 691), fill='#c5bdb0', width=1)
for i, (kicker, headline, body, pictogram) in enumerate(stories):
    x = 36 if i % 2 == 0 else 536
    y = 427 if i < 2 else 712
    textblock(pictogram+' kicker', kicker, (x, y, x+452, y+22), 14, True, RED)
    end = textblock(pictogram+' headline', headline, (x, y+33, x+373, y+127), 29, True, leading=34)
    icon(pictogram, x+387, y+33, 60)
    textblock(pictogram+' body', body, (x, end+13, x+452, y+250), 18, leading=24)

d.line((32, 982, 992, 982), fill=RED, width=2)
textblock('sources', 'Sources: Reuters · AP · The Hindu · ANI · UNN · Ukrenergo · Lvivoblenergo', (32, 995, 992, 1015), 14, center=True)


def validate_text():
    for name, actual, box in blocks:
        assert box[0] <= actual[0] <= actual[2] <= box[2] and box[1] <= actual[1] <= actual[3] <= box[3], name
    print(f'PASS: all {len(blocks)} measured text lines/glyphs fit their boxes')


if __name__ == '__main__':
    validate_text()
    target = ROOT / 'entry.png'
    im.save(target, format='PNG', optimize=True)
    raw = target.read_bytes()
    with Image.open(target) as check:
        assert check.size == (1024, 1024) and check.format == 'PNG'
    assert len(raw) < 1048576
    print(f'PNG: 1024x1024; {len(raw)} bytes; under 1048576: PASS')
    print('SHA256:', hashlib.sha256(raw).hexdigest())
