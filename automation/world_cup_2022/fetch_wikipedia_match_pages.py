from pathlib import Path
from urllib.request import Request, urlopen

pages = {
    'tournament': 'https://en.wikipedia.org/wiki/2022_FIFA_World_Cup',
    'officials': 'https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_officials',
}
for letter in 'ABCDEFGH':
    pages[f'group_{letter.lower()}'] = f'https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_Group_{letter}'

out = Path('/tmp/wiki_pages')
out.mkdir(parents=True, exist_ok=True)
for name, url in pages.items():
    request = Request(url, headers={'User-Agent': 'Data-Driven-em-Campo-2022/1.0'})
    with urlopen(request, timeout=120) as response:
        data = response.read()
    (out / f'{name}.html').write_bytes(data)
    print(name, len(data), url)
