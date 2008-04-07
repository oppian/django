import unittest
from django.contrib.gis.gdal import OGRGeometry, OGRGeomType, \
    OGRException, OGRIndexError, SpatialReference, CoordTransform
from django.contrib.gis.tests.geometries import *

class OGRGeomTest(unittest.TestCase):
    "This tests the OGR Geometry."

    def test00_geomtype(self):
        "Testing OGRGeomType object."

        # OGRGeomType should initialize on all these inputs.
        try:
            g = OGRGeomType(1)
            g = OGRGeomType(7)
            g = OGRGeomType('point')
            g = OGRGeomType('GeometrycollectioN')
            g = OGRGeomType('LINearrING')
        except:
            self.fail('Could not create an OGRGeomType object!')

        # Should throw TypeError on this input
        self.assertRaises(TypeError, OGRGeomType.__init__, 23)
        self.assertRaises(TypeError, OGRGeomType.__init__, 'fooD')
        self.assertRaises(TypeError, OGRGeomType.__init__, 9)

        # Equivalence can take strings, ints, and other OGRGeomTypes
        self.assertEqual(True, OGRGeomType(1) == OGRGeomType(1))
        self.assertEqual(True, OGRGeomType(7) == 'GeometryCollection')
        self.assertEqual(True, OGRGeomType('point') == 'POINT')
        self.assertEqual(False, OGRGeomType('point') == 2)
        self.assertEqual(True, OGRGeomType(6) == 'MULtiPolyGON')
        
    def test01a_wkt(self):
        "Testing WKT output."
        for g in wkt_out:
            geom = OGRGeometry(g.wkt)
            self.assertEqual(g.wkt, geom.wkt)

    def test01b_gml(self):
        "Testing GML output."
        for g in wkt_out:
            geom = OGRGeometry(g.wkt)
            self.assertEqual(g.gml, geom.gml)

    def test01c_hex(self):
        "Testing HEX input/output."
        for g in hex_wkt:
            geom1 = OGRGeometry(g.wkt)
            self.assertEqual(g.hex, geom1.hex)
            # Constructing w/HEX
            geom2 = OGRGeometry(g.hex)
            self.assertEqual(geom1, geom2)

    def test01d_wkb(self):
        "Testing WKB input/output."
        from binascii import b2a_hex
        for g in hex_wkt:
            geom1 = OGRGeometry(g.wkt)
            wkb = geom1.wkb
            self.assertEqual(b2a_hex(wkb).upper(), g.hex)
            # Constructing w/WKB.
            geom2 = OGRGeometry(wkb)
            self.assertEqual(geom1, geom2)

    def test01e_json(self):
        "Testing GeoJSON input/output."
        from django.contrib.gis.gdal.prototypes.geom import GEOJSON
        if not GEOJSON: return
        for g in json_geoms:
            geom = OGRGeometry(g.wkt)
            self.assertEqual(g.json, geom.json)
            self.assertEqual(g.json, geom.geojson)
            self.assertEqual(OGRGeometry(g.wkt), OGRGeometry(geom.json))

    def test02_points(self):
        "Testing Point objects."

        prev = OGRGeometry('POINT(0 0)')
        for p in points:
            if not hasattr(p, 'z'): # No 3D
                pnt = OGRGeometry(p.wkt)
                self.assertEqual(1, pnt.geom_type)
                self.assertEqual('POINT', pnt.geom_name)
                self.assertEqual(p.x, pnt.x)
                self.assertEqual(p.y, pnt.y)
                self.assertEqual((p.x, p.y), pnt.tuple)

    def test03_multipoints(self):
        "Testing MultiPoint objects."

        for mp in multipoints:
            mgeom1 = OGRGeometry(mp.wkt) # First one from WKT
            self.assertEqual(4, mgeom1.geom_type)
            self.assertEqual('MULTIPOINT', mgeom1.geom_name)
            mgeom2 = OGRGeometry('MULTIPOINT') # Creating empty multipoint
            mgeom3 = OGRGeometry('MULTIPOINT')
            for g in mgeom1:
                mgeom2.add(g) # adding each point from the multipoints
                mgeom3.add(g.wkt) # should take WKT as well
            self.assertEqual(mgeom1, mgeom2) # they should equal
            self.assertEqual(mgeom1, mgeom3)
            self.assertEqual(mp.points, mgeom2.tuple)
            self.assertEqual(mp.n_p, mgeom2.point_count)
                                                                            
    def test04_linestring(self):
        "Testing LineString objects."
        prev = OGRGeometry('POINT(0 0)')
        for ls in linestrings:
            linestr = OGRGeometry(ls.wkt)
            self.assertEqual(2, linestr.geom_type)
            self.assertEqual('LINESTRING', linestr.geom_name)
            self.assertEqual(ls.n_p, linestr.point_count)
            self.assertEqual(ls.tup, linestr.tuple)
            self.assertEqual(True, linestr == OGRGeometry(ls.wkt))
            self.assertEqual(True, linestr != prev)
            self.assertRaises(OGRIndexError, linestr.__getitem__, len(linestr))
            prev = linestr

            # Testing the x, y properties.
            x = [tmpx for tmpx, tmpy in ls.tup]
            y = [tmpy for tmpx, tmpy in ls.tup]
            self.assertEqual(x, linestr.x)
            self.assertEqual(y, linestr.y)

    def test05_multilinestring(self):
        "Testing MultiLineString objects."
        prev = OGRGeometry('POINT(0 0)')
        for mls in multilinestrings:
            mlinestr = OGRGeometry(mls.wkt)
            self.assertEqual(5, mlinestr.geom_type)
            self.assertEqual('MULTILINESTRING', mlinestr.geom_name)
            self.assertEqual(mls.n_p, mlinestr.point_count)
            self.assertEqual(mls.tup, mlinestr.tuple)
            self.assertEqual(True, mlinestr == OGRGeometry(mls.wkt))
            self.assertEqual(True, mlinestr != prev)
            prev = mlinestr
            for ls in mlinestr:
                self.assertEqual(2, ls.geom_type)
                self.assertEqual('LINESTRING', ls.geom_name)
            self.assertRaises(OGRIndexError, mlinestr.__getitem__, len(mlinestr)) 

    def test06_linearring(self):
        "Testing LinearRing objects."
        prev = OGRGeometry('POINT(0 0)')
        for rr in linearrings:
            lr = OGRGeometry(rr.wkt)
            #self.assertEqual(101, lr.geom_type.num)
            self.assertEqual('LINEARRING', lr.geom_name)
            self.assertEqual(rr.n_p, len(lr))
            self.assertEqual(True, lr == OGRGeometry(rr.wkt))
            self.assertEqual(True, lr != prev)
            prev = lr

    def test07a_polygons(self):
        "Testing Polygon objects."
        prev = OGRGeometry('POINT(0 0)')
        for p in polygons:
            poly = OGRGeometry(p.wkt)
            self.assertEqual(3, poly.geom_type)
            self.assertEqual('POLYGON', poly.geom_name)
            self.assertEqual(p.n_p, poly.point_count)
            self.assertEqual(p.n_i + 1, len(poly))

            # Testing area & centroid.
            self.assertAlmostEqual(p.area, poly.area, 9)
            x, y = poly.centroid.tuple
            self.assertAlmostEqual(p.centroid[0], x, 9)
            self.assertAlmostEqual(p.centroid[1], y, 9)

            # Testing equivalence
            self.assertEqual(True, poly == OGRGeometry(p.wkt))
            self.assertEqual(True, poly != prev)
            
            if p.ext_ring_cs:
                ring = poly[0]
                self.assertEqual(p.ext_ring_cs, ring.tuple)
                self.assertEqual(p.ext_ring_cs, poly[0].tuple)
                self.assertEqual(len(p.ext_ring_cs), ring.point_count)
            
            for r in poly:
                self.assertEqual('LINEARRING', r.geom_name)

    def test07b_closepolygons(self):
        "Testing closing Polygon objects."
        # Both rings in this geometry are not closed.
        poly = OGRGeometry('POLYGON((0 0, 5 0, 5 5, 0 5), (1 1, 2 1, 2 2, 2 1))')
        self.assertEqual(8, poly.point_count)
        print "\nBEGIN - expecting IllegalArgumentException; safe to ignore.\n"
        try:
            c = poly.centroid
        except OGRException:
            # Should raise an OGR exception, rings are not closed
            pass
        else:
            self.fail('Should have raised an OGRException!')
        print "\nEND - expecting IllegalArgumentException; safe to ignore.\n"

        # Closing the rings
        poly.close_rings()
        self.assertEqual(10, poly.point_count) # Two closing points should've been added
        self.assertEqual(OGRGeometry('POINT(2.5 2.5)'), poly.centroid)

    def test08_multipolygons(self):
        "Testing MultiPolygon objects."
        prev = OGRGeometry('POINT(0 0)')
        for mp in multipolygons:
            mpoly = OGRGeometry(mp.wkt)
            self.assertEqual(6, mpoly.geom_type)
            self.assertEqual('MULTIPOLYGON', mpoly.geom_name)
            if mp.valid:
                self.assertEqual(mp.n_p, mpoly.point_count)
                self.assertEqual(mp.num_geom, len(mpoly))
                self.assertRaises(OGRIndexError, mpoly.__getitem__, len(mpoly))
                for p in mpoly:
                    self.assertEqual('POLYGON', p.geom_name)
                    self.assertEqual(3, p.geom_type)
            self.assertEqual(mpoly.wkt, OGRGeometry(mp.wkt).wkt)

    def test09a_srs(self):
        "Testing OGR Geometries with Spatial Reference objects."
        for mp in multipolygons:
            # Creating a geometry w/spatial reference
            sr = SpatialReference('WGS84')
            mpoly = OGRGeometry(mp.wkt, sr)
            self.assertEqual(sr.wkt, mpoly.srs.wkt)
          
            # Ensuring that SRS is propagated to clones.
            klone = mpoly.clone()
            self.assertEqual(sr.wkt, klone.srs.wkt)
  
            # Ensuring all children geometries (polygons and their rings) all
            # return the assigned spatial reference as well.
            for poly in mpoly:
                self.assertEqual(sr.wkt, poly.srs.wkt)
                for ring in poly:
                    self.assertEqual(sr.wkt, ring.srs.wkt)

            # Ensuring SRS propagate in topological ops.
            a, b = topology_geoms[0]
            a, b = OGRGeometry(a.wkt, sr), OGRGeometry(b.wkt, sr)
            diff = a.difference(b)
            union = a.union(b)
            self.assertEqual(sr.wkt, diff.srs.wkt)
            self.assertEqual(sr.srid, union.srs.srid)

            # Instantiating w/an integer SRID
            mpoly = OGRGeometry(mp.wkt, 4326)
            self.assertEqual(4326, mpoly.srid)
            mpoly.srs = SpatialReference(4269)
            self.assertEqual(4269, mpoly.srid)
            self.assertEqual('NAD83', mpoly.srs.name)
          
            # Incrementing through the multipolyogn after the spatial reference
            # has been re-assigned.
            for poly in mpoly:
                self.assertEqual(mpoly.srs.wkt, poly.srs.wkt)
                poly.srs = 32140
                for ring in poly:
                    # Changing each ring in the polygon
                    self.assertEqual(32140, ring.srs.srid)
                    self.assertEqual('NAD83 / Texas South Central', ring.srs.name)
                    ring.srs = str(SpatialReference(4326)) # back to WGS84
                    self.assertEqual(4326, ring.srs.srid)

                    # Using the `srid` property.
                    ring.srid = 4322
                    self.assertEqual('WGS 72', ring.srs.name)
                    self.assertEqual(4322, ring.srid)

    def test09b_srs_transform(self):
        "Testing transform()."
        orig = OGRGeometry('POINT (-104.609 38.255)', 4326)
        trans = OGRGeometry('POINT (992385.4472045 481455.4944650)', 2774)

        # Using an srid, a SpatialReference object, and a CoordTransform object
        # or transformations.
        t1, t2, t3 = orig.clone(), orig.clone(), orig.clone()
        t1.transform(trans.srid)
        t2.transform(SpatialReference('EPSG:2774'))
        ct = CoordTransform(SpatialReference('WGS84'), SpatialReference(2774))
        t3.transform(ct)

        # Testing use of the `clone` keyword.
        k1 = orig.clone()
        k2 = k1.transform(trans.srid, clone=True)
        self.assertEqual(k1, orig)
        self.assertNotEqual(k1, k2)

        prec = 3
        for p in (t1, t2, t3, k2):
            self.assertAlmostEqual(trans.x, p.x, prec)
            self.assertAlmostEqual(trans.y, p.y, prec)

    def test10_difference(self):
        "Testing difference()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = OGRGeometry(g_tup[0].wkt)
            b = OGRGeometry(g_tup[1].wkt)
            d1 = OGRGeometry(diff_geoms[i].wkt)
            d2 = a.difference(b)
            self.assertEqual(d1, d2)
            self.assertEqual(d1, a - b) # __sub__ is difference operator
            a -= b # testing __isub__
            self.assertEqual(d1, a)

    def test11_intersection(self):
        "Testing intersects() and intersection()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = OGRGeometry(g_tup[0].wkt)
            b = OGRGeometry(g_tup[1].wkt)
            i1 = OGRGeometry(intersect_geoms[i].wkt)
            self.assertEqual(True, a.intersects(b))
            i2 = a.intersection(b)
            self.assertEqual(i1, i2)
            self.assertEqual(i1, a & b) # __and__ is intersection operator
            a &= b # testing __iand__
            self.assertEqual(i1, a)

    def test12_symdifference(self):
        "Testing sym_difference()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = OGRGeometry(g_tup[0].wkt)
            b = OGRGeometry(g_tup[1].wkt)
            d1 = OGRGeometry(sdiff_geoms[i].wkt)
            d2 = a.sym_difference(b)
            self.assertEqual(d1, d2)
            self.assertEqual(d1, a ^ b) # __xor__ is symmetric difference operator
            a ^= b # testing __ixor__
            self.assertEqual(d1, a)
            
    def test13_union(self):
        "Testing union()."
        for i in xrange(len(topology_geoms)):
            g_tup = topology_geoms[i]
            a = OGRGeometry(g_tup[0].wkt)
            b = OGRGeometry(g_tup[1].wkt)
            u1 = OGRGeometry(union_geoms[i].wkt)
            u2 = a.union(b)
            self.assertEqual(u1, u2)
            self.assertEqual(u1, a | b) # __or__ is union operator
            a |= b # testing __ior__
            self.assertEqual(u1, a)

    def test14_add(self):
        "Testing GeometryCollection.add()."
        # Can't insert a Point into a MultiPolygon.
        mp = OGRGeometry('MultiPolygon')
        pnt = OGRGeometry('POINT(5 23)')
        self.assertRaises(OGRException, mp.add, pnt)

        # GeometryCollection.add may take an OGRGeometry (if another collection
        # of the same type all child geoms will be added individually) or WKT.
        for mp in multipolygons:
            mpoly = OGRGeometry(mp.wkt)
            mp1 = OGRGeometry('MultiPolygon')
            mp2 = OGRGeometry('MultiPolygon')
            mp3 = OGRGeometry('MultiPolygon')

            for poly in mpoly:
                mp1.add(poly) # Adding a geometry at a time
                mp2.add(poly.wkt) # Adding WKT
            mp3.add(mpoly) # Adding a MultiPolygon's entire contents at once.
            for tmp in (mp1, mp2, mp3): self.assertEqual(mpoly, tmp)

    def test15_extent(self):
        "Testing `extent` property."
        # The xmin, ymin, xmax, ymax of the MultiPoint should be returned.
        mp = OGRGeometry('MULTIPOINT(5 23, 0 0, 10 50)')
        self.assertEqual((0.0, 0.0, 10.0, 50.0), mp.extent)
        # Testing on the 'real world' Polygon.
        poly = OGRGeometry(polygons[3].wkt)
        ring = poly.shell
        x, y = ring.x, ring.y
        xmin, ymin = min(x), min(y)
        xmax, ymax = max(x), max(y)
        self.assertEqual((xmin, ymin, xmax, ymax), poly.extent)

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(OGRGeomTest))
    return s

def run(verbosity=2):
    unittest.TextTestRunner(verbosity=verbosity).run(suite())
