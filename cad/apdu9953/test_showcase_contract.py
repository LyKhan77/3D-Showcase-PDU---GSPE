from pathlib import Path
import json
import struct


ROOT = Path(__file__).resolve().parents[2]
SHOWCASE = ROOT / 'showcase'


def test_landing_has_seven_stages_and_components():
    html = (SHOWCASE / 'index.html').read_text()
    js = (SHOWCASE / 'assets' / 'showcase.js').read_text()
    assert 'GSPE APDU9953' in html
    assert html.count('data-stage=') == 7
    assert "const LAYERS" in js
    assert js.count("{ id: ") == 7
    for key in ('housing', 'mounting', 'power', 'breakers', 'outlet_banks', 'nmc3', 'internal'):
        assert key in js


def test_component_directory_covers_all_modules():
    expected = {
        'housing.html', 'mounting.html', 'power.html', 'breakers.html',
        'outlet-banks.html', 'nmc3.html', 'internal-busbars-pcb.html',
    }
    actual = {path.name for path in (SHOWCASE / 'components').glob('*.html')}
    assert expected <= actual
    for filename in expected:
        html = (SHOWCASE / 'components' / filename).read_text()
        assert 'GSPE' in html
        assert 'model-viewer' in html
        assert 'data-component-spec' in html


def test_showcase_material_visibility_contract():
    js = (SHOWCASE / 'assets' / 'showcase.js').read_text()
    css = (SHOWCASE / 'assets' / 'showcase.css').read_text()
    assert 'setBaseColorFactor' in js
    assert 'setAlphaMode' in js
    assert 'hotspot-card' in css
    assert 'timeline' in css


def test_generated_asset_contract():
    expected = {'housing', 'mounting', 'power', 'breakers', 'outlet_banks', 'nmc3', 'internal'}
    for mode in ('assembled', 'exploded'):
        manifest = ROOT / 'temp' / 'blender_staging_apdu9953' / mode / 'manifest.json'
        data = json.loads(manifest.read_text())
        assert set(data['layers']) == expected
        glb = SHOWCASE / ('gspe_pdu_apdu9953_exploded.glb' if mode == 'exploded' else 'gspe_pdu_apdu9953.glb')
        raw = glb.read_bytes()
        offset = 12
        document = None
        while offset < len(raw):
            length, chunk_type = struct.unpack_from('<II', raw, offset)
            if chunk_type == 0x4E4F534A:
                document = json.loads(raw[offset + 8:offset + 8 + length].rstrip(b' \0'))
                break
            offset += 8 + length
        assert document and document['asset']['version'] == '2.0'
        names = ' '.join(node.get('name', '') for node in document.get('nodes', []))
        assert all(f'LAYER_{layer}' in names for layer in expected)


if __name__ == "__main__":
    # pytest is not installed here, so run the test_* functions directly; any failure raises and exits non-zero.
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_") and callable(f)]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"{len(tests)}/{len(tests)} passed")
