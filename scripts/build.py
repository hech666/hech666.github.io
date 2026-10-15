#!/usr/bin/env python3
"""Build a flat APT repository. Requires Python 3 and dpkg-deb."""
import pathlib, subprocess, hashlib, gzip, bz2, shutil, datetime, html, json
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'public'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
(OUT / 'debs').mkdir()
entries, packages, arches = [], [], set()
for deb in sorted((ROOT / 'debs').glob('*.deb')):
    control = subprocess.check_output(['dpkg-deb', '-f', str(deb)], text=True).strip()
    fields = {}
    for line in control.splitlines():
        if line and not line[0].isspace() and ':' in line:
            k, v = line.split(':', 1)
            fields[k] = v.strip()
    for key in ('Package', 'Version', 'Architecture'):
        if not fields.get(key): raise SystemExit(f'{deb.name}: missing {key}')
    data = deb.read_bytes()
    # Publish under an ASCII content-addressed name; keep uploaded deb bytes intact.
    published_name = hashlib.sha256(data).hexdigest() + '.deb'
    # Strip generated index fields if present in a package control.
    lines, skip = [], False
    for line in control.splitlines():
        if line and not line[0].isspace():
            skip = line.split(':', 1)[0] in ('Filename', 'Size', 'MD5sum', 'SHA1', 'SHA256', 'SHA512')
        if not skip: lines.append(line)
    lines += [f'Filename: debs/{published_name}', f'Size: {len(data)}',
              f'MD5sum: {hashlib.md5(data).hexdigest()}', f'SHA1: {hashlib.sha1(data).hexdigest()}',
              f'SHA256: {hashlib.sha256(data).hexdigest()}']
    entries.append('\n'.join(lines) + '\n\n')
    arches.add(fields['Architecture'])
    shutil.copy2(deb, OUT / 'debs' / published_name)
    packages.append({'name': fields.get('Name', fields['Package']), 'version': fields['Version'], 'arch': fields['Architecture']})
index = ''.join(entries).encode()
(OUT / 'Packages').write_bytes(index)
(OUT / 'Packages.gz').write_bytes(gzip.compress(index, mtime=0))
(OUT / 'Packages.bz2').write_bytes(bz2.compress(index))
release = ['Origin: haoge', 'Label: haoge', 'Suite: stable', 'Codename: haoge',
           'Version: 1.0', 'Architectures: ' + ' '.join(sorted(arches | {'iphoneos-arm', 'iphoneos-arm64', 'iphoneos-arm64e'})),
           'Components: main', 'Description: haoge jailbreak repository',
           'Date: ' + datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')]
for label, algorithm in [('MD5Sum', 'md5'), ('SHA1', 'sha1'), ('SHA256', 'sha256')]:
    release.append(label + ':')
    for name in ('Packages', 'Packages.gz', 'Packages.bz2'):
        data = (OUT / name).read_bytes()
        release.append(f' {hashlib.new(algorithm, data).hexdigest()} {len(data)} {name}')
(OUT / 'Release').write_text('\n'.join(release) + '\n')
(OUT / '.nojekyll').touch()
source = (ROOT / 'site' / 'index.html').read_text()
rows = ''.join('<li>' + html.escape(f"{p['name']} · {p['version']} · {p['arch']}") + '</li>' for p in packages)
(OUT / 'index.html').write_text(source.replace('{{PACKAGES}}', rows or '<li>暂无软件包，稍后上传。</li>'))
print(f'Built {len(packages)} packages in {OUT}')
