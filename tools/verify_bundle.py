#!/usr/bin/env python3
"""Compare every final web file with the bytes actually embedded in the APK."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    dist = ROOT / 'web/dist'
    apk = ROOT / 'artifacts/android/HOMELESS-Rendezvous-debug.apk'
    mismatches = []
    files = sorted(p for p in dist.rglob('*') if p.is_file())
    with zipfile.ZipFile(apk) as bundle:
        for path in files:
            name = str(path.relative_to(dist))
            try:
                actual = bundle.read('assets/public/' + name)
            except KeyError:
                mismatches.append({'path': name, 'reason': 'missing in APK'})
                continue
            if actual != path.read_bytes():
                mismatches.append({'path': name, 'reason': 'different bytes'})
        license_carried = bundle.read('assets/public/assets/runtime/ROCKETBOX-LICENSE.txt') == (ROOT / 'assets/runtime/ROCKETBOX-LICENSE.txt').read_bytes()
    result = {
        'status': 'pass' if files and not mismatches and license_carried else 'fail',
        'web_revision': json.loads((dist / 'build-manifest.json').read_text())['revision'],
        'apk_sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
        'files_compared': len(files),
        'mismatches': mismatches,
        'rocketbox_mit_notice_carried': license_carried,
        'scope': 'Embedded static client equality; does not execute Android WebView or certify device behavior.'
    }
    (ROOT / 'evidence/android_bundle_match.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
