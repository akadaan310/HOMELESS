"""Numerical and provenance checks for the observed HYG sky."""
import json
import math
import numpy as np
import pytest
from worldloom import sky


def test_spherical_geometry_wrap_poles_and_rotations():
    a = sky.unit_vector(359.0, 0.0)
    b = sky.unit_vector(1.0, 0.0)
    assert math.degrees(sky.angular_separation(a, b)) == pytest.approx(2.0, abs=1e-10)
    assert sky.angular_separation(sky.unit_vector(0, 90), sky.unit_vector(170, 90)) < 1e-14
    q, _ = np.linalg.qr(np.random.default_rng(7).normal(size=(3, 3)))
    assert sky.angular_separation(a @ q, b @ q) == pytest.approx(sky.angular_separation(a, b), abs=1e-14)


def test_proper_motion_spherical_transport_reverses_without_pole_division():
    initial = sky.unit_vector(12, 89.9999)
    moved, velocity = sky.propagate(initial, np.array([0.01, -0.02, 0.0]), 50)
    restored, _ = sky.propagate(moved, velocity, -50)
    assert sky.angular_separation(initial, restored) < 1e-13
    assert np.linalg.norm(moved) == pytest.approx(1)
    with pytest.raises(ValueError, match='epoch'):
        sky.observer(epoch=2500)


def test_horizontal_known_zenith_and_horizon():
    at = '2000-01-01T12:00:00Z'
    lst = sky.gmst_deg(at)
    alt, az = sky.horizontal(lst, 25, 25, 0, at)
    assert alt == pytest.approx(90, abs=1e-6)
    alt, _ = sky.horizontal(lst+90, 0, 0, 0, at)
    assert alt == pytest.approx(0, abs=1e-10)


def test_catalog_is_pinned_actual_input_and_cone_query_handles_ra_wrap():
    meta = sky.overview()
    assert meta['source_catalog'] == 'HYG'
    assert meta['source_count'] > 119000
    assert len(meta['source_sha256']) == 64
    catalog = sky.catalog()
    found = catalog.query_cone(0, 0, 10)
    brute = np.flatnonzero(catalog.vectors @ sky.unit_vector(0, 0) >= math.cos(math.radians(10)))
    assert set(found) == set(brute)
    polar = catalog.query_cone(359, 89, 5)
    expected = np.flatnonzero(catalog.vectors @ sky.unit_vector(359, 89) >= math.cos(math.radians(5)))
    assert set(polar) == set(expected)


def test_observer_reports_source_positions_visibility_and_approximation():
    result = sky.observer(lat=27.95, lon=-82.5, at='2026-10-20T02:00:00Z', max_mag=6, limit=40)
    assert result['status'] == 'ok'
    assert result['visible_count'] > 100
    assert len(result['stars']) == 40
    assert all(s['altitude_deg'] > 0 for s in result['stars'])
    assert all(s['source_id'].startswith('hyg:') for s in result['stars'])
    assert result['quality_mask']['astrometry'] == 'approximate_inference'
    assert result['quality_mask']['weather'] == 'incomplete'
    json.dumps(result, allow_nan=False)


def test_discovery_extracts_before_template_labels_and_calibrates_selection():
    result = sky.discover(seed=42, null_trials=19)
    repeated = sky.discover(seed=42, null_trials=19)
    assert result['content_hash'] == repeated['content_hash']
    assert result['star_ids'] == repeated['star_ids']
    assert 3 <= len(result['star_ids']) <= 12
    assert result['known_template_compared_after_discovery'] is True
    assert result['calibration']['selection_adjusted'] is True
    assert result['calibration']['heldout_seed'] != result['calibration']['training_seed']
    assert 0 < result['p_value'] <= 1
    assert len(result['angular_edges']) >= 3
    assert result['source_catalog'] == 'HYG'
    json.dumps(result, allow_nan=False)


def test_known_line_art_is_only_a_post_discovery_benchmark():
    result = sky.discover(seed=42, null_trials=19)
    benchmark = result['benchmark']
    assert benchmark['template_source'] == 'Stellarium modern skyculture'
    assert len(benchmark['template_source_sha256']) == 64
    assert benchmark['template_lookup_after_freeze_hash'] == result['discovery_freeze_hash']
    assert 0 <= benchmark['star_precision'] <= 1
    assert 0 <= benchmark['star_recall'] <= 1
    assert benchmark['traditional_shape_match'] in {'partial_vertex_agreement','exact_vertex_agreement','no_match'}


def test_horizons_pinned_reference_is_replayed_with_sparse_coverage_mask():
    body = sky.body_reference('Sun', '2026-10-20T02:00:00Z')
    assert body['status'] == 'ok'
    assert body['ra_deg'] == pytest.approx(204.420889579, abs=1e-9)
    assert body['dec_deg'] == pytest.approx(-10.160207096, abs=1e-9)
    assert body['source_model'] == 'JPL Horizons DE441'
    assert len(body['source_sha256']) == 64
    missing = sky.body_reference('Sun', '2030-01-01T00:00:00Z')
    assert missing['status'] == 'unsupported'
    assert missing['quality_mask'] == 'incomplete'


def test_mined_winner_is_rechecked_at_guarded_epoch_endpoints():
    result = sky.discover(seed=42, null_trials=19)
    assert {r['epoch'] for r in result['epoch_stability']} == {1900,2000,2100}
    assert all(r['winner_identity_stable'] for r in result['epoch_stability'])
    assert all(r['selected_winner_star_ids'] == result['star_ids'] for r in result['epoch_stability'])
