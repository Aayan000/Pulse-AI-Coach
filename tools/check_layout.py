import urllib.request

url = 'http://127.0.0.1:8000/static/index.html'
try:
    resp = urllib.request.urlopen(url, timeout=2)
    html = resp.read().decode('utf-8')
    markers = ['class="app-container"', 'class="left-panel"', 'class="right-panel"']
    present = {m: (m in html) for m in markers}
    print('STATUS: UP')
    print('MARKERS:')
    for m, ok in present.items():
        print(f'  {m}: {ok}')
except Exception as e:
    print('STATUS: DOWN', e)
