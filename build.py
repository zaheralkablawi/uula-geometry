# UULA Geometry — build app.html from src/app.template.html (adds the UULA Sans font).
#   python3 build.py
import pathlib
R = pathlib.Path(__file__).parent
t = (R / 'src' / 'app.template.html').read_text(encoding='utf8')
t = t.replace('/*FONT*/', (R / 'src' / 'font.css').read_text(encoding='utf8'))
(R / 'app.html').write_text(t, encoding='utf8')
print('app.html', len(t))
