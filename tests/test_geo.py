"""Geographic contracts: actual source topology, conservative permissions, finite budgets."""
import hashlib
import json
import math
import unittest
from pathlib import Path
from worldloom import geo


class EarthGeometryTests(unittest.TestCase):
    def test_wgs84_roundtrip_including_poles_and_negative_height(self):
        for coord in [(0, 0, 0), (90, 70, 30), (-90, -160, -15), (27.959, -82.505, 13), (0, 180, -430), (-33.9,151.2,9000)]:
            xyz=geo.geodetic_to_ecef(*coord)
            result=geo.ecef_to_geodetic(*xyz)
            self.assertAlmostEqual(result[0], coord[0], places=7)
            if abs(coord[0]) < 90:
                self.assertAlmostEqual(geo.normalize_lon(result[1]-coord[1]),0,places=7)
            self.assertAlmostEqual(result[2],coord[2],places=4)

    def test_local_enu_origin_and_roundtrip(self):
        origin=(27.95946425,-82.5055696,0)
        self.assertLess(math.dist(geo.geodetic_to_enu(*origin,origin=origin),(0,0,0)),1e-8)
        local=geo.geodetic_to_enu(27.96,-82.506,15,origin=origin)
        point=geo.enu_to_geodetic(*local,origin=origin)
        self.assertAlmostEqual(point[0],27.96,places=8)
        self.assertAlmostEqual(point[1],-82.506,places=8)
        self.assertAlmostEqual(point[2],15,places=5)

    def test_antimeridian_distance_is_short(self):
        distance=geo.geodesic_distance(0,179.999,0,-179.999)
        self.assertAlmostEqual(distance,222.63898,places=2)
        self.assertLess(geo.geodesic_distance(90,0,90,180),1e-6)

    def test_lazy_tile_cache_bound_and_longitude_equivalence(self):
        store=geo.TileStore(max_tiles=3)
        self.assertEqual(store.info()['loaded_tiles'],0)
        self.assertEqual(store.resolve(0,180)['cell_id'],store.resolve(0,-180)['cell_id'])
        for lat,lon in [(0,0),(89,179),(-89,-179),(15,67),(55,23)]: store.resolve(lat,lon)
        self.assertEqual(store.info()['loaded_tiles'],3)
        self.assertGreaterEqual(store.info()['evictions'],2)
        with self.assertRaises(ValueError): store.resolve(91,0)


class ActualSourceTests(unittest.TestCase):
    def test_raw_sources_are_sha256_pinned(self):
        manifest=geo.sources()
        self.assertGreaterEqual(len(manifest['sources']),7)
        for s in manifest['sources']:
            path=geo.ROOT/s['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),s['sha256'],s['id'])
            self.assertTrue(s['license'])
            self.assertTrue(s['source_url'].startswith('https://'))

    def test_named_tampa_intersection_has_actual_shared_nodes(self):
        graph=geo.load_graph('tampa')
        intersection=geo.tampa_anchor()
        self.assertEqual(set(intersection['source_node_ids']),{'2057042478','1603574189'})
        for node in intersection['source_node_ids']:
            names={way['tags'].get('name') for way in graph['ways'] if node in way['nodes']}
            self.assertIn('North Dale Mabry Highway',names)
            self.assertIn('West Spruce Street',names)
        self.assertAlmostEqual(intersection['lat'],27.95946425)

    def test_pedestrian_spawn_and_route_follow_sourced_allowed_edges(self):
        result=geo.route()
        self.assertEqual(result['status'],'ok')
        self.assertGreater(result['length_m'],50)
        self.assertGreater(len(result['nodes']),2)
        self.assertEqual(result['quality_mask']['geometry'],'source-confirmed')
        self.assertIn('tag-based',result['quality_mask']['access'])
        graph=geo.load_graph('tampa')
        edges=geo.adjacency(graph,'walk')
        for a,b in zip(result['nodes'],result['nodes'][1:]):
            self.assertIn(b,{e['to'] for e in edges[a]})
        self.assertIn(graph['nodes'][result['nodes'][0]]['tags'].get('highway'),('crossing',None))
        self.assertGreaterEqual(result['certificate']['source_graph_1']['sha256'].__len__(),64)

    def test_motorway_private_and_oneway_permissions(self):
        self.assertFalse(geo.way_allowed({'highway':'motorway'},'walk'))
        self.assertFalse(geo.way_allowed({'highway':'footway','access':'private'},'walk'))
        self.assertTrue(geo.way_allowed({'highway':'footway','foot':'designated'},'walk'))
        self.assertFalse(geo.way_allowed({'highway':'footway'},'drive'))
        graph=geo.load_graph('tampa'); adj=geo.adjacency(graph,'drive')
        way=next(w for w in graph['ways'] if w['tags'].get('oneway')=='yes' and w['tags'].get('name')=='North Dale Mabry Highway')
        a,b=way['nodes'][:2]
        self.assertTrue(any(e['to']==b and e['way_id']==way['id'] for e in adj[a]))
        self.assertFalse(any(e['to']==a and e['way_id']==way['id'] for e in adj.get(b,[])))

    def test_unknown_source_route_refuses_instead_of_fabricating(self):
        self.assertEqual(geo.route(city='tokyo')['status'],'unsupported')
        self.assertEqual(geo.route(mode='ship')['status'],'unsupported')
        self.assertEqual(geo.route(start=[0,0],end=[0,0])['status'],'infeasible')

    def test_global_queries_return_source_masks_and_gaps(self):
        for lat,lon in [(27.959,-82.505),(51.508,-.127),(-33.868,151.209),(35.68,139.69),(-1.286,36.817),(-22.9,-43.2),(90,0),(-90,0),(0,180),(0,-140)]:
            cell=geo.resolve_cell(lat,lon)
            self.assertEqual(cell['status'],'ok')
            self.assertEqual(cell['coords']['lon'],geo.normalize_lon(lon))
            self.assertIn('coverage',cell)
            self.assertIn('population_grid',cell['coverage'])
            self.assertEqual(cell['coverage']['population_grid']['status'],'gap')
            self.assertEqual(cell['coverage']['maritime_routes']['status'],'gap')
        self.assertEqual(geo.resolve_cell(27.959,-82.505)['coverage']['roads']['status'],'present')
        self.assertEqual(geo.resolve_cell(0,-140)['coverage']['roads']['status'],'gap')

    def test_weather_snapshot_respects_its_actual_15_minute_interval(self):
        live=geo.weather_field(epoch='2026-10-20T19:20:00Z')
        early=geo.weather_field(epoch='2026-10-20T19:00:00Z')
        late=geo.weather_field(epoch='2026-10-20T19:30:00Z')
        self.assertEqual(live['status'],'snapshot')
        self.assertEqual(early['status'],'stale')
        self.assertEqual(late['status'],'stale')
        self.assertEqual(live['source_kind'],'estimated')
        self.assertEqual(geo.weather_field(0,0)['status'],'gap')

    def test_scene_contains_real_footprints_and_explicit_fictional_names(self):
        scene=geo.scene()
        self.assertGreater(len(scene['roads']),20)
        self.assertGreater(len(scene['buildings']),20)
        self.assertEqual(scene['quality_mask']['geometry'],'source-confirmed')
        self.assertEqual(scene['quality_mask']['building_height'],'estimated-when-tag-absent')
        self.assertIn('fictional',scene['buildings'][0]['alias_kind'])
        self.assertEqual(len(scene['roads'][0]['points_enu'][0]),3)
        self.assertGreaterEqual(len(scene['buildings'][0]['footprint_enu']),3)
        self.assertTrue(scene['spawn']['source_node_id'])

    def test_cross_continent_comparison_reports_empirical_controls(self):
        witness=geo.match_routes('tampa','london',seed=31,samples=64)
        self.assertEqual(witness['status'],'ok')
        self.assertEqual(witness['certificate']['source_graph_1']['city'],'tampa')
        self.assertEqual(witness['certificate']['source_graph_2']['city'],'london')
        self.assertEqual(witness['certificate']['calibration']['heldout_samples'],64)
        self.assertGreaterEqual(witness['certificate']['calibration']['p_value'],1/65)
        self.assertLessEqual(witness['certificate']['calibration']['p_value'],1)
        self.assertIn(witness['conclusion'],('negative','candidate'))
        self.assertEqual(witness['certificate']['fictional_portal_effect'],False)
        self.assertEqual(geo.match_routes('tampa','london',seed=31,samples=64),witness)

if __name__=='__main__': unittest.main()
