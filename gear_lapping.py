# gear_lapping.py
# version 0.46, 2026-11-10
# blender add-on: two gears imprint each other in turn by kinematic rolling.
#
# a gear = an empty (its local z is the rotation axis) with z tooth elements as children.
# all elements share one mesh (linked copies), turned by 360/z: edit any element, all follow.
# names: gear_<number>_<teeth>_tooth_m<module>, numbered from 1; a worm worm_<number>_<starts>_start_m<axial
# module>, its wheel wormwheel_...; sun_, planet_, ring_, pinion_, rack_ in the ready made sets. a pair
# lives in its own empty pair_<number>_<kind>; its gears are named P<number>_<gear name>.
# sidebar, four tabs:
#   "Gear"       one gear by its parameters: cylindrical (spur, helical, herringbone), internal
#                (ring, cut by a pinion rolling inside it), bevel (pitch cone angle), worm
#   "Gear Pair"  gears in mesh by the parameters of the pair: external, internal (pinion and the
#                ring it cuts), planetary (sun, planets on a carrier empty, ring cut by a planet;
#                planets equally spaced when (sun + ring) / planets is whole, else at the nearest
#                angles where they mesh), bevel (straight or spiral), worm, cycloidal (clock);
#                helix and herringbone for the cylindrical ones
#   "Lapping"    blanks and rolling: a tool (any gear, or an own body made a gear with "make gear
#                from active"), a blank (by teeth in mesh with the tool, or by dimensions: a body of
#                revolution with axis angle, center distance and an optional throat), the ratio
#                (from the teeth or as tool turns : blank turns) and a whole-number slowdown of the
#                blank, then the imprint and the reverse pass
#   "Chain & Belt" roller chain sprockets (iso 606 / ansi: 05B to 12B, ansi 25 to 60, own pitch and roller) and
#                timing belt pulleys (GT2 2 and 3 mm, HTD 3M and 5M, T2.5, T5, MXL, XL, H) with flanges and hub;
#                a pair: two wheels at the center distance of a whole number of links (even) or belt teeth
#   every tab ends with the Print block: the gear it acts on, the print offset (Apply / Nominal), the chamfer of the
#   end faces and the ends it goes to, the printer's nozzle and layer, the overhang check, the printable copy, the
#   stl export, and the last result. (the clearance on the rubbing faces of a lapped gear is in the Lapping tab.)
#
#   starter teeth        cut by the gost 13755 basic rack: involute flanks and the root fillets of
#                        its rounded tip (0.38 m), undercut included. helical: the sections turned
#                        along the width; herringbone: turned by |z| (two halves of opposite hand,
#                        the apex in the middle plane)
#   spiral bevel         the sections of a bevel gear turned along the cone distance L by
#                        tan b ln(L / L_mean) / sin(delta): the tooth line on the crown gear a
#                        logarithmic spiral of the same spiral angle b everywhere (curved teeth); the
#                        mate the opposite hand. every sphere about the apex is then the same plane
#                        problem turned, so the section method laps them like helical gears
#   herringbone bevel    the same with |ln(L / L_mean)|: two halves of opposite spiral hand meeting in a
#                        chevron on the mean cone distance (the Herringbone button next to the spiral angle)
#   sprocket             iso 606: roller seat arc ri = 0.505 d1 + 0.069 d1^(1/3) about the roller centre on the pitch
#                        circle, seating angle 120 - 90 / z, the flank an arc re = 0.12 d1 (z + 2) tangent to it, tip
#                        circle between the iso limits (checked for rollers of every gap), tooth width 0.93 / 0.95 of
#                        the inner width. pulley: groove depth, width and pitch line differential after the common
#                        open tables; round teeth (GT2, HTD) an arc, trapezoid teeth (T, MXL, XL, H) with flat bottom
#                        and rounded corners. the sector may be stepped along the axis (flanges, hub)
#   cycloidal (clock)    bs 978 part 2 proportions, the wheel drives: wheel teeth pi m / 2 thick, the
#                        addendum the epicycloid of a circle of half the pinion pitch radius (conjugate
#                        to the radial flanks of the leaves), up to a tip land 0.35 m wide; pinion
#                        leaves 1.05 m (up to 7) or 1.25 m thick, radial flanks, round addendum;
#                        dedenda the mating addendum + 0.4 m
#   bevel pair           both gears with starter teeth (an internal second gear stays a blank), from
#                        the two tooth counts and the shaft angle:
#                        tan d1 = sin S / (z2 / z1 + cos S), d2 = S - d1; both empties and the
#                        common cone apex are in the world origin
#   worm pair            worm (source) and its wheel (target), axes crossed at 90 deg: starts z1,
#                        axial module m, diameter factor q (pitch diameter q m), lead angle
#                        atan(z1 / q), one element per start (one start: the whole ring, with a
#                        hairline slot between its sides that the print copy closes). the starter
#                        thread is a za worm (straight sided axial profile, 20 deg), as long as the
#                        wheel's outer diameter; the wheel is throated (tips 0.25 m clear of the worm
#                        roots), 0.75 of the worm tip diameter wide, its teeth cut at once by the hob
#                        of the worm (tip c* m higher, gost fillet), section by section. every worm
#                        element is the screw sweep of its axial profile. a worm lapped by its wheel
#                        is made the same way from one meridian section (a running worm); a globoid
#                        or slowed pair, and an own body as the target, is cut on every meridian
#                        half plane (2 deg apart) and joined by triangles. a worm as the source is a
#                        rack made from its stored axial profile while its mesh is the screw of that
#                        profile (checked before every pass), else it is turned for real
#   ratio and slowdown   the tool turns zt kt / (zs ks) times per blank turn; a blank whose teeth
#                        would differ under that ratio is refused, a worm is rebuilt with as many
#                        starts as its thread repeats per turn
#   create mating gear   smooth blank for the source, already in place: cylinders at the pitch
#                        distance, bevel gears apex on apex with sin(d2) = z2 sin(d1) / z1
#   imprint              target element minus the space the source teeth sweep while the pair turns
#                        once. cylindrical pairs with parallel axes (straight or helical, internal
#                        too) and straight bevel pairs with a common apex use the section method: one
#                        section (a plane, or a sphere about the apex seen through a gnomonic
#                        projection) is cut by all source positions in 2d and the element is built
#                        again from the new outline (helical: the outline twisted along the width).
#                        other placements use slices across the element (planes, spheres or
#                        cylinders), each cut the same way, then lofted.
#                        the cut faces are coloured by the order of the steps that cut them (red
#                        first, blue last, 12 bands). a face is parasitic (magenta) when it was cut
#                        by a non working face of the source (its tip land, root, walls), by a sharp
#                        corner of the source (the path of its tip), or when its normal cannot pass
#                        torque (steeper than the max pressure angle against the turning direction).
#                        with "simple non-working faces" the parasitic runs of every section become
#                        simple surfaces inside the cut, keeping the relief as clearance: the root
#                        as walls along the meridians, rounds and a cylinder / cone / plane on a
#                        fixed grid of meridians, the tip land with straight chamfers. the gear so
#                        made is the tool of the next pass: its sweep is the sweep of these surfaces
#                        and of the clean edges between them and the working flanks
#                        the root lies c* modules below the deepest cut (root clearance, gost 13755:
#                        c* = 0.25, 1.25 m below the pitch circle with a standard mate).
#                        slices: a cylindrical source is continued along its helix beyond its ends
#                        as far as the target reaches (at most "tool continued" of its length), so
#                        the target is cut by its flanks and not by the edges of its ends
#   print offset         made when a gear is created (scene setting "Print offset", 0 = none): every
#                        wall of the sector mesh moved into the material across the axis by it (what a
#                        3d printer adds), so the pieces can be corrected by hand; the nominal shape is
#                        kept ("Nominal" restores it, "Apply" makes it again, also for older gears)
#   sector pieces        open at their sides (no meridian faces: the pieces meet there once joined); the
#                        lapping closes them for the time of the operation and opens the result again
#   printable copy       the pieces copied round the axis and welded on their rims into one closed solid, the
#                        shaft seat ring united with it, the rims of the end faces chamfered (see chamfer);
#                        nothing taken out of the pieces (what was edited by hand stays), no offset (it is in the
#                        pieces), no repair. the gear itself is never changed
#   chamfer              against the elephant foot (the first layers, squashed wider by the bed): in the printable
#                        copy and the stl only. every rim of an end face (flat, normal along the axis, in the
#                        lowest or the highest plane): the outline of the teeth, the bore, the hole of the shaft
#                        seat, hubs; 45 deg, the size set in the Print block (0.4 = two layers of 0.2), both ends
#                        or one. the walls next to a rim are cut at the height of the chamfer and the points
#                        below the cut move into the material by the rest of that height (an own algorithm: the
#                        bevel of blender fails on outlines of thousands of points); where the moved outline of a
#                        thin tooth tip would cross itself the points are merged. every rim is checked afterwards
#                        (closed as before, volume positive, no triangle cutting another), else a smaller chamfer
#                        for that rim, at last none. a cone as flat as the plane (the back face of a bevel pinion
#                        with a small cone angle) leaves no foot and stays as it is
#   shaft seat           round, d, square, pentagon, hexagon, lego cross: a ring united at printing, the
#                        bore of the pieces wide enough for it; for bevel gears too (between the two end planes
#                        under the neck cone)
#   export stl           the active gear as one solid in an stl file (gear frame, axis = z): its parts
#                        (the linked elements, or a mesh joined by hand, cut where more than two faces
#                        meet an edge) made a hair (2e-4 m) thicker and united by the manifold boolean,
#                        so the walls between them vanish; slivers collapsed, holes closed, normals
#                        out, the rims of the end faces chamfered; the print offset is in the pieces
#   swap                 source <-> target
#   reverse blank        smooth copy of the source in its place; it becomes the target and the old
#                        target the source (a1 -> b1, then b1 -> a2)
#
# requires blender 4.5+ (manifold boolean solver for the 3d method).

bl_info = {
    "name": "Gear Lapping",
    "author": "darkfrei, Claude",
    "version": (0, 46, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Gear, Gear Pair, Lapping",
    "description": "Two gears imprint each other in turn by kinematic rolling",
    "category": "Object",
}

import bpy
import bmesh
import math
import time
import random
import numpy as np
from fractions import Fraction
import mathutils
import mathutils.kdtree
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils import geometry as mgeom

MAX_TOOL_FACES = 1500000      # safety limit for one imprint
BATCH_FACES = 300000          # faces subtracted per boolean call
RAMP_OVERLAP = 0.03           # each ramp reaches this share of a step into the next one
PRISM_GROW = 0.02             # prisms are grown by this share about their centre
CREASE_DEG = 3.0              # prisms at silhouette edges sharper than this
AREA_K = 4.0                  # a run is replaced by simple surfaces only if they take away at most this many
                              # times the area of the relief along it
ROUND_SEG = 8                 # segments of a quarter round at the root (11.25 deg each: no ramps there)
FLICKER_GROW = 0.0            # a flank end may move out over its parasitic neighbours by this much, in modules
CORNER_NEAR = 0.02            # a cut made this close to a corner of the source is parasitic, in modules
FLICKER = 0.1                 # where a flank ends: window of the majority of working / parasitic cuts and the
                              # shortest run of one kind, in modules
REMESH_EPS = 2e-3             # remeshing: allowed deviation of the triangles, in modules
SLOT = 2e-5                   # rad: the gap between the sides of a single element (one start worm)
WORM_CREASE_DEG = 35.0        # the same for a worm source
RAMP_CREASE_DEG = 15.0        # slice method: ramp prisms at edges sharper than this
NEUTRAL_COS = 0.02            # faces moving closer than this to their own plane count as neither side


class LapError(Exception):
    pass


# ---------------------------------------------------------------------------
# element geometry
# ---------------------------------------------------------------------------

def rotZ(a):
    return Matrix.Rotation(a, 4, 'Z')


def gridAngles(a0, a1, s):
    # a0, the multiples of s strictly between, a1
    res = [a0]
    j = int(math.floor(a0 / s)) + 1
    while j * s < a1 - 1e-9 * s:
        if j * s > a0 + 1e-9 * s:
            res.append(j * s)
        j += 1
    res.append(a1)
    return res


def polar(pts):
    return [(r * math.cos(a), r * math.sin(a)) for r, a in pts]


def finishMesh(bm, name):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


# face classes = material slots of every element mesh: 0 plain (blank, body, ends), 1..12 the
# order of the steps that cut the face (red = first, blue = last), 13 parasitic (cut, but its normal
# cannot pass torque, or cut by a tip or an edge of the source: relieved a little), 14 the flank of
# a starter tooth (not cut yet, but it can work)
BANDS = 12
CLS_PLAIN = 0
CLS_PARASITIC = BANDS + 1
CLS_FLANK = BANDS + 2


def working(c):
    # a face that can pass torque: cut and working, or the flank of a starter tooth
    return 1 <= c <= BANDS or c == CLS_FLANK


def starterClasses(top, tol):
    # classes of a starter tooth side (height, angle): its flank segments change the height, the root
    # and the tip are arcs of one height
    return [CLS_FLANK if abs(top[i + 1][0] - top[i][0]) > tol else CLS_PLAIN for i in range(len(top) - 1)]


def lapMaterials():
    import colorsys
    specs = [("LAP_plain", (0.62, 0.62, 0.62))]
    for i in range(BANDS):
        specs.append(("LAP_step_%02d" % (i + 1), colorsys.hsv_to_rgb(0.667 * i / (BANDS - 1), 0.85, 0.95)))
    specs.append(("LAP_parasitic", (1.0, 0.0, 1.0)))
    specs.append(("LAP_flank", (0.80, 0.78, 0.55)))
    mats = []
    for name, c in specs:
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
            m.diffuse_color = (c[0], c[1], c[2], 1.0)
        mats.append(m)
    return mats


def attachMaterials(me):
    # material slots of the classes; removing slots shifts the face indices, so they are kept aside
    mats = lapMaterials()
    if list(me.materials) == mats:
        return
    idx = [p.material_index for p in me.polygons]
    me.materials.clear()
    for m in mats:
        me.materials.append(m)
    for p, i in zip(me.polygons, idx):
        p.material_index = i


_LOW = [False]                # low poly mode (set by the operators): straight flanks, few points


def lowTop(z, module, internal=False, clearance=0.25, alpha=20.0):
    # low poly tooth side (radius, angle) from -p/2 to p/2: root and tip as straight chords, each
    # flank two straight segments (root -> pitch -> tip) on the involute points, no fillets
    p = 2 * math.pi / z
    rp = z * module / 2
    rb = rp * math.cos(math.radians(alpha))
    inv = lambda x: math.tan(x) - x
    a0 = math.radians(alpha)

    def half(r):              # half thickness angle of the external tooth at r
        if r <= rb:
            return math.pi / (2 * z) + inv(a0)
        return math.pi / (2 * z) + inv(a0) - inv(math.acos(rb / r))
    ha, hf = module, (1.0 + clearance) * module
    if internal:
        ra, rf = rp - ha, rp + hf
        # straight segments inside a ring cut into the pinion tips: the ring teeth 0.15 m thinner
        h = lambda r: p / 2 - half(r) - 0.075 * module / r
    else:
        ra, rf = rp + ha, rp - hf
        h = half
    ht = min(h(ra), p / 2 - 1e-4)
    ht = max(ht, 0.04 * p)
    hr = min(max(h(rf), 0.04 * p), p / 2 - 0.04 * p)
    hp = h(rp)
    right = [(rf, -hr), (rp, -hp), (ra, -ht)]
    return [(rf, -p / 2)] + right + [(q, -a) for q, a in reversed(right)] + [(rf, p / 2)]


def spurTop(z, module, tooth, internal, addendum=None, clearance=0.25):
    # tooth side of the section as (radius, angle) from -p/2 to p/2
    p = 2 * math.pi / z
    rp = z * module / 2
    ha = module if addendum is None else addendum
    if tooth and _LOW[0]:
        return lowTop(z, module, internal, clearance)
    if tooth:
        if internal:
            raise LapError("the starter tooth is only for external gears: the ring is made by lapping")
        return toothOutline(z, module, clearance)
    r = rp - ha if internal else rp + ha
    return [(r, a) for a in gridAngles(-p / 2, p / 2, p / 16)]


def turnTop(top, phi, p):
    # a tooth side (radius, angle) over one pitch turned by phi about the axis and cut again to the
    # sector -p/2 .. p/2 (the outline is periodic: it goes on in the neighbouring sectors)
    phi = (phi + p / 2) % p - p / 2
    chain = []
    for sh in (-p, 0.0, p):
        for k, (r, a) in enumerate(top):
            if chain and k == 0:
                continue
            chain.append((r, a + sh + phi))
    out = []
    for k in range(len(chain) - 1):
        (r0, a0), (r1, a1) = chain[k], chain[k + 1]
        for lim in (-p / 2, p / 2):
            if (a0 - lim) * (a1 - lim) < 0:
                t = (lim - a0) / (a1 - a0)
                out.append((k + t, (r0 + (r1 - r0) * t, lim)))
    eps = 1e-12
    for k, (r0, a0) in enumerate(chain):
        if -p / 2 - eps <= a0 <= p / 2 + eps:
            out.append((k, (r0, min(p / 2, max(-p / 2, a0)))))
    out.sort(key=lambda e: e[0])
    pts = []
    for t, q in out:
        if not pts or abs(q[0] - pts[-1][0]) > 1e-12 or abs(q[1] - pts[-1][1]) > 1e-12:
            pts.append(q)
    i0 = next(i for i, q in enumerate(pts) if abs(q[1] + p / 2) < 1e-9)
    i1 = next(i for i in range(len(pts) - 1, -1, -1) if abs(pts[i][1] - p / 2) < 1e-9)
    return pts[i0:i1 + 1]


def tileStrip(bm, A, B, ca, cb, metric, twist=0.0, quads=False):
    # faces between two polylines A and B (bmesh verts, the contours of two neighbouring sections,
    # running the same way from one sector side to the other): quads when both are the same outline,
    # else triangles. the features of both contours (the ends of working, parasitic and blank runs,
    # sharp corners) are matched first and joined by edges, so the borders between the surfaces run
    # as clean lines from section to section; between them the triangulation with the smallest total
    # length of the new edges (dynamic programming) follows the surface where it moves across the
    # sector
    if len(A) == len(B) and (quads or all(abs(p[0] - q[0]) < 1e-12 and abs(p[1] - q[1]) < 1e-12
                                         for p, q in zip(metric[0], metric[1]))):
        for i in range(len(A) - 1):
            f = bm.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
            f.material_index = ca[i] if ca else 0
        return
    PA = np.array([tuple(v.co) for v in A])
    PB = np.array([tuple(v.co) for v in B])
    if twist:
        # a helical surface (worm thread): B is compared turned back by the twist between the
        # sections, so the points of the same thread line pair up
        c_, s_ = math.cos(-twist), math.sin(-twist)
        PB = PB.copy()
        PB[:, 0], PB[:, 1] = c_ * PB[:, 0] - s_ * PB[:, 1], s_ * PB[:, 0] + c_ * PB[:, 1]
    n, m = len(A), len(B)
    tris, cost = dpTile(PA, PB)
    pairs = matchFeatures(PA, PB, ca, cb) if (ca and cb and not _NOMATCH) else [(0, 0), (n - 1, m - 1)]
    if len(pairs) > 2:
        # the features joined, unless that makes the strip much longer than the free one (then the
        # features do not correspond: joining them would fold the surface across the gap)
        ft, fc = [], 0.0
        for (i0, j0), (i1, j1) in zip(pairs[:-1], pairs[1:]):
            t_, c_ = dpTile(PA[i0:i1 + 1], PB[j0:j1 + 1])
            ft += [(kind, a + i0, b + j0) for kind, a, b in t_]
            fc += c_
        if fc <= 1.6 * cost:
            tris = ft
    for kind, a, b in tris:
        if kind == 'A':
            f = bm.faces.new((A[a], A[a + 1], B[b]))
            f.material_index = ca[a] if ca else 0
        else:
            f = bm.faces.new((A[a], B[b + 1], B[b]))
            f.material_index = cb[b] if cb else 0


def dpTile(PA, PB):
    # triangles between two polylines with the smallest total length of the new edges:
    # ('A', i, j) = (A[i], A[i+1], B[j]), ('B', i, j) = (A[i], B[j+1], B[j])
    n, m = len(PA), len(PB)
    if n == 1 and m == 1:
        return [], 0.0
    D = np.linalg.norm(PA[:, None, :] - PB[None, :, :], axis=2)
    INF = float('inf')
    cost = np.full((n, m), INF)
    back = np.zeros((n, m), dtype=np.int8)
    cost[0, 0] = D[0, 0]
    for i in range(n):
        ci = cost[i]
        Di = D[i]
        if i > 0:
            ci[:] = cost[i - 1] + Di
            back[i, :] = 1
        for j in range(1, m):
            c = ci[j - 1] + Di[j]
            if c < ci[j]:
                ci[j] = c
                back[i, j] = 2
    i, j = n - 1, m - 1
    tris = []
    total = float(cost[n - 1, m - 1])
    while i > 0 or j > 0:
        if back[i, j] == 1:
            tris.append(('A', i - 1, j))
            i -= 1
        else:
            tris.append(('B', i, j - 1))
            j -= 1
    return tris[::-1], total


def contourFeatures(P, cls):
    # features of a contour: the points where the kind of the surface changes (working, parasitic,
    # blank) and the corners sharper than 25 degrees, as (index, label)
    def kind(c):
        return 'W' if working(c) else ('P' if c == CLS_PARASITIC else 'O')
    out = []
    cc = math.cos(math.radians(25))
    P = np.asarray(P, dtype=float)
    if len(P) < 3:
        return out
    A_ = P[1:-1] - P[:-2]
    B_ = P[2:] - P[1:-1]
    la_ = np.linalg.norm(A_, axis=1)
    lb_ = np.linalg.norm(B_, axis=1)
    dot_ = (A_ * B_).sum(axis=1)
    sharp = (la_ > 0) & (lb_ > 0) & (dot_ < cc * la_ * lb_)
    kinds = [kind(c) for c in cls]
    for i in range(1, len(P) - 1):
        k0, k1 = kinds[i - 1], kinds[i]
        if k0 != k1:
            out.append((i, k0 + k1))
            continue
        if sharp[i - 1]:
            out.append((i, 'C' + k0))
    return out


def matchFeatures(PA, PB, ca, cb):
    # pairs of points of the two contours to be joined: the ends, and the features with the same
    # label that are each other's nearest (mutual nearest neighbours) and closer than a few section
    # spacings, kept in order along both contours (the longest such chain)
    FA, FB = contourFeatures(PA, ca), contourFeatures(PB, cb)
    n, m = len(PA), len(PB)
    if not FA or not FB:
        return [(0, 0), (n - 1, m - 1)]
    gap = 0.5 * (np.linalg.norm(PA[0] - PB[0]) + np.linalg.norm(PA[-1] - PB[-1]))
    far = 3.0 * max(gap, 1e-12)
    cand = []
    # all distances between the features at once; a label mismatch counts as infinitely far (ties
    # go to the smaller index, as a minimum over (distance, index) would)
    iA = np.array([ia for ia, la in FA])
    iB = np.array([ib for ib, lb in FB])
    lA = [la for ia, la in FA]
    lB = [lb for ib, lb in FB]
    D = np.linalg.norm(PA[iA][:, None, :] - PB[iB][None, :, :], axis=2)
    same = np.array([[a_ == b_ for b_ in lB] for a_ in lA], dtype=bool)
    D = np.where(same, D, np.inf)
    oA = np.argsort(iA, kind='stable')
    oB = np.argsort(iB, kind='stable')
    for r, (ia, la) in enumerate(FA):
        row_ = D[r]
        if not np.isfinite(row_).any():
            continue
        c_ = oB[int(np.argmin(row_[oB]))]
        d, ib = float(row_[c_]), int(iB[c_])
        if d >= far:
            continue
        col_ = D[:, c_]
        rb = oA[int(np.argmin(col_[oA]))]
        if int(iA[rb]) == ia and 0 < ia < n - 1 and 0 < ib < m - 1:
            cand.append((ia, ib))
    cand.sort()
    # the longest chain increasing in both contours
    best = [1] * len(cand)
    prev = [-1] * len(cand)
    for i in range(len(cand)):
        for j in range(i):
            if cand[j][0] < cand[i][0] and cand[j][1] < cand[i][1] and best[j] + 1 > best[i]:
                best[i], prev[i] = best[j] + 1, j
    chain = []
    if cand:
        i = max(range(len(cand)), key=lambda q: best[q])
        while i >= 0:
            chain.append(cand[i])
            i = prev[i]
    return [(0, 0)] + chain[::-1] + [(n - 1, m - 1)]


def adaptiveTop(top, cls, met, tol, hmin, hmax, pins=()):
    # the points of a tooth side for meshing: corners (turn over 20 degrees), class changes and the
    # pinned points are kept, the smooth runs between them get points spaced by the curvature:
    # h = sqrt(8 tol R), the chord of an arc of radius R then deviates by tol
    M = [met(h, f) for h, f in top]
    n = len(M)
    keep = [0]
    for k in range(1, n - 1):
        a = (M[k][0] - M[k - 1][0], M[k][1] - M[k - 1][1])
        b = (M[k + 1][0] - M[k][0], M[k + 1][1] - M[k][1])
        la, lb = math.hypot(*a), math.hypot(*b)
        sharp = la > 0 and lb > 0 and (a[0] * b[0] + a[1] * b[1]) / (la * lb) < math.cos(math.radians(20))
        if sharp or cls[k] != cls[k - 1] or k in pins:
            keep.append(k)
    keep.append(n - 1)
    # curvature at the points (circle through the neighbours)
    kap = [0.0] * n
    for k in range(1, n - 1):
        (x0, y0), (x1, y1), (x2, y2) = M[k - 1], M[k], M[k + 1]
        a, b, c = math.dist(M[k - 1], M[k]), math.dist(M[k], M[k + 1]), math.dist(M[k - 1], M[k + 1])
        cr = abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0))
        kap[k] = 2 * cr / max(a * b * c, 1e-30)
    out, oc = [top[0]], []
    for r in range(len(keep) - 1):
        k0, k1 = keep[r], keep[r + 1]
        acc = [0.0]
        for k in range(k0, k1):
            acc.append(acc[-1] + math.dist(M[k], M[k + 1]))
        tot = acc[-1]
        # spacing along the run from the curvature of the nearest original point
        ts = [0.0]
        while ts[-1] < tot:
            s0 = ts[-1]
            k = min(range(k0, k1 + 1), key=lambda q: abs(acc[q - k0] - s0))
            kv = max(kap[k] if k0 < k < k1 else 0.0, 1e-9)
            h = min(hmax, max(hmin, math.sqrt(8 * tol / kv)))
            ts.append(s0 + h)
        ts[-1] = tot
        if len(ts) > 2 and ts[-1] - ts[-2] < 0.3 * (ts[-2] - ts[-3]):
            ts.pop(-2)
        q = k0
        for t in ts[1:]:
            while q < k1 - 1 and acc[q + 1 - k0] < t:
                q += 1
            seg = acc[q + 1 - k0] - acc[q - k0]
            u = (t - acc[q - k0]) / seg if seg > 0 else 1.0
            u = min(1.0, max(0.0, u))
            out.append((top[q][0] + (top[q + 1][0] - top[q][0]) * u, top[q][1] + (top[q + 1][1] - top[q][1]) * u))
            oc.append(cls[q])
        out[-1] = top[k1]
    return out, oc


def spurLoft(name, z, levels, tops, classes, r_body, turns=None, quads=False, shifts=None):
    # shifts: per level a turn of the whole sector (twisted "helical meridians": the same outline on
    # every level, joined by quads; neighbouring elements meet on the same twisted sides)
    # cylindrical element over several sections: levels z_k, tops[k] = tooth side (radius, angle)
    # from -p/2 to p/2 at z_k, classes[k] their segment classes. the body side is an arc of radius
    # r_body (bore of an external gear, mantle of a ring); the ends are the first and last section
    p = 2 * math.pi / z
    body = [(r_body, a) for a in reversed(gridAngles(-p / 2, p / 2, p / (2 if _LOW[0] else 16)))]
    if z == 1:
        # a single element is the whole ring: its sector sides would lie on each other and its
        # sections would not be simple polygons. it is squeezed into a hairline slot (the sides
        # SLOT apart), which the print copy closes
        sq = 1.0 - SLOT / (2 * math.pi)
        body = [(r, a * sq) for r, a in body]
        tops = [[(r, a * sq) for r, a in t] for t in tops]
    bm = bmesh.new()
    T, B, M = [], [], []
    for li, (zk, top) in enumerate(zip(levels, tops)):
        s0 = shifts[li] if shifts is not None else 0.0
        xy = polar([(r, a + s0) for r, a in top])
        T.append([bm.verts.new((x, y, zk)) for x, y in xy])
        B.append([bm.verts.new((x, y, zk)) for x, y in polar([(r, a + s0) for r, a in body])])
        M.append(xy)
    for k in range(len(levels) - 1):
        tileStrip(bm, T[k], T[k + 1], classes[k] if classes else None,
                  classes[k + 1] if classes else None, (M[k], M[k + 1]),
                  (turns[k + 1] - turns[k]) if turns else 0.0, quads or shifts is not None)
        for i in range(len(body) - 1):
            bm.faces.new((B[k][i], B[k][i + 1], B[k + 1][i + 1], B[k + 1][i]))
        bm.faces.new((T[k][-1], B[k][0], B[k + 1][0], T[k + 1][-1]))
        bm.faces.new((B[k][-1], T[k][0], T[k + 1][0], B[k + 1][-1]))
    bm.faces.new(T[0] + B[0])
    bm.faces.new(list(reversed(T[-1] + B[-1])))
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def spurElement(name, z, width, top, classes, r_body):
    # straight cylindrical element: the same section over the face width, centred on z = 0
    return spurLoft(name, z, [-width / 2, width / 2], [top, top], [classes, classes] if classes else None,
                    r_body)


def wallCDT(bm, bnd, bverts, place, sc, grid):
    # a curved wall given by its boundary in a (u, v) plane (bverts: its bmesh verts), filled by a
    # constrained triangulation with a grid of inner points; place(u, v) -> 3d point
    nb = len(bnd)
    pts = [Vector((u * sc, v)) for u, v in bnd]
    us = [u for u, v in bnd]
    vs = [v for u, v in bnd]
    extra = []
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    nu = max(1, int((u1 - u0) / grid[0]))
    nv = max(1, int((v1 - v0) / grid[1]))
    for iu in range(1, nu):
        for iv in range(1, nv):
            extra.append(Vector(((u0 + (u1 - u0) * iu / nu) * sc, v0 + (v1 - v0) * iv / nv)))
    res = mgeom.delaunay_2d_cdt(pts + extra, [(i, (i + 1) % nb) for i in range(nb)], [], 0, 1e-12 * sc * 10, True)
    ov, of, overts = res[0], res[2], res[3]
    V = np.array([(v[0], v[1]) for v in ov])
    T = trisOf(of)
    inside = insidePoly(V[T].mean(axis=1), np.array([(q[0], q[1]) for q in pts]))
    vm = {}
    for k, orig in enumerate(overts):
        if orig and orig[0] < nb:
            vm[k] = bverts[orig[0]]
    # a point the triangulation adds on the boundary (where the outline touches itself) would not
    # be joined to the neighbouring faces: then the wall is one polygon instead
    bset = set(range(nb))
    onb = set()
    E = np.array(res[1], dtype=np.int64).reshape(-1, 2)
    for (a, b), o in zip(E, res[4]):
        if o:
            onb.update((int(a), int(b)))
    if any(k not in vm for k in onb):
        try:
            bm.faces.new(bverts)
        except ValueError:
            pass
        return
    new = []
    for tri in T[inside]:
        vv = []
        for k in tri:
            k = int(k)
            if k not in vm:
                x, y = ov[k]
                vm[k] = bm.verts.new(place(x / sc, y))
                new.append(vm[k])
            vv.append(vm[k])
        try:
            bm.faces.new(vv)
        except ValueError:
            pass


def faceLoft(name, z, levels, tops, classes, h_body, sgn):
    # cylindrical gear with the teeth cut into a face (face gear): sections on cylinders r = levels[k]
    # about the axis, tops[k] = (height, phi) from -p/2 to p/2 with z = sgn * height, the body face at
    # z = sgn * h_body. inner and outer walls are the first and the last cylinder
    p = 2 * math.pi / z
    grid = gridAngles(-p / 2, p / 2, p / 16)
    bm = bmesh.new()
    T, B, M = [], [], []
    for r, top in zip(levels, tops):
        T.append([bm.verts.new((r * math.cos(f), r * math.sin(f), sgn * h)) for h, f in top])
        B.append([bm.verts.new((r * math.cos(f), r * math.sin(f), sgn * h_body)) for f in grid])
        M.append([(r * f, h) for h, f in top])
    for k in range(len(levels) - 1):
        tileStrip(bm, T[k], T[k + 1], classes[k] if classes else None,
                  classes[k + 1] if classes else None, (M[k], M[k + 1]))
        for i in range(len(grid) - 1):
            bm.faces.new((B[k][i], B[k][i + 1], B[k + 1][i + 1], B[k + 1][i]))
        bm.faces.new((B[k][0], B[k + 1][0], T[k + 1][0], T[k][0]))
        bm.faces.new((B[k][-1], T[k][-1], T[k + 1][-1], B[k + 1][-1]))
    for k in (0, len(levels) - 1):
        r = levels[k]
        top = tops[k]
        bnd = [(f, h_body) for f in grid] + [(f, h) for h, f in reversed(top)]
        bv = B[k] + list(reversed(T[k]))
        wallCDT(bm, bnd, bv, lambda u, v, r=r: (r * math.cos(u), r * math.sin(u), sgn * v), r,
                (p / 16, max(0.25 * (max(h for h, f in top) - h_body), 1e-6)))
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def elementMesh(name, z, module, width, tooth, r_in, r_out):
    # external cylindrical element between the bore r_in and the tip circle r_out
    if tooth and z * module / 2 - 1.25 * module <= r_in:
        raise LapError("the starter tooth does not fit: use more teeth or a smaller bore")
    p = 2 * math.pi / z
    top = toothOutline(z, module) if tooth else [(r_out, a) for a in gridAngles(-p / 2, p / 2, p / 16)]
    return spurElement(name, z, width, top, None, r_in)


# bevel gear: the gear frame has its origin in the cone apex and the gear body lies along +z.
# a point of the rim is given by its distance L from the apex and its direction (theta from the
# axis, phi around it). all tooth surfaces are cones through the apex (straight bevel), the face
# width runs along the generatrix from L_in to L_out, and the rim ends are spheres about the apex,
# so the ends of two meshing bevel gears lie on the same spheres and slide on each other.
# below the rim (from the neck cone theta_k on) the body is bounded by two planes normal to the axis
# and a cylinder: the bore of an external gear, the outer mantle of an internal one (pitch cone
# over 90 degrees: its teeth point toward the axis).

NECK = 1.75                   # neck cone below the pitch cone, in modules at the large end


def sphereDir(theta, phi):
    s = math.sin(theta)
    return Vector((s * math.cos(phi), s * math.sin(phi), math.cos(theta)))


def bevelBody(delta, module, l_in, l_out, theta_a, bore, clearance=0.25):
    # neck angle, inward (bore) or outward (mantle) body, cylinder radius
    theta_k = delta - max(NECK, 1.5 + clearance) * module / l_out
    if theta_k <= 0.02:
        raise LapError("the pitch cone is too narrow for the tooth depth: use more teeth")
    if math.cos(theta_k) > 0.05:
        r_max = l_in * math.sin(theta_k)
        # automatic bore: the wall at the small end of the neck stays 0.3 module thick (at most 0.875 of the rim)
        r = bore if bore > 0 else max(0.5 * r_max, min(0.875 * r_max, r_max - 0.3 * module))
        if r >= 0.95 * r_max:
            raise LapError("the bore reaches the rim: at most %.4g" % (0.95 * r_max))
        return theta_k, r
    s = 1.0 if theta_k < math.pi / 2 < theta_a else max(math.sin(theta_k), math.sin(theta_a))
    return theta_k, l_out * s + 2 * module


_EXACT = [True]               # bevel teeth by the formula (spherical involute); False: the old tredgold tooth


def sphInvTop(z, module, delta, l_out, clearance=0.25, alpha=20.0, twist_deg=0.0):
    # the tooth side of an external bevel gear as (theta, phi) from phi = -p/2 to p/2 and the classes of
    # its segments, by the formula: the flanks are spherical involutes (a great circle plane rolling on
    # the base cone, sin(delta_b) = sin(delta) cos(alpha)), the thickness p/4 on each side at the pitch
    # cone, tip and root cones at +m and -(1 + c) m along the generatrix (arc on the sphere of the
    # large end), a radial line below the base cone and a root fillet. no lapping is needed
    p = 2 * math.pi / z
    a0 = math.radians(alpha)
    sdb = math.sin(delta) * math.cos(a0)
    db = math.asin(sdb)
    cdb = math.cos(db)

    def inv(t):
        cg = min(1.0, math.cos(t) / cdb)
        g = math.acos(cg)
        return g / sdb - math.atan2(math.sin(g), cg * sdb)
    inv_p = inv(delta)

    def half(t):                       # half thickness of the tooth (angle phi) on the cone theta
        return p / 4 + inv_p - (inv(t) if t > db else 0.0)
    th_a = delta + module / l_out
    th_f = delta - (1.0 + clearance) * module / l_out
    if th_f <= 0.02:
        raise LapError("the pitch cone is too narrow for the tooth depth: use more teeth")
    # a tooth that would end in a point: the tip is cut lower (the mate has room: its root is deeper)
    tmin = 0.06 * p
    if half(th_a) < tmin:
        lo, hi = delta, th_a
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if half(mid) < tmin:
                hi = mid
            else:
                lo = mid
        th_a = lo
        if th_a - delta < 0.3 * module / l_out:
            raise LapError("the teeth come to a point: use more teeth")
    if half(max(th_f, db)) > 0.5 * p - 0.1 * p:
        raise LapError("the teeth are too thick at the root: use more teeth")
    sd = math.sin(delta)
    th_s = max(th_f, db)                 # the involute flank ends here
    nf = 2 if _LOW[0] else 10
    # the right flank from the tip down to th_s
    # the flank points spaced evenly in the turn of the tangent (equal dihedral angles of the facets)
    ts = [th_a + (th_s - th_a) * i / 400.0 for i in range(401)]
    xy = [(half(t) * math.sin(t), t - delta) for t in ts]
    ang = [math.atan2(xy[i + 1][1] - xy[i][1], xy[i + 1][0] - xy[i][0]) for i in range(400)]
    cum = [0.0]
    for i in range(1, 400):
        cum.append(cum[-1] + abs(ang[i] - ang[i - 1]))
    tot = cum[-1]
    if not _LOW[0]:
        # a twisted flank turns its facets more across the profile: finer by about 1 + tan(spiral angle); facets turn by about 3 degrees at most
        nf = max(nf, int(math.ceil(tot * (1.0 + 1.0 * math.tan(math.radians(abs(twist_deg)))) / math.radians(3.0))))
    right = []
    j = 0
    for i in range(nf + 1):
        want = tot * i / nf
        while j < 399 and cum[j + 1] < want:
            j += 1
        d = cum[j + 1] - cum[j] if j < 399 else 0.0
        f = (want - cum[j]) / d if d > 1e-15 else 0.0
        right.append((ts[j] + (ts[j + 1] - ts[j]) * min(1.0, max(0.0, f)), None))
    right[0] = (th_a, None)
    right[-1] = (th_s, None)
    right = [(t, half(t)) for t, _ in right]
    ncls = len(right) - 1                # flank segments
    if th_f < db - 1e-12:
        right.append((th_f, half(db)))   # radial line below the base cone
    # root fillet between the last segment and the floor (planar, in the units of the arc on the sphere)
    rho = 0.0 if _LOW[0] else 0.5 * clearance * module / l_out
    fl = []
    if rho > 0:
        Q, C = right[-2], right[-1]
        q = (Q[1] * sd, Q[0] - delta)
        c = (C[1] * sd, C[0] - delta)
        d1 = (c[0] - q[0], c[1] - q[1])
        ln = math.hypot(*d1)
        d1 = (d1[0] / ln, d1[1] / ln)
        turn = math.atan2(-d1[1], d1[0])                  # signed turn from d1 to the floor direction (1, 0)
        tl = abs(math.tan(abs(turn) / 2.0))
        r = min(rho, 0.9 * ln / tl if tl > 1e-9 else rho)
        t_len = r * tl
        if r > 1e-9 and abs(turn) > 1e-6:
            T1 = (c[0] - d1[0] * t_len, c[1] - d1[1] * t_len)
            sg = 1.0 if turn > 0 else -1.0
            nL = (-d1[1], d1[0])
            O = (T1[0] + sg * r * nL[0], T1[1] + sg * r * nL[1])
            nfil = 4
            for k in range(nfil + 1):
                a = sg * abs(turn) * k / nfil
                ca, sa = math.cos(a), math.sin(a)
                rx, ry = ca * nL[0] - sa * nL[1], sa * nL[0] + ca * nL[1]
                P = (O[0] - sg * r * rx, O[1] - sg * r * ry)
                fl.append((delta + P[1], P[0] / sd))
            right = right[:-1] + [(t, a) for t, a in fl]
            # the floor starts at the end of the fillet; it keeps the theta of the root cone
            right[-1] = (th_f, right[-1][1])
    if not fl:
        right.append((th_f, right[-1][1])) if abs(right[-1][0] - th_f) > 1e-12 else None
    # the floor from the end of the fillet to the sector side
    fl0 = right[-1][1]
    floor = [(th_f, a) for a in gridAngles(fl0, p / 2, p / 16)[1:]]
    right = right + floor
    left = [(t, -a) for t, a in reversed(right)]
    top = left + right
    # classes: the flanks (the first ncls segments from the tip) can work, the rest is plain
    cl_r = [CLS_FLANK if i < ncls else CLS_PLAIN for i in range(len(right) - 1)]
    cls = list(reversed(cl_r)) + [CLS_PLAIN] + cl_r
    return top, cls


def bevelTop(z, module, delta, l_out, tooth, clearance=0.25):
    # tooth side of the rim as (theta, phi) from phi = -p/2 to p/2. the starter tooth is either exact
    # (spherical involute, see sphInvTop) or, with _EXACT off, the involute of the virtual spur gear on
    # the back cone (tredgold) laid onto the sphere: depth along theta (normal to the pitch cone),
    # tooth width along phi (across the tooth line)
    p = 2 * math.pi / z
    if not tooth:
        return [(delta + module / l_out, a) for a in gridAngles(-p / 2, p / 2, p / 16)]
    if delta >= math.pi / 2 - 1e-6:
        raise LapError("the starter tooth is only for external bevel gears (pitch cone under 90 deg): "
                       "let the internal gear be the second one, it is made by lapping")
    if _EXACT[0]:
        return sphInvTop(z, module, delta, l_out, clearance)[0]
    zv = z / math.cos(delta)
    rpv = zv * module / 2
    src_ = lowTop(zv, module, False, clearance) if _LOW[0] else toothOutline(zv, module, clearance)
    return [(delta + (r - rpv) / l_out, a / math.cos(delta)) for r, a in src_]


def bevelElement(name, z, l_in, l_out, top, classes, theta_k, rc, ngon=False):
    # straight bevel element: the same outline (theta, phi) at every distance from the apex
    return bevelLoft(name, z, [l_in, l_out], [top, top], [classes, classes] if classes else None,
                     theta_k, rc, ngon=ngon)


def bevelLoft(name, z, levels, tops, classes, theta_k, rc, shifts=None, ngon=False):
    # shifts: per level a turn of the whole sector (twisted sector of a spiral gear: the same
    # outline on every sphere, joined by quads)
    # bevel element over several sphere sections: levels L_k from l_in to l_out, tops[k] = tooth
    # side (theta, phi) from phi = -p/2 to p/2 on the sphere L_k. the rim ends are caps on the first
    # and the last sphere (triangulated in the (phi, theta) plane, so any outline works, also an
    # undercut one). body: from the neck cone theta_k two planes normal to the axis and a cylinder
    # of radius rc. ngon: the exact tooth, the end caps are triangulated on their boundary points only (no inner grid)
    p = 2 * math.pi / z
    l_in, l_out = levels[0], levels[-1]
    for top in tops:
        if min(t for t, a in top) <= theta_k + 1e-9:
            raise LapError("the teeth reach below the neck of the rim")
    nk = 3 if _LOW[0] else 17
    neck = [-p / 2 + p * j / (nk - 1) for j in range(nk)]
    z_f = l_in * math.cos(theta_k)
    z_b = l_out * math.cos(theta_k)
    sc = math.sin(0.5 * (theta_k + max(t for top in tops for t, a in top)))

    def sideThetas(t_end):
        c = 0 if (_LOW[0] or ngon) else max(0, int(math.ceil((t_end - theta_k) / (p / 16))) - 1)
        return [theta_k + (t_end - theta_k) * i / (c + 1) for i in range(1, c + 1)]

    sh = shifts if shifts is not None else [0.0] * len(levels)
    bm = bmesh.new()
    caps = []
    for L, top, s0 in ((l_in, tops[0], sh[0]), (l_out, tops[-1], sh[-1])):
        sl = sideThetas(top[0][0])
        sr = sideThetas(top[-1][0])
        # boundary of the cap in the (phi, theta) plane: neck left to right, right side up, top
        # right to left, left side down
        bnd = [(f, theta_k) for f in neck] + [(p / 2, t) for t in sr] + \
              [(a, t) for t, a in reversed(top)] + [(-p / 2, t) for t in reversed(sl)]
        ring = [bm.verts.new(L * sphereDir(t, f + s0)) for f, t in bnd]
        nb = len(bnd)
        i_last = nk + len(sr)
        n = len(top)
        tv = [ring[i_last + (n - 1 - i)] for i in range(n)]                 # verts of top[i]
        left = [ring[nb - 1 - i] for i in range(len(sl))]                  # left side, upward
        right = [ring[nk + i] for i in range(len(sr))]
        caps.append((L, bnd, ring, tv, left, right, s0))
    # flanks: strips between neighbouring sections
    tvs = [caps[0][3]]
    for k in range(1, len(levels) - 1):
        tvs.append([bm.verts.new(levels[k] * sphereDir(t, a + sh[k])) for t, a in tops[k]])
    tvs.append(caps[1][3])
    metric = [[(a * sc, t) for t, a in top] for top in tops]
    for k in range(len(levels) - 1):
        tileStrip(bm, tvs[k], tvs[k + 1], classes[k] if classes else None,
                  classes[k + 1] if classes else None, (metric[k], metric[k + 1]), quads=shifts is not None)
    vin, vout = caps[0][2], caps[1][2]
    cols = []
    for f in neck:
        cb, sb = math.cos(f + sh[-1]), math.sin(f + sh[-1])
        cf, sf = math.cos(f + sh[0]), math.sin(f + sh[0])
        cols.append((bm.verts.new((rc * cb, rc * sb, z_b)), bm.verts.new((rc * cf, rc * sf, z_f))))
    for j in range(nk - 1):
        a0, b0 = cols[j]
        a1, b1 = cols[j + 1]
        bm.faces.new((vout[j], vout[j + 1], a1, a0))          # back plane
        bm.faces.new((a0, a1, b1, b0))                        # cylinder
        bm.faces.new((b0, b1, vin[j + 1], vin[j]))            # front plane
    # sector sides (planes through the axis), with the tooth corner of every section
    loops = []
    for base, side, end in ((0, 4, 0), (nk - 1, 5, -1)):
        loops.append([vin[base]] + caps[0][side] + [tv[end] for tv in tvs] + list(reversed(caps[1][side])) +
                     [vout[base], cols[base][0], cols[base][1]])
    if shifts is None or len(loops[0]) != len(loops[1]):
        for loop in loops:
            bm.faces.new(loop)
    else:
        # twisted sides are not plane: both triangulated alike (in distance from the apex and angle
        # from the axis), so that neighbouring elements meet face on face
        P2 = [Vector((v.co.length, math.atan2(math.hypot(v.co.x, v.co.y), v.co.z) * l_out)) for v in loops[0]]
        nl_ = len(P2)
        res = mgeom.delaunay_2d_cdt(P2, [(i, (i + 1) % nl_) for i in range(nl_)], [], 0, 1e-9 * l_out, True)
        ov, of, overts = res[0], res[2], res[3]
        ok = all(o and o[0] < nl_ for o in overts) and len(ov) == nl_
        if not ok:
            for loop in loops:
                bm.faces.new(loop)
        else:
            idx = [overts[k][0] for k in range(len(ov))]
            T = trisOf(of)
            Pn = np.array([(q.x, q.y) for q in P2])
            cen = np.array([[(ov[a][0] + ov[b][0] + ov[c][0]) / 3, (ov[a][1] + ov[b][1] + ov[c][1]) / 3]
                            for a, b, c in T])
            ins = insidePoly(cen, Pn)
            for (a, b, c), i_ in zip(T, ins):
                if not i_:
                    continue
                tri = (idx[a], idx[b], idx[c])
                for loop in loops:
                    try:
                        bm.faces.new([loop[q] for q in tri])
                    except ValueError:
                        pass
    # caps: constrained triangulation with a grid of inner points (the cap lies on a sphere)
    g = p / 16
    for L, bnd, ring, tv, left, right, s0 in caps:
        nb = len(bnd)
        pts = [Vector((f * sc, t)) for f, t in bnd]
        tmax = max(t for f, t in bnd)
        extra = [] if (_LOW[0] or ngon) else [(-p / 2 + ix * g, theta_k + iy * g) for ix in range(1, 16)
                                    for iy in range(1, int((tmax - theta_k) / g) + 1)]
        allp = pts + [Vector((f * sc, t)) for f, t in extra]
        # full triangulation with the boundary as constraint edges; the triangles inside are
        # picked by their centres (the face flags differ between blender versions)
        res = mgeom.delaunay_2d_cdt(allp, [(i, (i + 1) % nb) for i in range(nb)], [], 0, 1e-12 * sc * 10, True)
        ov, of, overts = res[0], res[2], res[3]
        V = np.array([(v[0], v[1]) for v in ov])
        T = trisOf(of)
        inside = insidePoly(V[T].mean(axis=1), np.array([(q[0], q[1]) for q in pts]))
        vm = {}
        for k, orig in enumerate(overts):
            if orig and orig[0] < nb:
                vm[k] = ring[orig[0]]
        onb = set()
        for (a, b), o in zip(res[1], res[4]):
            if o:
                onb.update((int(a), int(b)))
        if any(k not in vm for k in onb):
            # the outline touches itself: the cap as one polygon
            try:
                bm.faces.new(ring)
            except ValueError:
                pass
            continue
        for tri in T[inside]:
            vs = []
            for k in tri:
                k = int(k)
                if k not in vm:
                    x, t = ov[k]
                    vm[k] = bm.verts.new(L * sphereDir(t, x / sc + s0))
                vs.append(vm[k])
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def bevelAngles(z1, z2, shaft_deg):
    # pitch cone half angles of a pair with this shaft angle
    s = math.radians(shaft_deg)
    d1 = math.atan2(math.sin(s), z2 / float(z1) + math.cos(s))
    return d1, s - d1


def rackCutter(module, clearance, alpha=20.0, teeth=7, nf=10):
    # the basic rack of gost 13755 as a cutter: pressure angle alpha, addendum of the cutter (the
    # dedendum of the gear) (1 + c*) m, tip rounded with the largest fillet c* m / (1 - sin alpha)
    # (0.38 m for c* = 0.25). pitch line x = 0, teeth pointing to -x, a tooth centred on y = 0 and
    # the others every pi m; a closed outline, the back at x = 3 m
    ta = math.tan(math.radians(alpha))
    ca = math.cos(math.radians(alpha))
    sa = math.sin(math.radians(alpha))
    pl = math.pi * module
    hf = (1.0 + clearance) * module
    rho = clearance * module / (1.0 - sa) if clearance > 0 else 0.0
    xt = -hf                                   # tip line
    xc = xt + rho                              # fillet centres

    def half(x):                               # half thickness of the cutter tooth at x
        return pl / 4 + x * ta
    yc = half(xc) - rho / ca                   # fillet centre, tangent to the flank
    # one tooth from its left flank top over the tip to the right flank top (y from - to +)
    xh = 1.5 * module                          # flank tops, above the gear tips (x = m)
    tooth = [(xh, -half(xh))]
    # left fillet: from the flank tangent point (direction 3 pi / 2 - alpha from the centre) to the
    # tip line (direction pi); the right one mirrored
    pts_l = []
    for i in range(nf + 1):
        th = (math.pi * 1.5 - math.radians(alpha)) * (1 - i / nf) + math.pi * (i / nf)
        pts_l.append((xc + rho * math.cos(th), -yc + rho * math.sin(th)))
    tooth += pts_l
    tooth += [(x, -y) for x, y in reversed(pts_l)]
    tooth.append((xh, half(xh)))
    out = []
    for k in range(-(teeth // 2), teeth // 2 + 1):
        out += [(x, y + k * pl) for x, y in tooth]
    # close over the back
    out.append((3 * module, out[-1][1]))
    out.append((3 * module, out[0][1]))
    return out, rho


def toothOutline(z, module, clearance=0.25):
    # starter tooth as the gost 13755 basic rack generates it (a hob or a rack cutter): involute
    # flanks, 20 deg, addendum 1 m, dedendum (1 + c*) m, and the root fillets the rounded rack tip
    # cuts (trochoids; also the undercut of few teeth), as (radius, angle) from angle -p/2 to p/2.
    # z may be fractional (the virtual gear of a bevel gear). the rack rolls on the pitch circle in
    # small steps, every position subtracted exactly from a sector of the blank
    p = 2 * math.pi / z
    rp = z * module / 2
    ra = rp + module
    rf = rp - (1.0 + clearance) * module
    if rf <= 0.2 * rp:
        raise LapError("the starter tooth does not fit: use more teeth")
    r_in = max(0.05 * rp, rf - module)
    cutter, rho = rackCutter(module, clearance)
    # the blank: the sector -p/2 .. p/2 between r_in and the tip circle
    arc = gridAngles(-p / 2, p / 2, p / 64)
    blank = [(r_in * math.cos(a), r_in * math.sin(a)) for a in reversed(arc)] + \
            [(ra * math.cos(a), ra * math.sin(a)) for a in arc]
    blank = blank[::-1] if area2(blank) < 0 else blank
    attrs = [('T', 0)] * len(blank)
    # tooth spaces at +-p/2: the rack teeth at y = +-pi m / 2 with the rack at rest; the gear turns
    # by phi, the rack moves by rp phi along y (rolling on the pitch circle)
    C = np.array(cutter)
    C[:, 0] += rp
    C[:, 1] += math.pi * module / 2
    nstep = 300
    span = 2.2 * math.pi * module / rp
    polys = []
    for i in range(nstep + 1):
        phi = -span + 2 * span * i / nstep
        c, s_ = math.cos(-phi), math.sin(-phi)
        X = C[:, 0]
        Y = C[:, 1] + rp * phi
        P = np.column_stack([c * X - s_ * Y, s_ * X + c * Y])
        polys.append(((i,), [tuple(q) for q in P]))
    lp, at = blank, attrs
    c = 0
    while c < len(polys):
        c1, nv = c, 0
        while c1 < len(polys) and (c1 == c or nv + len(polys[c1][1]) <= 3000):
            nv += len(polys[c1][1])
            c1 += 1
        lp, at = subtract2d(lp, at, polys[c:c1], 0.0)
        c = c1
        lp, at = dropCollinear(lp, at, 1e-9 * module)
    # the tooth side: the outline above the inner arc, from the -p/2 side to the +p/2 side
    pol = [(math.hypot(x, y), math.atan2(y, x)) for x, y in lp]
    n = len(pol)
    inner = [abs(r - r_in) < 1e-5 * module for r, a in pol]
    i0 = next(i for i in range(n) if inner[i] and not inner[(i + 1) % n])
    seq = [pol[(i0 + 1 + k) % n] for k in range(n)]
    seq = [q for q in seq if abs(q[0] - r_in) > 1e-5 * module]
    if seq[0][1] > seq[-1][1]:
        seq = seq[::-1]
    # the points on the sector sides: only the topmost (the side runs down to the inner arc)
    while len(seq) > 1 and abs(seq[1][1] + p / 2) < 1e-9 and abs(seq[0][1] + p / 2) < 1e-9:
        seq.pop(0)
    while len(seq) > 1 and abs(seq[-2][1] - p / 2) < 1e-9 and abs(seq[-1][1] - p / 2) < 1e-9:
        seq.pop()
    # fewer points: the scallops of the steps are far below this tolerance
    keep = douglasPeucker([(r * math.cos(a), r * math.sin(a)) for r, a in seq], 2e-4 * module)
    top = [seq[i] for i in keep]
    top[0] = (top[0][0], -p / 2)
    top[-1] = (top[-1][0], p / 2)
    return top


def _autoBore(z, module):
    rp = z * module / 2
    return max(0.3 * rp, rp - 3.0 * module)


def defaultBore(z, module):
    # the bore of a new gear: the shaft seat of the creating operator when one is set, else a wide bore
    return seatBore(_autoBore(z, module))


# ---------------------------------------------------------------------------
# shaft seats and fdm printing. a gear's sectors keep a round bore; a seat other than a plain circle
# (d-shaft, square, pentagon, hexagon, lego cross, none) is a ring of its own under the gear empty that
# fills the bore down to the shaft shape (child "<gear>_seat"). the printable copy and the stl unite it
# with the teeth (a ring grown a little into the gear body, so the walls do not lie on each other).
# fdm: line width 1.125 nozzle; a downward face may lean from the vertical by atan(line / 2 / layer)
# (half a line of shift per layer): 48 deg at 0.2 mm, 66 at 0.1, 37 at 0.3 with a 0.4 nozzle
# ---------------------------------------------------------------------------

_SEAT = [None]           # the seat of the operator that is creating gears now (dict), else None
SEAT_WALL = 1.0          # the round bore of the sectors at least this far outside the seat shape
LEGO_D, LEGO_W = 4.8, 1.8


def fdmParams():
    # (line width, layer height, overhang limit in degrees from the vertical)
    try:
        ps = bpy.context.scene.lap
        nozzle, layer = float(ps.fdm_nozzle), float(ps.fdm_layer)
    except Exception:
        nozzle, layer = 0.4, 0.2
    lw = 1.125 * nozzle
    return lw, layer, min(75.0, math.degrees(math.atan2(0.5 * lw, max(layer, 1e-6))))


def seatSpec(ps):
    return {'shape': ps.seat_shape, 'd': float(ps.seat_d), 'flat': float(ps.seat_flat), 'fit': float(ps.seat_fit)}


def seatOutline(spec, low=False):
    # the hole of the seat (x, y) counter clockwise, the fit clearance included; None: no hole.
    # convex corners of the shaft are rounded by the fit (the outline is the shaft grown by it)
    shape, d, flat, c = spec['shape'], spec['d'], spec['flat'], max(0.0, spec['fit'])
    n = 16 if low else 64
    if shape == 'NONE':
        return None
    if shape == 'ROUND':
        r = d / 2 + c
        return [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    if shape == 'D':
        r = d / 2 + c
        xf = d / 2 - flat + c
        if flat <= 0 or xf <= -r * 0.5:
            raise LapError("d-shaft: the flat must be deeper than 0 and leave at least half the shaft")
        a0 = math.acos(max(-1.0, min(1.0, xf / r)))
        k = max(4, int(n * (2 * math.pi - 2 * a0) / (2 * math.pi)))
        return [(r * math.cos(a0 + (2 * math.pi - 2 * a0) * i / k), r * math.sin(a0 + (2 * math.pi - 2 * a0) * i / k))
                for i in range(k + 1)]
    if shape in ('SQUARE', 'PENT', 'HEX'):
        ns = {'SQUARE': 4, 'PENT': 5, 'HEX': 6}[shape]
        rv = d / 2 / math.cos(math.pi / ns)              # d: across the flats (twice the inscribed radius)
        pts = []
        seg = 1 if low else 4
        for k in range(ns):
            va = (2 * k + 1) * math.pi / ns              # flats face 0, 2 pi / ns, ... (one flat towards +x)
            vx, vy = rv * math.cos(va), rv * math.sin(va)
            if c <= 1e-9:
                pts.append((vx, vy))
                continue
            for j in range(seg + 1):
                phi = 2 * math.pi * k / ns + (2 * math.pi / ns) * j / seg
                pts.append((vx + c * math.cos(phi), vy + c * math.sin(phi)))
        return pts
    if shape == 'CROSS':
        R, hw = LEGO_D / 2 + c, LEGO_W / 2 + c
        al = math.asin(hw / R)
        pts = []
        na = 2 if low else 6
        for k in range(4):
            b = k * math.pi / 2
            pts += [(R * math.cos(b - al + 2 * al * i / na), R * math.sin(b - al + 2 * al * i / na)) for i in range(na + 1)]
            cb, sb = math.cos(b), math.sin(b)
            pts.append((hw * cb - hw * sb, hw * sb + hw * cb))
        return pts
    raise LapError("unknown seat shape %s" % shape)


def seatRadius(spec):
    o = seatOutline(spec)
    return 0.0 if o is None else max(math.hypot(x, y) for x, y in o)


def seatRoundBore():
    # the bore radius of a new bevel gear for the seat: the seat circle itself (round seat), for other shapes
    # wide enough that the seat ring fits in it; 0 = its own default
    s = _SEAT[0]
    if s is None or s['shape'] == 'NONE':
        return 0.0
    if s['shape'] == 'ROUND':
        return s['d'] / 2 + max(0.0, s['fit'])
    return seatRadius(s) + SEAT_WALL


def bodyRadius(g):
    # the radius of the bore of the sectors: the body of a bevel gear is cut by a cylinder of lap_rc
    return float(g["lap_rc"]) if g.get("lap_kind") == 'BEVEL' else float(g["lap_rbody"])


def seatBore(auto_r):
    # the round bore of the sectors of a new gear: the seat circle itself, or for other seats wide
    # enough that the seat ring fits in it
    s = _SEAT[0]
    if s is None:
        return auto_r
    if s['shape'] == 'ROUND':
        return s['d'] / 2 + max(0.0, s['fit'])
    if s['shape'] == 'NONE':
        return auto_r
    return max(auto_r, seatRadius(s) + SEAT_WALL)


def seatChild(gear):
    for c in gear.children:
        if c.get("lap_seat"):
            return c
    return None


def seatSpecOf(gear):
    return {'shape': gear.get("lap_seat_shape", 'ROUND'), 'd': float(gear.get("lap_seat_d", 5.0)),
            'flat': float(gear.get("lap_seat_flat", 0.5)), 'fit': float(gear.get("lap_seat_fit", 0.0))}


def seatMesh(name, spec, r_out, z0, z1, n_out):
    # the seat ring: a circle r_out round the hole of the seat (or a disc without one), extruded from z0
    # to z1. the hole is star shaped about the axis, so the ends are strips between the two loops in the
    # order of their angles (no triangulation library: the same in every blender)
    hole = seatOutline(spec, _LOW[0])
    outer = [(r_out * math.cos(2 * math.pi * i / n_out), r_out * math.sin(2 * math.pi * i / n_out)) for i in range(n_out)]
    bm = bmesh.new()
    O0 = [bm.verts.new((x, y, z0)) for x, y in outer]
    O1 = [bm.verts.new((x, y, z1)) for x, y in outer]
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((O0[i], O0[j], O1[j], O1[i]))
    if hole is None:
        bm.faces.new(O0)
        bm.faces.new(O1[::-1])
    else:
        if area2(hole) < 0:
            hole = hole[::-1]
        # both loops from the angle nearest -pi on, counter clockwise
        k0 = min(range(len(hole)), key=lambda i: math.atan2(hole[i][1], hole[i][0]))
        hole = hole[k0:] + hole[:k0]
        m_ = len(hole)
        I0 = [bm.verts.new((x, y, z0)) for x, y in hole]
        I1 = [bm.verts.new((x, y, z1)) for x, y in hole]
        for i in range(m_):
            j = (i + 1) % m_
            bm.faces.new((I0[i], I1[i], I1[j], I0[j]))
        ao = [math.atan2(y, x) for x, y in outer]
        ai = [math.atan2(y, x) for x, y in hole]
        k1 = min(range(n), key=lambda i: ao[i])
        oidx = [(k1 + i) % n for i in range(n)]
        unwrap = lambda a_, base: a_ if a_ >= base - 1e-12 else a_ + 2 * math.pi
        base = min(ao[oidx[0]], ai[0])
        A_o = [unwrap(ao[i], base) for i in oidx] + [unwrap(ao[oidx[0]], base) + 2 * math.pi]
        A_i = [unwrap(a_, base) for a_ in ai] + [unwrap(ai[0], base) + 2 * math.pi]
        for V_o, V_i, up in ((O0, I0, False), (O1, I1, True)):
            i = j = 0
            while i < n or j < m_:
                adv_o = j >= m_ or (i < n and A_o[i + 1] <= A_i[j + 1])
                a_o, a_i = V_o[oidx[i % n]], V_i[j % m_]
                if adv_o:
                    tri = (a_o, V_o[oidx[(i + 1) % n]], a_i)
                    i += 1
                else:
                    tri = (a_o, V_i[(j + 1) % m_], a_i)
                    j += 1
                bm.faces.new(tri[::-1] if up else tri)
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def offsetOf(gear):
    # the print offset made in the pieces of the gear (0: none)
    return float(gear.get("lap_offset") or 0.0)


def seatGrow(gear):
    # how far the printed seat ring reaches into the gear body: 0.4 of the way to the next radius of the
    # sectors (the tooth roots), at most 1. the bore of the sectors is wider by the print offset
    r0 = bodyRadius(gear) + offsetOf(gear)
    V = np.empty(len(gearMesh(gear).vertices) * 3)
    gearMesh(gear).vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    R = np.hypot(V[:, 0], V[:, 1])
    # the next radius above the bore: not the bore itself (its points differ by the rounding of single floats and of
    # the offset, a few 1e-6, and then the ring would not reach into the body at all)
    R = R[R > r0 + 2e-4 * max(r0, 1.0)]
    if not len(R):
        return 0.0
    return min(1.0, 0.4 * (float(R.min()) - r0))


def seatSolidBM(gear, grow=True):
    # the seat ring of the gear as a closed bmesh in the gear frame (grown into the body for the union)
    ch = seatChild(gear)
    spec = seatSpecOf(gear)
    spec['fit'] += offsetOf(gear)                    # the hole of the seat is wider by the print offset
    z0, z1 = float(gear["lap_seat_z0"]), float(gear["lap_seat_z1"])
    r_out = bodyRadius(gear) + offsetOf(gear) + (seatGrow(gear) if grow else 0.0)
    n = max(64, 16 * int(gear["lap_teeth"]))
    me = seatMesh("LAP_seat_tmp", spec, r_out, z0, z1, n)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    return bm


def addSeat(context, g, spec, report):
    # the seat ring for a new gear (round seats need none: the sectors' bore is the seat)
    g["lap_seat_shape"] = spec['shape']
    g["lap_seat_d"] = spec['d']
    g["lap_seat_flat"] = spec['flat']
    g["lap_seat_fit"] = spec['fit']
    if spec['shape'] == 'ROUND':
        return None
    if g.get("lap_internal") or isRack(g) or g.get("lap_part"):
        return None
    r0 = bodyRadius(g)
    off = offsetOf(g)
    spec_e = dict(spec, fit=spec['fit'] + off)
    rc = seatRadius(spec_e)
    if rc >= r0 + off - 0.2:
        raise LapError("the shaft seat (%.3g across its corners) does not fit in '%s' (body radius %.3g)"
                       % (2 * rc, g.name, r0))
    if isBevel(g):
        # the body between the two planes normal to the axis under the neck cone (the teeth reach beyond the
        # front plane): the ring runs from plane to plane
        th = float(g["lap_neck"])
        z0, z1 = float(g["lap_lin"]) * math.cos(th), float(g["lap_lout"]) * math.cos(th)
    else:
        z0, z1 = axialRange(g, gearFrame(g).inverted())
    g["lap_seat_z0"], g["lap_seat_z1"] = float(z0), float(z1)
    z = int(g["lap_teeth"])
    n = max(64, (16 if not _LOW[0] else 4) * z)
    me = seatMesh(g.name + "_seat_mesh", spec_e, r0 + off, z0, z1, n)
    ob = bpy.data.objects.new(g.name + "_seat", me)
    (g.users_collection[0] if g.users_collection else context.collection).objects.link(ob)
    ob.parent = g
    ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Identity(4)
    ob.lock_location = ob.lock_rotation = ob.lock_scale = (True, True, True)
    ob["lap_seat"] = 1
    return ob


def seatRebuild(gear):
    # the mesh of the seat ring again, after the print offset of the pieces changed
    ch = seatChild(gear)
    if ch is None or "lap_seat_z0" not in gear:
        return
    spec = seatSpecOf(gear)
    off = offsetOf(gear)
    spec['fit'] += off
    n = max(64, (16 if not _LOW[0] else 4) * int(gear["lap_teeth"]))
    me = seatMesh(gear.name + "_seat_mesh", spec, bodyRadius(gear) + off,
                  float(gear["lap_seat_z0"]), float(gear["lap_seat_z1"]), n)
    old = ch.data
    ch.data = me
    if old is not None and old.users == 0:
        bpy.data.meshes.remove(old)


def seatRings(context, objs, report):
    # seat rings for the gears among new objects (with their children)
    spec = _SEAT[0]
    if spec is None:
        return 0
    n = 0
    for o in objs:
        for g in [o] + list(o.children_recursive):
            if isGear(g) and not g.get("lap_part") and elements(g):
                if addSeat(context, g, spec, report) is not None:
                    n += 1
    return n


def bmUnion(bm_a, bm_b, m):
    # union of two closed bmeshes by the boolean modifier (manifold solver); a new bmesh
    coll = bpy.data.collections.new("LAP_union_tmp")
    bpy.context.scene.collection.children.link(coll)
    objs = []
    try:
        for i, b0 in enumerate((bm_a, bm_b)):
            # triangles in, points on one spot joined: the manifold solver takes nothing less
            b = b0.copy()
            bmesh.ops.triangulate(b, faces=list(b.faces), quad_method='BEAUTY', ngon_method='BEAUTY')
            bmesh.ops.remove_doubles(b, verts=list(b.verts), dist=1e-7 * m)
            me = bpy.data.meshes.new("LAP_u%d" % i)
            b.to_mesh(me)
            b.free()
            ob = bpy.data.objects.new(me.name, me)
            coll.objects.link(ob)
            objs.append(ob)
        mod = objs[0].modifiers.new("union", 'BOOLEAN')
        mod.operation = 'UNION'
        mod.operand_type = 'OBJECT'
        mod.object = objs[1]
        mod.solver = 'MANIFOLD'
        dg = bpy.context.evaluated_depsgraph_get()
        ev = objs[0].evaluated_get(dg)
        out = bmesh.new()
        out.from_mesh(ev.to_mesh())
        ev.to_mesh_clear()
    finally:
        for ob in objs:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        bpy.data.collections.remove(coll)
    va, vb, vo = bm_a.calc_volume(signed=True), bm_b.calc_volume(signed=True), out.calc_volume(signed=True)
    if vo < max(va, vb) - 1e-6 * max(abs(va), abs(vb), 1.0) or abs(vo - va) < 1e-9 * max(abs(va), 1.0):
        out.free()
        raise LapError("the union with the shaft seat failed (the boolean solver refused the meshes)")
    bmesh.ops.remove_doubles(out, verts=list(out.verts), dist=1e-6 * m)
    # the union cuts the flat ends into slivers along its seam: merged back into whole faces (flat
    # neighbours only), so the offset and the chamfer see clean ends
    bmesh.ops.dissolve_degenerate(out, dist=1e-5 * m, edges=list(out.edges))
    bmesh.ops.dissolve_limit(out, angle_limit=math.radians(0.05), use_dissolve_boundaries=False,
                             verts=list(out.verts), edges=list(out.edges))
    bmesh.ops.triangulate(out, faces=[f for f in out.faces if len(f.verts) > 4], quad_method='BEAUTY',
                          ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(out, faces=list(out.faces))
    if out.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(out, faces=list(out.faces))
    out.normal_update()
    return out


def overhangCheck(bm, report, name, chamfer=0.0):
    # faces that lean further from the vertical than the layer height allows, the part printed as it
    # lies (lowest end on the bed) and upside down; the bed face and the chamfer above it left out.
    # a flat ceiling held by walls below it on at least half its rim and at most 15 wide (2 area /
    # rim) is a bridge (a groove under a flange), a ledge narrower than two lines is nothing: counted apart
    lw, layer, th = fdmParams()
    s = math.sin(math.radians(th))
    bm.normal_update()
    zs = [v.co.z for v in bm.verts]
    if not zs:
        return
    z0, z1 = min(zs), max(zs)
    band = 1.5 * chamfer + 1e-4
    flat_s = math.sin(math.radians(88.0))

    c45 = math.sin(math.radians(45.0))

    def chamf(f):
        # a face of the end chamfer (45 deg, less where the bevel was clamped): no higher than the chamfer,
        # a layer or two, it prints at any layer height
        if chamfer <= 0 or not (0.3 < abs(f.normal.z) < 0.97):
            return False
        zz = [v.co.z for v in f.verts]
        return max(zz) - min(zz) <= 1.01 * chamfer + 1e-6

    def area(sg):
        steep, flat = 0.0, set()
        base = z0 if sg > 0 else -z1
        for f in bm.faces:
            nz = f.normal.z * sg
            if nz >= -s - 1e-9 or f.calc_area() < 1e-12 or chamf(f):
                continue
            if max(v.co.z * sg for v in f.verts) <= base + band:
                continue
            if nz < -flat_s:
                flat.add(f)
            else:
                steep += f.calc_area()
        bridge = hang = 0.0
        seen = set()
        for f0 in flat:
            if f0 in seen:
                continue
            reg, stack = [], [f0]
            seen.add(f0)
            while stack:
                f = stack.pop()
                reg.append(f)
                for e in f.edges:
                    for g in e.link_faces:
                        if g in flat and g not in seen:
                            seen.add(g)
                            stack.append(g)
            regset = set(reg)
            a_ = sum(f.calc_area() for f in reg)
            rim = held = 0.0
            for f in reg:
                for e in f.edges:
                    others = [g for g in e.link_faces if g not in regset]
                    if not others:
                        continue
                    ln = e.calc_length()
                    rim += ln
                    g = others[0]
                    ez = 0.5 * (e.verts[0].co.z + e.verts[1].co.z) * sg
                    if (g.normal.z * sg >= -s - 1e-9 or chamf(g)) and g.calc_center_median().z * sg < ez - 1e-6:
                        held += ln
            if rim > 0 and ((held >= 0.5 * rim and 2 * a_ / rim <= 15.0) or 2 * a_ / rim < 2 * lw):
                bridge += a_
            else:
                hang += a_
        return steep + hang, bridge
    (up, br_up), (down, br_down) = area(1.0), area(-1.0)
    line = ("overhang of '%s' (layer %.3g, line %.3g: faces may lean %.0f deg from the vertical): %.3g mm2 as it "
            "lies, %.3g mm2 upside down; short bridges %.3g / %.3g mm2" % (name, layer, lw, th, up, down, br_up,
                                                                            br_down))
    if up > 0.5:
        better = " - print it upside down" if down < 0.5 * up else ""
        both = " (both ways: a plate over a hub or a step needs supports, or a hub on one side only)" if down >= 0.5 * up and up > 20 else ""
        report.append("WARNING: " + line + better + both + " (or with supports / a smaller layer)")
    else:
        report.append(line)
    return up, down


def meshCheck(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    open_edges = sum(1 for e in bm.edges if not e.is_manifold)
    vol = bm.calc_volume(signed=True)
    bm.free()
    return open_edges, vol


# ---------------------------------------------------------------------------
# gears: empty + linked elements
# ---------------------------------------------------------------------------

def isGear(obj):
    return obj is not None and obj.type == 'EMPTY' and "lap_teeth" in obj


def elements(gear):
    els = [c for c in gear.children if "lap_index" in c]
    els.sort(key=lambda o: o["lap_index"])
    return els


def gearMesh(gear):
    els = elements(gear)
    if not els:
        raise LapError("gear '%s' has no elements" % gear.name)
    me = els[0].data
    if _ENG['on'] and gear.get("lap_kind") != 'RACK' and meshIsOpen(me):
        ent = _ENG['cache'].get(me.name)
        if ent is None:
            z, m = int(gear["lap_teeth"]), sizeModule(gear)
            t = closedTemp(me, z, m)
            ent = (me, t, meshSnapshot(t), z, m)
            _ENG['cache'][me.name] = ent
        return ent[1]
    return me


def counterNext(key, prop):
    # numbers are never used twice in a file: the scene keeps the last one (a deleted gear or pair
    # does not free its number, its printable copies still carry it)
    sc = bpy.context.scene
    n = int(sc.get(key, 0))
    for o in bpy.data.objects:
        if prop in o:
            n = max(n, int(o[prop]))
    sc[key] = n + 1
    return n + 1


def nextNumber():
    return counterNext("lap_last_gear", "lap_no")


def fmtM(m):
    return "%g" % round(float(m), 4)


def renameGear(g, name):
    # the empty, its elements and their mesh
    g.name = name
    els = elements(g)
    if els:
        els[0].data.name = g.name + "_mesh"
    for k, el in enumerate(els):
        el.name = "%s_e%03d" % (g.name, k + 1)
    for c in g.children:
        if c.get("lap_seat"):
            c.name = g.name + "_seat"
            if c.data is not None:
                c.data.name = g.name + "_seat_mesh"


def makeGear(context, z, me, matrix, module, width, internal, bevel=None, prefix="gear", unit="tooth", strip=True):
    # bevel = (delta, l_in, l_out) for a bevel gear (frame origin in the cone apex)
    no = nextNumber()
    # a worm is named worm_<n>_<starts>_start, its wheel wormwheel_<n>_<teeth>_tooth
    name = "%s_%d_%d_%s_m%s" % (prefix, no, z, unit, fmtM(module))
    gear = bpy.data.objects.new(name, None)
    gear.empty_display_type = 'SINGLE_ARROW'
    gear["lap_no"] = no
    gear["lap_teeth"] = int(z)
    gear["lap_module"] = float(module)
    gear["lap_width"] = float(width)
    gear["lap_internal"] = bool(internal)
    if bevel is None:
        gear["lap_kind"] = 'SPUR'
        gear.empty_display_size = z * module / 2 + 2 * module
    else:
        gear["lap_kind"] = 'BEVEL'
        gear["lap_delta"] = math.degrees(bevel[0])
        gear["lap_lin"] = float(bevel[1])
        gear["lap_lout"] = float(bevel[2])
        gear.empty_display_size = bevel[2] * 1.1
    context.collection.objects.link(gear)
    gear.matrix_world = matrix
    me.name = name + "_mesh"
    for k in range(z):
        el = bpy.data.objects.new("%s_e%03d" % (name, k + 1), me)
        el["lap_index"] = k
        context.collection.objects.link(el)
        el.parent = gear
        el.matrix_parent_inverse = Matrix.Identity(4)
        el.matrix_basis = rotZ(2 * math.pi * k / z)
        el.lock_location = (True, True, True)
        el.lock_rotation = (True, True, True)
        el.lock_scale = (True, True, True)
    if strip:
        # the sector sides ('meridian faces') are not part of the pieces: they meet once joined
        stripSides(me, z, module)
    return gear


def setStarts(gear, z):
    # a worm given another number of starts: z elements of its mesh, turned by 2 pi / z, and the name
    me = gearMesh(gear)
    els = elements(gear)
    coll = els[0].users_collection[0] if els[0].users_collection else bpy.context.collection
    for el in els[z:]:
        bpy.data.objects.remove(el, do_unlink=True)
    no = int(gear.get("lap_no", 0))
    gear.name = "worm_%d_%d_start_m%s" % (no, z, fmtM(sizeModule(gear)))
    me.name = gear.name + "_mesh"
    els = elements(gear)
    for k in range(z):
        if k < len(els):
            el = els[k]
        else:
            el = bpy.data.objects.new("x", me)
            el["lap_index"] = k
            coll.objects.link(el)
            el.parent = gear
            el.matrix_parent_inverse = Matrix.Identity(4)
            el.lock_location = (True, True, True)
            el.lock_rotation = (True, True, True)
            el.lock_scale = (True, True, True)
        el.name = "%s_e%03d" % (gear.name, k + 1)
        el.matrix_basis = rotZ(2 * math.pi * k / z)
    gear["lap_teeth"] = int(z)


def removeGear(gear):
    me = gearMesh(gear)
    for c in [c for c in gear.children if c.get("lap_seat")]:
        sm = c.data
        bpy.data.objects.remove(c, do_unlink=True)
        if sm is not None and sm.users == 0:
            bpy.data.meshes.remove(sm)
    for el in elements(gear):
        bpy.data.objects.remove(el, do_unlink=True)
    bpy.data.objects.remove(gear, do_unlink=True)
    if me.users == 0:
        bpy.data.meshes.remove(me)


def selectOnly(context, obj):
    for o in context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def gearFrame(gear):
    # rotation frame without scale; local z = axis
    loc, rot, sca = gear.matrix_world.decompose()
    return Matrix.Translation(loc) @ rot.to_matrix().to_4x4()


def sizeModule(gear):
    # the module as a size of the teeth (tolerances, relief, clearance): a worm stores the module of
    # its pitch radius (q m / starts), its teeth have the axial module
    if gear.get("lap_worm"):
        return float(gear.get("lap_axial_module", 1.0))
    return float(gear.get("lap_module", 1.0))


def isBevel(gear):
    return gear.get("lap_kind") == 'BEVEL'


def isRack(g):
    return g is not None and g.get("lap_kind") == 'RACK'


def checkRotary(g, what="lapping"):
    if isRack(g):
        raise LapError("'%s' is a rack: %s works on gears that turn about an axis" % (g.name, what))


def checkVersion(gear):
    if "lap_kind" not in gear and float(gear.get("lap_cone", 0.0)) > 0:
        raise LapError("'%s' is a conical gear of version 0.4 (flat ends, profile in the wrong plane): "
                       "create it again" % gear.name)


def newBevelGear(context, z, module, delta, width, tooth, bore, matrix, clearance=0.25, spiral=0.0, herring=False,
                 spiral_in=None, ushape=False, apex=0.0):
    # bevel gear with the apex at matrix; width runs along the generatrix, module is at the large end
    l_out = z * module / 2 / math.sin(delta)
    if width >= 0.8 * l_out:
        raise LapError("face width %.4g is too large for a cone distance of %.4g (at most a third is usual)"
                       % (width, l_out))
    l_in = l_out - width
    return bevelGear(context, z, module, delta, l_in, l_out, tooth, bore, matrix, clearance, spiral, herring,
                     spiral_in, ushape, 0.5 * (l_in + l_out) + apex)


def bevelTwist(delta, spiral_deg, lmid, herring=False, spiral_in=None, ushape=False, l_in=None, l_out=None):
    # turn of the sections of a spiral bevel gear about its axis at the cone distance L: the tooth
    # line on the crown gear is a logarithmic spiral (the same spiral angle everywhere),
    # d theta_c / dL = tan b / L, and the gear turns by theta_c / sin(delta); zero at lmid
    # herringbone: two halves of opposite hand meeting at lmid (the apex of the chevron): |ln|.
    # V: the angle of the inner half (L < lmid) may differ: spiral_in (None = the same as the outer one; 0 a
    # straight inner half; positive: mirrored to the outer half, a chevron; negative: the same hand, a spiral).
    # U (ushape): no kink, the turn is c ln^2(L / lmid), the spiral angle grows from 0 at the apex
    # as tan b(L) = 2 c sin(delta) ln(L / lmid); spiral_deg is the angle at the end farther from
    # the apex (the curvature of the U follows from it), l_in and l_out are needed for that
    sd = math.sin(delta)
    t = math.tan(math.radians(spiral_deg)) / sd
    if herring and ushape:
        umax = max(abs(math.log(l_out / lmid)), abs(math.log(l_in / lmid)))
        c = t / (2.0 * umax)
        return lambda L: c * math.log(L / lmid) ** 2
    if herring:
        t_in = t if spiral_in is None else math.tan(math.radians(spiral_in)) / sd
        return lambda L: t * math.log(L / lmid) if L >= lmid else -t_in * math.log(L / lmid)
    return lambda L: t * math.log(L / lmid)


def twistOf(g):
    # the turn function of a bevel gear from its properties (None for a straight one)
    sp = float(g.get("lap_spiral", 0.0))
    if abs(sp) < 1e-9:
        return None
    return bevelTwist(math.radians(float(g["lap_delta"])), sp, float(g.get("lap_lmid", 0.5 * (float(g["lap_lin"]) + float(g["lap_lout"])))),
                      bool(g.get("lap_herring", False)),
                      float(g["lap_spiral_in"]) if "lap_spiral_in" in g else None,
                      bool(g.get("lap_ushape", False)), float(g["lap_lin"]), float(g["lap_lout"]))


def apexBalance(l_in, l_out, k=1.0, ushape=False):
    # the apex of the chevron that cancels the sum of the spiral thrust when the load per unit
    # length of the tooth goes as L^k (V: equal load on both halves, U: the integral of
    # w ln(L / Lc) vanishes)
    a, b, n = l_in, l_out, k + 1.0
    if not ushape:
        return math.sqrt(a * b) if abs(n) < 1e-9 else ((a ** n + b ** n) / 2.0) ** (1.0 / n)
    if abs(n) < 1e-9:
        return math.sqrt(a * b)
    return math.exp((b ** n * math.log(b) - a ** n * math.log(a)) / (b ** n - a ** n) - 1.0 / n)


def bevelSpheres(psi, l_in, l_out, lmid, herring, step, delta=None, dbeta=None):
    # spheres for a twisted bevel element, one per `step` of the turn and, when the spiral angle changes
    # along the width (a U), one per dbeta of that angle, spaced evenly in ln L (the turn and the angle
    # change evenly then); herringbone: each half for itself, one sphere on the apex (lmid)
    def beta(L, h):
        return math.atan(math.sin(delta) * (psi(L * math.exp(h)) - psi(L * math.exp(-h))) / (2 * h))

    def run(a, b):
        n = int(math.ceil(abs(psi(b) - psi(a)) / step))
        if delta is not None and dbeta:
            # the angle just inside both ends (a V has a kink at its apex)
            r_ = math.log(b / a)
            h = 1e-5 * r_
            n = max(n, int(math.ceil(abs(beta(b * math.exp(-2e-3 * r_), h) - beta(a * math.exp(2e-3 * r_), h)) / dbeta)))
        n = max(2, n + 1)
        r = math.log(b / a)
        return [a * math.exp(r * k / (n - 1)) for k in range(n)]
    if not herring:
        return run(l_in, l_out)
    lo, hi = run(l_in, lmid), run(lmid, l_out)
    return lo + hi[1:]


def bevelGear(context, z, module, delta, l_in, l_out, tooth, bore, matrix, clearance=0.25, spiral=0.0, herring=False,
              spiral_in=None, ushape=False, lc=None):
    # spiral: spiral angle (degrees, positive right hand); 0 straight. herringbone: the apex of the
    # chevron at the cone distance lc (the middle by default), spiral the angle of the outer half and
    # spiral_in that of the inner half (None = the same, 0 straight, negative the same hand); ushape: a U instead of a V, spiral the angle
    # at the farther end
    theta_a = delta + module / l_out
    theta_k, rc = bevelBody(delta, module, l_in, l_out, theta_a, bore, clearance)
    exact = bool(tooth and _EXACT[0] and delta < math.pi / 2 - 1e-6)
    if exact:
        top, cl = sphInvTop(z, module, delta, l_out, clearance,
                            twist_deg=max(abs(spiral), abs(spiral_in) if spiral_in is not None else 0.0))
    else:
        top = bevelTop(z, module, delta, l_out, tooth, clearance)
        cl = starterClasses(top, 1e-9 * module / l_out) if tooth else None
    lmid = 0.5 * (l_in + l_out)
    herring = bool(herring or ushape)
    if herring and lc is not None:
        lmid = float(lc)
        if abs(spiral) > 1e-9 and not (l_in + 0.05 * (l_out - l_in) <= lmid <= l_out - 0.05 * (l_out - l_in)):
            raise LapError("the apex of the chevron must lie inside the face width (at %.4g .. %.4g from the "
                           "small end)" % (0.05 * (l_out - l_in), 0.95 * (l_out - l_in)))
    if tooth and abs(spiral) > 1e-9:
        if abs(spiral) >= 60 or (spiral_in is not None and abs(spiral_in) >= 60):
            raise LapError("spiral angle too large (at most 60 deg)")
        psi = bevelTwist(delta, spiral, lmid, herring, spiral_in, ushape, l_in, l_out)
        p = 2 * math.pi / z
        # the sector turns with the teeth: every sphere the same outline, joined by quads; a
        # sphere per 2 deg of turn, the outline to 0.002 m
        levels = bevelSpheres(psi, l_in, l_out, lmid, herring, math.radians(10.0 if _LOW[0] else 3.5), delta,
                              None if _LOW[0] else math.radians(3.0))
        nlv = len(levels)
        keep = douglasPeucker([(l_out * t, l_out * a * math.sin(delta)) for t, a in top],
                              (3e-4 if exact else 2e-3) * module)
        if exact:
            cl = [cl[keep[i]] for i in range(len(keep) - 1)]
            top = [top[i] for i in keep]
        else:
            top = [top[i] for i in keep]
            cl = starterClasses(top, 1e-9 * module / l_out)
        me = bevelLoft("tmp", z, levels, [top] * nlv, [cl] * nlv, theta_k, rc, shifts=[psi(L) for L in levels],
                       ngon=exact)
    else:
        me = bevelElement("tmp", z, l_in, l_out, top, cl, theta_k, rc, ngon=exact)
    g = makeGear(context, z, me, matrix, module, l_out - l_in, delta > math.pi / 2, (delta, l_in, l_out))
    g["lap_bore"] = float(bore)
    g["lap_neck"] = float(theta_k)
    g["lap_rc"] = float(rc)
    g["lap_spiral"] = float(spiral)
    g["lap_lmid"] = float(lmid)
    g["lap_herring"] = bool(herring and tooth and abs(spiral) > 1e-9)
    g["lap_ushape"] = bool(ushape and tooth and abs(spiral) > 1e-9)
    if herring and not ushape and spiral_in is not None and tooth and abs(spiral) > 1e-9:
        g["lap_spiral_in"] = float(spiral_in)
    elif "lap_spiral_in" in g:
        del g["lap_spiral_in"]
    return g


def twistShape(herring):
    # how the teeth turn along the width: helical z, herringbone |z| (two halves of opposite hand
    # meeting in the middle plane, the apex of the chevron)
    return (lambda z: abs(z)) if herring else (lambda z: z)


def twistLevels(z0, z1, twist_per_len, p, herring):
    # sections along the width for a twisted (helical, herringbone) element: one per 1/24 pitch of
    # the turn; herringbone: an odd number, one of them in the middle plane (the apex)
    w = z1 - z0
    if herring:
        nh = max(1, int(math.ceil(abs(twist_per_len) * w / 2 / (p / 24))))
        return [z0 + w * k / (2 * nh) for k in range(2 * nh + 1)]
    nl = max(2, int(math.ceil(abs(twist_per_len) * w / (p / 24))) + 1)
    return [z0 + w * k / (nl - 1) for k in range(nl)]


def spurGear(context, z, module, width, tooth, internal, r_body, matrix, helix=0.0, addendum=None, clearance=0.25,
             herring=False, prefix="gear"):
    # cylindrical gear; module is the transverse module (pitch radius z m / 2), helix the angle of the
    # teeth at the pitch radius in degrees (positive: right hand; herringbone: the hand of the half
    # at +z). a helical starter tooth is built from sections turned along the width
    rp = z * module / 2
    ded = (1.0 + clearance) * module
    if internal and r_body <= rp + ded:
        raise LapError("the ring mantle must lie outside the tooth roots")
    if not internal and r_body >= rp - ded:
        raise LapError("the bore reaches the tooth roots: use more teeth or a smaller bore")
    top = spurTop(z, module, tooth, internal, addendum, clearance)
    if herring and abs(helix) < 1e-9:
        herring = False
    if tooth and abs(helix) > 1e-9:
        if abs(helix) >= 80:
            raise LapError("helix angle too large")
        p = 2 * math.pi / z
        tau = math.tan(math.radians(helix)) / rp
        shape = twistShape(herring)
        # a level per 2 deg of turn, the sector turned with the teeth (quads)
        tw = abs(tau) * width / (2 if herring else 1)
        nh = max(1, int(math.ceil(tw / math.radians(10.0 if _LOW[0] else 2.0))))
        levels = ([-width / 2 + width * k / (2 * nh) for k in range(2 * nh + 1)] if herring else
                  [-width / 2 + width * k / nh for k in range(nh + 1)])
        keep = douglasPeucker([(r * math.cos(a), r * math.sin(a)) for r, a in top], 2e-3 * module)
        top = [top[i] for i in keep]
        cl = starterClasses(top, 1e-9 * module)
        me = spurLoft("tmp", z, levels, [top] * len(levels), [cl] * len(levels), r_body,
                      shifts=[tau * shape(zk) for zk in levels])
    else:
        me = spurElement("tmp", z, width, top, starterClasses(top, 1e-9 * module) if tooth else None, r_body)
    g = makeGear(context, z, me, matrix, module, width, internal, prefix=prefix)
    g["lap_rbody"] = float(r_body)
    g["lap_helix"] = float(helix)
    g["lap_herring"] = bool(herring)
    return g


def wormRack(mx, q, clearance=0.25, alpha=20.0):
    # axial profile of a ZA worm (straight flanks, flank angle alpha) over one axial pitch, from the
    # middle of a root to the middle of the next one: [(u, r)] and the class of every segment
    px = math.pi * mx
    r1 = q * mx / 2
    ra, rf = r1 + mx, r1 - (1.0 + clearance) * mx
    ta = math.tan(math.radians(alpha))
    s_tip = px / 4 - mx * ta
    s_root = px / 4 + (1.0 + clearance) * mx * ta
    if s_tip <= 0 or s_root >= px / 2:
        raise LapError("the thread profile does not fit the axial pitch (flank angle or clearance)")
    prof = [(-px / 2, rf), (-s_root, rf), (-s_tip, ra), (s_tip, ra), (s_root, rf)]
    cls = [CLS_PLAIN, CLS_FLANK, CLS_PLAIN, CLS_FLANK, CLS_PLAIN]
    return prof, cls


def wormSweep(name, z1, mx, prof, cls, zlo, zhi, bore, dth_deg=4.0):
    # worm element as a screw sweep of its axial profile: prof = [(u, r)] over one axial pitch
    # (u0 <= u < u0 + pi mx, repeated), cls[i] the class of the segment from point i to the next.
    # the element spans the sector of one start; on the meridian at the angle t the profile is
    # shifted by lead t / 2 pi. every meridian has the same points, so neighbouring meridians are
    # joined by quads along the thread; points beyond an end are pulled onto the end plane (where
    # the thread runs out the quads become triangles). ends and bore are quad strips, the sector
    # sides one face each
    px = math.pi * mx
    lead = z1 * px
    p = 2 * math.pi / z1
    # meridians: a multiple of 48 per start, so that the steps of the imprint (1/48 of a wheel tooth
    # = 7.5 / z1 deg of the worm) fall on meridians; at most about 4 deg apart
    nm = max(4, int(12 / z1)) if _LOW[0] else 48 * int(math.ceil(7.5 / (dth_deg * z1)))
    sq = 1.0 - SLOT / (2 * math.pi) if z1 == 1 else 1.0
    u0 = prof[0][0]
    # enough pitches that every meridian covers zlo .. zhi after its shift of at most px / 2
    k0 = int(math.floor((zlo - px - u0) / px)) - 1
    k1 = int(math.ceil((zhi + px - u0) / px)) + 1
    U, R, C = [], [], []
    for kk in range(k0, k1 + 1):
        for (u, r), c in zip(prof, cls):
            U.append(u + kk * px)
            R.append(r)
            C.append(c)
    n = len(U)
    bm = bmesh.new()
    grid = []                 # per meridian: vertex of every profile point (shared where pulled together)
    ends = []                 # per meridian: (bottom end vertex, top end vertex, bore bottom, bore top)
    for j in range(nm + 1):
        t = -p / 2 + p * j / nm
        sh = lead * t / (2 * math.pi)
        z = [u + sh for u in U]
        c_, s_ = math.cos(t * sq), math.sin(t * sq)

        def vert(r, zz):
            return bm.verts.new((r * c_, r * s_, zz))
        i_in = [i for i in range(n) if zlo < z[i] < zhi]
        ia, ib = i_in[0], i_in[-1]
        # where the profile crosses the end planes
        f0 = (zlo - z[ia - 1]) / (z[ia] - z[ia - 1])
        v_lo = vert(R[ia - 1] + (R[ia] - R[ia - 1]) * f0, zlo)
        f1 = (zhi - z[ib]) / (z[ib + 1] - z[ib])
        v_hi = vert(R[ib] + (R[ib + 1] - R[ib]) * f1, zhi)
        row = []
        for i in range(n):
            if i < ia:
                row.append(v_lo)
            elif i > ib:
                row.append(v_hi)
            else:
                row.append(vert(R[i], z[i]))
        grid.append(row)
        ends.append((v_lo, v_hi, vert(bore, zlo), vert(bore, zhi)))

    def face(vs, c):
        out = []
        for v in vs:
            if v not in out:
                out.append(v)
        if len(out) >= 3:
            f = bm.faces.new(out)
            f.material_index = c
    for j in range(nm):
        A, B = grid[j], grid[j + 1]
        for i in range(n - 1):
            face((A[i], A[i + 1], B[i + 1], B[i]), C[i])
        (la, ha, ba, ta_), (lb, hb, bb, tb) = ends[j], ends[j + 1]
        face((ha, hb, tb, ta_), CLS_PLAIN)          # top end
        face((la, ba, bb, lb), CLS_PLAIN)           # bottom end
        face((ba, ta_, tb, bb), CLS_PLAIN)          # bore
    for j in (0, nm):
        ring = []
        for v in grid[j]:
            if not ring or ring[-1] is not v:
                ring.append(v)
        ring += [ends[j][3], ends[j][2]]
        f = bm.faces.new(ring if j == 0 else list(reversed(ring)))
        f.material_index = CLS_PLAIN
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def wormGear(context, z1, mx, q, length, bore, matrix, tooth=True, clearance=0.25):
    # cylindrical worm: z1 starts (one element per start), axial module mx, diameter factor q
    # (pitch diameter q mx), lead angle tan g = z1 / q. stored as a helical gear of z1 teeth with the
    # helix 90 - g at the pitch radius, so that the imprint turns it like any cylindrical gear. the
    # element is the screw sweep of the axial profile (quads along the thread)
    if z1 < 1:
        raise LapError("a worm needs at least one start")
    r1 = q * mx / 2
    rf = r1 - (1.0 + clearance) * mx
    if rf <= 0.2 * r1:
        raise LapError("q is too small for this module: the thread roots reach the axis")
    if bore <= 0:
        bore = seatBore(0.5 * rf)
    if bore >= rf:
        raise LapError("the bore reaches the thread roots")
    gamma = math.atan2(z1, q)
    helix = 90.0 - math.degrees(gamma)
    if tooth:
        prof, cls = wormRack(mx, q, clearance)
    else:
        prof, cls = [(-math.pi * mx / 2, r1 + mx)], [CLS_PLAIN]
    me = wormSweep("tmp", z1, mx, prof, cls, -length / 2, length / 2, bore, dth_deg=15.0 if _LOW[0] else 4.0)
    g = makeGear(context, z1, me, matrix, q * mx / z1, length, False, prefix="worm", unit="start")
    setWormProfile(g, prof, cls)
    g["lap_rbody"] = float(bore)
    g["lap_helix"] = float(helix)
    g["lap_worm"] = 1.0
    g["lap_axial_module"] = float(mx)
    renameGear(g, "worm_%d_%d_start_m%s" % (int(g["lap_no"]), z1, fmtM(mx)))
    g["lap_q"] = float(q)
    g.empty_display_size = r1 + 2 * mx
    return g


def hobProfile(mx, q, clearance=0.25, alpha=20.0, nf=6):
    # axial profile of the hob that cuts the wheel of a ZA worm: the worm thread with its tip c* m
    # higher (the wheel roots clear the worm tips) and rounded with the gost fillet c* m / (1 - sin
    # alpha), over one axial pitch from the middle of a root: [(u, r)] and segment classes
    px = math.pi * mx
    r1 = q * mx / 2
    ta = math.tan(math.radians(alpha))
    ca, sa = math.cos(math.radians(alpha)), math.sin(math.radians(alpha))
    rt = r1 + (1.0 + clearance) * mx
    rr = r1 - mx
    rho = clearance * mx / (1.0 - sa) if clearance > 0 else 0.0

    def w(r):                                  # half thickness of the thread at r
        return px / 4 - (r - r1) * ta
    s_root = w(rr)
    if w(rt) - rho * (1 - sa) / ca <= 0 or s_root >= px / 2:
        raise LapError("the hob profile does not fit the axial pitch")
    rc = rt - rho
    uc = w(rc) - rho / ca
    arc = [(uc + rho * math.cos(t), rc + rho * math.sin(t))
           for t in (math.radians(alpha) + (math.pi / 2 - math.radians(alpha)) * i / nf for i in range(nf + 1))]
    # from the middle of a root: root, left flank, fillet, tip, fillet, right flank
    pts = [(-px / 2, rr), (-s_root, rr)] + [(-u, r) for u, r in arc] + [(u, r) for u, r in reversed(arc)] + \
          [(s_root, rr)]
    cls = []
    for (u0, r0), (u1, r1_) in zip(pts, pts[1:] + [(pts[0][0] + px, pts[0][1])]):
        flank = abs(r1_ - r0) > 1e-9 and abs(abs(u1 - u0) / max(abs(r1_ - r0), 1e-30) - ta) < 1e-6
        cls.append(CLS_FLANK if flank else CLS_PLAIN)
    return pts, cls


def globoidLoft(name, z1, chains):
    # worm element from its meridian outlines: chains = [(t, [(r, z)], classes)] over the sector of one
    # start, each from the bottom end at the bore to the top end at the bore (the bore closes it).
    # neighbouring meridians are joined by triangles, features matched first (tileStrip); the bore is
    # a strip of quads, the sector sides one face each (squeezed to a hairline slot for one start)
    sq = 1.0 - SLOT / (2 * math.pi) if z1 == 1 else 1.0
    bm = bmesh.new()
    rows, M = [], []
    for t, ch, cc in chains:
        c_, s_ = math.cos(t * sq), math.sin(t * sq)
        rows.append([bm.verts.new((r * c_, r * s_, zz)) for r, zz in ch])
        M.append([(r * c_, r * s_) for r, zz in ch])
    size = max(max(abs(r), abs(zz)) for t, ch, cc in chains for r, zz in ch)
    solid = chains[0][1][0][0] < 1e-9 * size
    for k in range(len(chains) - 1):
        A, B = rows[k], rows[k + 1]
        tileStrip(bm, A, B, chains[k][2], chains[k + 1][2], (M[k], M[k + 1]))
        if not solid:
            f = bm.faces.new((A[-1], A[0], B[0], B[-1]))
            f.material_index = CLS_PLAIN
    for k in (0, len(chains) - 1):
        f = bm.faces.new(rows[k])
        f.material_index = CLS_PLAIN
    if solid:
        # no bore: the ends of every meridian lie on the axis, one point each
        axis = [row[0] for row in rows] + [row[-1] for row in rows]
        bmesh.ops.remove_doubles(bm, verts=axis, dist=1e-7 * size)
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def curveDeviation(P, C):
    # largest distance of the points P (n, 2) from the polyline C (m, 2)
    A, B = C[:-1], C[1:]
    D = B - A
    ll = np.maximum((D * D).sum(axis=1), 1e-30)
    t = np.clip(((P[:, None, 0] - A[None, :, 0]) * D[None, :, 0] + (P[:, None, 1] - A[None, :, 1]) * D[None, :, 1])
                / ll[None, :], 0.0, 1.0)
    d2 = (P[:, None, 0] - A[None, :, 0] - t * D[None, :, 0]) ** 2 + (P[:, None, 1] - A[None, :, 1] - t * D[None, :, 1]) ** 2
    return float(np.sqrt(d2.min(axis=1)).max())


def wormWheelTeeth(*args, **kw):
    with engineMode():
        return _wormWheelTeeth(*args, **kw)


def _wormWheelTeeth(context, worm, wheel, report, clearance=0.25, sign=1.0, nlev=None, npos=180, tol=0.01):
    # the teeth of a worm wheel as the hob of its worm cuts them: on every section of the wheel
    # (planes across its axis) the hob is a rack made exactly from its axial profile, sliding while
    # the wheel turns (a screw turned is a screw slid), every position subtracted from the throated
    # blank. the sections are laid out with the same number of points each and joined by quads
    t0 = time.time()
    zs = int(worm["lap_teeth"])
    zt = int(wheel["lap_teeth"])
    mx = sizeModule(worm)
    q = float(worm["lap_q"])
    px = math.pi * mx
    lead = zs * px
    prof, pcls = hobProfile(mx, q, clearance)
    a_, rho_, cap_ = wheel["lap_throat"]
    bore = float(wheel["lap_rbody"])
    me_t = gearMesh(wheel)
    zz = [v.co.z for v in me_t.vertices]
    z0, z1 = min(zz), max(zz)
    # sections 0.3 m apart in the middle, closer toward the faces (z = zm + hw sin t, t even): there
    # the thread of the worm leaves the plane and the cut changes fast across the width
    zm, hw = 0.5 * (z0 + z1), 0.5 * (z1 - z0)
    if nlev is None:
        nlev = max(16, int(math.ceil(math.pi * hw / (0.3 * mx))) + 1)
    levels = [zm + hw * math.sin(-math.pi / 2 + math.pi * k / (nlev - 1)) for k in range(nlev)]
    cut_at = [min(max(v, z0 + 1e-6 * (z1 - z0)), z1 - 1e-6 * (z1 - z0)) for v in levels]
    P0, e_h, e_t, wc0 = rackFrame(worm, wheel, zs, zt, sign)
    psi0 = math.atan2(wc0.y, wc0.x)
    span = 3.5 * 2 * math.pi / zt
    poses = []
    for k in range(npos + 1):
        beta = psi0 - span + 2 * span * k / npos
        alpha = sign * (zt / float(zs)) * beta
        sh = -(lead * alpha / (2 * math.pi)) % px
        poses.append(np.array(rotZ(-beta) @ P0 @ Matrix.Translation((0.0, 0.0, sh))))
    p = 2 * math.pi / zt
    arc = gridAngles(-p / 2, p / 2, p / 32)
    zlen = 2 * (cap_ + 4 * mx)
    data = []
    for val in cut_at:
        ro = cap_ if abs(val) >= rho_ else min(cap_, a_ - math.sqrt(rho_ * rho_ - val * val))
        blank = [(bore * math.cos(t), bore * math.sin(t)) for t in reversed(arc)] + \
                [(ro * math.cos(t), ro * math.sin(t)) for t in arc]
        if area2(blank) < 0:
            blank = blank[::-1]
        attrs = [('T', CLS_PLAIN)] * len(blank)
        B = np.array(blank)
        lo, hi = B.min(axis=0) - 0.01 * mx, B.max(axis=0) + 0.01 * mx
        br = rackBranch(prof, pcls, lead, px, val - wc0.z, e_h, e_t, zlen, mx)
        polys = []
        if br is not None:
            BP, BC, BN, bst = br
            pid_pt = np.zeros(len(BP), dtype=np.int64)
            for qq in range(len(bst) - 1):
                pid_pt[bst[qq]:bst[qq + 1]] = qq
            pid_pt[-1] = len(bst) - 2
            for k, M in enumerate(poses):
                Q = BP @ M[:3, :3].T + M[:3, 3]
                inb = np.nonzero((Q[:, 0] >= lo[0]) & (Q[:, 0] <= hi[0]) & (Q[:, 1] >= lo[1]) & (Q[:, 1] <= hi[1]))[0]
                if not len(inb):
                    continue
                b, e = bst[pid_pt[inb[0]]], bst[min(pid_pt[inb[-1]] + 1, len(bst) - 1)]
                back = []
                for idx in (e, b):
                    v = e_h * (val - wc0.z) + e_t * (-mx)
                    back.append(np.array((v.x, v.y, BP[idx, 2])) @ M[:3, :3].T + M[:3, 3])
                poly = list(map(tuple, Q[b:e + 1, :2].tolist())) + [(float(qp[0]), float(qp[1])) for qp in back]
                ea = [(0, BC[j]) for j in range(b, e)] + [(0, CLS_PLAIN)] * 3
                poly, ea = clipSource(poly, ea, lo, hi, (0, CLS_PLAIN))
                if poly:
                    polys.append(((k, [c for _, c in ea]), poly))
        lp, at = blank, attrs
        c = 0
        while c < len(polys):
            c1, nv = c, 0
            while c1 < len(polys) and (c1 == c or nv + len(polys[c1][1]) <= 3000):
                nv += len(polys[c1][1])
                c1 += 1
            lp, at = subtract2d(lp, at, polys[c:c1], 0.0)
            c = c1
            if not lp:
                raise LapError("the hob cut a whole section of the wheel away")
            lp, at = dropCollinear(lp, at, 1e-9 * mx)
        cls = [a[1][1][a[2]] if a[0] == 'S' else a[1] for a in at]
        data.append((lp, cls, Plane2d(val)))
    tops, tcls, phi0 = sectorTops(wheel, data, False, zt, mx, bodyTest(wheel, False, mx), choice={})
    for k in range(len(tops)):
        # the ends of a tooth side meet the neighbour element: one radius for both (the cut leaves
        # them a few 1e-5 apart)
        ra_ = 0.5 * (tops[k][0][0] + tops[k][-1][0])
        tops[k][0] = (ra_, tops[k][0][1])
        tops[k][-1] = (ra_, tops[k][-1][1])
    met = lambda h, f: (h * math.cos(f), h * math.sin(f))
    # fewer sections where the tooth changes slowly across the width: a section stays only where the
    # blend of its kept neighbours misses it by more than tol_z (recursively, like douglas-peucker
    # across the sections); the tooth sides compared as even layouts of their length
    tol_z, tol_p = 2.0 * tol * mx, tol * mx
    # (compared turned back by the twist of the teeth across the width, so that the same tooth
    # lies in the same place of every section)
    tau = math.tan(math.radians(float(wheel.get("lap_helix", 0.0)))) / (zt * mx / 2)
    U = []
    for top, lv in zip(tops, levels):
        tt = turnTop(top, -tau * lv, p)
        pr_, _ = resampleTopUniform(tt, [0] * (len(tt) - 1), 400, met)
        U.append(np.array([met(h, f) for h, f in pr_]))
    keep = {0, len(tops) - 1}

    def split(i, j):
        if j - i < 2:
            return
        best, bk = -1.0, None
        for k in range(i + 1, j):
            t = (levels[k] - levels[i]) / (levels[j] - levels[i])
            e = curveDeviation(U[k], (1 - t) * U[i] + t * U[j])
            if e > best:
                best, bk = e, k
        if best > tol_z:
            keep.add(bk)
            split(i, bk)
            split(bk, j)
    split(0, len(tops) - 1)
    ks = sorted(keep)
    # every kept section: its runs of one class simplified on their own (douglas-peucker, tol_p):
    # points close where the outline bends (fillets, corners), far apart where it is nearly straight
    # curved meridians: the sector of every kept section turned so that its sides lie in the middle
    # of the tooth spaces (the tooth centred on the middle of its tip land); the sections are joined
    # in that turned frame, the sector turned back per section (shifts): the element sides follow
    # the teeth across the throat
    def tipMiddle(k):
        top = tops[k]
        rmax = max(h for h, f in top)
        sel = [f for h, f in top if h > rmax - 0.1 * mx]
        base = tau * levels[k]
        d = [((f - base + p / 2) % p) - p / 2 for f in sel]
        return base + 0.5 * (min(d) + max(d))

    def centred(k, c):
        tt = turnTop(tops[k], -c, p)
        n0 = len(tops[k]) - 1
        M = np.array([met(0.5 * (tops[k][i][0] + tops[k][i + 1][0]),
                          0.5 * (tops[k][i][1] + tops[k][i + 1][1]) + sh)
                      for sh in (-p, 0.0, p) for i in range(n0)])
        Mt = np.array([met(0.5 * (tt[i][0] + tt[i + 1][0]), 0.5 * (tt[i][1] + tt[i + 1][1]) + c)
                       for i in range(len(tt) - 1)])
        idx = np.argmin(((Mt[:, None, :] - M[None, :, :]) ** 2).sum(2), axis=1) % n0
        cl = [tcls[k][int(i)] for i in idx]
        for _ in range(3):
            for i in range(1, len(cl) - 1):
                if cl[i - 1] == cl[i + 1] != cl[i]:
                    cl[i] = cl[i - 1]
        return tt, cl
    lv2, tops2, cls2, shifts2 = [], [], [], []
    for k in ks:
        c = tipMiddle(k)
        top, cl = centred(k, c)
        out, oc = [top[0]], []
        i = 0
        while i < len(cl):
            j = i
            while j + 1 < len(cl) and cl[j + 1] == cl[i]:
                j += 1
            run = top[i:j + 2]
            kept = douglasPeucker([met(h, f) for h, f in run], tol_p)
            for q in kept[1:]:
                out.append(run[q])
                oc.append(cl[i])
            i = j + 1
        lv2.append(levels[k])
        tops2.append(out)
        cls2.append(oc)
        shifts2.append(c)
    mcount = max(len(t) for t in tops2)
    nlev_used = len(ks)
    quads_used = False
    me_new = spurLoft("LAP_new", zt, lv2, tops2, cls2, bore, shifts=shifts2)
    if phi0:
        me_new.transform(rotZ(phi0))
    ob, vol = meshCheck(me_new)
    bm = bmesh.new()
    bm.from_mesh(me_new)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(me_new)
    attachMaterials(me_t)
    me_t.update()
    report.append("worm wheel cut by the hob of %s: %d of %d sections kept, up to %d points each, %s; "
                  "volume %.6g, open edges %d, %.1f s" % (worm.name, nlev_used, nlev, mcount, "quads" if quads_used else "triangles", vol, ob, time.time() - t0))
    return ob


def throatElement(name, z, width, a, rho, cap, r_body):
    # smooth element of a worm wheel blank: the tip is a torus about the worm axis (distance a from
    # the wheel axis, radius rho) and no larger than cap, so the teeth are cut over the whole width
    p = 2 * math.pi / z
    nl = 25
    levels = [-width / 2 + width * k / (nl - 1) for k in range(nl)]
    tops = []
    for zk in levels:
        r = cap if abs(zk) >= rho else min(cap, a - math.sqrt(rho * rho - zk * zk))
        tops.append([(r, q) for q in gridAngles(-p / 2, p / 2, p / 16)])
    return spurLoft(name, z, levels, tops, None, r_body)


def faceGear(context, src, z2, report):
    # face gear for a cylindrical pinion, axes meeting at 90 degrees: the pinion rolls without
    # sliding on the radius R = z2 / z1 * r1 of the face gear, so the pinion is centred there. the
    # tooth ring covers 80% of the pinion width about R (the teeth run out at both walls); the face
    # (tip plane) lies an addendum above the pitch plane, which touches the pinion pitch cylinder
    z1 = int(src["lap_teeth"])
    m = float(src["lap_module"])
    b = float(src["lap_width"])
    if abs(float(src.get("lap_helix", 0.0))) > 1e-9:
        raise LapError("a face gear with a helical pinion needs offset axes: not supported yet")
    if src.get("lap_internal", False) or src.get("lap_kind") != 'SPUR':
        raise LapError("the source must be an external cylindrical gear")
    r1 = z1 * m / 2
    R = z2 / float(z1) * r1
    r_in, r_out = R - 0.4 * b, R + 0.4 * b
    if r_in < 0.3 * R or r_in <= r1:
        raise LapError("the pinion is too wide for this face gear: use more face gear teeth or a narrower "
                       "pinion")
    w = 4.0 * m
    p = 2 * math.pi / z2
    me = spurElement("tmp", z2, w, [(r_out, a) for a in gridAngles(-p / 2, p / 2, p / 16)], None, r_in)
    # in the pinion frame: pinion axis z; face gear axis along +y through (0, 0, -R); its face (local
    # z = +w/2) at y = -(r1 - m)
    mat = gearFrame(src) @ Matrix.Translation((0.0, -(r1 - m) - w / 2, -R)) @ \
        Matrix.Rotation(math.radians(-90), 4, 'X')
    g = makeGear(context, z2, me, mat, m, w, False)
    g["lap_rbody"] = float(r_in)
    g["lap_face"] = 1.0
    g["lap_helix"] = 0.0
    return g, "face gear radius %.4g (teeth %.4g .. %.4g), pinion centred on it" % (R, r_in, r_out)


def meshPhaseInternal(src, ring, pitch_point, sgn=1.0):
    # an internal gear turned to mesh with the pinion src at the pitch point (src coordinates)
    z1, z2 = int(src["lap_teeth"]), int(ring["lap_teeth"])
    th = math.atan2(pitch_point[1], pitch_point[0])
    p1 = 2 * math.pi / z1
    delta = th - round(th / p1) * p1
    q = ring.matrix_world.inverted() @ (src.matrix_world @ Vector(pitch_point))
    psi = math.atan2(q.y, q.x)
    ring.matrix_world = ring.matrix_world @ rotZ(psi - math.pi / z2 + sgn * delta * z1 / float(z2))


def meshPhase(src, g2, pitch_point):
    # turn g2 (external mate) about its axis so that it meshes with the source at the pitch point
    # (source coordinates; the starter tooth of element 0 is centred on the local +x, the others
    # every 2 pi / z): a tooth space of g2 faces a source tooth centred there, and when no source
    # tooth is centred there (off by delta), g2 is turned on as the pair rolls, by delta z1 / z2
    z1 = int(src["lap_teeth"])
    th = math.atan2(pitch_point[1], pitch_point[0])
    p1 = 2 * math.pi / z1
    delta = th - round(th / p1) * p1
    q = g2.matrix_world.inverted() @ (src.matrix_world @ Vector(pitch_point))
    psi = math.atan2(q.y, q.x)
    p2 = 2 * math.pi / int(g2["lap_teeth"])
    g2.matrix_world = g2.matrix_world @ rotZ(psi - p2 / 2 + delta * z1 / float(int(g2["lap_teeth"])))


def createMating(context, src, z2, internal, cross=0.0, tooth=False):
    checkRotary(src, "a mating gear")
    checkVersion(src)
    z1 = int(src["lap_teeth"])
    m = float(src.get("lap_module", 1.0))
    w = float(src.get("lap_width", 6.0))
    rp1 = z1 * m / 2
    rp2 = z2 * m / 2
    fs = gearFrame(src)
    if isBevel(src):
        d1 = math.radians(float(src["lap_delta"]))
        l_in, l_out = float(src["lap_lin"]), float(src["lap_lout"])
        # apex on apex, same cone distances: z1 / sin d1 = z2 / sin d2; the internal gear takes
        # the pitch cone over 90 degrees
        sd2 = z2 * math.sin(d1) / z1
        if sd2 > 1.0:
            raise LapError("%d teeth do not fit this source: its pitch cone was made for fewer mating "
                           "teeth (use New Bevel Pair to set both counts and the shaft angle)" % z2)
        d2 = math.asin(sd2)
        if internal:
            if d1 >= math.pi / 2:
                raise LapError("the source is internal already")
            d2 = math.pi - d2
        sig = d1 + d2
        if sig >= math.pi - 1e-6:
            raise LapError("the axes would be parallel: use a cylindrical pair")
        a2 = Vector((math.sin(sig), 0.0, math.cos(sig)))
        rot = a2.to_track_quat('Z', 'Y').to_matrix().to_4x4()
        tooth2 = tooth and d2 < math.pi / 2 - 1e-6
        sp1 = float(src.get("lap_spiral", 0.0))
        g = bevelGear(context, z2, m, d2, l_in, l_out, tooth2, 0.0, fs @ rot, spiral=-sp1,
                      herring=bool(src.get("lap_herring", False)),
                      spiral_in=-float(src["lap_spiral_in"]) if "lap_spiral_in" in src else None,
                      ushape=bool(src.get("lap_ushape", False)),
                      lc=float(src["lap_lmid"]) if "lap_lmid" in src else None)
        if tooth2:
            # at the mean cone distance, where the spiral teeth are not turned
            lm = float(src.get("lap_lmid", 0.5 * (l_in + l_out)))
            meshPhase(src, g, (lm * math.sin(d1), 0.0, lm * math.cos(d1)))
        return g, "pitch cone %.4g deg%s, shaft angle %.4g deg" % (
            math.degrees(d2), " (internal)" if d2 > math.pi / 2 else "", math.degrees(sig))
    b1 = float(src.get("lap_helix", 0.0))
    if src.get("lap_worm"):
        # worm wheel: axes crossed at 90 deg, the wheel takes the lead angle as its helix and the
        # axial module of the worm as its transverse module; its width about 0.75 of the worm tip
        # diameter (a plain cylinder: the lapping cuts its throat)
        if internal:
            raise LapError("a worm drives an external wheel")
        mx = float(src["lap_axial_module"])
        cross = 90.0 if b1 >= 0 else -90.0
        b2 = cross - b1
        r2 = z2 * mx / 2
        a = rp1 + r2
        w2 = min(w, 0.75 * (2 * rp1 + 2 * mx))
        # throat: the tips clear the worm roots by c* = 0.25 (a torus of radius r1 - mx about the worm
        # axis), at the sides at most 6 mx / (z1 + 2) over the tip diameter (gost 19650)
        rho = rp1 - mx
        cap = r2 + mx + 3 * mx / (z1 + 2)
        bore = defaultBore(z2, mx)
        me = throatElement("tmp", z2, w2, a, rho, cap, bore)
        g = makeGear(context, z2, me, fs @ Matrix.Translation((a, 0, 0)) @ Matrix.Rotation(math.radians(cross), 4, 'X'),
                     mx, w2, False, prefix="wormwheel")
        g["lap_rbody"] = float(bore)
        g["lap_helix"] = b2
        g["lap_throat"] = (float(a), float(rho), float(cap))
        return g, "worm wheel: lead angle %.4g deg, width %.4g, center distance %.4g, throated blank" % (b2, w2, a)
    if (abs(cross) > 1e-9 or src.get("lap_worm")) and src.get("lap_herring"):
        raise LapError("herringbone gears mesh only on parallel axes")
    if abs(cross) > 1e-9:
        # crossed helical gears: helix angles add up to the crossing angle; the normal module is
        # the same for both, the blank is turned about the line joining the centres
        if internal:
            raise LapError("crossed axes only for external gears")
        b2 = cross - b1
        if abs(math.cos(math.radians(b2))) < 0.15:
            raise LapError("the mating helix angle %.4g deg is too steep (a worm): change the crossing angle "
                           "or the source helix" % b2)
        mn = m * math.cos(math.radians(b1))
        m2 = mn / math.cos(math.radians(b2))
        r2 = z2 * m2 / 2
        a = rp1 + r2
        g = spurGear(context, z2, m2, w, False, False, defaultBore(z2, m2),
                     fs @ Matrix.Translation((a, 0, 0)) @ Matrix.Rotation(math.radians(cross), 4, 'X'),
                     addendum=mn)
        g["lap_helix"] = b2
        return g, "crossed %.4g deg, mating helix %.4g deg, center distance %.4g" % (cross, b2, a)
    hb = bool(src.get("lap_herring", False))
    if internal:
        g = spurGear(context, z2, m, w, False, True, rp2 + 3 * m, fs @ Matrix.Translation((-(rp2 - rp1), 0, 0)))
        g["lap_helix"] = b1
        g["lap_herring"] = hb
        return g, "internal, center distance %.4g" % (rp2 - rp1)
    g = spurGear(context, z2, m, w, False, False, defaultBore(z2, m), fs @ Matrix.Translation((rp1 + rp2, 0, 0)))
    g["lap_helix"] = -b1
    g["lap_herring"] = hb
    return g, "center distance %.4g%s" % (rp1 + rp2, ", opposite hand helix" if abs(b1) > 1e-9 else "")


# ---------------------------------------------------------------------------
# ready made gears and pairs (first two tabs): external gears get the starter tooth of the basic
# rack; an internal gear (ring) is cut by a pinion rolling inside it (the section method), as a
# shaper cutter does - for a pair by its own pinion, for a single ring by a temporary cutter
# ---------------------------------------------------------------------------

LAP_DEFAULTS = dict(steps=12, sub=4, sign_mode='AUTO', smooth=True, limit_deg=45.0, relief=0.03)


def cutWith(context, src, tgt, report, clearance=0.25, lp=None):
    # one imprint of src into tgt with the settings of the scene (or the defaults)
    ps = getattr(context.scene, "lap", None)
    kw = dict(LAP_DEFAULTS)
    if lp is None and ps is not None:
        kw.update(steps=ps.steps, sub=ps.substeps, smooth=ps.smooth, limit_deg=ps.pressure_limit, relief=ps.relief)
    imprint(context, src, tgt, kw['steps'], kw['sub'], kw['sign_mode'], kw['smooth'], kw['limit_deg'],
            kw['relief'], report, clearance=clearance)


def ringGear(context, z, m, width, helix, herring, clearance, matrix, report, cutter_z=0, tooth=True, rim=0.0):
    # internal gear with z teeth, its centre at matrix: a blank ring (tips at the pitch radius less
    # one module, mantle rim beyond the roots), cut by a temporary pinion of cutter_z teeth (0: about
    # half of z, at least 10 fewer) rolling inside
    rp = z * m / 2
    r_out = rim if rim > 0 else rp + 3.5 * m
    if r_out <= rp + (1.5 + clearance) * m:
        raise LapError("the rim of the ring must lie outside its tooth roots")
    if _LOW[0] and tooth:
        return spurGear(context, z, m, width, True, True, r_out, matrix, helix, clearance=clearance, herring=herring,
                        prefix="ring")
    blank = spurGear(context, z, m, width, False, True, r_out, matrix, prefix="ring")
    blank["lap_helix"] = float(helix)
    blank["lap_herring"] = bool(herring and abs(helix) > 1e-9)
    if not tooth:
        return blank
    z0 = cutter_z if cutter_z > 0 else max(10, min(z - 10, int(round(z / 2.0))))
    if z - z0 < 6:
        removeGear(blank)
        raise LapError("the cutter needs at least 6 teeth fewer than the ring (%d teeth: at most %d)" % (z, z - 6))
    a = (z - z0) * m / 2
    cutter = spurGear(context, z0, m, width, True, False, defaultBore(z0, m), matrix @ Matrix.Translation((a, 0, 0)),
                      helix, clearance=clearance, herring=herring, prefix="cutter")
    try:
        cutWith(context, cutter, blank, report, clearance)
    finally:
        removeGear(cutter)
    report.append("ring cut by a pinion of %d teeth rolling inside it" % z0)
    return blank


def gearPair(context, z1, z2, m, width, helix, herring, internal, tooth, clearance, matrix, report):
    # two cylindrical gears in mesh. external: both with starter teeth, opposite hand, a tooth space
    # of the second facing the tooth of the first. internal: a pinion and the ring it cuts itself
    g1 = spurGear(context, z1, m, width, tooth, False, defaultBore(z1, m), matrix, helix, clearance=clearance,
                  herring=herring, prefix="pinion" if internal else "gear")
    try:
        if internal:
            if z2 - z1 < 6:
                raise LapError("an internal pair needs at least 6 teeth more on the ring")
            a = (z2 - z1) * m / 2
            ring = spurGear(context, z2, m, width, _LOW[0] and tooth, True, z2 * m / 2 + 3.5 * m,
                            gearFrame(g1) @ Matrix.Translation((-a, 0, 0)), helix, clearance=clearance,
                            herring=herring, prefix="ring")
            if _LOW[0] and tooth:
                meshPhaseInternal(g1, ring, (z1 * m / 2, 0.0, 0.0))
                return g1, ring, a
            ring["lap_helix"] = float(helix)
            ring["lap_herring"] = bool(herring and abs(helix) > 1e-9)
            if tooth:
                try:
                    cutWith(context, g1, ring, report, clearance)
                except LapError:
                    removeGear(ring)
                    raise
            return g1, ring, a
        a = (z1 + z2) * m / 2
        g2 = spurGear(context, z2, m, width, tooth, False, defaultBore(z2, m),
                      gearFrame(g1) @ Matrix.Translation((a, 0, 0)), -helix, clearance=clearance, herring=herring)
        if tooth:
            meshPhase(g1, g2, (z1 * m / 2, 0.0, 0.0))
        return g1, g2, a
    except LapError:
        removeGear(g1)
        raise


# ---------------------------------------------------------------------------
# cycloidal (clock) gearing, in the proportions of bs 978 part 2: the wheel drives the pinion.
# wheel teeth half a pitch thick, their addendum the epicycloid of a circle of half the pinion's
# pitch radius rolling on the wheel's pitch circle (conjugate to the radial flanks of the pinion,
# which that circle traces inside the pinion's pitch circle), up to a tip land 0.35 m wide;
# dedendum radial. pinion leaves 1.05 m thick (up to 7 leaves) or 1.25 m (8 and more), radial
# flanks, a semicircular addendum. dedenda: the addendum of the mate plus 0.4 m
# ---------------------------------------------------------------------------

def clockLeaf(zp, backlash=None):
    # leaf thickness in modules: bs 978 (1.05 up to 7 leaves, else 1.25), or the rest of the pitch
    # after the wheel tooth (pi / 2) and the backlash
    if backlash is None or backlash < 0:
        return 1.05 if zp <= 7 else 1.25
    return math.pi / 2 - backlash


def rootFillet(rf, th0, rho, lo):
    # fillet in a tooth space between the root circle rf and the radial flank th = th0 (the space
    # at th < th0, not past th = lo): points (r, th) from the root to the flank, the angle where it
    # leaves the root circle and the radius where it meets the flank. rho clamped to the space
    if rho <= 0:
        return [], th0, rf
    while True:
        thc = th0 - math.asin(rho / (rf + rho))
        if thc > lo + 1e-6 or rho < 1e-6 * rf:
            break
        rho *= 0.8
    C = ((rf + rho) * math.cos(thc), (rf + rho) * math.sin(thc))
    a1 = math.atan2(-math.sin(thc), -math.cos(thc))
    a2 = math.atan2(math.cos(th0), -math.sin(th0))
    sw = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    ns = 3 if _LOW[0] else 8
    pts = []
    for i in range(ns + 1):
        a = a1 + sw * i / ns
        x, y = C[0] + rho * math.cos(a), C[1] + rho * math.sin(a)
        pts.append((math.hypot(x, y), math.atan2(y, x)))
    return pts, thc, pts[-1][0]


def withFillet(root_l, rf, th0, rho, lo):
    # root points up to the fillet, then the fillet; its last point lies on the flank line
    pts, thc, rl = rootFillet(rf, th0, rho, lo)
    if not pts:
        return root_l, 0
    base = [q for q in root_l if q[1] < thc - 1e-9]
    return base + pts, len(pts)


def clockWheelTop(zw, zp, m, clear=0.4, tip_chord=0.35, ha_max=2.0, backlash=None, fillet=0.0):
    # tooth side of the wheel (radius, angle) from -p/2 to p/2, its classes, the addendum
    R = zw * m / 2
    r = zp * m / 4                               # rolling circle: half the pinion pitch radius
    p = 2 * math.pi / zw
    h = (math.pi * m / 4) / R                    # half the tooth thickness (pi m / 2) as an angle
    k = (R + r) / r
    c_, s_ = math.cos(-h), math.sin(-h)
    flank = []
    tip = None
    n = 2000
    for i in range(n + 1):
        ph = 1.2 * i / n
        x = (R + r) * math.cos(ph) - r * math.cos(k * ph)
        y = (R + r) * math.sin(ph) - r * math.sin(k * ph)
        X, Y = c_ * x - s_ * y, s_ * x + c_ * y
        rho, th = math.hypot(X, Y), math.atan2(Y, X)
        if th >= 0 or 2 * rho * math.sin(-th) <= tip_chord * m or rho >= R + ha_max * m:
            tip = (rho, th) if th < 0 else flank.pop()
            break
        flank.append((rho, th))
    if tip is None:
        raise LapError("the wheel tooth does not close: check the numbers of teeth")
    keep = douglasPeucker([(q * math.cos(a), q * math.sin(a)) for q, a in flank], (5e-2 if _LOW[0] else 2e-4) * m)
    flank = [flank[i] for i in keep]
    ha = tip[0] - R
    hf = clockLeaf(zp, backlash) * m / 2 + clear * m        # pinion addendum + clearance
    rf = R - hf
    if rf <= 0.3 * R:
        raise LapError("the wheel roots reach too deep: use more wheel teeth")
    root_l = [(rf, a) for a in gridAngles(-p / 2, -h, p / 32)]
    root_l, nfil = withFillet(root_l, rf, -h, fillet * m, -p / 2)
    tip_arc = [(tip[0], a) for a in gridAngles(tip[1], -tip[1], p / 64)][1:-1]
    right = flank + [tip]
    top = root_l + right + tip_arc + [(q, -a) for q, a in reversed(right)] + \
        [(q, -a) for q, a in reversed(root_l)]
    # classes: root, radial dedendum flank + epicycloid (working), tip, flank, root
    nl = len(root_l)
    cls = []
    for i in range(len(top) - 1):
        (r0, a0), (r1, a1) = top[i], top[i + 1]
        on_root = abs(r0 - rf) < 1e-9 * R and abs(r1 - rf) < 1e-9 * R
        on_tip = abs(r0 - tip[0]) < 1e-9 * R and abs(r1 - tip[0]) < 1e-9 * R
        on_fil = i < nl - 1 or i >= len(top) - nl
        cls.append(CLS_PLAIN if on_root or on_tip or on_fil else CLS_FLANK)
    return top, cls, ha, rf


def clockPinionTop(zp, m, ha_wheel, clear=0.4, backlash=None, fillet=0.0):
    # tooth side of the pinion: radial flanks, semicircular addendum; its classes, root radius
    Rp = zp * m / 2
    p = 2 * math.pi / zp
    tp = clockLeaf(zp, backlash) * m
    hp = math.asin(tp / (2 * Rp))
    rf = Rp - ha_wheel - clear * m
    if rf <= 0.15 * Rp:
        raise LapError("the pinion roots reach its axis: use more leaves or more wheel teeth")
    xc = Rp * math.cos(hp)
    semi = []
    ns_ = 4 if _LOW[0] else 24
    for i in range(1, ns_):
        u = -math.pi / 2 + math.pi * i / ns_
        x, y = xc + tp / 2 * math.cos(u), tp / 2 * math.sin(u)
        semi.append((math.hypot(x, y), math.atan2(y, x)))
    root_l = [(rf, a) for a in gridAngles(-p / 2, -hp, p / 32)]
    root_l, nfil = withFillet(root_l, rf, -hp, fillet * m, -p / 2)
    top = root_l + [(Rp, -hp)] + semi + [(Rp, hp)] + [(q, -a) for q, a in reversed(root_l)]
    nl = len(root_l)
    cls = []
    for i in range(len(top) - 1):
        (r0, a0), (r1, a1) = top[i], top[i + 1]
        on_root = abs(r0 - rf) < 1e-9 * Rp and abs(r1 - rf) < 1e-9 * Rp
        cls.append(CLS_PLAIN if on_root or i < nl - 1 or i >= len(top) - nl else CLS_FLANK)
    return top, cls, rf


def cylFromTop(context, z, m, width, top, cls, r_body, matrix, prefix):
    me = spurElement("tmp", z, width, top, cls, r_body)
    g = makeGear(context, z, me, matrix, m, width, False, prefix=prefix)
    g["lap_rbody"] = float(r_body)
    g["lap_helix"] = 0.0
    g["lap_herring"] = False
    return g


def clockPair(context, zw, zp, m, width, matrix, report, clear=0.4, backlash=None, fillet=0.0, bores=(0.0, 0.0)):
    # wheel (driver) at matrix and pinion in mesh on its +x side. backlash (modules) None: bs 978
    if zp < 5:
        raise LapError("at least 5 leaves on the pinion")
    if backlash is not None and backlash >= 0 and clockLeaf(zp, backlash) < 0.6:
        raise LapError("the backlash leaves the pinion leaves too thin")
    tw, cw, ha, rfw = clockWheelTop(zw, zp, m, clear, backlash=backlash, fillet=fillet)
    tpn, cp, rfp = clockPinionTop(zp, m, ha, clear, backlash, fillet)
    R, Rp = zw * m / 2, zp * m / 2
    bw = bores[0] if bores[0] > 0 else seatBore(min(_autoBore(zw, m), 0.8 * rfw))
    bp = bores[1] if bores[1] > 0 else seatBore(0.5 * rfp)
    if bw >= rfw or bp >= rfp:
        raise LapError("the bore reaches the roots (wheel root radius %.4g, pinion root radius %.4g)" % (rfw, rfp))
    wheel = cylFromTop(context, zw, m, width, tw, cw, bw, matrix, "wheel")
    try:
        pin = cylFromTop(context, zp, m, width, tpn, cp, bp, gearFrame(wheel) @ Matrix.Translation((R + Rp, 0, 0)),
                         "pinion")
    except LapError:
        removeGear(wheel)
        raise
    meshPhase(wheel, pin, (R, 0.0, 0.0))
    for g in (wheel, pin):
        g["lap_clock"] = 1
    bl = math.pi * m - clockLeaf(zp, backlash) * m - math.pi * m / 2
    report.append("cycloidal (clock) pair %d : %d, module %.4g: center distance %.4g, wheel addendum %.3g m, "
                  "pinion leaves %.3g m thick, backlash %.3g at the pitch circle, root clearance %.3g m, root "
                  "fillets %.3g m; the wheel drives"
                  % (zw, zp, m, R + Rp, ha / m, clockLeaf(zp, backlash), bl, clear, fillet))
    return wheel, pin, R + Rp


# ---------------------------------------------------------------------------
# roller chain sprockets (iso 606 / ansi) and timing belt pulleys (gt2, htd, t, mxl, xl, h): wheels with
# one tooth sector per tooth like every gear here. a sector may be stepped along the axis (belt flanges,
# hub): slabs of different outlines stacked on each other, the sector sides one stepped polygon, so the
# neighbouring sectors still meet face to face. the wheels do not mesh with a pair partner: a pair is two
# wheels at the center distance a whole number of links (teeth of the belt) gives
# ---------------------------------------------------------------------------

# roller chains: pitch, roller diameter, inner width (iso 606 "B" series, ansi)
CHAINS = {
    '05B': (8.0, 5.0, 3.0),
    '06B': (9.525, 6.35, 5.72),
    '08B': (12.7, 8.51, 7.75),
    '10B': (15.875, 10.16, 9.65),
    '12B': (19.05, 11.91, 11.68),
    'A25': (6.35, 3.30, 3.18),
    'A35': (9.525, 5.08, 4.77),
    'A40': (12.7, 7.92, 7.85),
    'A50': (15.875, 10.16, 9.40),
    'A60': (19.05, 11.91, 12.57),
}

# timing belts: pitch, groove depth, groove width at the outside circle, form ('round' tooth: an arc of
# the radius that fits depth and width, 'trap' trapezoid with the half angle phi), phi, pitch line
# differential (the outside radius is the pitch radius minus it), usual belt width
BELTS = {
    'GT2-2': (2.0, 0.764, 1.494, 'round', 0.0, 0.254, 6.0),
    'GT2-3': (3.0, 1.169, 2.31, 'round', 0.0, 0.381, 9.0),
    'HTD-3M': (3.0, 1.14, 2.67, 'round', 0.0, 0.381, 9.0),
    'HTD-5M': (5.0, 2.14, 3.67, 'round', 0.0, 0.5715, 15.0),
    'T2.5': (2.5, 0.7, 1.678, 'trap', 20.0, 0.381, 6.0),
    'T5': (5.0, 1.19, 3.264, 'trap', 20.0, 0.646, 10.0),
    'MXL': (2.032, 0.508, 1.321, 'trap', 20.0, 0.254, 6.4),
    'XL': (5.08, 1.27, 3.051, 'trap', 25.0, 0.254, 9.5),
    'H': (12.7, 1.905, 5.359, 'trap', 20.0, 0.381, 19.05),
}


def roundCorner(p0, p1, p2, r, n):
    # the corner p1 of the polyline p0 p1 p2 replaced by an arc of radius r (n segments), tangent to both
    ax, ay = p0[0] - p1[0], p0[1] - p1[1]
    bx, by = p2[0] - p1[0], p2[1] - p1[1]
    la, lb = math.hypot(ax, ay), math.hypot(bx, by)
    ax, ay, bx, by = ax / la, ay / la, bx / lb, by / lb
    ang = math.acos(max(-1.0, min(1.0, ax * bx + ay * by)))
    if ang > math.pi - 1e-6 or r <= 0:
        return [p1]
    t = min(r / math.tan(ang / 2), 0.45 * la, 0.45 * lb)
    r = t * math.tan(ang / 2)
    t0 = (p1[0] + ax * t, p1[1] + ay * t)
    t2 = (p1[0] + bx * t, p1[1] + by * t)
    mx, my = ax + bx, ay + by
    lm = math.hypot(mx, my)
    dc = r / math.sin(ang / 2)
    c = (p1[0] + mx / lm * dc, p1[1] + my / lm * dc)
    a0 = math.atan2(t0[1] - c[1], t0[0] - c[0])
    a1 = math.atan2(t2[1] - c[1], t2[0] - c[0])
    da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    return [(c[0] + r * math.cos(a0 + da * i / n), c[1] + r * math.sin(a0 + da * i / n)) for i in range(n + 1)]


def arcXY(r, a0, a1, step):
    # points on the circle of radius r from the angle a0 to a1 (both included), about step apart
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    return [(r * math.cos(a0 + (a1 - a0) * i / n), r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def sprocketOutline(z, p, d1):
    # one sector of an iso 606 sprocket: the tooth gap centred at the angle 0 (the roller centre on the
    # pitch circle at (R, 0)), the tooth centres on the sides of the sector (angle +-pi/z). points (x, y)
    # from the -pi/z side to the +pi/z side, the class of every segment, the data
    if z < 7:
        raise LapError("a sprocket needs at least 7 teeth")
    pa = 2 * math.pi / z
    R = p / (2 * math.sin(math.pi / z))
    ri = 0.505 * d1 + 0.069 * d1 ** (1.0 / 3.0)               # seat radius
    half = math.radians(60.0 - 45.0 / z)                      # half the seating angle (120 - 90 / z)
    nseat = 4 if _LOW[0] else 14
    seat = [(R - ri * math.cos(t), ri * math.sin(t))
            for t in [-half + 2 * half * i / nseat for i in range(nseat + 1)]]
    S = seat[0]
    # out of the seat the flank continues as an arc of the radius re = 0.12 d1 (z + 2) (iso 606) in the same
    # sense as the seat, tangent to it: its direction turns from the seat's end tangent towards the radial
    re_ = 0.12 * d1 * (z + 2)
    beta0 = -(math.pi / 2 - half)

    def Q(b):
        return (S[0] + re_ * (math.sin(b) - math.sin(beta0)), S[1] + re_ * (-math.cos(b) + math.cos(beta0)))
    da_max = 2 * R + 1.25 * p - d1
    da_min = 2 * R + (1.0 - 1.6 / z) * p - d1
    rda = 0.5 * min(da_max, max(da_min, p * (0.54 + 1.0 / math.tan(math.pi / z))))
    db = p / 500.0 / re_

    def march(wmin):
        b_hi, b_try, hit_r = beta0, beta0, False
        for k in range(1, 8000):
            b_try = beta0 + k * db
            x, y = Q(b_try)
            r_ = math.hypot(x, y)
            th = math.atan2(y, x)
            if r_ > rda:
                hit_r = True
                break
            if r_ * (pa / 2 - abs(th)) < wmin or th > -1e-6 or b_try - beta0 > math.radians(70.0):
                break
            b_hi = b_try
        if hit_r:
            lo, hi = b_hi, b_try
            for _ in range(50):
                mid = 0.5 * (lo + hi)
                if math.hypot(*Q(mid)) > rda:
                    hi = mid
                else:
                    lo = mid
            b_hi = lo
        return b_hi
    # the half tip land at least 0.04 p; a tooth that would stay below the iso tip circle gets a narrower one
    b_hi = march(0.04 * p)
    if math.hypot(*Q(b_hi)) < 0.5 * da_min - 1e-9:
        b_hi = max(b_hi, march(0.015 * p))
    tip = Q(b_hi)
    rt = math.hypot(*tip)
    tht = math.atan2(tip[1], tip[0])
    if not (-pa / 2 + 1e-6 < tht < -1e-6) or b_hi <= beta0:
        raise LapError("the tooth of this sprocket does not form: use more teeth or a smaller roller")
    step = pa / (4 if _LOW[0] else 16)
    land = arcXY(rt, -pa / 2, tht, step)
    nfl = 2 if _LOW[0] else 8
    flank = [Q(beta0 + (b_hi - beta0) * (nfl - i) / nfl) for i in range(1, nfl)]    # from the tip towards the seat
    left = list(land) + flank
    full = left + seat + [(x, -y) for x, y in reversed(left)]
    # land (plain), the flank arc from the tip corner to the seat and the seat (flank), the mirror
    fc = [CLS_PLAIN] * (len(land) - 1) + [CLS_FLANK] * (2 * len(flank) + len(seat) + 1) + [CLS_PLAIN] * (len(land) - 1)
    assert len(fc) == len(full) - 1
    info = {'R': R, 'root': R - ri, 'tip': rt, 'ri': ri, 'half': half}
    return full, fc, info


def pulleyOutline(z, prof):
    # one sector of a timing pulley: the groove centred at the angle 0 (axis along +x), the lands between
    # grooves on the sides of the sector
    P, h, w, form, phi, pld, bw = BELTS[prof]
    if z < 8:
        raise LapError("a timing pulley needs at least 8 teeth")
    pa = 2 * math.pi / z
    PD = z * P / math.pi
    Ro = PD / 2 - pld
    Rb = Ro - h
    if Rb < 0.8 * h:
        raise LapError("too few teeth for this belt: the grooves reach the axis")
    nar = 4 if _LOW[0] else 10
    half = []                                    # from the groove bottom outwards, y >= 0
    if form == 'round':
        rb = w / 2 if h >= w / 2 else (w * w / 4 + h * h) / (2 * h)
        cx = Rb + rb
        half = [(cx - rb * math.cos(t), rb * math.sin(t)) for t in [0.5 * math.pi * i / nar for i in range(nar + 1)]]
        half.append((Ro + 2 * h, rb))
    else:
        ta = math.tan(math.radians(phi))
        wb = w / 2 - h * ta                      # half width of the flat bottom
        if wb <= 0.05 * w:
            raise LapError("belt profile: bottom of the groove closes")
        A, B = (Rb, 0.0), (Rb, wb)
        C = (Rb + 3 * h, wb + 3 * h * ta)
        rc = min(0.35 * h, 0.8 * wb)
        half = [A] + roundCorner(A, B, C, rc, 2 if _LOW[0] else 6) + [C]
    # cut at the outside circle
    path = [half[0]]
    for q0, q1 in zip(half, half[1:]):
        r0, r1 = math.hypot(*q0), math.hypot(*q1)
        if r1 <= Ro:
            path.append(q1)
            continue
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if math.hypot(q0[0] + (q1[0] - q0[0]) * mid, q0[1] + (q1[1] - q0[1]) * mid) > Ro:
                hi = mid
            else:
                lo = mid
        path.append((q0[0] + (q1[0] - q0[0]) * lo, q0[1] + (q1[1] - q0[1]) * lo))
        break
    else:
        raise LapError("belt profile: the groove does not reach the outside circle")
    groove = [(x, -y) for x, y in reversed(path[1:])] + path
    th = math.atan2(groove[0][1], groove[0][0])      # negative: the groove corner on the left
    if th <= -pa / 2 + 1e-4:
        raise LapError("too few teeth for this belt: the grooves run into each other")
    step = pa / (3 if _LOW[0] else 12)
    land = arcXY(Ro, -pa / 2, th, step)
    full = land[:-1] + groove + [(x, -y) for x, y in reversed(land[:-1])]
    fc = [CLS_PLAIN] * (len(land) - 1) + [CLS_FLANK] * (len(groove) - 1) + [CLS_PLAIN] * (len(land) - 1)
    info = {'PD': PD, 'OD': 2 * Ro, 'root': Rb, 'tip': Ro, 'P': P, 'belt': bw}
    return full, fc, info


def discOutline(z, r):
    # a circle of radius r as the outline of a sector (from the -pi/z side to the +pi/z side)
    pa = 2 * math.pi / z
    pts = arcXY(r, -pa / 2, pa / 2, pa / (3 if _LOW[0] else 16))
    return pts, [CLS_PLAIN] * (len(pts) - 1)


def steppedElement(name, z, slabs, r_body):
    # slabs: [(z0, z1, outline [(x, y)] from the -pi/z side to the +pi/z side, classes[, top outline])]
    # stacked along z, z1 of one slab = z0 of the next. a slab with a top outline (as many points as the
    # outline) is a loft from the outline at z0 to it at z1 (a cone under a flange). neighbouring outlines
    # (the top of one slab, the bottom of the next) must not cross: one lies inside the other.
    p = 2 * math.pi / z
    slabs = [tuple(s_) if len(s_) == 5 else (s_[0], s_[1], s_[2], s_[3], s_[2]) for s_ in slabs]
    for s_ in slabs:
        if len(s_[4]) != len(s_[2]):
            raise LapError("a sloped slab needs as many points on top as at the bottom")
    same = []                    # the top of a slab is the bottom of the next: no step between them
    for (za, zb, xa, ca, ta), (zc, zd, xb, cb, tb) in zip(slabs, slabs[1:]):
        if abs(zb - zc) > 1e-9:
            raise LapError("the slabs of a stepped element must touch")
        same.append(len(ta) == len(xb) and all(abs(p0[0] - p1[0]) < 1e-12 and abs(p0[1] - p1[1]) < 1e-12
                                                for p0, p1 in zip(ta, xb)))
        if same[-1]:
            continue
        ra = [math.hypot(*q) for q in ta]
        rb_ = [math.hypot(*q) for q in xb]
        if not (max(ra) < min(rb_) - 1e-9 or max(rb_) < min(ra) - 1e-9):
            raise LapError("a hub or a flange runs into the teeth: its outline must lie clear of them")
    rmin = min(math.hypot(*q) for s_ in slabs for q in s_[2] + s_[4])
    if r_body >= rmin - 1e-6:
        raise LapError("the bore reaches the tooth roots or the hub wall: use a smaller bore")
    body = polar([(r_body, a) for a in reversed(gridAngles(-p / 2, p / 2, p / (2 if _LOW[0] else 16)))])
    bm = bmesh.new()
    zs = sorted({s[0] for s in slabs} | {s[1] for s in slabs})
    B = {zk: [bm.verts.new((x, y, zk)) for x, y in body] for zk in zs}
    Ob, Ot = [], []
    for k, (z0, z1, xy, cl, xt) in enumerate(slabs):
        Ob.append(Ot[k - 1] if k > 0 and same[k - 1] else [bm.verts.new((x, y, z0)) for x, y in xy])
        Ot.append([bm.verts.new((x, y, z1)) for x, y in xt])
    for k, (z0, z1, xy, cl, xt) in enumerate(slabs):
        for i in range(len(xy) - 1):
            bm.faces.new((Ob[k][i], Ob[k][i + 1], Ot[k][i + 1], Ot[k][i])).material_index = cl[i]
    for a, b in zip(zs, zs[1:]):
        for i in range(len(body) - 1):
            bm.faces.new((B[a][i], B[a][i + 1], B[b][i + 1], B[b][i]))
    bm.faces.new(Ob[0] + B[zs[0]])
    bm.faces.new(list(reversed(Ot[-1] + B[zs[-1]])))
    for k in range(len(slabs) - 1):
        if not same[k]:
            bm.faces.new(Ot[k] + Ob[k + 1][::-1])
    # the sides: one stepped polygon each (outline end, bore end of the same side)
    for io, ib in ((-1, 0), (0, -1)):
        poly = [B[zs[0]][ib]]
        for k in range(len(slabs)):
            for v in (Ob[k][io], Ot[k][io]):
                if v is not poly[-1]:
                    poly.append(v)
        poly.append(B[zs[-1]][ib])
        for zk in reversed(zs[1:-1]):
            poly.append(B[zk][ib])
        bm.faces.new(poly).material_index = CLS_PLAIN
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def beltWheel(context, kind, z, key, matrix, bore=0.0, width=0.0, flange=True, flange_ext=1.5, flange_t=1.2,
              hub_d=0.0, hub_len=6.0, hub_both=False, custom=None):
    # kind 'CHAIN' (key of CHAINS, or custom = (pitch, roller d, inner width)) or 'BELT' (key of BELTS)
    if kind == 'CHAIN':
        p, d1, b1 = custom if custom is not None else CHAINS[key]
        out, cl, info = sprocketOutline(z, p, d1)
        W = width if width > 0 else (0.93 if p <= 12.7 else 0.95) * b1
        flange = False
        pitch, tag = p, "p%s" % fmtM(p)
        prefix = "sprocket"
    else:
        P, h, w, form, phi, pld, bw = BELTS[key]
        out, cl, info = pulleyOutline(z, key)
        W = (width if width > 0 else bw) + 1.0                 # the belt and a little play between the flanges
        pitch, tag = P, key
        prefix = "pulley"
    root = info['root']
    r_body = bore if bore > 0 else seatBore(min(2.5, 0.5 * root))
    rf = info['tip'] + flange_ext
    # fdm, the wheel printed axis up as it lies: what hangs over the layer below leans at most the
    # overhang angle from the vertical. the upper flange gets a cone under it (from the tooth tips out
    # to its rim), a lower hub a cone up to what sits on it
    ta = math.tan(math.radians(fdmParams()[2] - 2.0))      # 2 deg steeper than the limit
    disc = lambda r: discOutline(z, r)
    slabs = []
    z_lo, z_hi = -W / 2, W / 2
    if flange:
        slabs.append((z_lo - flange_t, z_lo, disc(rf)[0], disc(rf)[1]))
        slabs.append((z_lo, z_hi, out, cl))
        # the cone under the upper flange from the tooth tips out to its rim (the grooves end under a flat
        # ceiling: a short bridge between the groove walls)
        r0 = info['tip'] + 0.02
        hc = (rf - r0) / ta
        slabs.append((z_hi, z_hi + hc, disc(r0)[0], disc(r0)[1], disc(rf)[0]))
        slabs.append((z_hi + hc, z_hi + hc + flange_t, disc(rf)[0], disc(rf)[1]))
        z_lo -= flange_t
        z_hi += hc + flange_t
    else:
        slabs.append((z_lo, z_hi, out, cl))
    if hub_d > 0:
        rh = hub_d / 2
        if r_body >= rh - 0.2:
            raise LapError("the hub wall is thinner than 0.2: a larger hub or a smaller bore")
        hp, hc_ = disc(rh)
        slabs.append((z_hi, z_hi + hub_len, hp, hc_))
        if hub_both:
            r_t = (rf if flange else root) - 0.02
            low = []
            if r_t > rh + 1e-3:
                h2 = (r_t - rh) / ta
                if h2 >= hub_len:
                    h2, r_t = hub_len, rh + hub_len * ta
                if hub_len - h2 > 1e-6:
                    low.append((z_lo - hub_len, z_lo - h2, hp, hc_))
                low.append((z_lo - h2, z_lo, hp, hc_, disc(r_t)[0]))
            else:
                low.append((z_lo - hub_len, z_lo, hp, hc_))
            slabs = low + slabs
    me = steppedElement("tmp", z, slabs, r_body)
    m = pitch / math.pi                                       # the module of the same pitch
    zmin, zmax = slabs[0][0], slabs[-1][1]
    g = makeGear(context, z, me, matrix, m, zmax - zmin, False, prefix=prefix)
    no = int(g["lap_no"])
    renameGear(g, "%s_%d_%d_tooth_%s" % (prefix, no, z, tag))
    g["lap_rbody"] = float(r_body)
    g["lap_helix"] = 0.0
    g["lap_herring"] = False
    g["lap_wheel"] = kind
    g["lap_wheel_key"] = key
    g["lap_pitch"] = float(pitch)
    g.empty_display_size = info['tip']
    return g, info, W


def beltCenter(L, d1, d2):
    # center distance of an open belt (chain) of the length L about two wheels of the pitch diameters d1 d2
    b = L - math.pi * (d1 + d2) / 2
    disc = b * b - 2 * (d2 - d1) ** 2
    if disc < 0:
        raise LapError("the belt is too short for these wheels")
    return (b + math.sqrt(disc)) / 4


def beltPair(context, kind, z1, z2, key, dist, matrix, report, bore1=0.0, bore2=0.0, width=0.0, flange=True,
             flange_ext=1.5, flange_t=1.2, hub_d=0.0, hub_len=6.0, hub_both=False, custom=None):
    # two wheels on parallel axes: the second on +x at the center distance of the nearest whole number of
    # links (chain: even) / belt teeth, never less than the wheels need
    if kind == 'CHAIN':
        flange = False
    g1, i1, W = beltWheel(context, kind, z1, key, matrix, bore1, width, flange, flange_ext, flange_t, hub_d, hub_len,
                          hub_both, custom)
    try:
        g2, i2, _ = beltWheel(context, kind, z2, key, matrix, bore2, width, flange, flange_ext, flange_t, hub_d,
                              hub_len, hub_both, custom)
    except LapError:
        removeGear(g1)
        raise
    P = float(g1["lap_pitch"])
    if kind == 'CHAIN':
        d1_, d2_ = P / math.sin(math.pi / z1), P / math.sin(math.pi / z2)
    else:
        d1_, d2_ = i1['PD'], i2['PD']
    rr = i1['tip'] + i2['tip'] + (2 * flange_ext if flange else 0.0)
    base = P * 2 if kind == 'CHAIN' else P
    L0 = 2 * dist + math.pi * (d1_ + d2_) / 2 + (d2_ - d1_) ** 2 / (4 * max(dist, 1e-9))
    n = max(1, int(round(L0 / base)))
    while True:
        L = n * base
        try:
            C = beltCenter(L, d1_, d2_)
        except LapError:
            n += 1
            continue
        if C > rr + 1.0 or n > 100000:
            break
        n += 1
    if C <= rr + 1.0:
        removeGear(g1)
        removeGear(g2)
        raise LapError("no belt length gives a usable center distance")
    g2.matrix_world = g1.matrix_world @ Matrix.Translation((C, 0.0, 0.0))
    if kind == 'CHAIN':
        msg = "%s + %s: chain %d links (length %.4g), center distance %.4g (asked %.4g), ratio %.4g" % (
            g1.name, g2.name, 2 * n, 2 * n * P, C, dist, z2 / float(z1))
    else:
        msg = "%s + %s: belt %d teeth (length %.4g), center distance %.4g (asked %.4g), ratio %.4g" % (
            g1.name, g2.name, n, n * P, C, dist, z2 / float(z1))
    return g1, g2, msg


# ---------------------------------------------------------------------------
# gear rack: an empty with n tooth elements, each one pitch of the gost 13755 basic rack (flanks
# 20 deg, addendum m, dedendum 1.25 m, root fillet 0.38 m), linked copies moved along the local x
# by the pitch. local x = along the rack, y = tooth height (pitch line y = 0), z = across (width).
# helical: the teeth sheared along x by tan(b) z (plane flanks, two levels, quads); herringbone by
# tan(b) |z| (three levels)
# ---------------------------------------------------------------------------

def rackProfile(m, clearance=0.25, alpha=20.0, low=False):
    # one pitch from the middle of a space (x = -pi m / 2) to the next (x = pi m / 2), the tooth
    # centred at x = 0: (x, y), pitch line y = 0
    pl = math.pi * m
    al = math.radians(alpha)
    ta = math.tan(al)
    ha, hf = m, (1.0 + clearance) * m
    xf = lambda y: pl / 4 - y * ta          # half tooth width at height y
    left = [(-pl / 2, -hf)]
    rho = 0.0 if low else 0.38 * m
    if rho > 0:
        # fillet tangent to the root line and to the left flank x = -xf(y)
        yc = -hf + rho
        xc = -xf(yc) - rho / math.cos(al)
        if xc - 1e-9 * m < -pl / 2:
            rho = 0.0
    if rho > 0:
        nseg = 6
        for i in range(nseg + 1):
            t = -math.pi / 2 + (math.pi / 2 - al) * i / nseg
            left.append((xc + rho * math.cos(t), yc + rho * math.sin(t)))
    else:
        left.append((-xf(-hf), -hf))
    left.append((-xf(ha), ha))
    right = [(-x, y) for x, y in reversed(left)]
    return left + right


def rackMesh(name, m, width, height, helix, herring, clearance=0.25, low=False, worm=None, blank=False):
    # worm = (r1, lead, sign): a worm rack (nut segment): the axial profile swept along the helix of
    # the worm at every radius, so the teeth wrap around the worm (exact screw contact).
    # blank: a smooth bar up to the tip line (to be cut)
    prof = rackBlankProfile(m) if blank else rackProfile(m, clearance, low=low)
    pl = math.pi * m
    yb = -(1.0 + clearance) * m - height
    if worm is not None:
        r1, lead, sg = worm
        rmin = r1 - m
        # the flanks curve off the middle plane: split every flank into short straight pieces
        dense = [prof[0]]
        for (x0, y0), (x1, y1) in zip(prof, prof[1:]):
            k = 1 if abs(y1 - y0) < 1e-12 else max(1, int(math.ceil(math.hypot(x1 - x0, y1 - y0) / (0.6 if low else 0.35) / m)))
            dense += [(x0 + (x1 - x0) * j / k, y0 + (y1 - y0) * j / k) for j in range(1, k + 1)]
        prof = dense
        ph = math.asin(min(0.999, width / 2 / rmin))
        nl = max(2, int(math.ceil(2 * math.degrees(ph) / (10.0 if low else 4.0))))
        levels = [rmin * math.sin(-ph + 2 * ph * i / nl) for i in range(nl + 1)]

        def mp(x, y, z):
            rho = r1 - y
            return x + sg * lead * math.asin(z / rho) / (2 * math.pi), r1 - math.sqrt(rho * rho - z * z)
    else:
        t = math.tan(math.radians(helix))
        if herring and abs(helix) > 1e-9:
            levels = [-width / 2, 0.0, width / 2]
            sh = lambda z: t * abs(z)
        else:
            levels = [-width / 2, width / 2]
            sh = lambda z: t * z

        def mp(x, y, z):
            return x + sh(z), y
    bm = bmesh.new()
    rows, bots = [], []
    for z in levels:
        row = [bm.verts.new(mp(x, y, z) + (z,)) for x, y in prof]
        rows.append(row)
        bots.append((bm.verts.new((row[0].co.x, yb, z)), bm.verts.new((row[-1].co.x, yb, z))))
    for k in range(len(levels) - 1):
        A, B = rows[k], rows[k + 1]
        for i in range(len(prof) - 1):
            f = bm.faces.new((A[i], A[i + 1], B[i + 1], B[i]))
            f.material_index = CLS_PLAIN if abs(prof[i][1] - prof[i + 1][1]) < 1e-12 else CLS_FLANK
        (la, ra), (lb, rb) = bots[k], bots[k + 1]
        bm.faces.new((la, ra, rb, lb))                         # bottom
        bm.faces.new((A[0], B[0], lb, la))
        bm.faces.new((A[-1], ra, rb, B[-1]))
    bm.faces.new(rows[0] + [bots[0][1], bots[0][0]])
    bm.faces.new(list(reversed(rows[-1] + [bots[-1][1], bots[-1][0]])))
    me = finishMesh(bm, name)
    attachMaterials(me)
    return me


def rackGear(context, n, m, width, height, helix, herring, matrix, clearance=0.25, low=False, worm=None,
             blank=False):
    me = rackMesh("tmp", m, width, height, helix, herring, clearance, low, worm, blank)
    no = nextNumber()
    name = "rack_%d_%d_tooth_m%s" % (no, n, fmtM(m))
    g = bpy.data.objects.new(name, None)
    g.empty_display_type = 'ARROWS'
    context.collection.objects.link(g)
    g.matrix_world = matrix
    me.name = name + "_mesh"
    pl = math.pi * m
    for k in range(n):
        el = bpy.data.objects.new("%s_e%03d" % (name, k + 1), me)
        el["lap_index"] = k
        context.collection.objects.link(el)
        el.parent = g
        el.matrix_parent_inverse = Matrix.Identity(4)
        el.matrix_basis = Matrix.Translation(((k - (n - 1) / 2.0) * pl, 0, 0))
        el.lock_location = el.lock_rotation = el.lock_scale = (True, True, True)
    g["lap_no"] = no
    g["lap_teeth"] = int(n)
    g["lap_module"] = float(m)
    g["lap_width"] = float(width)
    g["lap_internal"] = False
    g["lap_kind"] = 'RACK'
    g["lap_rack"] = 1
    g["lap_helix"] = float(helix)
    g["lap_herring"] = bool(herring)
    if worm is not None:
        g["lap_wormrack"] = float(worm[0])
    return g


RACK_SIGN = 1.0
RACK_TWIST = 1.0         # sign of the twist a helical rack tool gives the blank (checked by test)
RACK_CUT = 1.0           # sign of the rack shift a helical gear tool gives the rack blank


def rackPair(context, z, n, m, width, helix, herring, matrix, clearance=0.25, low=False):
    # gear at matrix, the rack below it: its pitch line tangent to the pitch circle, a tooth space of
    # the gear facing the middle tooth of the rack (n odd) or a space (n even)
    g = spurGear(context, z, m, width, True, False, defaultBore(z, m), matrix, helix, clearance=clearance,
                 herring=herring)
    rp = z * m / 2
    p = 2 * math.pi / z
    # a tooth space of the gear straight down (angle -90 deg), then turned on by half a pitch of
    # the rack when the rack has a space in the middle
    off = 0.0 if n % 2 else math.pi * m / 2 / rp
    g.matrix_world = g.matrix_world @ rotZ(-math.pi / 2 - p / 2 + off)
    r = rackGear(context, n, m, width, 2.0 * m, RACK_SIGN * helix, herring,
                 matrix @ Matrix.Translation((0, -rp, 0)), clearance, low)
    return g, r


WR_SIGN = -1.0


def wormRackPair(context, z1, m, q, n, width, length, bore, matrix, clearance=0.25, low=False):
    # worm (axis = local z) and a worm rack under it along the axis: the rack moves by the lead per
    # turn of the worm. width 0: the rack wraps +-35 deg of the worm
    r1 = q * m / 2
    if r1 - m <= 0.5 * m:
        raise LapError("q is too small for a worm rack")
    w = min(width, 1.8 * (r1 - m))
    ln = length if length > 0 else (n + 4) * math.pi * m
    worm = wormGear(context, z1, m, q, ln, bore, matrix, True, clearance)
    lead = z1 * math.pi * m
    # the worm thread crosses the bottom (-y) at u = -lead / 4: a rack tooth half a pitch from it
    sh = 0.5 * math.pi - 0.25 * math.pi * z1 + (0.0 if n % 2 else 0.5 * math.pi)
    mr = matrix @ Matrix.Translation((0, -r1, sh * m)) @ Matrix.Rotation(-math.pi / 2, 4, 'Y')
    r = rackGear(context, n, m, w, 2.0 * m, 0.0, False, mr, clearance, low, (r1, lead, WR_SIGN))
    return worm, r, "%s + %s: worm rack, %d teeth, lead %.4g per worm turn, face width %.4g" % (
        worm.name, r.name, n, lead, w)


# ---------------------------------------------------------------------------
# swiss lever escapement: an escape wheel with club teeth (turning clockwise, seen from +z) and the
# pallet fork (lever) above it. tangential lock: the locking corners of the pallets lie where the
# tangents from the pallet arbor touch the locking circle of the wheel (the pallets span `span`
# pitches). the fork swings +-phi (lock + lift) / 2 between the locks; the lift is shared: the
# pallet lift of the entry pallet is given, the club (impulse face of the tooth, from the locking
# corner at R out to the heel at Rh) and the exit pallet follow from equal drops on both pallets.
# locking faces inclined by the draw angle, so that the tooth pulls the pallet into the lock.
# the design is checked by rolling the pair: lock, unlock, impulse, drop, lock again (see tests)
# ---------------------------------------------------------------------------

def _rotp(p, a, c=(0.0, 0.0)):
    x, y = p[0] - c[0], p[1] - c[1]
    ca, sa = math.cos(a), math.sin(a)
    return (c[0] + ca * x - sa * y, c[1] + sa * x + ca * y)


def _pol(r, a):
    return (r * math.cos(a), r * math.sin(a))


def _ang(p):
    return math.atan2(p[1], p[0])


def _add(a, b, k=1.0):
    return (a[0] + k * b[0], a[1] + k * b[1])


def _newton(f, x, tol=1e-12, it=60):
    # small newton with a numeric jacobian
    x = np.array(x, dtype=float)
    for _ in range(it):
        F = np.array(f(x))
        if np.abs(F).max() < tol:
            return x, True
        J = np.empty((len(F), len(x)))
        for j in range(len(x)):
            dx = np.zeros(len(x))
            dx[j] = 1e-7
            J[:, j] = (np.array(f(x + dx)) - F) / 1e-7
        try:
            step = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            return x, False
        lam = 1.0
        n0 = np.abs(F).max()
        while lam > 1e-4:
            xn = x + lam * step
            if np.abs(np.array(f(xn))).max() < n0:
                break
            lam *= 0.5
        x = xn
    return x, np.abs(np.array(f(x))).max() < 1e-8


def escapeDesign(N, m, lock=1.5, lift=8.5, plift=5.0, club=None, drop=1.5, draw=12.0, span=None, run=0.5):
    R = N * m / 2                                   # locking circle of the wheel
    p = 2 * math.pi / N
    if club is None:
        club = 5.0 * 15.0 / N                       # the club spans about a fifth of the pitch
    if span is None:
        # the pallets embrace a half-integer number of pitches, about 60 deg (2.5 for 15 teeth)
        span = max(1.5, math.floor(N * 60.0 / 360.0) + 0.5)
    L, A, Ap = math.radians(lock), math.radians(lift), math.radians(plift)
    Phi = (L + A) / 2
    half = span * p / 2
    d = R / math.cos(half)
    P = (0.0, d)
    aE, aX = math.pi / 2 + half, math.pi / 2 - half
    dr, ct = math.radians(drop), math.radians(club)
    CE = _rotp(_pol(R, aE), -(Phi - L), P)
    CX = _rotp(_pol(R, aX), Phi - L, P)

    def entry(wp, wc):
        DE = _rotp(_pol(R, aE - wp), -(Phi - L - Ap), P)
        h = _rotp(_rotp(DE, -Phi, P), wp + wc)
        return DE, math.hypot(*h), _ang(h) - aE

    def exitSide(wp, apx, c):
        DX = _rotp(_pol(R, aX - wp), Phi - L - apx, P)
        hw = _rotp(DX, Phi, P)
        return DX, math.hypot(*hw), aX + c - _ang(hw) - wp

    def g(x):
        wpE, wcE, wpX, apx = x
        DE, Rh, c = entry(wpE, wcE)
        DX, Rhx, wcX = exitSide(wpX, apx, c)
        return [p / 2 - wpE - wcE - dr, p / 2 - wpX - wcX - dr, (Rhx - Rh) / R * 100, (c - ct) * 10]
    x0 = [p / 2 - dr - ct, ct, p / 2 - dr - ct, Ap]
    x, ok = _newton(g, x0)
    if not ok:
        raise LapError("no escapement for these angles (try a smaller lift or club, or a larger drop)")
    wpE, wcE, wpX, apx = x
    DE, Rh, c = entry(wpE, wcE)
    DX, _, wcX = exitSide(wpX, apx, c)
    if min(wpE, wcE, wpX, wcX) <= 0 or apx <= 0 or apx >= A or Rh <= R:
        raise LapError("the escapement does not close for these angles (lift %.3g: pallet %.3g / %.3g deg)"
                       % (lift, plift, math.degrees(apx)))
    des = dict(N=N, m=m, R=R, p=p, d=d, P=P, aE=aE, aX=aX, Phi=Phi, run=math.radians(run), L=L, A=A,
               CE=CE, DE=DE, CX=CX, DX=DX, Rh=Rh, c=c, draw=math.radians(draw),
               wpE=wpE, wcE=wcE, wpX=wpX, wcX=wcX, ApE=Ap, ApX=apx)
    des["fE"] = _lockDir(des, CE, True)
    des["fX"] = _lockDir(des, CX, False)
    return des


def _lockDir(des, C, entry):
    # the locking face through the locking corner: the radius of the wheel turned by the draw angle,
    # the way that makes the tooth pull the pallet into the lock
    l = math.hypot(*C)
    u = (C[0] / l, C[1] / l)
    P = des["P"]
    for sg in (1.0, -1.0):
        f = _rotp(u, sg * des["draw"])
        n = (-f[1], f[0])
        t = (u[1], -u[0])                           # the wheel turns clockwise
        if n[0] * t[0] + n[1] * t[1] < 0:
            n = (-n[0], -n[1])
        r = (C[0] - P[0], C[1] - P[1])
        tau = r[0] * n[1] - r[1] * n[0]
        if (tau > 0) == entry:
            return f
    raise LapError("no draw direction")


def escapeToothPoints(des, a0, rake=24.0, depth=0.25):
    # the tooth with its locking corner at a0 (wheel frame): root of the locking face F, locking
    # corner K, club face to the heel H, the back flank (a curve) down to the root at B
    R, Rh, c, p = des["R"], des["Rh"], des["c"], des["p"]
    Rr = R - depth * (2 * math.pi * R / des["N"]) * 2.4
    rk = math.radians(rake)
    K = _pol(R, a0)
    H = _pol(Rh, a0 + c)
    u = (math.cos(a0), math.sin(a0))
    t = (-math.sin(a0), math.cos(a0))
    f = (-u[0] * math.cos(rk) + t[0] * math.sin(rk), -u[1] * math.cos(rk) + t[1] * math.sin(rk))
    b = 2 * (K[0] * f[0] + K[1] * f[1])
    s = (-b - math.sqrt(b * b - 4 * (R * R - Rr * Rr))) / 2
    F = _add(K, f, s)
    B = _pol(Rr, _ang(H) + 0.45 * p)
    ctrl = _pol((Rh + Rr) / 2 * 0.98, _ang(H) + 0.15 * p)
    ns = 4 if _LOW[0] else 10
    back = []
    for i in range(1, ns + 1):
        q = i / ns
        back.append(((1 - q) ** 2 * H[0] + 2 * (1 - q) * q * ctrl[0] + q * q * B[0],
                     (1 - q) ** 2 * H[1] + 2 * (1 - q) * q * ctrl[1] + q * q * B[1]))
    return F, K, H, back, B, Rr


def escapeWheelElement(des, r_bore):
    # one sector of the wheel (the tooth whose corner lies at angle 0), from the middle of the root
    # before it to the middle of the root after it, down to the bore: (points, classes)
    p = des["p"]
    F, K, H, back, B, Rr = escapeToothPoints(des, 0.0)
    aF, aB = _ang(F), _ang(B)
    s0 = 0.5 * (aB - p + aF)                        # between the back of the tooth before and F
    s1 = s0 + p
    step = p / (6 if _LOW[0] else 24)
    pts, cls = [], []

    def put(q, c):
        pts.append(q)
        cls.append(c)
    put(_pol(r_bore, s0), CLS_PLAIN)
    for a in gridAngles(s0, aF, step)[:-1]:
        put(_pol(Rr, a), CLS_PLAIN)
    put(F, CLS_FLANK)                               # locking face F -> K
    put(K, CLS_FLANK)                               # club (impulse face) K -> H
    put(H, CLS_PLAIN)
    for q in back[:-1]:
        put(q, CLS_PLAIN)
    for a in gridAngles(aB, s1, step)[:-1]:
        put(_pol(Rr, a), CLS_PLAIN)
    put(_pol(Rr, s1), CLS_PLAIN)
    for a in reversed(gridAngles(s0, s1, step)[1:]):
        put(_pol(r_bore, a), CLS_PLAIN)
    return pts, cls, Rr


def _hull(pts):
    P = sorted(set(pts))
    if len(P) < 3:
        return P

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for q in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(P):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], q) <= 0:
            hi.pop()
        hi.append(q)
    return lo[:-1] + hi[:-1]


def _circle(c, r, n):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def forkOutline(des, lever=None, pin=None, stone_len=0.3, hub=0.16, gap=0.03):
    # the pallet fork in its own frame (the pallet arbor at the origin, the wheel centre at (0, -d)):
    # stones, arms, hub, lever with the fork horns. (points, classes), plus the lever length
    R, d, m = des["R"], des["d"], des["m"]
    P = des["P"]
    lever = lever if lever is not None else 1.1 * d
    pin = pin if pin is not None else 0.1 * R
    sl = stone_len * R
    nc = 16 if _LOW[0] else 64

    def loc(q):
        return (q[0] - P[0], q[1] - P[1])
    CE, DE, CX, DX = (loc(des[k]) for k in ("CE", "DE", "CX", "DX"))
    fE, fX = des["fE"], des["fX"]
    sE = [CE, DE, _add(DE, fE, sl), _add(CE, fE, sl)]
    sX = [CX, DX, _add(DX, fX, sl), _add(CX, fX, sl)]
    rh = hub * R
    hubc = _circle((0.0, 0.0), rh, nc)
    # arms: hull of the hub and the outer half of each stone
    armE = _hull(hubc + [_add(DE, fE, 0.5 * sl), _add(CE, fE, 0.5 * sl), sE[2], sE[3]])
    armX = _hull(hubc + [_add(DX, fX, 0.5 * sl), _add(CX, fX, 0.5 * sl), sX[2], sX[3]])
    # lever up (away from the wheel), the horns at its end with the notch for the impulse pin
    wl = 0.11 * R
    lv = [(-wl / 2, 0.0), (wl / 2, 0.0), (wl / 2, lever), (-wl / 2, lever)]
    hw = pin / 2 + 0.09 * R
    head = [(-hw, lever - 0.05 * R), (hw, lever - 0.05 * R), (hw, lever + 0.3 * R), (-hw, lever + 0.3 * R)]
    notch = [(-pin / 2, lever + 0.05 * R), (pin / 2, lever + 0.05 * R), (pin / 2, lever + 0.4 * R),
             (-pin / 2, lever + 0.4 * R)]
    # clearance: the wheel (out to the heels) in every position of the fork
    rc = des["Rh"] + gap * R
    ph = des["Phi"] + des["run"]
    clear = []
    for k in range(7):
        a = -ph + 2 * ph * k / 6
        clear.append(_circle(_rotp((0.0, -d), -a), rc, nc * 2))
    wk = lambda q: [CLS_PLAIN] * len(q)
    stE_cls = [CLS_FLANK, CLS_PLAIN, CLS_PLAIN, CLS_FLANK]   # impulse face C->D, locking face C'->C
    loops = [(sE, stE_cls), (sX, list(stE_cls)), (hubc, wk(hubc)), (armE, wk(armE)), (armX, wk(armX)),
             (lv, wk(lv)), (head, wk(head)), (notch, wk(notch))] + [(c, wk(c)) for c in clear]

    def keep(ins):
        body = ins[2] | ins[3] | ins[4] | ins[5] | ins[6]
        body &= ~ins[7]
        for c in ins[8:]:
            body &= ~c
        return body | ins[0] | ins[1]
    pts, att = region2d(loops, keep)
    if not pts:
        raise LapError("the fork outline could not be made")
    att = [a[1] if isinstance(a, tuple) else a for a in att]
    return pts, att, lever


def prismMesh(name, outer, cls, holes, z0, z1):
    # an outline (with holes: circles) extruded from z0 to z1; caps triangulated
    outer, cls = dedupe(list(outer), list(cls))
    bm = bmesh.new()
    loops = [(outer, cls)] + [(h, [CLS_PLAIN] * len(h)) for h in holes]
    rows = []
    for k, (lp, cl) in enumerate(loops):
        if (area2(lp) < 0) != (k > 0):
            lp = lp[::-1]
            cl = cl[::-1][1:] + cl[::-1][:1]
        lo = [bm.verts.new((x, y, z0)) for x, y in lp]
        hi = [bm.verts.new((x, y, z1)) for x, y in lp]
        n = len(lp)
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
            f.material_index = cl[i]
        rows.append((lp, lo, hi))
    allp = [q for lp, lo, hi in rows for q in lp]
    vlo = [v for lp, lo, hi in rows for v in lo]
    vhi = [v for lp, lo, hi in rows for v in hi]
    edges, faces, b = [], [], 0
    for lp, lo, hi in rows:
        n = len(lp)
        edges += [(b + i, b + (i + 1) % n) for i in range(n)]
        faces.append(list(range(b, b + n)))
        b += n
    ov, oe, of, overts, oedges, ofaces = mathutils.geometry.delaunay_2d_cdt(
        [Vector(q) for q in allp], edges, faces, 3, 1e-9 * max(1e-9, max(abs(c) for q in allp for c in q)), True)
    idx = []
    A = np.array(allp)
    for k, ids in enumerate(overts):
        if ids:
            idx.append(ids[0])
            continue
        dd = np.hypot(A[:, 0] - ov[k][0], A[:, 1] - ov[k][1])
        j = int(dd.argmin())
        if dd[j] > 1e-6 * float(np.ptp(A, axis=0).max()):
            raise LapError("the outline of '%s' crosses itself" % name)
        idx.append(j)
    for tri in of:
        a, b_, c = (idx[i] for i in tri)
        bm.faces.new((vlo[a], vlo[b_], vlo[c]))
        bm.faces.new((vhi[a], vhi[b_], vhi[c]))
    return finishMesh(bm, name)


def makePart(context, me, matrix, name, module, width, tag="m"):
    # a part that does not turn as a gear (the fork, the arms): an empty with one element; its
    # origin is its axis of rotation
    no = nextNumber()
    nm = "%s_%d_%s%s" % (name, no, tag, fmtM(module))
    g = bpy.data.objects.new(nm, None)
    g.empty_display_type = 'SINGLE_ARROW'
    context.collection.objects.link(g)
    g.matrix_world = matrix
    me.name = nm + "_mesh"
    attachMaterials(me)
    el = bpy.data.objects.new(nm + "_e001", me)
    el["lap_index"] = 0
    context.collection.objects.link(el)
    el.parent = g
    el.matrix_parent_inverse = Matrix.Identity(4)
    el.lock_location = el.lock_rotation = el.lock_scale = (True, True, True)
    g["lap_no"] = no
    g["lap_part"] = 1
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    g.empty_display_size = 0.35 * max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
    g["lap_module"] = float(module)
    g["lap_width"] = float(width)
    return g


def escapePair(context, N, m, width, matrix, report, lock=1.5, lift=8.5, drop=1.5, draw=12.0, lever=0.0,
               pin=0.0, bores=(0.0, 0.0), plift=5.0, club=None):
    if N < 12 or N > 40:
        raise LapError("an escape wheel with 12 to 40 teeth")
    des = escapeDesign(N, m, lock, lift, plift, club, drop, draw)
    R, d = des["R"], des["d"]
    # wheel
    F, K, H, back, B, Rr = escapeToothPoints(des, 0.0)
    rb = bores[0] if bores[0] > 0 else 0.15 * R
    if rb >= 0.8 * Rr:
        raise LapError("the wheel bore reaches the roots (root radius %.4g)" % Rr)
    pts, cls, Rr = escapeWheelElement(des, rb)
    me = rackOutlineMesh("tmp", pts, cls, [-width / 2, width / 2], [0.0, 0.0])
    wheel = makeGear(context, N, me, matrix, m, width, False, prefix="escwheel")
    wheel["lap_escape"] = 1
    wheel["lap_rbody"] = float(rb)
    # the aE tooth: rotate the wheel so that tooth k=0 (corner at angle 0) sits at aE, then back to
    # the entry lock with the fork on its banking
    fp, fcl, lv = forkOutline(des, lever * m if lever > 0 else None, pin * m if pin > 0 else None)
    rbf = bores[1] if bores[1] > 0 else 0.06 * R
    fork_me = prismMesh("tmp", fp, fcl, [_circle((0.0, 0.0), rbf, 16 if _LOW[0] else 48)], -width / 2, width / 2)
    phb = des["Phi"] + des["run"]
    w_lock = escapeLockAngle(des, phb)
    wheel.matrix_world = matrix @ rotZ(des["aE"] - w_lock)
    fork = makePart(context, fork_me, matrix @ Matrix.Translation((0.0, d, 0.0)) @ rotZ(phb), "escfork", m,
                    width)
    fork["lap_fork"] = 1
    report.append("swiss lever escapement: wheel %d teeth, module %.4g (locking circle d %.4g, heels d %.4g), "
                  "pallet arbor %.4g above the wheel, lever %.4g; fork swing +-%.3g deg (lock %.3g + lift %.3g, "
                  "run %.3g), pallet lift entry %.3g / exit %.3g deg, club %.3g deg, drop %.3g deg, draw %.3g deg"
                  % (N, m, 2 * R, 2 * des["Rh"], d, lv, math.degrees(phb), lock, lift, math.degrees(des["run"]),
                     math.degrees(des["ApE"]), math.degrees(des["ApX"]), math.degrees(des["c"]), drop, draw))
    return wheel, fork, d


def escapeLockAngle(des, phi):
    # wheel turn (clockwise, from the design position with a tooth corner at aE) at which that
    # corner rests on the entry locking face, the fork at phi
    P = des["P"]
    C = _rotp(des["CE"], phi, P)
    f = _rotp(des["fE"], phi)
    R = des["R"]
    b = 2 * (C[0] * f[0] + C[1] * f[1])
    cc = C[0] ** 2 + C[1] ** 2 - R * R
    disc = b * b - 4 * cc
    if disc < 0:
        return 0.0
    s = max((-b + math.sqrt(disc)) / 2, (-b - math.sqrt(disc)) / 2)
    q = _add(C, f, s)
    return des["aE"] - _ang(q)



# ---------------------------------------------------------------------------
# gravity escapement (double three-legged, after denison): the train only lifts two light arms and
# locks; the pendulum only unlocks and takes its impulse from the weight of the falling arm, so the
# impulse does not depend on the spring, the oil or the wear. layout in the plane of the pendulum
# (x across, y up, the pendulum hangs toward -y), everything built in xy with z the depth:
#   the arms and the pendulum turn about one axis through the origin (the bend of the suspension
#   spring); the locking wheel sits below on its own axis (0, -h). planes from the front:
#   front star + right arm plate | pins R + right lifting stud | disk | pins L + left lifting stud |
#   back star + left arm plate | the pendulum rod (not made) between the two contact pads.
# the wheel turns clockwise, 60 deg per beat. locking faces are arcs about the arm axis (dead lock:
# no recoil, the pressure of the leg passes through the axis); the lifting studs and the pads for the
# rod are radial faces through the axis (no sliding against the rod).
# ---------------------------------------------------------------------------

def gravityDesign(La, lift=1.5, unlock=0.8, h=0.45, Rs=0.12, rl=0.08, rpin=0.014):
    W = (0.0, -h * La)
    Rs, rl, rpin = Rs * La, rl * La, rpin * La
    li, un = math.radians(lift), math.radians(unlock)

    def Q(a):
        return (W[0] + rl * math.cos(a), W[1] + rl * math.sin(a))

    def gR(a):
        q = Q(a)
        return math.atan2(q[0], -q[1]) + math.asin(rpin / math.hypot(*q))

    def gL(a):
        q = Q(a)
        return math.atan2(q[0], -q[1]) - math.asin(rpin / math.hypot(*q))
    grid = [math.radians(-90 + 0.05 * i) for i in range(3601)]
    aR = max(grid, key=gR)
    gridL = [math.radians(90 + 0.05 * i) for i in range(3601)]
    aL = min(gridL, key=gL)
    return dict(La=La, W=W, Rs=Rs, rl=rl, rpin=rpin, lift=li, unlock=un, aR=aR, aL=aL,
                phiR=gR(aR) - li, phiL=gL(aL) + li, gR=gR, gL=gL,
                gamR=math.radians(-30.0), gamL=math.radians(150.0))


def _arc(r, a0, a1, n):
    return [(r * math.cos(a0 + (a1 - a0) * i / n), r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def _rot(pts, a):
    c, s = math.cos(a), math.sin(a)
    return [(c * x - s * y, s * x + c * y) for x, y in pts]


def gravityStar(des, gam, n_leg=3):
    # three pointed legs, the locking corner of leg 0 at angle gam (wheel frame = world at beta 0),
    # the hub; about the wheel axis (origin of the returned points)
    Rs, La = des["Rs"], des["La"]
    rh = 0.045 * La
    pts = []
    nc = 6 if _LOW[0] else 16
    for k in range(n_leg):
        a = gam + 2 * math.pi * k / n_leg
        # leg: from the hub, pointed; the corner at Rs; the hub arc to the next leg
        w = math.radians(28)
        pts += [_pol(rh, a - w), _pol(Rs, a), _pol(rh, a + w)]
        a2 = gam + 2 * math.pi * (k + 1) / n_leg
        for i in range(1, nc):
            aa = a + w + (a2 - w - a - w) * i / nc
            pts.append(_pol(rh, aa))
    return pts


def gravityArm(des, right, width=0.035, gap=0.03):
    # polygons of one arm in its frame at rest (psi = 0), the axis at the origin: hub, two bars of the
    # plate, the pad for the rod, the locking block, the lifting stud and the bridge that joins the
    # stud to the plate. right arm: outward = counter-clockwise, its block below the locking face (the
    # leg comes down onto it); left arm: outward = clockwise, the block above the face
    La, Rs, W = des["La"], des["Rs"], des["W"]
    li, un = des["lift"], des["unlock"]
    s = 1.0 if right else -1.0
    w = width * La
    xa = s * (Rs + gap * La + w)
    A = (xa, W[1])
    rod = 0.008 * La
    eps = s * math.asin(rod / La)
    rhub = 0.05 * La
    hub = _circle((0.0, 0.0), rhub, 12 if _LOW[0] else 40)
    bar1 = _hull([(-rhub * 0.6, 0.0), (rhub * 0.6, 0.0), (A[0] - w / 2, A[1] + w / 2), (A[0] + w / 2, A[1] - w / 2),
                  (A[0] + w / 2, A[1] + w / 2), (A[0] - w / 2, A[1] - w / 2)])
    r0, r1 = 0.9 * La, 1.02 * La
    f0 = (r0 * math.sin(eps), -r0 * math.cos(eps))
    f1 = (r1 * math.sin(eps), -r1 * math.cos(eps))
    pad = [f0, f1, (f1[0] + s * w, f1[1]), (f0[0] + s * w, f0[1])]
    bar2 = _hull([(A[0] - w / 2, A[1]), (A[0] + w / 2, A[1]), (f0[0], f0[1] + w), (f0[0] + s * w, f0[1] + w),
                  pad[3], f0])
    # locking block
    gam = des["gamR"] if right else des["gamL"]
    c = (W[0] + Rs * math.cos(gam), W[1] + Rs * math.sin(gam))
    c = _rot([c], -s * li)[0]                   # the corner seen from the arm at rest
    rc, ac = math.hypot(*c), math.atan2(c[1], c[0])
    face = _arc(rc, ac - s * (un + math.radians(0.2)), ac + s * math.radians(1.0), 4 if _LOW[0] else 12)
    tb = 0.035 * La
    dy = -tb if right else tb                   # the body below (right) or above (left) the face
    block = face + [(xa, face[-1][1]), (xa, face[-1][1] + dy), (face[0][0], face[0][1] + dy)]
    # lifting stud: a radial face through the axis at phi; the pin pushes it outward
    phi = des["phiR"] if right else des["phiL"]
    a0 = des["aR"] if right else des["aL"]
    qs = [math.hypot(W[0] + des["rl"] * math.cos(a0 + math.radians(k)), W[1] + des["rl"] * math.sin(a0 + math.radians(k)))
          for k in range(0, 100, 5)]
    ra, rb = min(qs) - 0.03 * La, max(qs) + 0.02 * La
    fa = (ra * math.sin(phi), -ra * math.cos(phi))
    fb = (rb * math.sin(phi), -rb * math.cos(phi))
    stud = [fa, fb, (A[0], fb[1]), (A[0], fa[1])]
    bridge = [(A[0] - w / 2, fa[1] + 0.005 * La), (A[0] + w / 2, fa[1] + 0.005 * La),
              (A[0] + w / 2, fb[1] - 0.005 * La), (A[0] - w / 2, fb[1] - 0.005 * La)]
    return dict(hub=hub, bar1=bar1, bar2=bar2, pad=pad, block=block, stud=stud, bridge=bridge, s=s)


def _dCircle(r, n, flat=0.8):
    # a bore with a flat (d-shaft): the circle cut at x = flat r
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = r * math.cos(a), r * math.sin(a)
        pts.append((min(x, flat * r), y))
    return dedupe(pts, None)[0]


def _union(polys):
    # one outline of overlapping polygons (region2d: the largest loop)
    loops = [(list(p), [CLS_PLAIN] * len(p)) for p in polys]
    pts, att = region2d(loops, lambda ins: np.any(np.array(ins), axis=0))
    return pts


def meshOfPrisms(name, prisms):
    # several closed prisms (outline, classes or None, holes, z0, z1) in one mesh
    bm = bmesh.new()
    for outer, cls, holes, z0, z1 in prisms:
        me = prismMesh("LAP_tmp", outer, cls if cls is not None else [CLS_PLAIN] * len(outer), holes, z0, z1)
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def gravityPair(context, La, t, gap, matrix, report, lift=1.5, unlock=0.8, bores=(0.0, 0.0)):
    des = gravityDesign(La, lift, unlock)
    W = des["W"]
    nb = 12 if _LOW[0] else 40
    rbw = bores[0] if bores[0] > 0 else 0.02 * La
    rba = bores[1] if bores[1] > 0 else 0.015 * La
    if rbw >= 0.04 * La or rba >= 0.045 * La:
        raise LapError("the bores are too large for the hubs (wheel r < %.3g, arms r < %.3g)" % (0.04 * La, 0.045 * La))
    # planes from the front (z grows backwards)
    z = [0.0]
    for th in (t, gap, t, gap, 0.5 * t, gap, t, gap, t, gap, t):
        z.append(z[-1] + th)
    zF, zPR, zD, zPL, zB, zRod = (z[0], z[1]), (z[2], z[3]), (z[4], z[5]), (z[6], z[7]), (z[8], z[9]), (z[10], z[11])
    # wheel (its axis at its origin)
    starF = gravityStar(des, des["gamR"])
    starB = gravityStar(des, des["gamL"] + math.radians(60))
    rh = 0.045 * La
    hole = [_dCircle(rbw, nb)]
    pinsR = [des["aR"] + 2 * math.pi * k / 3 for k in range(3)]
    pinsL = [des["aL"] + math.radians(60) + 2 * math.pi * k / 3 for k in range(3)]
    np_ = 8 if _LOW[0] else 24
    prisms = [(starF, None, hole, zF[0], zF[1]), (starB, None, hole, zB[0], zB[1]),
              (_circle((0.0, 0.0), rh, nb), None, hole, zF[1], zB[0]),
              (_circle((0.0, 0.0), des["rl"] + 1.6 * des["rpin"], nb), None, hole, zD[0], zD[1])]
    for a in pinsR:
        prisms.append((_circle(_pol(des["rl"], a), des["rpin"], np_), None, [], zF[1], zD[0]))
    for a in pinsL:
        prisms.append((_circle(_pol(des["rl"], a), des["rpin"], np_), None, [], zD[1], zB[0]))
    me_w = meshOfPrisms("tmp", prisms)
    wheel = makePart(context, me_w, matrix @ Matrix.Translation((W[0], W[1], 0.0)), "gravwheel", La, t, tag="L")
    # arms (axis at the origin, the axis of the pendulum)
    arms = []
    for right in (True, False):
        A = gravityArm(des, right)
        plate = _union([A["hub"], A["bar1"], A["bar2"], A["pad"], A["block"], A["bridge"]])
        stud = _union([A["stud"], A["bridge"]])
        zp, zs = (zF, zPR) if right else (zB, zPL)
        zlo, zhi = min(zp[0], zs[0]), max(zp[1], zs[1])
        prisms = [(plate, None, [_circle((0.0, 0.0), rba, nb)], zp[0], zp[1]),
                  (stud, None, [], zs[0], zs[1]),
                  (A["bridge"], None, [], zlo, zhi),
                  (A["pad"], None, [], zp[0] if right else zB[0], zRod[1])]
        me_a = meshOfPrisms("tmp", prisms)
        psi = des["lift"] if right else 0.0
        arm = makePart(context, me_a, matrix @ rotZ(psi), "gravarm_" + ("R" if right else "L"), La, t, tag="L")
        arms.append(arm)
    for g in [wheel] + arms:
        g["lap_gravity"] = 1
    amin = math.degrees(des["lift"] + des["unlock"]) + 0.2
    report.append("gravity escapement (double three-legged): arms %.4g long about the pendulum axis, wheel axis %.4g "
                  "below it, turning clockwise 60 deg per beat; lift %.3g deg, unlock %.3g deg: the pendulum must "
                  "swing more than +-%.3g deg; the rod (width %.3g) runs in the plane z %.3g..%.3g between the pads; "
                  "beat stops (not made) hold each arm at its rest angle 0"
                  % (La, -W[1], lift, unlock, amin, 0.016 * La, zRod[0], zRod[1]))
    return wheel, arms, des


def planetAngles(zs, zr, n):
    # planet positions: equally spaced when (zs + zr) / n is whole, else the nearest angles at which
    # a planet can mesh with sun and ring at once (multiples of 2 pi / (zs + zr))
    k = zs + zr
    if k % n == 0:
        return [2 * math.pi * i / n for i in range(n)], True
    return [2 * math.pi * round(i * k / float(n)) / k for i in range(n)], False


def planetary(context, zs, zp, n, m, width, helix, herring, tooth, clearance, matrix, report):
    # planetary gear set at matrix: sun (zs), n planets (zp) on the carrier radius (zs + zp) m / 2,
    # ring zs + 2 zp cut by the first planet. the planets hang on an empty (the carrier)
    zr = zs + 2 * zp
    if n < 1:
        raise LapError("at least one planet")
    a = (zs + zp) * m / 2
    # neighbouring planets must not touch: tip circles apart
    if n > 1 and 2 * a * math.sin(math.pi / n) <= (zp + 2) * m:
        raise LapError("%d planets of %d teeth do not fit around the sun (their tips touch): fewer planets or "
                       "smaller planets" % (n, zp))
    angs, even = planetAngles(zs, zr, n)
    if not even:
        report.append("WARNING: (sun + ring teeth) / planets = %d / %d is not whole: the planets are not equally "
                      "spaced (the nearest angles where they mesh)" % (zs + zr, n))
    sun = spurGear(context, zs, m, width, tooth, False, defaultBore(zs, m), matrix, helix, clearance=clearance,
                   herring=herring, prefix="sun")
    made = [sun]
    try:
        no = int(sun["lap_no"])
        carrier = bpy.data.objects.new("planet_carrier_%d" % no, None)
        carrier.empty_display_type = 'CIRCLE'
        carrier.empty_display_size = a
        context.collection.objects.link(carrier)
        carrier.matrix_world = gearFrame(sun)
        planets = []
        for i, th in enumerate(angs):
            pm = gearFrame(sun) @ rotZ(th) @ Matrix.Translation((a, 0, 0))
            pl = spurGear(context, zp, m, width, tooth, False, defaultBore(zp, m), pm, -helix, clearance=clearance,
                          herring=herring, prefix="planet")
            made.append(pl)
            if tooth:
                meshPhase(sun, pl, (zs * m / 2 * math.cos(th), zs * m / 2 * math.sin(th), 0.0))
            mw = pl.matrix_world.copy()
            pl.parent = carrier
            pl.matrix_world = mw
            planets.append(pl)
        ring = spurGear(context, zr, m, width, _LOW[0] and tooth, True, zr * m / 2 + 3.5 * m, gearFrame(sun), -helix,
                        clearance=clearance, herring=herring, prefix="ring")
        made.append(ring)
        ring["lap_helix"] = -float(helix)
        ring["lap_herring"] = bool(herring and abs(helix) > 1e-9)
        if tooth and _LOW[0]:
            context.view_layer.update()
            p0 = planets[0]
            meshPhaseInternal(p0, ring, tuple(p0.matrix_world.inverted() @ (gearFrame(sun) @ Vector((zr * m / 2, 0, 0)))))
        elif tooth:
            context.view_layer.update()
            cutWith(context, planets[0], ring, report, clearance)
    except LapError:
        for g in made:
            try:
                removeGear(g)
            except Exception:
                pass
        raise
    return sun, planets, ring, carrier, angs


def newBevelPair(context, z1, z2, m, shaft, width, tooth, bore, clearance, spiral=0.0, herring=False,
                 spiral_in=None, ushape=False, apex=0.0):
    # both gears of a bevel pair; the empties and the common cone apex in the world origin. spiral:
    # the spiral angle of the first gear (the second gets the opposite hand)
    mat = Matrix.Identity(4)
    d1, d2 = bevelAngles(z1, z2, shaft)
    gear = newBevelGear(context, z1, m, d1, width, tooth, bore, mat, clearance, spiral, herring, spiral_in, ushape, apex)
    try:
        g2, info = createMating(context, gear, z2, d2 > math.pi / 2, tooth=tooth)
        if tooth and d2 > math.pi / 2:
            info += " (internal: a blank, made by lapping)"
    except LapError:
        removeGear(gear)
        raise
    return gear, g2, "%s (pitch cone %.4g deg) -> %s: %s" % (gear.name, math.degrees(d1), g2.name, info)


def newWormPair(context, starts, m, q, z2, length, bore, tooth, clearance, tol, matrix):
    # worm and its wheel; auto length: the outer diameter of the wheel (the throat blank
    # d_aM2 = d2 + 2 m + 6 m / (z1 + 2))
    ln = length if length > 0 else (z2 + 2 + 6.0 / (starts + 2)) * m
    gear = wormGear(context, starts, m, q, ln, bore, matrix, tooth, clearance)
    try:
        g2, info = createMating(context, gear, z2, False)
        if tooth and _LOW[0]:
            # low poly: the wheel as a straight helical gear of the lead angle (no throat, not cut)
            mw, b2, w2 = g2.matrix_world.copy(), float(g2["lap_helix"]), float(g2["lap_width"])
            removeGear(g2)
            g2 = spurGear(context, z2, m, w2, True, False, defaultBore(z2, m), mw, b2, clearance=clearance,
                          prefix="wormwheel")
            info = "low poly wheel, helix %.4g deg" % b2
        elif tooth:
            rep = []
            wormWheelTeeth(context, gear, g2, rep, clearance, tol=tol)
            info += "; " + rep[-1]
    except LapError:
        removeGear(gear)
        raise
    return gear, g2, "%s (%d start(s), q %.4g, length %.4g) -> %s: %s" % (gear.name, starts, q, ln, g2.name, info)


def blankCopy(context, src):
    # smooth blank with the teeth, place and size of the source
    checkRotary(src, "a blank copy")
    checkVersion(src)
    z = int(src["lap_teeth"])
    me = gearMesh(src)
    if isBevel(src):
        return bevelGear(context, z, float(src["lap_module"]), math.radians(float(src["lap_delta"])),
                         float(src["lap_lin"]), float(src["lap_lout"]), False, float(src.get("lap_bore", 0.0)),
                         src.matrix_world.copy(), spiral=float(src.get("lap_spiral", 0.0)),
                         herring=bool(src.get("lap_herring", False)),
                         spiral_in=float(src["lap_spiral_in"]) if "lap_spiral_in" in src else None,
                         ushape=bool(src.get("lap_ushape", False)),
                         lc=float(src["lap_lmid"]) if "lap_lmid" in src else None)
    if "lap_rbody" in src:
        # the same radial range as the source (tip circle, bore), helix and face flags kept
        internal = bool(src.get("lap_internal", False))
        rr = [math.hypot(v.co.x, v.co.y) for v in me.vertices]
        zz = [v.co.z for v in me.vertices]
        p = 2 * math.pi / z
        r_tip = min(rr) if internal else max(rr)
        if src.get("lap_worm"):
            el = wormSweep("tmp", z, float(src["lap_axial_module"]), [(0.0, r_tip)], [CLS_PLAIN], min(zz), max(zz),
                           float(src["lap_rbody"]))
            g = makeGear(context, z, el, src.matrix_world.copy(), float(src["lap_module"]), float(src["lap_width"]),
                         internal, prefix="worm", unit="start")
            for key in ("lap_rbody", "lap_helix", "lap_worm", "lap_axial_module", "lap_q"):
                if key in src:
                    g[key] = src[key]
            setWormProfile(g, [(0.0, r_tip)], [CLS_PLAIN])
            return g
        if "lap_throat" in src:
            a_, rho_, cap_ = src["lap_throat"]
            el = throatElement("tmp", z, max(zz) - min(zz), a_, rho_, cap_, float(src["lap_rbody"]))
        else:
            el = spurElement("tmp", z, max(zz) - min(zz), [(r_tip, a) for a in gridAngles(-p / 2, p / 2, p / 16)],
                             None, float(src["lap_rbody"]))
        el.transform(Matrix.Translation((0, 0, 0.5 * (max(zz) + min(zz)))))
        g = makeGear(context, z, el, src.matrix_world.copy(), float(src["lap_module"]), float(src["lap_width"]),
                     internal, prefix="wormwheel" if "lap_throat" in src else "gear")
        for key in ("lap_rbody", "lap_helix", "lap_herring", "lap_face", "lap_worm", "lap_axial_module", "lap_q",
                    "lap_throat"):
            if key in src:
                g[key] = src[key]
        return g
    # gear of an older version or foreign element: blank over the radial range of its mesh
    r = [math.hypot(v.co.x, v.co.y) for v in me.vertices]
    zz = [v.co.z for v in me.vertices]
    m = float(src.get("lap_module", 1.0))
    w = max(zz) - min(zz)
    el = elementMesh("tmp", z, m, w, False, min(r), max(r))
    el.transform(Matrix.Translation((0, 0, 0.5 * (max(zz) + min(zz)))))
    g = makeGear(context, z, el, src.matrix_world.copy(), m, w, False)
    g["lap_rbody"] = min(r)
    return g


def toolMesh(gear, share=0.02):
    # copy of the element mesh with both ends pushed out by share of the face width: the tool then
    # reaches past the ends of a target of the same width, and no end faces coincide. every point
    # moves along the tooth line (along z for cylindrical gears, along its ray from the apex for
    # bevel gears), so straight teeth keep their flanks exactly
    me = gearMesh(gear).copy()
    me.name = "LAP_tool"
    n = len(me.vertices)
    v = np.empty(n * 3)
    me.vertices.foreach_get("co", v)
    v = v.reshape(-1, 3)
    if isBevel(gear):
        l_in, l_out = float(gear["lap_lin"]), float(gear["lap_lout"])
        e = share * (l_out - l_in)
        L = np.linalg.norm(v, axis=1)
        # rim: [l_in, l_out] -> [l_in - e, l_out + e]; the body nearer the apex is scaled along
        L2 = np.where(L >= l_in, l_in - e + (L - l_in) * (l_out - l_in + 2 * e) / (l_out - l_in),
                      L * (l_in - e) / l_in)
        v = v * (L2 / np.maximum(L, 1e-30))[:, None]
    else:
        z0, z1 = v[:, 2].min(), v[:, 2].max()
        e = share * (z1 - z0)
        v[:, 2] = z0 - e + (v[:, 2] - z0) * (z1 - z0 + 2 * e) / max(z1 - z0, 1e-30)
    me.vertices.foreach_set("co", v.ravel())
    me.update()
    return me


# ---------------------------------------------------------------------------
# kinematics and inside tests
# ---------------------------------------------------------------------------

# gears turned slower than their teeth say (name -> factor), set for one imprint: a wheel of 4
# lobes slowed 3 times turns like one of 12 teeth, so the worm gets a thread of a third of the lead
_SLOW = {}
_TURN = [2 * math.pi]         # the target turn of one cycle of the pair (more than 2 pi when slowed)


def slowCycle(src, tgt, zt):
    # a slowed pair repeats after N turns of the target (N = ks / gcd(ks, zt), ks and kt coprime);
    # positions per turn times kt, so the source moves no more per step than without slowdown.
    # returns (N, factor on the number of positions) and sets _TURN
    ks, kt = _SLOW.get(src.name, 1), _SLOW.get(tgt.name, 1)
    N = ks // math.gcd(ks, zt)
    _TURN[0] = 2 * math.pi * N
    return N, N * kt


def relative(src, tgt, zs, zt, sign, beta):
    # source element 0 local coords -> target frame coords, target turned by beta
    alpha = sign * (zt * _SLOW.get(tgt.name, 1) / float(zs * _SLOW.get(src.name, 1))) * beta
    fs = gearFrame(src)
    ft = gearFrame(tgt)
    return rotZ(-beta) @ ft.inverted() @ fs @ rotZ(alpha) @ fs.inverted() @ src.matrix_world


def insideParity(tree, p, eps):
    dirs = (Vector((0.3141, 0.7272, 0.6112)), Vector((-0.8017, 0.2861, 0.5244)),
            Vector((0.2218, -0.8697, 0.4409)))
    votes = 0
    for d in dirs:
        d = d.normalized()
        o = p.copy()
        cnt = 0
        for _ in range(100):
            loc, nor, idx, dist = tree.ray_cast(o, d)
            if loc is None:
                break
            cnt += 1
            o = loc + d * eps
        votes += cnt & 1
    return votes >= 2


def insideGear(tree, zs, q, eps):
    # q in the frame of a gear; fold its angle into element 0 (elements are identical)
    p = 2 * math.pi / zs
    j = round(math.atan2(q.y, q.x) / p)
    return insideParity(tree, rotZ(-j * p) @ q, eps)


def meshBox(me):
    v = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", v)
    v = v.reshape(-1, 3)
    return v.min(axis=0), v.max(axis=0)


def removedFraction(src, tgt, zs, zt, sign, tree_s, tree_t, me_t, size, removed=None):
    # share of the target element that the source sweeps away with this direction
    lo, hi = meshBox(me_t)
    rnd = random.Random(7)
    pts = []
    eps = size * 2e-5
    tries = 0
    while len(pts) < 150 and tries < 5000:
        tries += 1
        q = Vector((rnd.uniform(lo[0], hi[0]), rnd.uniform(lo[1], hi[1]), rnd.uniform(lo[2], hi[2])))
        if insideParity(tree_t, q, eps):
            pts.append(q)
    e_t = elements(tgt)[0]
    ft = gearFrame(tgt)
    pts = [ft.inverted() @ (e_t.matrix_world @ q) for q in pts]
    steps = zt * 4
    hit = [False] * len(pts)
    where = [None] * len(pts)
    for k in range(steps):
        beta = 2 * math.pi * k / steps
        m = relative(src, tgt, zs, zt, sign, beta).inverted()
        for i, q in enumerate(pts):
            if not hit[i] and insideGear(tree_s, zs, m @ q, eps):
                hit[i] = True
                where[i] = rotZ(beta) @ q          # the point when it is cut, in the resting target frame
    if removed is not None:
        removed += [w for w, h in zip(where, hit) if h]
    return sum(hit) / float(max(1, len(pts)))


# ---------------------------------------------------------------------------
# sweep: positions and ramps
# ---------------------------------------------------------------------------

def triangulateSafe(bm):
    # triangulate without creating an edge twice: an n-gon of the boolean result can have two
    # vertices that another face already joins by an edge (next to needle triangles), and a plain
    # triangulation would put a third and fourth face on that edge. such faces get a centre vertex
    for _ in range(5):
        bm.verts.index_update()
        tb = bm.copy()
        bmesh.ops.triangulate(tb, faces=tb.faces)
        bad = {(e.verts[0].index, e.verts[1].index) for e in tb.edges if len(e.link_faces) != 2}
        tb.free()
        if not bad:
            break
        bm.verts.ensure_lookup_table()
        sel = set()
        for i, j in bad:
            a, b = bm.verts[i], bm.verts[j]
            for f in set(a.link_faces) & set(b.link_faces):
                vs = list(f.verts)
                d = (vs.index(a) - vs.index(b)) % len(vs)
                if len(vs) > 3 and d not in (1, len(vs) - 1):
                    sel.add(f)
        if not sel:
            break
        bmesh.ops.poke(bm, faces=list(sel))
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 3])


def triangles(me):
    # vertices, triangles and the pairs of triangles sharing an edge
    bm = bmesh.new()
    bm.from_mesh(me)
    triangulateSafe(bm)
    bm.verts.index_update()
    bm.faces.index_update()
    verts = np.array([tuple(v.co) for v in bm.verts])
    tris = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64)
    pairs = np.array([[e.link_faces[0].index, e.link_faces[1].index] for e in bm.edges
                      if len(e.link_faces) == 2], dtype=np.int64).reshape(-1, 2)
    bm.free()
    return verts, tris, pairs


def npApply(m, v):
    a = np.array(m)
    return v @ a[:3, :3].T + a[:3, 3]


def rampPrisms(verts, tris, pairs, m0, m1, lo, hi, min_area):
    # the motion between two positions as convex prisms: for every face that moves forward and lies
    # near the target, the convex hull of the face at both positions. the union covers the swept
    # volume (a point entering the tooth passes a forward face), and convex bodies cannot fold
    p0 = npApply(m0, verts)
    p1 = npApply(m1, verts)
    p1 = p1 + (p1 - p0) * RAMP_OVERLAP
    a0, b0, c0 = p0[tris[:, 0]], p0[tris[:, 1]], p0[tris[:, 2]]
    a1, b1, c1 = p1[tris[:, 0]], p1[tris[:, 1]], p1[tris[:, 2]]
    n = np.cross(b0 - a0, c0 - a0)
    d = (a1 + b1 + c1 - a0 - b0 - c0) / 3.0
    nd = np.einsum("ij,ij->i", n, d)
    cosnd = nd / np.maximum(np.linalg.norm(n, axis=1) * np.linalg.norm(d, axis=1), 1e-30)
    # the space missed between two positions lies at the silhouette (where the surface turns from
    # forward to rear facing); elsewhere the tooth at the next position covers it. prisms only for
    # forward faces next to a rear face (sharp edges) or moving nearly in their own plane
    # the space missed between two positions is only noticeable where the silhouette runs along a
    # sharp edge (the surface turns from forward to rear facing over one edge); on a smooth surface
    # the positions alone leave a scallop of about step^2 / (8 radius). prisms for the forward face
    # at every silhouette edge sharper than CREASE_DEG
    nlen = np.linalg.norm(n, axis=1)
    nn = n / np.maximum(nlen, 1e-30)[:, None]
    f0 = pairs[:, 0]
    f1 = pairs[:, 1]
    # faces moving in their own plane (end caps) are neutral; slivers left by earlier booleans have
    # random normals and are ignored
    big = nlen > 2.0 * min_area
    sil = (((cosnd[f0] > NEUTRAL_COS) & (cosnd[f1] < -NEUTRAL_COS)) |
           ((cosnd[f1] > NEUTRAL_COS) & (cosnd[f0] < -NEUTRAL_COS))) & big[f0] & big[f1]
    sharp = np.einsum("ij,ij->i", nn[f0], nn[f1]) < math.cos(math.radians(CREASE_DEG))
    e = sil & sharp
    front = np.zeros(len(tris), dtype=bool)
    front[np.where(cosnd[f0[e]] > 0, f0[e], f1[e])] = True
    tmin = np.minimum.reduce([a0, b0, c0, a1, b1, c1])
    tmax = np.maximum.reduce([a0, b0, c0, a1, b1, c1])
    near = np.all((tmax >= lo) & (tmin <= hi), axis=1)
    idx = np.nonzero(front & near)[0]
    if len(idx) == 0:
        return None
    bm = bmesh.new()
    for i in idx:
        pts = [a0[i], b0[i], c0[i], a1[i], b1[i], c1[i]]
        # grow each prism a little about its centre: neighbours overlap instead of touching
        # face to face (touching faces leave zero-thickness films in the boolean)
        cen = sum(pts) / 6.0
        pts = [cen + (q - cen) * (1.0 + PRISM_GROW) for q in pts]
        vs = [bm.verts.new(tuple(q)) for q in pts]
        res = bmesh.ops.convex_hull(bm, input=vs)
        # drop degenerate (flat) hulls and leftovers
        for g in res["geom_interior"] + res["geom_unused"]:
            if isinstance(g, bmesh.types.BMVert) and g.is_valid:
                bm.verts.remove(g)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("LAP_prisms")
    bm.to_mesh(me)
    bm.free()
    return me


def splitPieces(me, min_thick=0.0):
    # one mesh per connected piece (each prism is a separate closed body); open or flat pieces
    # (thinner than min_thick on average) are dropped
    bm = bmesh.new()
    bm.from_mesh(me)
    out = []
    seen = set()
    bm.verts.ensure_lookup_table()
    for f in bm.faces:
        if f.index in seen:
            continue
        stack = [f]
        comp = []
        seen.add(f.index)
        while stack:
            g = stack.pop()
            comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        stack.append(h)
        vmap = {}
        nb = bmesh.new()
        for g in comp:
            vv = []
            for v in g.verts:
                if v.index not in vmap:
                    vmap[v.index] = nb.verts.new(v.co)
                vv.append(vmap[v.index])
            try:
                nb.faces.new(vv)
            except ValueError:
                pass                     # duplicate face left by the boolean
        ok = all(e.is_manifold for e in nb.edges) and len(nb.faces) >= 4
        if ok:
            vol = abs(nb.calc_volume())
            area = sum(f.calc_area() for f in nb.faces)
            ok = area > 0 and vol / area > min_thick
        if ok:
            pm = bpy.data.meshes.new("LAP_prism")
            nb.to_mesh(pm)
            out.append(pm)
        nb.free()
    bm.free()
    return out


def packDisjoint(pieces):
    # join pieces whose bounding boxes do not touch into shared meshes: a set of disjoint closed
    # bodies is a valid operand, and every operand costs the boolean about the same time
    boxes = []
    for pm in pieces:
        lo_, hi_ = meshBox(pm)
        boxes.append((lo_, hi_))
    groups = []          # (list of pieces, array lo, array hi)
    for pm, (lo_, hi_) in zip(pieces, boxes):
        placed = False
        for g in groups:
            glo_ = np.array(g[1])
            ghi_ = np.array(g[2])
            hit = np.all((ghi_ >= lo_) & (glo_ <= hi_), axis=1)
            if not hit.any():
                g[0].append(pm)
                g[1].append(lo_)
                g[2].append(hi_)
                placed = True
                break
        if not placed:
            groups.append(([pm], [lo_], [hi_]))
    out = []
    for g in groups:
        bm = bmesh.new()
        for pm in g[0]:
            bm.from_mesh(pm)
        me = bpy.data.meshes.new("LAP_pack")
        bm.to_mesh(me)
        bm.free()
        out.append(me)
    for pm in pieces:
        bpy.data.meshes.remove(pm)
    return out


def dropCrumbs(me):
    # remove loose pieces of negligible volume left by the boolean
    pieces = splitPieces(me)
    if len(pieces) <= 1:
        for pm in pieces:
            bpy.data.meshes.remove(pm)
        return me
    vols = [abs(meshCheck(pm)[1]) for pm in pieces]
    if not vols:
        return me
    keep = [pm for pm, v in zip(pieces, vols) if v > 1e-4 * max(vols)]
    bm = bmesh.new()
    for pm in keep:
        bm.from_mesh(pm)
    for pm in pieces:
        bpy.data.meshes.remove(pm)
    out = bpy.data.meshes.new("LAP_res")
    bm.to_mesh(out)
    bm.free()
    bpy.data.meshes.remove(me)
    return out


def booleanChecked(context, base_me, base_matrix, tools, report):
    # difference that notices a silently rejected batch (result = input) and bisects it to drop
    # the operand the solver refuses
    res = booleanDifference(context, base_me.copy(), base_matrix, tools)
    if len(tools) == 0 or meshCheck(res)[1] < meshCheck(base_me)[1] - 1e-12 or len(res.polygons) == 0:
        return res
    bpy.data.meshes.remove(res)
    if len(tools) == 1:
        report.append("WARNING: one tool body was rejected by the boolean and skipped")
        return base_me.copy()
    half = len(tools) // 2
    first = booleanChecked(context, base_me, base_matrix, tools[:half], report)
    second = booleanChecked(context, first, base_matrix, tools[half:], report)
    bpy.data.meshes.remove(first)
    return second


def booleanDifference(context, base_me, base_matrix, tools, max_ops=1000000):
    # base minus all tools (mesh, world matrix), in batches of at most max_ops tools
    col = bpy.data.collections.new("LAP_tmp")
    context.scene.collection.children.link(col)
    res = base_me
    i = 0
    while i < len(tools):
        batch = []
        faces = 0
        while i < len(tools) and len(batch) < max_ops and \
                (not batch or faces + len(tools[i][0].polygons) <= BATCH_FACES):
            batch.append(tools[i])
            faces += len(tools[i][0].polygons)
            i += 1
        ops = bpy.data.collections.new("LAP_ops")
        col.children.link(ops)
        base = bpy.data.objects.new("LAP_base", res)
        col.objects.link(base)
        base.matrix_world = base_matrix
        for tme, m in batch:
            o = bpy.data.objects.new("LAP_tool", tme)
            ops.objects.link(o)
            o.matrix_world = m
        md = base.modifiers.new("lap", 'BOOLEAN')
        md.operation = 'DIFFERENCE'
        md.solver = 'MANIFOLD'
        md.operand_type = 'COLLECTION'
        md.collection = ops
        dg = context.evaluated_depsgraph_get()
        new = bpy.data.meshes.new_from_object(base.evaluated_get(dg), depsgraph=dg)
        for o in list(ops.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.objects.remove(base, do_unlink=True)
        bpy.data.collections.remove(ops)
        if res.users == 0:
            bpy.data.meshes.remove(res)
        res = new
    bpy.data.collections.remove(col)
    return res


# ---------------------------------------------------------------------------
# 2d engine: straight teeth (cylindrical pairs with parallel axes, straight bevel pairs with a common
# apex). the whole imprint happens in one section: the plane z = mid for cylindrical gears, the
# sphere L = mid seen through a gnomonic projection from the apex for bevel gears (every flank is a
# plane through the apex, so its section is a great circle arc and the projection makes it a
# straight line: the section polygons are exact). the target section minus all positions of the
# source section is computed with blender's constrained delaunay triangulation, then the element
# is built again from the new outline: clean topology and the same number of faces every pass
# ---------------------------------------------------------------------------

WORM_QUADS = False            # worm wheel as helical-meridian quads (tested: heavier, rarely possible)
NPOLY = 24                    # source polygons per triangulation on a meridian
CHUNK = 8                     # source positions subtracted per triangulation
SIMPLIFY = 2e-4               # outline tolerance, in modules


def sectionLoop(me, sphere, value):
    # the section of a closed mesh by the plane z = value or the sphere |p| = value: the largest
    # closed loop, as (points, classes of the segments point i -> i + 1)
    bm = bmesh.new()
    bm.from_mesh(me)
    triangulateSafe(bm)
    bm.edges.index_update()
    cross = {}
    for e in bm.edges:
        a, b = e.verts[0].co, e.verts[1].co
        da = (a.length if sphere else a.z) - value
        db = (b.length if sphere else b.z) - value
        if (da < 0) == (db < 0):
            continue
        if sphere:
            d = b - a
            qa, qb, qc = d.dot(d), 2 * a.dot(d), a.dot(a) - value * value
            disc = math.sqrt(max(0.0, qb * qb - 4 * qa * qc))
            ts = [(-qb - disc) / (2 * qa), (-qb + disc) / (2 * qa)]
            t = min(ts, key=lambda x: abs(x - 0.5))
        else:
            t = da / (da - db)
        cross[e.index] = a + (b - a) * t
    nxt = {}
    for f in bm.faces:
        es = [e.index for e in f.edges if e.index in cross]
        if len(es) == 2:
            nxt.setdefault(es[0], []).append((es[1], f.material_index))
            nxt.setdefault(es[1], []).append((es[0], f.material_index))
    bm.free()
    loops = []
    seen = set()
    for start in nxt:
        if start in seen:
            continue
        pts, cls = [], []
        prev, cur = None, start
        while True:
            seen.add(cur)
            pts.append(cross[cur].copy())
            cand = [c for c in nxt[cur] if c[0] != prev] or nxt[cur]
            nx, c = cand[0]
            cls.append(c)
            prev, cur = cur, nx
            if cur == start or cur in seen:
                break
        loops.append((pts, cls))
    if not loops:
        raise LapError("the section of the element is empty")
    return max(loops, key=lambda l: len(l[0]))


def area2(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return 0.5 * a


def clipBoxAttr(poly, vflag, eatt, lo, hi):
    # sutherland-hodgman against an axis aligned box, carrying a flag per point (False for the new points on the box) and an attribute per
    # edge i -> i + 1 (None for the new edges along the box)
    if len(poly) >= 3:
        x0, y0, x1, y1 = lo[0], lo[1], hi[0], hi[1]
        for p in poly:
            if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
                break
        else:                                                # all inside the box: nothing to cut
            return list(poly), list(vflag), list(eatt)
    for axis, val, keep_greater in ((0, lo[0], True), (0, hi[0], False), (1, lo[1], True), (1, hi[1], False)):
        if len(poly) < 3:
            return [], [], []
        out, of, ein = [], [], []
        n = len(poly)
        for i in range(n):
            a = poly[i - 1]
            b = poly[i]
            ea = eatt[i - 1]
            ina = (a[axis] >= val) if keep_greater else (a[axis] <= val)
            inb = (b[axis] >= val) if keep_greater else (b[axis] <= val)
            if inb:
                if not ina:
                    t = (val - a[axis]) / (b[axis] - a[axis])
                    out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                    of.append(False)
                    ein.append(None)
                out.append(b)
                of.append(vflag[i])
                ein.append(ea)
            elif ina:
                t = (val - a[axis]) / (b[axis] - a[axis])
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
                of.append(False)
                ein.append(ea)
        m = len(out)
        poly, vflag, eatt = out, of, [ein[(j + 1) % m] for j in range(m)]
    if len(poly) < 3:
        return [], [], []
    return poly, vflag, eatt


def clipSource(poly, eatt, lo, hi, fill=None):
    # a source section cut to the box about the target section: [(x, y)], per edge (triangle,
    # class); the new edges along the box (outside the target) get fill, or the first attribute
    P, _, E = clipBoxAttr(poly, [True] * len(poly), eatt, lo, hi)
    if len(P) < 3:
        return [], []
    f = fill if fill is not None else eatt[0]
    f = (f[0], CLS_PLAIN)
    return P, [a if a is not None else f for a in E]


def sourceRoles(poly, roles, crease_deg, any_work):
    # the edges of a source section that can pass torque (roles[i]: class of the edge i -> i + 1)
    # and its corners: a turn sharper than crease_deg, or the end of a working edge. a cut made by
    # a non working edge or by a corner (the tip of a tooth, its edges) cannot pass torque: it is
    # parasitic. a source without any working class (a foreign mesh) is taken as working all over
    wk = np.array([working(r) or not any_work for r in roles], dtype=bool)
    P = np.asarray(poly, dtype=float)
    U = P - np.roll(P, 1, axis=0)                   # edge into the point
    W = np.roll(U, -1, axis=0)                      # edge out of it
    lu = np.linalg.norm(U, axis=1)
    lw = np.linalg.norm(W, axis=1)
    ok = (lu > 0) & (lw > 0)
    cs = np.einsum("ij,ij->i", U, W) / np.where(ok, lu * lw, 1.0)
    # 2: a sharp corner (its path cuts a band about it), 1: only the end of a working edge on a
    # smooth outline (only a cut touching it counts)
    corner = np.where(ok & (cs < math.cos(math.radians(crease_deg))), 2, np.where(np.roll(wk, 1) != wk, 1, 0))
    return wk.tolist(), corner.tolist()


def cornerCut(p0, p1, poly, vflag, sg, tol):
    # is the cut edge p0 p1 (a piece of the source edge sg) made near a corner of the source: closer
    # than tol to one of its corner points? such a cut follows the path of the corner (the tip or
    # the end of a working flank), not the flank: it cannot pass torque. a distance instead of the
    # touching corner makes the end of the working flank on the target the image of a fixed point
    # of the source flank, the same in every section and for every phase of the steps
    cs = corners_of(poly, vflag)
    if not cs:
        return False
    a = np.array(p0)
    d = np.array(p1) - a
    ll = float(d @ d)
    C = np.array([q for q, k in cs])
    lim = np.array([tol if k == 2 else 1e-4 * tol for q, k in cs])
    t = np.clip(((C - a) @ d) / ll, 0.0, 1.0) if ll > 0 else np.zeros(len(C))
    return bool((np.linalg.norm(C - (a + t[:, None] * d), axis=1) < lim).any())


_corner_cache = {}


def corners_of(poly, vflag):
    key = id(poly)
    hit = _corner_cache.get(key)
    if hit is not None and hit[0] is poly:
        return hit[1]
    cs = [(poly[i], vflag[i]) for i in range(len(poly)) if vflag[i]]
    if len(_corner_cache) > 200000:
        _corner_cache.clear()
    _corner_cache[key] = (poly, cs)
    return cs


def trisOf(faces):
    # triangles of the triangulation output (a face may come with more corners: fan)
    try:
        T = np.array(faces, dtype=np.int64)              # the usual case: triangles only
        if T.ndim == 2 and T.shape[1] == 3:
            return T
    except ValueError:
        pass
    out = []
    for f in faces:
        for i in range(1, len(f) - 1):
            out.append((f[0], f[i], f[i + 1]))
    return np.array(out, dtype=np.int64).reshape(-1, 3)


import os as _os
from itertools import chain as _chain
_NOREG = bool(_os.environ.get("LAP_NOREG"))
_DBGPAR = None
_NOCLIP = bool(_os.environ.get("LAP_NOCLIP"))
_NOMATCH = bool(_os.environ.get("LAP_NOMATCH"))


def triRegions(T, V, oe, oedges):
    # connected regions of triangles that do not cross a constraint edge: (region of every
    # triangle, one representative triangle per region: the largest, its centre is safely inside)
    nt = len(T)
    nv = len(V) + 1
    if nt == 0:
        return np.zeros(0, dtype=np.int64), np.zeros(0, dtype=np.int64)
    E = np.array(oe, dtype=np.int64).reshape(-1, 2)
    ecode = np.minimum(E[:, 0], E[:, 1]) * nv + np.maximum(E[:, 0], E[:, 1])
    constr = np.fromiter(map(len, oedges), dtype=np.int64, count=len(oedges)) > 0
    order = np.argsort(ecode)
    sc = ecode[order]
    a = np.concatenate([T[:, 0], T[:, 1], T[:, 2]])
    b = np.concatenate([T[:, 1], T[:, 2], T[:, 0]])
    tcode = np.minimum(a, b) * nv + np.maximum(a, b)
    tid = np.tile(np.arange(nt), 3)
    pos = np.clip(np.searchsorted(sc, tcode), 0, len(sc) - 1)
    free = (sc[pos] != tcode) | ~constr[order[pos]]
    tcode, tid = tcode[free], tid[free]
    o2 = np.argsort(tcode, kind='stable')
    tcode, tid = tcode[o2], tid[o2]
    same = np.nonzero(tcode[1:] == tcode[:-1])[0]
    p0, p1 = tid[same], tid[same + 1]
    lab = np.arange(nt)
    for _ in range(10000):
        m = np.minimum(lab[p0], lab[p1])
        new = lab.copy()
        np.minimum.at(new, p0, m)
        np.minimum.at(new, p1, m)
        while True:                                      # follow the labels to their ends before the next round
            nn = new[new]
            if np.array_equal(nn, new):
                break
            new = nn
        if np.array_equal(new, lab):
            break
        lab = new
    uniq, reg = np.unique(lab, return_inverse=True)
    A = V[T]
    area = np.abs((A[:, 1, 0] - A[:, 0, 0]) * (A[:, 2, 1] - A[:, 0, 1]) -
                  (A[:, 1, 1] - A[:, 0, 1]) * (A[:, 2, 0] - A[:, 0, 0]))
    o3 = np.lexsort((area, reg))
    last = np.nonzero(np.r_[reg[o3][1:] != reg[o3][:-1], True])[0]
    return reg, o3[last]


def insidePoly(C, P):
    # even-odd test of the points C (n, 2) against the polygon P (m, 2), in blocks of about 2
    # million point-edge pairs (many points against a long outline would need gigabytes at once)
    inside = np.zeros(len(C), dtype=bool)
    Bn = np.roll(P, -1, axis=0)
    for s0 in range(0, len(P), 2000):
        A = P[s0:s0 + 2000]
        B = Bn[s0:s0 + 2000]
        x0, y0, x1, y1 = A[:, 0][None, :], A[:, 1][None, :], B[:, 0][None, :], B[:, 1][None, :]
        rows = max(1, 2000000 // max(1, len(A)))
        for r0 in range(0, len(C), rows):
            x = C[r0:r0 + rows, 0][:, None]
            y = C[r0:r0 + rows, 1][:, None]
            cond = (y0 > y) != (y1 > y)
            dy = np.where(cond, y1 - y0, 1.0)
            xin = x0 + (y - y0) * (x1 - x0) / dy
            inside[r0:r0 + rows] ^= (np.count_nonzero(cond & (x < xin), axis=1) & 1).astype(bool)
    return inside


def mergeShort(pts, cls, tol):
    # points closer than tol to the previous kept point are dropped; the edge that ends there
    # takes the longer of the two classes
    out_p, out_c = [pts[0]], [cls[0]]
    for i in range(1, len(pts)):
        if math.dist(pts[i], out_p[-1]) < tol:
            continue
        out_p.append(pts[i])
        out_c.append(cls[i])
    while len(out_p) > 3 and math.dist(out_p[-1], out_p[0]) < tol:
        out_p.pop()
        out_c.pop()
    return out_p, out_c


def dedupe(pts, att):
    # drop a point equal to the next one (a zero-length edge and its attribute go)
    out_p, out_a = [], []
    n = len(pts)
    for i in range(n):
        if pts[i] == pts[(i + 1) % n] and n > 1:
            continue
        out_p.append(pts[i])
        if att is not None:
            out_a.append(att[i])
    return out_p, (out_a if att is not None else None)


def subtract2d(loop, attrs, polys, eps):
    # loop minus the polygons; attrs[i] belongs to the edge loop[i] -> loop[i + 1] and is carried to
    # the result, a result edge on a polygon edge gets ('S', k) of that polygon
    loop, attrs = dedupe(loop, attrs)
    verts = [Vector(p) for p in loop]
    n = len(loop)
    edges = [(i, (i + 1) % n) for i in range(n)]
    eattr = list(attrs)
    faces = [list(range(n))]
    for k, poly in polys:
        # ('S', k, i): edge i of the polygon k (the indices follow the dedupe and the reversal)
        poly, segs = dedupe(poly, list(range(len(poly))))
        if len(poly) < 3:
            continue
        if area2(poly) < 0:
            poly = poly[::-1]
            segs = segs[::-1][1:] + segs[::-1][:1]
        b = len(verts)
        m = len(poly)
        verts += [Vector(p) for p in poly]
        edges += [(b + i, b + (i + 1) % m) for i in range(m)]
        eattr += [('S', k, sg) for sg in segs]
        faces.append(list(range(b, b + m)))
    ne = len(edges)
    # full triangulation of all edges; which triangles belong to the result is decided here by a
    # point in polygon test of their centres (the face flags of the triangulation are not reliable
    # for many overlapping faces). a tiny positive epsilon: with 0 the triangulation can crash on
    # points that coincide
    Xa = np.array(verts, dtype=np.float64).reshape(-1, 2)
    eps = max(eps, 1e-11 * float(np.ptp(Xa, axis=0).max()))
    Ea = np.array(edges, dtype=np.int64).reshape(-1, 2)
    keep_e = np.nonzero((Xa[Ea[:, 0]] != Xa[Ea[:, 1]]).any(axis=1))[0].tolist()
    if len(keep_e) < ne:
        edges = [edges[i] for i in keep_e]
        eattr = [eattr[i] for i in keep_e]
        ne = len(edges)
    ov, oe, of, overts, oedges, ofaces = mgeom.delaunay_2d_cdt(verts, edges, [], 0, eps, True)
    V = np.array(ov, dtype=np.float64).reshape(-1, 2)
    T = trisOf(of)
    X = Xa
    # triangles between the same constraint edges lie in the same polygons: one test per region
    # (the triangulation can drop a constraint edge now and then; then every triangle is tested)
    seen_e = set(_chain.from_iterable(oedges))
    if _NOREG or len(seen_e) < ne:
        reg, rep = np.arange(len(T)), np.arange(len(T))
    else:
        reg, rep = triRegions(T, V, oe, oedges)
    C = V[T[rep]].mean(axis=1)
    inside = insidePoly(C, X[faces[0]])
    for f in faces[1:]:
        if not inside.any():
            break
        P = X[f]
        lo, hi = P.min(axis=0), P.max(axis=0)
        sel = np.nonzero(inside & (C[:, 0] >= lo[0]) & (C[:, 0] <= hi[0]) & (C[:, 1] >= lo[1]) & (C[:, 1] <= hi[1]))[0]
        if len(sel):
            inside[sel] &= ~insidePoly(C[sel], P)
    return boundaryLoop(ov, oe, T[inside[reg]], oedges, eattr, ne)


def collinearKeep(pts, eps):
    # indices of the points that are not on the straight line through their neighbours
    n = len(pts)
    keep = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        dx, dy = c[0] - a[0], c[1] - a[1]
        ll = math.hypot(dx, dy)
        if ll > 0:
            d = abs((b[0] - a[0]) * dy - (b[1] - a[1]) * dx) / ll
            t = ((b[0] - a[0]) * dx + (b[1] - a[1]) * dy) / (ll * ll)
            if d <= eps and 0 < t < 1:
                continue
        keep.append(i)
    return keep


def dropCollinear(pts, att, eps):
    changed = True
    while changed and len(pts) > 3:
        changed = False
        out_p, out_a = [], []
        n = len(pts)
        i = 0
        skip = set()
        for i in range(n):
            if (i - 1) % n in skip:
                continue
            a = pts[i - 1]
            b = pts[i]
            c = pts[(i + 1) % n]
            if att[i - 1] == att[i]:
                dx, dy = c[0] - a[0], c[1] - a[1]
                ll = math.hypot(dx, dy)
                if ll > 0:
                    d = abs((b[0] - a[0]) * dy - (b[1] - a[1]) * dx) / ll
                    t = ((b[0] - a[0]) * dx + (b[1] - a[1]) * dy) / (ll * ll)
                    if d < eps and 0 < t < 1:
                        skip.add(i)
                        changed = True
        if changed:
            pts = [p for i, p in enumerate(pts) if i not in skip]
            att = [a for i, a in enumerate(att) if i not in skip]
            # the edge before a removed point takes over its span: attrs stay with the kept edge
    return pts, att


def simplifyRuns(pts, att, tol):
    # douglas-peucker inside every run of equal attributes; run ends stay
    n = len(pts)
    starts = [i for i in range(n) if att[i] != att[i - 1]]
    if not starts:
        return pts, att
    keep = set(starts)

    def dp(i0, i1):
        # indices along the loop from i0 to i1 (mod n)
        idx = [(i0 + k) % n for k in range((i1 - i0) % n + 1)]
        if len(idx) < 3:
            return
        a, b = pts[idx[0]], pts[idx[-1]]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = math.hypot(dx, dy) or 1e-30
        best, bi = -1.0, None
        for k in idx[1:-1]:
            p = pts[k]
            d = abs((p[0] - a[0]) * dy - (p[1] - a[1]) * dx) / ll
            if d > best:
                best, bi = d, k
        if best > tol:
            keep.add(bi)
            dp(idx[0], bi)
            dp(bi, idx[-1])

    for si, s0 in enumerate(starts):
        s1 = starts[(si + 1) % len(starts)]
        dp(s0, s1)
    order = sorted(keep)
    return [pts[i] for i in order], [att[i] for i in order]


class Plane2d:
    # section coordinates in a plane z = val normal to the target axis: x, y of the target frame
    def __init__(self, val=0.0):
        self.val = val

    def project(self, P):              # P: (n, 3) in the target frame
        return P[:, :2], np.ones(len(P), dtype=bool)

    def back(self, x, y):             # direction/point in the target frame (z irrelevant)
        return Vector((x, y, 0.0))

    def point(self, x, y):
        return Vector((x, y, self.val))

    def polar(self, x, y):            # (height, phi): height grows toward the teeth
        return math.hypot(x, y), math.atan2(y, x)

    def rot(self, pts, a):
        c, s_ = math.cos(a), math.sin(a)
        return [(c * x - s_ * y, s_ * x + c * y) for x, y in pts]

    def crossT(self, A, B, psi):      # where the segment A B crosses the half plane phi = psi
        n = (-math.sin(psi), math.cos(psi))
        ga = A[0] * n[0] + A[1] * n[1]
        gb = B[0] * n[0] + B[1] * n[1]
        return ga / (ga - gb) if ga != gb else 0.0


class Gnomonic:
    # section coordinates on a sphere about the apex: gnomonic projection from the apex onto the
    # plane touching the unit sphere in t0, scaled by lref (lengths near t0 are true at the sphere
    # lref). great circles (sections of planes through the apex) are straight lines
    def __init__(self, t0, lref):
        self.t0 = np.array(t0)
        self.e1 = np.array(sphereDir(math.acos(max(-1, min(1, t0[2]))) + math.pi / 2, math.atan2(t0[1], t0[0])))
        self.e2 = np.cross(self.t0, self.e1)
        self.lref = lref
        self.val = lref

    def project(self, P):
        D = P / np.linalg.norm(P, axis=1)[:, None]
        w = D @ self.t0
        ok = w > 0.15
        w = np.where(ok, w, 1.0)
        return np.stack([self.lref * (D @ self.e1) / w, self.lref * (D @ self.e2) / w], axis=1), ok

    def back(self, x, y):
        v = self.t0 + self.e1 * (x / self.lref) + self.e2 * (y / self.lref)
        return Vector(v / np.linalg.norm(v))

    def lin(self, x, y):
        return self.t0 + self.e1 * (x / self.lref) + self.e2 * (y / self.lref)

    def point(self, x, y):
        return self.back(x, y) * self.val

    def polar(self, x, y):
        d = self.back(x, y)
        return math.acos(max(-1.0, min(1.0, d.z))), math.atan2(d.y, d.x)

    def rot(self, pts, a):
        c, s_ = math.cos(a), math.sin(a)
        out = []
        for x, y in pts:
            v = self.back(x, y)
            q, ok = self.project(np.array(((c * v.x - s_ * v.y, s_ * v.x + c * v.y, v.z),)))
            out.append((float(q[0, 0]), float(q[0, 1])))
        return out

    def crossT(self, A, B, psi):
        n = np.array((-math.sin(psi), math.cos(psi), 0.0))
        ga, gb = float(self.lin(*A) @ n), float(self.lin(*B) @ n)
        return ga / (ga - gb) if ga != gb else 0.0


class CylProj:
    # section coordinates on a cylinder of radius c about the target axis, unrolled: (c phi, sgn z).
    # sgn = +1 when the teeth are cut into the face at the larger z, so height grows toward them
    def __init__(self, c, sgn):
        self.c = c
        self.sgn = sgn
        self.val = c

    def project(self, P):
        return np.stack([self.c * np.arctan2(P[:, 1], P[:, 0]), self.sgn * P[:, 2]], axis=1), \
            np.ones(len(P), dtype=bool)

    def back(self, x, y):
        return self.point(x, y)

    def point(self, x, y):
        f = x / self.c
        return Vector((self.c * math.cos(f), self.c * math.sin(f), self.sgn * y))

    def polar(self, x, y):
        return y, x / self.c

    def rot(self, pts, a):
        return [(x + self.c * a, y) for x, y in pts]

    def crossT(self, A, B, psi):
        return (self.c * psi - A[0]) / (B[0] - A[0]) if B[0] != A[0] else 0.0


def mat4np(m):
    return np.array(m)


def pairMode(src, tgt):
    # 'SPUR' or 'BEVEL' when the 2d engine applies, else None
    ks, kt = src.get("lap_kind"), tgt.get("lap_kind")
    if ks != kt or ks not in ('SPUR', 'BEVEL'):
        return None
    fs, ft = gearFrame(src), gearFrame(tgt)
    rel = ft.inverted() @ fs
    if ks == 'SPUR':
        zs = rel.to_3x3() @ Vector((0, 0, 1))
        if abs(abs(zs.z) - 1.0) > 1e-7:
            return None
        if src.get("lap_face") or tgt.get("lap_face"):
            return None
        # helical teeth on parallel axes: every plane across the axes is the same plane problem, only
        # turned (the source by its helix, the result by the ratio): one section, twisted again
        if abs(float(src.get("lap_helix", 0.0))) > 1e-9 or abs(float(tgt.get("lap_helix", 0.0))) > 1e-9:
            return 'HELICAL'
        return 'SPUR'
    if rel.to_translation().length > 1e-6 * float(tgt["lap_lout"]):
        return None
    return 'BEVEL'


def imprint2d(context, src, tgt, mode, steps, sub, sign_mode, limit_deg, relief, report, simple=True,
              clearance=0.25):
    t0 = time.time()
    zs = int(src["lap_teeth"])
    zt = int(tgt["lap_teeth"])
    m_t = sizeModule(tgt)
    me_s = gearMesh(src)
    me_t = gearMesh(tgt)
    tau_s = 0.0
    rsrc = isRack(src)
    if rsrc:
        # a rack as the tool: it moves along its x by v per radian of the blank (v = the rolling
        # radius: zt rack pitches per turn), its teeth repeat by the rack pitch
        el_r = elements(src)[0]
        pl_r = math.pi * float(src["lap_module"])
        v_r = zt * pl_r / (2 * math.pi)
        dir_r = gearFrame(src).to_3x3() @ Vector((1.0, 0.0, 0.0))
        R_t = max(v.co.xy.length for v in me_t.vertices)
        o_t = gearFrame(tgt).to_translation()
        E_r = elWorld(el_r)
        x0_r = (E_r.to_translation() - o_t).dot(dir_r)
        ft_inv = gearFrame(tgt).inverted()
    if mode in ('SPUR', 'HELICAL'):
        vs = [v.co.z for v in me_s.vertices]
        vt = [v.co.z for v in me_t.vertices]
        zs0, zs1, zt0, zt1 = min(vs), max(vs), min(vt), max(vt)
        mid_s = 0.5 * (zs0 + zs1) + 1e-7 * (zs1 - zs0)
        mid_t = 0.5 * (zt0 + zt1) + 1e-7 * (zt1 - zt0)
        pr = Plane2d()
        sphere = False
        # the source must cover the width of the target
        rel0 = gearFrame(tgt).inverted() @ gearFrame(src)
        c0 = (rel0 @ Vector((0, 0, zs0))).z
        c1 = (rel0 @ Vector((0, 0, zs1))).z
        if min(c0, c1) > zt0 + 1e-6 or max(c0, c1) < zt1 - 1e-6:
            report.append("WARNING: the source does not cover the whole face width of the target; the "
                          "section method cuts the whole width")
        if mode == 'HELICAL':
            # the source section in the plane of the middle section of the target
            e0 = (rel0 @ Vector((0, 0, 0))).z
            ez = (rel0 @ Vector((0, 0, 1))).z - e0                    # +-1: axes the same way or not
            mid_s = (mid_t - e0) / ez
            if not zs0 < mid_s < zs1:
                raise LapError("the helical source does not reach the middle section of the target")
            m_s = float(src.get("lap_module", 1.0))
            if rsrc:
                # rack shifted by tan(b) z_r: the cut turned by that / (sign v): tau_t set below
                tau_s = math.tan(math.radians(float(src.get("lap_helix", 0.0))))
            else:
                tau_s = math.tan(math.radians(float(src.get("lap_helix", 0.0)))) / (zs * m_s / 2)
            herring = bool(src.get("lap_herring", False))
            if herring and abs(mid_s) > 1e-5 * (zs1 - zs0):
                raise LapError("a herringbone source must have its middle (the apex of the chevron) in the middle "
                               "plane of the target: move the gears to the same height")
            if herring:
                # not in the apex itself (the section would run along the kink of the source): a
                # thousandth of the width above it, on the helical upper half
                mid_t += 1e-3 * (zt1 - zt0)
                mid_s = (mid_t - e0) / ez
    else:
        l_in, l_out = float(tgt["lap_lin"]), float(tgt["lap_lout"])
        mid_t = 0.5 * (l_in + l_out) + 1e-7 * (l_out - l_in)
        mid_s = 0.5 * (float(src["lap_lin"]) + float(src["lap_lout"])) + 1e-7 * (l_out - l_in)
        pr = Gnomonic(sphereDir(math.radians(float(tgt["lap_delta"])), 0.0), mid_t)
        sphere = True
        spiral_s = float(src.get("lap_spiral", 0.0))
        herr_b = bool(src.get("lap_herring", False)) and abs(spiral_s) > 1e-9
        lm_s = float(src.get("lap_lmid", 0.5 * (float(src["lap_lin"]) + float(src["lap_lout"]))))
        if herr_b:
            # not on the apex of the chevron itself: a thousandth of the width above it, on the outer half
            mid_t = lm_s + 1e-3 * (l_out - l_in)
            mid_s = mid_t
            pr = Gnomonic(sphereDir(math.radians(float(tgt["lap_delta"])), 0.0), mid_t)
        if abs(spiral_s) > 1e-9:
            psi_s = twistOf(src)
    pts_t, cls_t = sectionLoop(me_t, sphere, mid_t)
    pts_s, cls_s = sectionLoop(me_s, sphere, mid_s)
    P_t = np.array([tuple(p) for p in pts_t])
    # the section has a point on every quad diagonal too: drop the points in line with their
    # neighbours (checked in the section coordinates of the source itself)
    P_s = np.array([tuple(p) for p in pts_s])
    if sphere:
        own = Gnomonic(sphereDir(math.radians(float(src["lap_delta"])), 0.0), mid_s).project(P_s)[0]
    else:
        own = P_s[:, :2]
    keep = collinearKeep([tuple(q) for q in own], 1e-9 * float(np.ptp(own, axis=0).max()))
    P_s = P_s[keep]
    # roles of the source edges and its corners (in its own section)
    own = [tuple(own[i]) for i in keep]
    role_s = [cls_s[i] for i in keep]
    any_work = any(working(c) for c in role_s)
    wk_s, corner_s = sourceRoles(own, role_s, RAMP_CREASE_DEG, any_work)
    if not any_work:
        report.append("the source has no working faces marked (a foreign mesh?): all of it is taken as "
                      "working, only its corners cut parasitic faces")
    loop, ok = pr.project(P_t)
    if not ok.all():
        raise LapError("the target element is too wide for the section projection")
    loop = [tuple(p) for p in loop]
    attrs = [('T', c) for c in cls_t]
    # drop the extra section points on quad diagonals (in line with their neighbours, same class)
    loop, attrs = dropCollinear(loop, attrs, 1e-9 * float(np.ptp(np.array(loop), axis=0).max()))
    if area2(loop) < 0:
        loop = loop[::-1]
        attrs = attrs[::-1][1:] + attrs[::-1][:1]
    lo = np.array(loop).min(axis=0)
    hi = np.array(loop).max(axis=0)
    size = float(np.linalg.norm(hi - lo))
    glo, ghi = lo - 0.01 * size, hi + 0.01 * size
    eps = 0.0                     # exact: a positive epsilon merges points and can break the fill

    def positions(sign, n):
        # (id, source polygon in section coords) of every source tooth near the target; info[id] =
        # (sub index, working edges, corner points, polygon)
        out = []
        info = []
        frames = {}
        for k in range(n):
            beta = _TURN[0] * k / n
            if rsrc:
                d = sign * v_r * beta
                base = rotZ(-beta) @ ft_inv @ Matrix.Translation(dir_r * d) @ E_r
                j0 = int(math.ceil((-R_t - pl_r - x0_r - d) / pl_r))
                j1 = int(math.floor((R_t + pl_r - x0_r - d) / pl_r))
                copies = [base @ Matrix.Translation((j * pl_r, 0.0, 0.0)) for j in range(j0, j1 + 1)]
            else:
                base = relative(src, tgt, zs, zt, sign, beta)
                copies = [base @ rotZ(2 * math.pi * j / zs) for j in range(zs)]
            frames[k] = mat4np(base)
            for Mc in copies:
                M = mat4np(Mc)
                Q, okq = pr.project(P_s @ M[:3, :3].T + M[:3, 3])
                if not okq.all():
                    continue
                if (Q.max(axis=0) < glo).any() or (Q.min(axis=0) > ghi).any():
                    continue
                # clipped to the box around the target (a concave polygon gets zero-width bridges
                # along the box: harmless for the even-odd test in subtract2d)
                poly, vf, ew = clipBoxAttr(list(map(tuple, Q.tolist())), corner_s, wk_s, glo, ghi)
                if poly:
                    out.append((len(info), poly))
                    info.append((k, [bool(w) for w in ew], vf, poly))
        return out, frames, info


    def run(sign, n):
        pos, frames, info = positions(sign, n)
        lp, at = list(loop), list(attrs)
        for c in range(0, len(pos), CHUNK):
            lp, at = subtract2d(lp, at, pos[c:c + CHUNK], eps)
            if not lp:
                break
            lp, at = dropCollinear(lp, at, 1e-7 * size)
        return lp, at, pos, frames, info

    if sign_mode == 'AUTO':
        res = {}
        for sg in (1.0, -1.0):
            lp, at, pos, fr, inf = run(sg, zt * 3 * slowCycle(src, tgt, zt)[1])
            res[sg] = abs(area2(lp)) if lp else 0.0
        sign = 1.0 if res[1.0] >= res[-1.0] else -1.0
        a0 = abs(area2(loop))
        report.append("direction test: section keeps %.0f%% with +1, %.0f%% with -1 -> %+d"
                      % (100 * res[1.0] / a0, 100 * res[-1.0] / a0, int(sign)))
    else:
        sign = 1.0 if sign_mode == 'PLUS' else -1.0
    n = zt * steps * sub * slowCycle(src, tgt, zt)[1]
    lp, at, pos, frames, info = run(sign, n)
    if not lp:
        raise LapError("the imprint removed the whole element (wrong direction or placement?)")
    report.append(("imprint '%s' -> '%s' (section method, %s): %d -> %d teeth, " + ("rack travel per turn" if rsrc else "ratio") + " %.6g, %d steps of 1/%d "
                  "tooth, %d source positions near the target element")
                  % (src.name, tgt.name, 'rack tool' if rsrc else 'bevel' if sphere else 'cylindrical', zs, zt,
                     (2 * math.pi * v_r) if rsrc else zt * _SLOW.get(tgt.name, 1) / float(zs * _SLOW.get(src.name, 1)), n,
                     steps * sub, len(pos)))
    # classify the cut edges: parasitic when cut by a non working edge or a corner of the source,
    # or when the normal cannot pass torque; else the order of the cutting step
    cut = [i for i, a in enumerate(at) if a[0] == 'S']
    if not cut:
        report.append("WARNING: the source did not reach the target")
    cos_lim = math.cos(math.radians(limit_deg))
    par = {}
    n_edge = n_corner = 0
    N = len(lp)
    for i in cut:
        a = at[i]
        k, ew, vf, poly = info[a[1]]
        sg = a[2]
        p0, p1 = lp[i], lp[(i + 1) % N]
        if not ew[sg]:
            par[i] = True
            n_edge += 1
            continue
        if cornerCut(p0, p1, poly, vf, sg, CORNER_NEAR * m_t):
            par[i] = True
            n_corner += 1
            continue
        F = frames[k]
        if sphere:
            u0, u1 = pr.back(*p0), pr.back(*p1)
            nrm = u0.cross(u1)
            u = (u0 + u1).normalized()
            tt = Vector((-u.y, u.x, 0.0))
            ax = Vector(F[:3, :3] @ np.array((0.0, 0.0, 1.0)))
            ts = ax.cross(u)
        else:
            d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
            nrm = Vector((d.y, -d.x, 0.0))
            u = Vector((0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.0))
            tt = Vector((-u.y, u.x, 0.0))
            if rsrc:
                ts = Vector(F[:3, :3] @ np.array((1.0, 0.0, 0.0)))
                ts.z = 0.0
            else:
                c = Vector((F[0, 3], F[1, 3], 0.0))
                w = u - c
                ts = Vector((-w.y, w.x, 0.0))
        if nrm.length < 1e-30 or tt.length < 1e-30 or ts.length < 1e-30:
            par[i] = True
            continue
        nrm.normalize()
        axs = Vector(F[:3, :3] @ np.array((0.0, 0.0, 1.0)))
        ct = transverseCos(nrm, tt, Vector((0.0, 0.0, 1.0)))
        cs = transverseCos(nrm, ts, axs)
        par[i] = min(ct, cs) < cos_lim
    # order of the working cuts; the contact can run over the start of the turn (target element
    # facing the source at beta = 0), so the steps are counted from the largest gap
    nmain = zt * steps * slowCycle(src, tgt, zt)[1]
    ks = sorted(set(info[at[i][1]][0] // sub for i in cut if not par[i]))
    kstart = 0
    if ks:
        gaps = [((ks[(i + 1) % len(ks)] - ks[i]) % nmain or nmain, i) for i in range(len(ks))]
        kstart = ks[(max(gaps)[1] + 1) % len(ks)]
    kmain = [(k - kstart) % nmain for k in ks]
    kmin, kmax = (min(kmain), max(kmain)) if ks else (0, 0)
    cls = []
    npar = 0
    for i in range(N):
        a = at[i]
        if a[0] != 'S':
            cls.append(a[1])
        elif par[i]:
            cls.append(CLS_PARASITIC)
            npar += 1
        else:
            b = int(BANDS * ((info[a[1]][0] // sub - kstart) % nmain - kmin) / float(kmax - kmin + 1))
            cls.append(1 + min(BANDS - 1, max(0, b)))
    report.append("cut edges: %d, parasitic %d (%d cut by non working faces, %d by corners of the source)"
                  % (len(cut), npar, n_edge, n_corner))
    order = toothOrder(lp, pr, sphere, bodyTest(tgt, sphere, m_t), 2 * math.pi / zt)
    cls = majorityRuns(lp, cls, FLICKER * m_t, order)
    cls = filterRuns(lp, cls, FLICKER * m_t, order)
    lp, cls = simplifyRuns(lp, cls, SIMPLIFY * m_t)
    lp_u, cls_u = mergeShort(lp, cls, 1e-5 * m_t)
    # relief of the parasitic faces (lengths of the bevel section are true at the middle sphere);
    # with simple surfaces only where a run cannot be replaced (the simple surfaces keep the relief
    # as their clearance)
    up_r = -1 if (not sphere and tgt.get("lap_internal", False)) else 1
    floor2d = bodyFloor(tgt, sphere, m_t, mid_t if sphere else 1.0, up_r)
    lp, cls = reliefRuns(lp, cls, relief * m_t, eps, sideTest(pr, sphere, zt), clearance * m_t,
                         lambda q: up_r * pr.polar(q[0], q[1])[0], floor2d, mid_t if sphere else 1.0)
    if not lp:
        raise LapError("the outline collapsed after the relief: make the relief smaller")
    lp, cls = mergeShort(lp, cls, 1e-5 * m_t)
    report.append("outline: %d points, %d parasitic segments (relieved by %.3g), cut in %d steps"
                  % (len(lp), sum(1 for c in cls if c == CLS_PARASITIC), relief * m_t,
                     (kmax - kmin + 1) if cut else 0))
    # back to the gear: tooth side of the outline, then the element is built again. helical: the
    # outline turned along the width (a source turned by d gives the cut turned by d zs / (sign zt)),
    # one section per 1/24 pitch of the twist, all cut to the same element sector
    p_t = 2 * math.pi / zt
    if rsrc:
        tau_t = RACK_TWIST * tau_s / (sign * v_r * ez) if mode == 'HELICAL' else 0.0
    else:
        tau_t = tau_s * zs / (sign * zt * ez) if mode == 'HELICAL' else 0.0
    turns = [0.0]
    herring = mode == 'HELICAL' and bool(src.get("lap_herring", False))
    if mode == 'HELICAL' and abs(tau_t) * (zt1 - zt0) > 1e-9:
        mid0 = 0.5 * (zt0 + zt1) if herring else mid_t
        levels = twistLevels(zt0, zt1, tau_t, p_t, herring)
        shape = twistShape(herring)
        # the cut is the section at mid_t: turned back by its own twist
        turns = [tau_t * (shape(zk - mid0) - shape(mid_t - mid0)) for zk in levels]
    spiral_t = None
    if sphere and abs(float(src.get("lap_spiral", 0.0))) > 1e-9:
        # spiral bevel: on every sphere about the common apex the same plane problem, the source
        # turned by its spiral twist, the cut by that times zs / (sign zt)
        k_ = zs / float(sign * zt)
        l_in_t, l_out_t = float(tgt["lap_lin"]), float(tgt["lap_lout"])
        psi_k = lambda L: psi_s(L) * abs(k_)
        levels = bevelSpheres(psi_k, l_in_t, l_out_t, lm_s if herr_b else 0.5 * (l_in_t + l_out_t), herr_b, p_t / 24,
                              math.radians(float(tgt["lap_delta"])), None if _LOW[0] else math.radians(1.5))
        turns = [(psi_s(L) - psi_s(mid_s)) * k_ for L in levels]
        d_t = math.radians(float(tgt["lap_delta"]))
        # the spiral angle of the cut: its twist is tan b_t ln(L / mid_t) / sin d_t
        spiral_t = math.degrees(math.atan(math.tan(math.radians(float(src["lap_spiral"]))) * k_ * math.sin(d_t)
                                          / math.sin(math.radians(float(src["lap_delta"])))))
    choice = {}
    if simple:
        # the sector is chosen on the cut outline; the relieved one is cut to the same sector
        tops_u, tcl_u, phi0 = sectorTops(tgt, [(lp_u, cls_u, pr)], sphere, zt, m_t,
                                         turns=None, choice=choice)
    tops, tcl, phi0 = sectorTops(tgt, [(lp, cls, pr)], sphere, zt, m_t,
                                 turns=None, choice=choice)
    if simple:
        up = -1 if (not sphere and tgt.get("lap_internal", False)) else 1
        if sphere:
            met = lambda h, f: (math.sin(h) * f * mid_t, h * mid_t)
        else:
            met = lambda h, f: (h * math.cos(f), h * math.sin(f))
        n0 = len(tops[0])
        STATS.clear()
        for k in range(len(tops)):
            tops[k], tcl[k], pins = simplifyTop(tops_u[k], tcl_u[k], p_t, up, m_t, met, -phi0,
                                                (tops[k], tcl[k]), relief * m_t, clearance * m_t, floor2d)
        report.append("tool surfaces: tooth side %d -> %d points (non working runs as arcs on meridians, "
                      "chamfers and walls; %d runs kept as cut)" % (n0, len(tops[0]), STATS.get("runs_failed", 0)))
    if sphere and spiral_t is not None:
        # spiral: one outline, the sector turned along the cone distance (quads)
        me_new = bevelLoft("LAP_new", zt, levels, [tops[0]] * len(levels), [tcl[0]] * len(levels),
                           float(tgt["lap_neck"]), float(tgt["lap_rc"]), shifts=[t_ + phi0 for t_ in turns])
        phi0 = 0.0
        tgt["lap_spiral"] = spiral_t
        tgt["lap_lmid"] = lm_s if herr_b else mid_t
        tgt["lap_herring"] = bool(herr_b)
        tgt["lap_ushape"] = bool(src.get("lap_ushape", False)) and bool(herr_b)
        if "lap_spiral_in" in src and herr_b and not src.get("lap_ushape", False):
            tgt["lap_spiral_in"] = math.degrees(math.atan(math.tan(math.radians(float(src["lap_spiral_in"]))) * k_
                                                          * math.sin(d_t) / math.sin(math.radians(float(src["lap_delta"])))))
        elif "lap_spiral_in" in tgt:
            del tgt["lap_spiral_in"]
    elif False:
        me_new = bevelLoft("LAP_new", zt, levels, tops, tcl, float(tgt["lap_neck"]), float(tgt["lap_rc"]))
        report.append("spiral bevel: %d sphere sections, twist %.4g deg, spiral angle %.4g deg at the mean cone "
                      "distance" % (len(levels), math.degrees(turns[-1] - turns[0]), spiral_t))
    elif sphere:
        me_new = bevelElement("LAP_new", zt, float(tgt["lap_lin"]), float(tgt["lap_lout"]), tops[0], tcl[0],
                              float(tgt["lap_neck"]), float(tgt["lap_rc"]))
        tgt["lap_spiral"] = 0.0
    elif len(turns) > 1:
        me_new = spurLoft("LAP_new", zt, levels, [tops[0]] * len(levels), [tcl[0]] * len(levels),
                          float(tgt["lap_rbody"]), shifts=[t_ + phi0 for t_ in turns])
        phi0 = 0.0
        tgt["lap_helix"] = math.degrees(math.atan(tau_t * zt * m_t / 2))
        tgt["lap_herring"] = herring
        report.append("%s: %d sections over the width, twist %.4g deg, helix %.4g deg at the pitch radius"
                      % ("herringbone" if herring else "helical", len(levels),
                         math.degrees(tau_t * (zt1 - zt0) / (2 if herring else 1)), float(tgt["lap_helix"])))
    else:
        w = zt1 - zt0
        me_new = spurElement("LAP_new", zt, w, tops[0], tcl[0], float(tgt["lap_rbody"]))
        me_new.transform(Matrix.Translation((0, 0, 0.5 * (zt0 + zt1))))
        if mode == 'HELICAL':
            tgt["lap_helix"] = 0.0
    if phi0:
        me_new.transform(rotZ(phi0))
        report.append("element sector turned by %.4g deg (its sides cross the teeth once)" % math.degrees(phi0))
    ob, vol = meshCheck(me_new)
    bm = bmesh.new()
    bm.from_mesh(me_new)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(me_new)
    attachMaterials(me_t)
    me_t.update()
    report.append("target element: %d faces, volume %.6g, open edges %d" % (len(me_t.polygons), vol, ob))
    if ob:
        report.append("WARNING: the element is not closed")
    report.append("done in %.1f s" % (time.time() - t0))
    tgt["lap_source"] = src.name
    tgt["lap_sign"] = int(sign)
    tgt["lap_steps"] = int(steps)
    return sign


def rot2d(pr, pts, a):
    # section points turned by a about the target axis (exact for straight edges)
    return pr.rot(pts, a)


def polarOf(pr, sphere, pts):
    # (height, phi) of section points
    return [pr.polar(x, y) for x, y in pts]


def region2d(loops, keep):
    # boundary of a region made of loops: loops = [(points, attrs)], keep(inside flags per loop) ->
    # bool array for the triangle centres. the largest resulting loop, counter-clockwise, with the
    # attributes of the input edges it lies on
    verts, edges, eattr, faces = [], [], [], []
    for pts, att in loops:
        pts, att = dedupe(pts, att)
        if area2(pts) < 0:
            pts = pts[::-1]
            att = att[::-1][1:] + att[::-1][:1]
        b = len(verts)
        m = len(pts)
        verts += [Vector(p) for p in pts]
        edges += [(b + i, b + (i + 1) % m) for i in range(m)]
        eattr += att
        faces.append(list(range(b, b + m)))
    ne = len(edges)
    X = np.array([(v[0], v[1]) for v in verts])
    # a small epsilon joins the edges the turned copies share (equal only up to rounding)
    eps = 1e-9 * float(np.ptp(X, axis=0).max())
    ov, oe, of, overts, oedges, ofaces = mgeom.delaunay_2d_cdt(verts, edges, [], 0, eps, True)
    V = np.array([(v[0], v[1]) for v in ov])
    T = trisOf(of)
    C = V[T].mean(axis=1)
    kept = keep([insidePoly(C, X[f]) for f in faces])
    return boundaryLoop(ov, oe, T[kept], oedges, eattr, ne)


def boundaryLoop(ov, oe, tris, oedges, eattr, ne):
    if len(tris) == 0:
        return [], []
    nv = len(ov) + 1
    A = np.concatenate([tris[:, 0], tris[:, 1], tris[:, 2]])
    B = np.concatenate([tris[:, 1], tris[:, 2], tris[:, 0]])
    code = A * nv + B
    rev = B * nv + A
    bnd = ~np.isin(rev, code)
    half = set(zip(A[bnd].tolist(), B[bnd].tolist()))
    Eo = np.array(oe, dtype=np.int64).reshape(-1, 2)
    eidx = dict(zip((Eo.min(axis=1) * nv + Eo.max(axis=1)).tolist(), range(len(oe))))    # undirected edge -> its index
    nxt = {}
    for a, b in half:
        nxt.setdefault(a, []).append(b)
    best = None
    used = set()
    for s0 in list(nxt):
        for s1 in nxt[s0]:
            if (s0, s1) in used:
                continue
            lp = [s0]
            a, b = s0, s1
            while (a, b) not in used:
                used.add((a, b))
                lp.append(b)
                c = [x for x in nxt.get(b, []) if (b, x) not in used]
                if not c:
                    break
                a, b = b, c[0]
            if lp[-1] == lp[0]:
                lp = lp[:-1]
            if len(lp) >= 3:
                ar = area2([ov[i] for i in lp])
                if best is None or abs(ar) > abs(best[0]):
                    best = (ar, lp)
    if best is None:
        return [], []
    lp = best[1]
    if best[0] < 0:
        lp = lp[::-1]
    pts = [(ov[i][0], ov[i][1]) for i in lp]
    att = []
    for i in range(len(lp)):
        ea, eb = lp[i], lp[(i + 1) % len(lp)]
        ids = [j for j in oedges[eidx[min(ea, eb) * nv + max(ea, eb)]] if j < ne]
        src_ids = [j for j in ids if isinstance(eattr[j], tuple) and eattr[j][0] == 'S']
        att.append(eattr[src_ids[0]] if src_ids else (eattr[ids[0]] if ids else ('T', CLS_PLAIN)))
    return pts, att


STATS = {}


def filterRuns(pts, cls, lmin, order=None):
    # the classes of a closed outline without flicker: where a working flank ends, the cuts of the
    # source corner and of its flank take turns step by step. a working run shorter than lmin next
    # to a parasitic run becomes parasitic (the corner touches there: relieved), then a parasitic
    # run shorter than lmin between working runs becomes working (no dent in a flank).
    # order: the segments to look at, as one cycle (the tooth side of an element, whose ends meet
    # in the neighbouring element); default the whole outline
    n = len(pts)
    cls = list(cls)
    if order is None:
        order = list(range(n))
    m = len(order)
    if m < 4:
        return cls
    seg = {i: math.dist(pts[i], pts[(i + 1) % n]) for i in order}

    def key(c):
        return 'W' if working(c) else ('P' if c == CLS_PARASITIC else 'O')

    def runs():
        ks = [key(cls[i]) for i in order]
        s0 = next((j for j in range(m) if ks[j] != ks[j - 1]), None)
        if s0 is None:
            return []
        out = []
        j = s0
        while True:
            idx = []
            k = ks[j]
            while ks[j] == k and (not idx or j != s0):
                idx.append(order[j])
                j = (j + 1) % m
            out.append((k, idx, sum(seg[i] for i in idx)))
            if j == s0:
                return out

    for kind, nb, new in (('W', ('P',), CLS_PARASITIC), ('P', ('W',), None)):
        rs = runs()
        r_n = len(rs)
        for r in range(r_n):
            k, idx, ln = rs[r]
            if k != kind or ln >= lmin:
                continue
            kp, kn = rs[r - 1][0], rs[(r + 1) % r_n][0]
            if kind == 'W' and (kp in nb or kn in nb):
                for j in idx:
                    cls[j] = new
            elif kind == 'P' and kp in nb and kn in nb:
                c = cls[rs[r - 1][1][-1]]
                for j in idx:
                    cls[j] = c
    return cls


def majorityRuns(pts, cls, w, order=None):
    # where a working flank ends, the cuts of the source corner and of its flank take turns step by
    # step, often over a long stretch where both nearly touch. every working or parasitic segment
    # takes the kind that has the greater length within +-w/2 about it (blank segments are left
    # out), so the end of the flank falls where the two kinds balance, whatever the phase of the
    # steps. a segment that turns working takes the class of the nearest working segment
    n = len(pts)
    cls = list(cls)
    if order is None:
        order = list(range(n))
    m = len(order)
    if m < 4:
        return cls
    L = np.array([math.dist(pts[i], pts[(i + 1) % n]) for i in order])
    K = np.array([1 if working(cls[i]) else (-1 if cls[i] == CLS_PARASITIC else 0) for i in order])
    if not (K == 1).any() or not (K == -1).any():
        return cls
    L3, K3 = np.tile(L, 3), np.tile(K, 3)
    c = np.concatenate([[0.0], np.cumsum(L3)])
    mid = 0.5 * (c[m:2 * m] + c[m + 1:2 * m + 1])
    lo, hi = mid - 0.5 * w, mid + 0.5 * w
    ov = np.clip(np.minimum(hi[:, None], c[None, 1:]) - np.maximum(lo[:, None], c[None, :-1]), 0.0, None)
    bal = (ov * K3[None, :]).sum(axis=1)                       # working length - parasitic length
    newK = np.where(K == 0, 0, np.where(bal > 0, 1, np.where(bal < 0, -1, K)))
    if (newK == K).all():
        return cls
    wk = [j for j in range(m) if K[j] == 1]
    for j in range(m):
        if newK[j] == K[j]:
            continue
        if newK[j] == -1:
            cls[order[j]] = CLS_PARASITIC
        else:
            q = min(wk, key=lambda q: min(abs(q - j), m - abs(q - j)))
            cls[order[j]] = cls[order[q]]
    return cls


def toothOrder(pts, pr, sphere, body_h, p):
    # the segments of the tooth side of an element outline, in order (for filterRuns)
    try:
        pol = polarOf(pr, sphere, pts)
        idx = toothSideIdx(pol, [body_h(h) for h, f in pol], p)
    except (LapError, StopIteration):
        return None
    return idx[:-1]


def bodyFloor(tgt, sphere, m_t, lref, up):
    # the lowest the root may go (up * height): a little above the neck of a bevel rim, a quarter
    # module off the bore of a gear or the mantle of a ring
    if sphere:
        return float(tgt["lap_neck"]) + 0.05 * m_t / lref
    rb = float(tgt["lap_rbody"])
    return up * (rb + up * 0.25 * m_t)


def bodyTest(tgt, sphere, m_t):
    # is a point of an element section (height) on the body of the gear?
    if sphere:
        theta_k = float(tgt["lap_neck"])
        return lambda h: h < theta_k + 1e-9
    rb = float(tgt["lap_rbody"])
    return lambda h: abs(h - rb) < 0.01 * m_t


def flankRuns(lp, cls, order, pr, up):
    # the working runs of a tooth side as flanks. the side is periodic (it goes on in the next
    # element), so a run over its ends is one flank. per flank: 'down' or 'up' (the height falls or
    # grows along the outline), its segments from the upper end to the lower end and whether that
    # walk goes along the outline (dir +1) or against it, the heights of both ends, its length.
    # returns (flanks, heights of the points)
    n = len(lp)
    m = len(order) if order else 0
    if m < 2:
        return [], None
    H = [up * pr.polar(x, y)[0] for x, y in lp]
    wk = [working(cls[i]) for i in order]
    if all(wk) or not any(wk):
        return [], H
    s0 = next(j for j in range(m) if wk[j] and not wk[j - 1])
    flanks = []
    j, seen = s0, 0
    while seen < m:
        if not wk[j]:
            j = (j + 1) % m
            seen += 1
            continue
        run = []
        while wk[j] and seen < m:
            run.append(order[j])
            j = (j + 1) % m
            seen += 1
        h0, h1 = H[run[0]], H[(run[-1] + 1) % n]
        length = sum(math.dist(lp[i], lp[(i + 1) % n]) for i in run)
        if h0 >= h1:
            flanks.append({'orient': 'down', 'segs': run, 'dir': 1, 'upper': h0, 'lower': h1, 'len': length})
        else:
            flanks.append({'orient': 'up', 'segs': run[::-1], 'dir': -1, 'upper': h1, 'lower': h0, 'len': length})
    return flanks, H


def movePlan(f, H, n, lp, cls, side, target, allowed, walk_max):
    # the pieces of segments that change when the end of flank f (side 'upper' or 'lower') moves to
    # the height target: shortening turns flank pieces parasitic, lengthening turns the parasitic
    # pieces beyond the end into flank (only segments in allowed, not over the blank).
    # returns [(segment, u0, u1, class)] with u along the segment in the outline direction
    d = f['dir']
    out = []
    upper = side == 'upper'
    end = f[side]
    if abs(target - end) < 1e-12:
        return out
    segs = f['segs'] if upper else f['segs'][::-1]
    # walking direction along the outline from this end into the flank: +1 or -1
    w_in = d if upper else -d

    def piece(i, h_from, h_to, cut_at, into):
        # the part of segment i between its end at height h_from (walking) and the height cut_at
        t = (h_from - cut_at) / (h_from - h_to) if h_from != h_to else 1.0
        t = min(1.0, max(0.0, t))
        forward = (w_in > 0) == into            # walking along the outline direction
        return (0.0, t) if forward else (1.0 - t, 1.0)

    def hts(i, forward):
        a, b = H[i], H[(i + 1) % n]
        return (a, b) if forward else (b, a)
    shorten = (target < end) if upper else (target > end)
    if shorten:
        for i in segs:
            h0, h1 = hts(i, w_in > 0)
            beyond = (h1 >= target) if upper else (h1 <= target)
            if beyond:
                out.append((i, 0.0, 1.0, CLS_PARASITIC))
                continue
            inside = (h0 > target) if upper else (h0 < target)
            if inside:
                u0, u1 = piece(i, h0, h1, target, True)
                out.append((i, u0, u1, CLS_PARASITIC))
            break
        return out
    # lengthen: walk out of the flank over the parasitic segments next to its end, as long as the
    # outline goes on in the direction of the flank (at most a few times the allowed height)
    c_w = cls[segs[0]]
    first = segs[0]
    i = (first - 1) % n if w_in > 0 else (first + 1) % n
    walked = 0.0
    for _ in range(n):
        if i not in allowed or cls[i] != CLS_PARASITIC:
            break
        h0, h1 = hts(i, w_in < 0)
        if (h1 < h0 - 1e-12) if upper else (h1 > h0 + 1e-12):
            break                                          # the outline turns back
        walked += math.dist(lp[i], lp[(i + 1) % n])
        if walked > walk_max:
            break
        reach = (h1 <= target) if upper else (h1 >= target)
        if reach:
            out.append((i, 0.0, 1.0, c_w))
        else:
            done = (h0 < target) if upper else (h0 > target)
            if done:
                t = (target - h0) / (h1 - h0) if h1 != h0 else 1.0
                t = min(1.0, max(0.0, t))
                out.append((i, 1.0 - t, 1.0) + (c_w,) if w_in > 0 else (i, 0.0, t, c_w))
            break
        i = (i - 1) % n if w_in > 0 else (i + 1) % n
    return out


def applyCuts(lp, cls, cuts):
    # the outline with the pieces in cuts ({segment: [(u0, u1, class)]}) given a new class (points
    # added where a piece starts or ends)
    n = len(lp)
    out_p, out_c = [], []
    for i in range(n):
        out_p.append(lp[i])
        ivs = cuts.get(i)
        if not ivs:
            out_c.append(cls[i])
            continue
        us = [0.0] + sorted(set(u for iv in ivs for u in iv[:2] if 1e-9 < u < 1.0 - 1e-9)) + [1.0]
        a, b = lp[i], lp[(i + 1) % n]
        for q in range(len(us) - 1):
            um = 0.5 * (us[q] + us[q + 1])
            if q > 0:
                out_p.append((a[0] + (b[0] - a[0]) * us[q], a[1] + (b[1] - a[1]) * us[q]))
            c = cls[i]
            for u0, u1, cn in ivs:
                if u0 - 1e-12 <= um <= u1 + 1e-12:
                    c = cn
            out_c.append(c)
    return out_p, out_c


def robustSmooth(h):
    # jumps of single sections out (running median of 5), then the steps smoothed (running mean of 3)
    n = len(h)
    med = np.array([np.median(h[max(0, k - 2):k + 3]) for k in range(n)])
    return np.array([med[max(0, k - 1):k + 2].mean() for k in range(n)])


def harmonizeFlanks(secs, cap, walk_max):
    # the ends of the working flanks as smooth lines over the sections: from section to section they
    # jump with the phase of the steps and the classification, and the edges of the simple surfaces
    # (chamfer starts, wall tops) would zigzag. every flank end moves onto the robustly smoothed
    # line over the sections: shortening a flank is always allowed, lengthening it over parasitic
    # cut surface only by cap (in heights of that section).
    # secs: per level (outline, classes, tooth side order, projection, up); cap: per level.
    # returns (outline, classes) per level and the number of sections changed
    info = []
    for lp, cls, order, pr, up in secs:
        flanks, H = flankRuns(lp, cls, order, pr, up)
        fl = {}
        for o in ('down', 'up'):
            c = [f for f in flanks if f['orient'] == o]
            if c:
                fl[o] = max(c, key=lambda f: f['len'])
        info.append((fl, H))
    targets = [dict() for _ in secs]
    for o in ('down', 'up'):
        for key in ('upper', 'lower'):
            ks = [k for k in range(len(secs)) if o in info[k][0]]
            if len(ks) < 3:
                continue
            g = robustSmooth(np.array([info[k][0][o][key] for k in ks], dtype=float))
            for k, v in zip(ks, g):
                targets[k][(o, key)] = float(v)
    out = []
    changed = 0
    for k, (lp, cls, order, pr, up) in enumerate(secs):
        fl, H = info[k]
        cuts = {}
        allowed = set(order or [])
        for o, f in fl.items():
            span = f['upper'] - f['lower']
            hu = targets[k].get((o, 'upper'), f['upper'])
            hl = targets[k].get((o, 'lower'), f['lower'])
            hu = min(hu, f['upper'] + cap[k])
            hl = max(hl, f['lower'] - cap[k])
            if hu - hl < 0.3 * span:
                continue                                   # it would take most of the flank: left
            for side, tg in (('upper', hu), ('lower', hl)):
                for i, u0, u1, c in movePlan(f, H, len(lp), lp, cls, side, tg, allowed, walk_max):
                    cuts.setdefault(i, []).append((u0, u1, c))
        if cuts:
            changed += 1
            lp, cls = applyCuts(lp, cls, cuts)
        out.append((lp, cls))
    return out, changed


def simplifyTop(top, cls, p, up, module, met, grid0=0.0, alt=None, margin=0.0, root_clear=0.0, floor=None):
    # the tool is made of simple surfaces where it does not work: the non-working runs of a tooth
    # side (blank, parasitic) are replaced by primitives that lie in the old material (material is
    # only removed, never added):
    #   run with the tip        -> the uncut tip land stays (a cut one becomes an arc on the
    #                              meridians), joined to the working flanks by straight chamfers
    #   run with the root       -> walls along the meridians (planes through the axis) from the
    #                              working flanks down to the deepest level of the run, the root an
    #                              arc there, the corners rounded as far as the old material allows
    #   run in between          -> a straight chord
    # arcs get points on a fixed grid of meridians, so neighbouring sections share them. a run over
    # a sector side is taken as one run with its other end in the next sector (the outline is
    # periodic); the new outline crosses the side once, at the same height on both sides.
    # top: (height, phi) from -p/2 to p/2, cls per segment; up = +1 when the teeth point to greater
    # height (-1 for a ring); met(height, phi) -> 2d point in true lengths; grid0 turns the grid of
    # meridians (it turns with the teeth of a helical gear).
    # the primitives keep the clearance margin (the relief) from the cut outline top, except where
    # they start on a working flank; a run that cannot be replaced is taken from alt = (top, cls),
    # the same outline with its parasitic runs relieved. the root lies root_clear (true length) below
    # the deepest cut (the clearance c* m to the mating tips), at least margin, but not below floor
    # (up * height of the body: the neck of a bevel rim, the bore).
    # returns the top, its classes and the indices of the points to keep when it is resampled
    n = len(top)
    if n < 3:
        return top, cls, set()
    work = [working(c) for c in cls]
    if not any(work) or all(work):
        # nothing to replace between working flanks: as cut (relieved)
        return (alt[0], alt[1], set()) if alt is not None else (top, cls, set())
    H = [up * h for h, f in top]
    hmax, hmin = max(H), min(H)
    hm, fm = top[n // 2]
    sh = math.dist(met(hm + 1e-6, fm), met(hm - 1e-6, fm)) / 2e-6          # length of a unit of height
    tol = 0.05 * module / sh
    ton = 0.1 * SIMPLIFY * module                                          # on the old outline
    grid = p / 32
    # the old material in the (phi, up * height) plane over three sectors: below the tooth side
    ext = [(h, f - p) for h, f in top] + [(h, f) for h, f in top[1:]] + [(h, f + p) for h, f in top[1:]]
    base = hmin - 10 * tol - 1.0
    poly = np.array([(f, up * h) for h, f in ext] + [(1.5 * p + 1e-9, base), (-1.5 * p - 1e-9, base)])
    M_old = np.array([met(h, f) for h, f in ext])

    def sag(hh):
        # how far the chord between two meridians of the grid lies under the arc (in height)
        A, B, C = met(up * hh, fm), met(up * hh, fm + grid), met(up * hh, fm + grid / 2)
        return math.dist(C, ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)) / sh

    def arc(f0, f1, hh):
        # points strictly between f0 and f1 on the meridian grid, at height hh (up direction)
        out = []
        k = math.floor((f0 - grid0) / grid) + 1
        while k * grid + grid0 < f1 - 1e-9 * p:
            if k * grid + grid0 > f0 + 1e-9 * p:
                out.append((up * hh, k * grid + grid0))
            k += 1
        return out

    def dist(X):
        # distance of the points X (true lengths) to the old outline
        A, B = M_old[:-1], M_old[1:]
        D = B - A
        L2 = np.maximum(np.einsum("ij,ij->i", D, D), 1e-300)
        t = np.clip(np.einsum("kij,ij->ki", X[:, None, :] - A[None], D) / L2, 0.0, 1.0)
        C = A[None] + t[..., None] * D[None]
        return np.linalg.norm(X[:, None, :] - C, axis=2).min(axis=1)

    def inMaterial(path, clear=0.0, free=None):
        # every piece of the path lies in the old material or on the old outline; with clear > 0 its
        # points farther than free from the start and the end of the path lie that deep inside
        S = []
        for q0, q1 in zip(path[:-1], path[1:]):
            for t in (0.0, 0.25, 0.5, 0.75):
                S.append((q0[0] + (q1[0] - q0[0]) * t, q0[1] + (q1[1] - q0[1]) * t))
        S.append(path[-1])
        P2 = np.array([(f, up * h) for h, f in S])
        ins = insidePoly(P2, poly)
        X = np.array([met(h, f) for h, f in S])
        if not ins.all() and not bool((dist(X[~ins]) < ton).all()):
            return False
        if clear <= 0:
            return True
        free = 3.0 * clear if free is None else free
        e0, e1 = np.array(met(*path[0])), np.array(met(*path[-1]))
        far = (np.linalg.norm(X - e0, axis=1) > free) & (np.linalg.norm(X - e1, axis=1) > free)
        if not far.any():
            return True
        return bool(ins[far].all() and (dist(X[far]) >= clear - ton).all())

    def replace(R, C, side0, side1):
        # new points for the run R (points (height, phi), C classes of its segments): a list of
        # (point, class of the segment to it) from after R[0] up to R[-1], or None. side0 / side1:
        # the run ends on a sector side there (no wall, the end stays)
        m = len(R)
        HR = [up * h for h, f in R]
        FR = [f for h, f in R]
        has_tip = max(HR) >= hmax - tol
        has_root = min(HR) <= hmin + tol
        if has_tip and not has_root:
            km = max(range(m), key=lambda k: HR[k])
            k0 = k1 = km
            while k0 > 0 and C[k0 - 1] == CLS_PLAIN:
                k0 -= 1
            while k1 < m - 1 and C[k1] == CLS_PLAIN:
                k1 += 1
            if k1 > k0:
                # the blank tip was not cut: it stays, the chamfers end on it as close to the flanks
                # as the old material allows (t: a place on the land as a fractional point index)
                def L(t):
                    j = min(int(math.floor(t)), k1 - 1)
                    u = t - j
                    return (R[j][0] + (R[j + 1][0] - R[j][0]) * u, R[j][1] + (R[j + 1][1] - R[j][1]) * u)

                def firstOk(test, ts):
                    # the first t of ts that passes, refined toward the one before it
                    for q, t in enumerate(ts):
                        if test(t):
                            if q == 0:
                                return t
                            lo_, hi_ = ts[q - 1], t
                            for _ in range(12):
                                mid = 0.5 * (lo_ + hi_)
                                lo_, hi_ = (lo_, mid) if test(mid) else (mid, hi_)
                            return hi_
                    return None
                tl = 0.0 if side0 else firstOk(lambda t: inMaterial([R[0], L(t)], margin),
                                               [float(k) for k in range(k0, k1 + 1)])
                tr = float(m - 1) if side1 else firstOk(lambda t: inMaterial([L(t), R[-1]], margin),
                                                        [float(k) for k in range(k1, k0 - 1, -1)])
                if tl is None or tr is None or tl > tr:
                    return None
                new = []
                if not side0:
                    new.append((L(tl), CLS_PARASITIC))
                new += [(R[k], C[k - 1]) for k in range(int(math.floor(tl)) + 1, int(math.ceil(tr)))
                        if tl < k < tr]
                if not side1:
                    new.append((L(tr), C[min(int(math.floor(tr)), k1 - 1)]))
                    new.append((R[-1], CLS_PARASITIC))
                else:
                    new.append((R[-1], C[m - 2]))
                return [(q, c) for q, c in new if q != R[0]]
            # a cut tip: an arc on the meridians at its lowest level
            lv = [HR[k] for k in range(m) if HR[k] >= hmax - tol]
            hl = min(lv) - margin / sh - sag(min(lv))
            k0 = next(k for k in range(m) if HR[k] >= hmax - tol)
            k1 = next(k for k in range(m - 1, -1, -1) if HR[k] >= hmax - tol)
            for j in range(12):
                f0 = FR[0] if side0 else FR[k0] + j * grid
                f1 = FR[-1] if side1 else FR[k1] - j * grid
                if f1 < f0:
                    break
                pts = ([] if side0 else [(up * hl, f0)]) + arc(f0, f1, hl) + ([] if side1 else [(up * hl, f1)])
                if inMaterial([R[0]] + pts + [R[-1]]):
                    return [(q, CLS_PARASITIC) for q in pts] + [(R[-1], CLS_PARASITIC)]
            return None
        if has_root and not has_tip:
            hs = min(HR) - max(margin, root_clear) / sh - sag(min(HR))
            if floor is not None and hs < floor:
                hs = max(floor, min(HR) - margin / sh - sag(min(HR)))
                if hs > min(HR) - 1e-12:
                    return None
            fl, fr = min(FR), max(FR)
            sf = math.dist(met(up * hs, fl + 1e-6), met(up * hs, fl - 1e-6)) / 2e-6     # length per radian

            def rootPath(rho):
                pts = []
                if not side0:
                    if FR[0] - fl > 1e-9 * p:
                        pts.append((up * HR[0], fl))        # step into the flank end
                    pts.append((up * (hs + rho / sh), fl))  # wall along the meridian
                    for j in range(1, ROUND_SEG):
                        t = 0.5 * math.pi * j / ROUND_SEG
                        pts.append((up * (hs + rho * (1 - math.sin(t)) / sh), fl + rho * (1 - math.cos(t)) / sf))
                    if rho > 0:
                        pts.append((up * hs, fl + rho / sf))
                pts += arc(FR[0] if side0 else fl + rho / sf, FR[-1] if side1 else fr - rho / sf, hs)
                if not side1:
                    if rho > 0:
                        pts.append((up * hs, fr - rho / sf))
                    for j in range(ROUND_SEG - 1, 0, -1):
                        t = 0.5 * math.pi * j / ROUND_SEG
                        pts.append((up * (hs + rho * (1 - math.sin(t)) / sh), fr - rho * (1 - math.cos(t)) / sf))
                    pts.append((up * (hs + rho / sh), fr))
                    if fr - FR[-1] > 1e-9 * p:
                        pts.append((up * HR[-1], fr))
                return [q for i_, q in enumerate(pts) if i_ == 0 or math.dist(q, pts[i_ - 1]) > 1e-12]

            if not inMaterial([R[0]] + rootPath(0.0) + [R[-1]]):
                return None
            walls = ([] if side0 else [HR[0] - hs]) + ([] if side1 else [HR[-1] - hs])
            rmax = 0.999 * min([w * sh for w in walls] + [0.5 * (fr - fl) * sf])

            def roundOk(rho):
                rp = rootPath(rho)
                if not inMaterial([R[0]] + rp + [R[-1]]):
                    return False
                if margin <= 0:
                    return True
                # the rounds keep the clearance from the cut outline
                X = np.array([met(*q) for q in rp if abs(up * q[0] - hs) > 1e-12 and
                              min(abs(q[1] - fl), abs(q[1] - fr)) > 1e-12])
                return len(X) == 0 or bool((dist(X) >= margin - ton).all())
            lo_, hi_ = 0.0, rmax
            if roundOk(hi_):
                lo_ = hi_
            else:
                for _ in range(10):
                    mid = 0.5 * (lo_ + hi_)
                    if roundOk(mid):
                        lo_ = mid
                    else:
                        hi_ = mid
            rho = lo_ if lo_ > 0.02 * module else 0.0
            return [(q, CLS_PARASITIC) for q in rootPath(rho)] + [(R[-1], CLS_PARASITIC)]
        if not has_tip and not has_root and not side0 and not side1:
            if inMaterial([R[0], R[-1]], margin):
                return [(R[-1], CLS_PARASITIC)]
        return None

    def replaceChecked(R, C, side0, side1):
        # the primitives, unless they take away much more than a relief would: where a flank is
        # parasitic over a long way (crossed axes, the ends of a tool), walls and chords would thin
        # the teeth; there the cut outline stays (relieved)
        new = replace(R, C, side0, side1)
        if new is None:
            return None
        ring = [met(*R[0])] + [met(*q) for q, c in new] + [met(*q) for q in reversed(R[1:-1])]
        area = abs(area2(ring))
        run = sum(math.dist(met(*R[k]), met(*R[k + 1])) for k in range(len(R) - 1))
        deep = min(up * h for h, f in R) <= hmin + tol                      # the root: its clearance counts
        ratio = area / (max(margin, 0.03 * module, root_clear if deep else 0.0) * max(run, 1e-12))
        STATS.setdefault("ratios", []).append(ratio)
        return new if ratio <= AREA_K else None

    # runs of non working segments: points a..b, segments a..b-1
    runs = []
    i = 0
    while i < n - 1:
        if work[i]:
            i += 1
            continue
        a = i
        while i < n - 1 and not work[i]:
            i += 1
        runs.append((a, i))
    # a run over the sector side: the end run and the start run are one, continued into the next sector
    wrap = None
    if len(runs) >= 2 and runs[0][0] == 0 and runs[-1][1] == n - 1:
        (a0, b0), (a1, b1) = runs[0], runs[-1]
        R = top[a1:] + [(h, f + p) for h, f in top[1:b0 + 1]]
        C = cls[a1:n - 1] + cls[0:b0]
        new = replaceChecked(R, C, False, False)
        if new is not None:
            # split where the new outline crosses the side phi = p/2
            chain = [(R[0], None)] + new
            for j in range(1, len(chain)):
                (h0, f0), (h1, f1) = chain[j - 1][0], chain[j][0]
                if f0 <= p / 2 <= f1 and f1 > f0:
                    t = (p / 2 - f0) / (f1 - f0)
                    hx = h0 + (h1 - h0) * t
                    right = [q for q in chain[1:j] if q[0][1] < p / 2 - 1e-12] + [((hx, p / 2), chain[j][1])]
                    left = [((q[0][0], q[0][1] - p), q[1]) for q in chain[j:] if q[0][1] > p / 2 + 1e-12]
                    wrap = (hx, left, right, b0, a1)
                    runs = runs[1:-1]
                    break

    out, oc, pins = [(wrap[0], -p / 2) if wrap else top[0]], [], {0}

    def emit(new):
        for q, c in new:
            if math.dist(q, out[-1]) < 1e-12:
                continue
            pins.add(len(out))
            out.append(q)
            oc.append(c)
        pins.add(len(out) - 1)

    def fallback(a, b, relieved=True):
        # the run a..b as in alt (relieved), between the same working points; else as it is.
        # returns (points with classes, taken from alt)
        if alt is not None and relieved:
            at, ac = alt
            key = lambda q: (round(q[0], 9), round(q[1], 9))
            pos = {key(q): j for j, q in enumerate(at)}
            ia = 0 if a == 0 else pos.get(key(top[a]))
            ib = len(at) - 1 if b == n - 1 else pos.get(key(top[b]))
            if ia is not None and ib is not None and ia < ib:
                return [(at[j + 1], ac[j]) for j in range(ia, ib)], True
        return [(top[k + 1], cls[k]) for k in range(a, b)], False

    nfail = [0, 0]
    i = 0
    if wrap:
        emit(wrap[1])
        i = wrap[3]
    # the two runs on the sector sides (when not joined above) are replaced both or neither: the
    # element must end at the same height on both sides
    side_new = {}
    side_rel = True
    sides = [r for r in runs if r[0] == 0 or r[1] == n - 1]
    for a, b in sides:
        side_new[(a, b)] = replaceChecked(top[a:b + 1], cls[a:b], a == 0, b == n - 1)
    if any(v is None for v in side_new.values()):
        for key in side_new:
            side_new[key] = None
        # both from the relieved outline, or both as cut
        side_rel = all(fallback(a, b)[1] for a, b in sides)
        if side_rel and alt is not None and any(a == 0 for a, b in sides):
            out[0] = alt[0][0]
    for a, b in runs:
        while i < a:                                       # working segments before the run
            out.append(top[i + 1])
            oc.append(cls[i])
            i += 1
        new = side_new[(a, b)] if (a, b) in side_new else replaceChecked(top[a:b + 1], cls[a:b], a == 0, b == n - 1)
        if new is None:
            new, ok = fallback(a, b, side_rel if (a, b) in side_new else True)
            nfail[0 if ok else 1] += 1
            for q, c in new:
                out.append(q)
                oc.append(c)
        else:
            emit(new)
        i = b
    last = wrap[4] if wrap else n - 1
    while i < last:
        out.append(top[i + 1])
        oc.append(cls[i])
        i += 1
    if wrap:
        emit(wrap[2])
    out[-1] = (out[-1][0], p / 2)
    pins.add(len(out) - 1)
    STATS["runs_failed"] = STATS.get("runs_failed", 0) + nfail[0] + nfail[1]
    STATS["runs_unrelieved"] = STATS.get("runs_unrelieved", 0) + nfail[1]
    return out, oc, pins


def sectorTops(tgt, data, sphere, zt, m_t, body_h=None, turns=None, choice=None):
    # tooth sides of the sections, for the element sector whose sides cross the tooth side of every
    # section only once (else the side wall of the element would run along a cut surface and the
    # sections could not be joined). data: [(points, classes, projection)] per section. returns
    # tops (height, phi) with sides at -+p/2, their classes, and the turn phi0 of the new sector.
    # body_h(height) tells the points of the body (default: from the gear). turns: one section
    # turned by each of these angles about the axis instead (the sections of helical teeth).
    # choice: a dict that keeps the chosen sector for the next call (the same sector for another
    # version of the same sections)
    p = 2 * math.pi / zt
    if body_h is None:
        body_h = bodyTest(tgt, sphere, m_t)
    tops2d = []
    for lp, cls, pr in data:
        pol = polarOf(pr, sphere, lp)
        body = [body_h(h) for h, f in pol]
        idx = toothSideIdx(pol, body, p)
        t2 = [lp[k] for k in idx]
        tc = [cls[idx[k]] for k in range(len(idx) - 1)]
        tp = [pol[k] for k in idx]
        if tp[0][1] > tp[-1][1]:
            t2, tc, tp = t2[::-1], tc[::-1], tp[::-1]
        if turns is None:
            tops2d.append((t2, tc, tp, pr))
        else:
            for a in turns:
                t2a = rot2d(pr, t2, a)
                tops2d.append((t2a, tc, [(h, f + a) for h, f in tp], pr))
    turned = turns is not None and any(abs(a) > 1e-12 for a in turns)

    def shiftIn(tp, psi):
        # psi moved by whole pitches into the range of the tooth side (it starts on one sector side)
        return psi + p * math.ceil((tp[0][1] - psi) / p - 1e-12)

    def crossings(tp, psi):
        if turned:
            psi = shiftIn(tp, psi)
        return sum(1 for k in range(len(tp) - 1) if (tp[k][1] - psi) * (tp[k + 1][1] - psi) < 0)

    best = choice.get('best') if choice else None
    for i in range(32 if best is None else 0):
        psi = -p / 2 + p * i / 32.0
        c = 1 if i == 0 else max(crossings(tp, psi) for t2, tc, tp, pr in tops2d)
        if turned:
            c = max(crossings(tp, psi) for t2, tc, tp, pr in tops2d)
            key = (c if c > 0 else 99, min(i, 32 - i))
            if best is None or key < best[0]:
                best = (key, psi, i + 100)
            continue
        if i == 0:
            # the default sides: the outline must touch them only at its ends
            c = max(1 + sum(1 for k in range(1, len(tp) - 1) if abs(abs(tp[k][1]) - p / 2) < 1e-5)
                    for t2, tc, tp, pr in tops2d)
        key = (c, min(i, 32 - i))
        if best is None or key < best[0]:
            best = (key, psi, i)
    if choice is not None:
        choice['best'] = best
    tops, tcls = [], []
    if best[2] == 0:
        for t2, tc, tp, pr in tops2d:
            tp = list(tp)
            tp[0] = (tp[0][0], -p / 2)
            tp[-1] = (tp[-1][0], p / 2)
            tops.append(tp)
            tcls.append(tc)
        return tops, tcls, 0.0
    psi0 = best[1]
    phi0 = psi0 + p / 2
    for t2, tc, tp, pr in tops2d:
        # the tooth side continued into the next element, cut where it crosses phi = psi and
        # phi = psi + p (the same point turned by one pitch). a turned section may meet the side one
        # pitch further on: its part there is the same element, turned back by that pitch
        psi = shiftIn(tp, psi0) if turned else psi0
        C = t2 + rot2d(pr, t2, p)[1:]
        Cc = tc + tc
        Cp = [(h, f) for h, f in tp] + [(h, f + p) for h, f in tp[1:]] if turned else polarOf(pr, sphere, C)
        n1 = len(t2) - 1
        k1 = next((k for k in range(n1) if (Cp[k][1] - psi) * (Cp[k + 1][1] - psi) <= 0), None)
        if k1 is None and turned:
            # psi on the end of the side within rounding (an untwisted section, e.g. the apex of a
            # herringbone gear, has its ends on the sector sides): the crossing is that end
            if abs(psi - p - Cp[0][1]) < 1e-7 or abs(psi - Cp[n1][1]) < 1e-7:
                psi = Cp[n1][1] if abs(psi - Cp[n1][1]) < 1e-7 else psi - p
                k1 = next((k for k in range(n1) if (Cp[k][1] - psi) * (Cp[k + 1][1] - psi) <= 0), None)
        if k1 is None:
            raise LapError("the sector side does not cross the tooth side of a section")
        t = pr.crossT(C[k1], C[k1 + 1], psi)
        X1 = (C[k1][0] + (C[k1 + 1][0] - C[k1][0]) * t, C[k1][1] + (C[k1 + 1][1] - C[k1][1]) * t)
        X2 = rot2d(pr, [X1], p)[0]
        k2 = k1 + n1
        pts = [X1] + C[k1 + 1:k2 + 1] + [X2]
        cl = [Cc[k1]] + Cc[k1 + 1:k2] + [Cc[k2]]
        ph = psi + p / 2
        pol = [(h, (f - ph + math.pi) % (2 * math.pi) - math.pi) for h, f in polarOf(pr, sphere, pts)]
        pol[0] = (pol[0][0], -p / 2)
        pol[-1] = (pol[-1][0], p / 2)
        # drop points that fell together at the cuts
        pts2, cl2 = [pol[0]], []
        for k in range(1, len(pol)):
            if math.dist(pol[k], pts2[-1]) < 1e-9:
                continue
            pts2.append(pol[k])
            cl2.append(cl[k - 1])
        if math.dist(pol[-1], pts2[-1]) >= 1e-9 or len(pts2) < 2:
            pass
        pts2[-1] = pol[-1]
        tops.append(pts2)
        tcls.append(cl2)
    return tops, tcls, phi0


def toothSideIdx(pol, body, p):
    # indices of the part of the outline between the two sector sides, above the body
    n = len(pol)
    if all(body) or not any(body):
        raise LapError("the source cuts through the whole tooth side of the target, down into its body: "
                       "move the gears apart or use a smaller source")
    s = next(i for i in range(n) if body[i] and not body[(i + 1) % n])
    idx = []
    i = (s + 1) % n
    while not body[i]:
        idx.append(i)
        i = (i + 1) % n

    def onSide(k, sgn):
        return abs(pol[k][1] - sgn * p / 2) < 1e-5
    first_sgn = -1 if pol[idx[0]][1] < 0 else 1
    while len(idx) > 2 and onSide(idx[0], first_sgn) and onSide(idx[1], first_sgn):
        idx.pop(0)
    while len(idx) > 2 and onSide(idx[-1], -first_sgn) and onSide(idx[-2], -first_sgn):
        idx.pop()
    return idx


def transverseCos(n, t, axis):
    # cosine of the transverse pressure angle: the normal against the turning direction t, with the
    # axial part of the normal left out (axial thrust of helical teeth is carried by the bearings and
    # does not make a contact parasitic). a normal nearly along the axis passes no torque at all
    a = axis.normalized()
    nperp = n - a * n.dot(a)
    if nperp.length < 0.25 or t.length < 1e-30:
        return 0.0
    return abs(n.dot(t.normalized())) / nperp.length


def sideTest(pr, sphere, z):
    # is a section point on a side of the element sector (phi = +-p/2)?
    half = math.pi / z

    def test(q):
        return abs(abs(pr.polar(q[0], q[1])[1]) - half) < 1e-5
    return test


def reliefRuns(pts, cls, depth_all, eps, on_side=None, root_depth=0.0, hfun=None, hfloor=None, hscale=1.0):
    # parasitic runs are moved into the material by depth, with ramps of 2 depth at both run ends:
    # the loop minus a strip along every parasitic segment (and a wedge at every vertex), all
    # subtracted with the triangulation, so the relieved outline cannot cross itself. the deepest
    # run (the root, hfun(point) = height toward the teeth) goes root_depth deep (the clearance to
    # the mating tips), if that is more
    n = len(pts)
    if max(depth_all, root_depth) <= 0 or CLS_PARASITIC not in cls or all(c == CLS_PARASITIC for c in cls):
        return pts, cls
    polys = []
    i0 = next(i for i in range(n) if cls[i] != CLS_PARASITIC)
    order = [(i0 + k) % n for k in range(n)]
    runs = []
    k = 0
    while k < n:
        if cls[order[k]] != CLS_PARASITIC:
            k += 1
            continue
        run = []
        while k < n and cls[order[k]] == CLS_PARASITIC:
            run.append(order[k])
            k += 1
        runs.append(run)
    root = None
    if hfun is not None and root_depth > depth_all:
        low = [min(hfun(pts[j]) for j in run + [(run[-1] + 1) % n]) for run in runs]
        root = min(range(len(runs)), key=lambda r: low[r])
        if hfloor is not None:
            # not below the body (the neck of a bevel rim, the bore)
            root_depth = max(depth_all, min(root_depth, (low[root] - hfloor) * hscale))
    for r, run in enumerate(runs):
        depth = root_depth if r == root else depth_all
        if depth <= 0:
            continue
        chain = [pts[j] for j in run] + [pts[(run[-1] + 1) % n]]
        seg = [math.dist(chain[j], chain[j + 1]) for j in range(len(chain) - 1)]
        total = sum(seg)
        ramp = min(2 * depth, 0.5 * total)
        if ramp <= 0:
            continue
        acc = [0.0]
        for l in seg:
            acc.append(acc[-1] + l)
        # no ramp where the run meets a sector side: the neighbouring element goes on there
        free0 = on_side is not None and on_side(chain[0])
        free1 = on_side is not None and on_side(chain[-1])
        w = [min(1.0, 1.0 if free0 else a / ramp, 1.0 if free1 else (total - a) / ramp) for a in acc]
        nrm = []
        for j in range(len(seg)):
            a, b = chain[j], chain[j + 1]
            l = seg[j] or 1e-30
            nrm.append(((b[1] - a[1]) / l, -(b[0] - a[0]) / l))          # outward (ccw loop)
        for j in range(len(seg)):
            if seg[j] <= 0:
                continue
            a, b = chain[j], chain[j + 1]
            nx, ny = nrm[j]
            da, db = depth * w[j], depth * w[j + 1]
            # the strip reaches a little outside, so its outer edge is not on the outline itself
            o = 1e-3 * depth
            q = [(a[0] + o * nx, a[1] + o * ny), (b[0] + o * nx, b[1] + o * ny),
                 (b[0] - db * nx, b[1] - db * ny), (a[0] - da * nx, a[1] - da * ny)]
            if da + db > 0:
                polys.append((('R', 0), q))
        for j in range(1, len(seg)):
            p0 = chain[j]
            d = depth * w[j]
            if d <= 0:
                continue
            (ax, ay), (bx, by) = nrm[j - 1], nrm[j]
            q = [(p0[0] + 1e-3 * depth * (ax + bx), p0[1] + 1e-3 * depth * (ay + by)),
                 (p0[0] - d * ax, p0[1] - d * ay), (p0[0] - d * bx, p0[1] - d * by)]
            if abs(area2(q)) > 1e-18:
                polys.append((('R', 0), q))
    if not polys:
        return pts, cls
    lp, at = subtract2d(pts, [('T', c) for c in cls], [(k, q) for k, q in polys], eps)
    return lp, [CLS_PARASITIC if a[0] == 'S' else a[1] for a in at]


# ---------------------------------------------------------------------------
# slice engine: any placement of the axes (crossed, intersecting away from the apex, a cylindrical
# gear against a bevel gear...). the target element is cut into sections: planes normal to its
# axis for a cylindrical target, spheres about its apex for a bevel target. a section of the space
# the source sweeps is the union of the sections of all source positions, so every section is
# the target section minus the source sections, exactly as in the section method. the sections are
# then joined into the element again (lofted), so the surfaces follow the envelopes of the motion
# ---------------------------------------------------------------------------

def meshArrays(me, crease_deg=None):
    # triangulated arrays: verts (n, 3), edges (e, 2), triangle edges (t, 3), triangle normals
    bm = bmesh.new()
    bm.from_mesh(me)
    triangulateSafe(bm)
    bm.verts.index_update()
    bm.edges.index_update()
    bm.faces.index_update()
    bm.normal_update()
    V = np.array([tuple(v.co) for v in bm.verts])
    E = np.array([[e.verts[0].index, e.verts[1].index] for e in bm.edges], dtype=np.int64)
    TE = np.array([[e.index for e in f.edges] for f in bm.faces], dtype=np.int64)
    TV = np.array([[v.index for v in f.verts] for f in bm.faces], dtype=np.int64)
    N = np.array([tuple(f.normal) for f in bm.faces])
    MI = np.array([f.material_index for f in bm.faces], dtype=np.int64)
    cc = math.cos(math.radians(CREASE_DEG if crease_deg is None else crease_deg))
    SP = np.array([[e.link_faces[0].index, e.link_faces[1].index] for e in bm.edges
                   if len(e.link_faces) == 2 and e.link_faces[0].normal.dot(e.link_faces[1].normal) < cc],
                  dtype=np.int64).reshape(-1, 2)
    bm.free()
    return V, E, TE, TV, N, SP, MI


def levelOf(kind):
    # the level coordinate of the slice family: plane z, sphere |p|, cylinder |xy|
    if kind == 'SPHERE':
        return lambda P: np.linalg.norm(P, axis=-1)
    if kind == 'CYL':
        return lambda P: np.linalg.norm(P[..., :2], axis=-1)
    return lambda P: P[..., 2]


def sliceLoops(Vt, E, TE, kind, value):
    # closed loops of the section of a triangle mesh (verts already in the target frame) with the
    # plane z = value, the sphere |p| = value or the cylinder |xy| = value:
    # [(points (m, 3), triangle of every segment)]
    if kind is True or kind is False:
        kind = 'SPHERE' if kind else 'PLANE'
    d = levelOf(kind)(Vt) - value
    neg = d < 0
    cr = neg[E[:, 0]] != neg[E[:, 1]]
    if not cr.any():
        return []
    ids = np.nonzero(cr)[0]
    a = Vt[E[ids, 0]]
    b = Vt[E[ids, 1]]
    if kind in ('SPHERE', 'CYL'):
        k = 3 if kind == 'SPHERE' else 2
        dd = (b - a)[:, :k]
        a2 = a[:, :k]
        qa = np.einsum("ij,ij->i", dd, dd)
        qb = 2 * np.einsum("ij,ij->i", a2, dd)
        qc = np.einsum("ij,ij->i", a2, a2) - value * value
        disc = np.sqrt(np.maximum(0.0, qb * qb - 4 * qa * qc))
        qa = np.maximum(qa, 1e-300)
        t1 = (-qb - disc) / (2 * qa)
        t2 = (-qb + disc) / (2 * qa)
        t = np.where(np.abs(t1 - 0.5) < np.abs(t2 - 0.5), t1, t2)
    else:
        t = d[E[ids, 0]] / (d[E[ids, 0]] - d[E[ids, 1]])
    P = a + (b - a) * t[:, None]
    row = np.full(len(E), -1, dtype=np.int64)
    row[ids] = np.arange(len(ids))
    tc = cr[TE]
    sel = np.nonzero(tc.sum(axis=1) == 2)[0]
    if len(sel):
        # fast path: every crossed edge in exactly two crossed triangles. the neighbours of a node
        # are kept in the order of the triangles, so the loops come out as in the general walk
        es = TE[sel][tc[sel]].reshape(-1, 2)
        u = row[es[:, 0]]
        v = row[es[:, 1]]
        src_ = np.empty(2 * len(sel), dtype=np.int64)
        dst_ = np.empty(2 * len(sel), dtype=np.int64)
        src_[0::2], src_[1::2] = u, v
        dst_[0::2], dst_[1::2] = v, u
        tri_ = np.repeat(sel, 2)
        order = np.argsort(src_, kind='stable')
        deg = np.bincount(src_, minlength=len(ids))
        if (deg == 2).all():
            nb = dst_[order].reshape(-1, 2).tolist()
            nt = tri_[order].reshape(-1, 2).tolist()
            # start nodes in the order of their first appearance
            _, first = np.unique(src_, return_index=True)
            starts = src_[np.sort(first)].tolist()
            seen = bytearray(len(ids))
            loops = []
            for start in starts:
                if seen[start]:
                    continue
                pts, tris = [], []
                prev, cur = -1, start
                while True:
                    seen[cur] = 1
                    pts.append(cur)
                    a0, a1 = nb[cur]
                    if a0 != prev or a1 == prev:
                        nx, ti = a0, nt[cur][0]
                    else:
                        nx, ti = a1, nt[cur][1]
                    tris.append(ti)
                    prev, cur = cur, nx
                    if cur == start or seen[cur]:
                        break
                if len(pts) >= 3 and cur == start:
                    loops.append((P[pts], tris))
            return loops
    nxt = {}
    for ti in sel:
        es = TE[ti][tc[ti]]
        e0, e1 = int(row[es[0]]), int(row[es[1]])
        nxt.setdefault(e0, []).append((e1, int(ti)))
        nxt.setdefault(e1, []).append((e0, int(ti)))
    loops = []
    seen = set()
    for start in nxt:
        if start in seen:
            continue
        pts, tris = [], []
        prev, cur = None, start
        while True:
            seen.add(cur)
            pts.append(cur)
            cand = [c for c in nxt[cur] if c[0] != prev] or nxt[cur]
            nx, ti = cand[0]
            tris.append(ti)
            prev, cur = cur, nx
            if cur == start or cur in seen:
                break
        if len(pts) >= 3 and cur == start:
            loops.append((P[pts], tris))
    return loops


def sliceSub(Vt, E, TE, cand):
    # sliceLoops (plane z = 0) restricted to the candidate triangles cand (sorted): every triangle
    # that crosses the plane where a loop is wanted must be among them; loops left open by the
    # restriction are dropped. the loops of the candidates come out as in sliceLoops
    if not len(cand):
        return []
    TEc = TE[cand]
    eu = np.unique(TEc)
    d = Vt[:, 2]
    ea, eb = E[eu, 0], E[eu, 1]
    cr = (d[ea] < 0) != (d[eb] < 0)
    if not cr.any():
        return []
    pos = np.searchsorted(eu, TEc)
    tc = cr[pos]
    s2 = tc.sum(axis=1) == 2
    if not s2.any():
        return []
    node = np.cumsum(cr) - 1
    a = ea[cr]
    b = eb[cr]
    t = d[a] / (d[a] - d[b])
    P = Vt[a] + (Vt[b] - Vt[a]) * t[:, None]
    selr = np.nonzero(s2)[0]
    es = pos[selr][tc[selr]].reshape(-1, 2)
    u = node[es[:, 0]]
    v = node[es[:, 1]]
    m = len(selr)
    src_ = np.empty(2 * m, dtype=np.int64)
    dst_ = np.empty(2 * m, dtype=np.int64)
    src_[0::2], src_[1::2] = u, v
    dst_[0::2], dst_[1::2] = v, u
    tri_ = np.repeat(cand[selr], 2)
    nn = len(P)
    deg = np.bincount(src_, minlength=nn)
    order = np.argsort(src_, kind='stable')
    # nodes met once only (their other triangle was not a candidate) end open chains
    st = np.zeros(nn + 1, dtype=np.int64)
    st[1:] = np.cumsum(deg)
    dsto = dst_[order].tolist()
    trio = tri_[order].tolist()
    stl = st.tolist()
    degl = deg.tolist()
    _, first = np.unique(src_, return_index=True)
    starts = src_[np.sort(first)].tolist()
    seen = bytearray(nn)
    loops = []
    for start in starts:
        if seen[start] or degl[start] != 2:
            continue
        pts, tris = [], []
        prev, cur = -1, start
        ok = True
        while True:
            seen[cur] = 1
            if degl[cur] != 2:
                ok = False
                break
            pts.append(cur)
            k0 = stl[cur]
            a0, a1 = dsto[k0], dsto[k0 + 1]
            if a0 != prev or a1 == prev:
                nx, ti = a0, trio[k0]
            else:
                nx, ti = a1, trio[k0 + 1]
            tris.append(ti)
            prev, cur = cur, nx
            if cur == start or seen[cur]:
                break
        if ok and len(pts) >= 3 and cur == start:
            loops.append((P[pts], tris))
    return loops


PAIRS15 = np.array([(i, j) for i in range(6) for j in range(i + 1, 6)], dtype=np.int64)


def hull2d(pts):
    # convex hull, counter-clockwise (monotone chain)
    pts = sorted(set(pts))
    if len(pts) < 3:
        return []

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    h = lower[:-1] + upper[:-1]
    return h if len(h) >= 3 else []


def prismSections(prisms, lvl, val, pr, lo, hi):
    # sections of convex prisms (6 points each) with the level surface: the convex hull of the
    # crossings of all 15 segments between their points, and per hull point whether it lies on the
    # path of a sharp edge (a segment between two points of sharp edges: the edge itself or the way
    # of one of its ends between the two positions)
    P, ids, SM = prisms
    L = lvl(P) - val                                   # (p, 6)
    cr = (L.min(axis=1) < 0) & (L.max(axis=1) > 0)
    if not cr.any():
        return []
    P, L, ids, SM = P[cr], L[cr], ids[cr], SM[cr]
    a, b = PAIRS15[:, 0], PAIRS15[:, 1]
    da, db = L[:, a], L[:, b]                          # (c, 15)
    m = da * db < 0
    t = np.where(m, da / np.where(m, da - db, 1.0), 0.0)
    X = P[:, a] + (P[:, b] - P[:, a]) * t[..., None]   # (c, 15, 3)
    Q, ok = pr.project(X.reshape(-1, 3))
    Q = Q.reshape(len(P), 15, 2)
    sharp = SM[:, a] & SM[:, b]                        # (c, 15)
    out = []
    for i in range(len(P)):
        q = Q[i][m[i]]
        if len(q) < 3 or (q.max(axis=0) < lo).any() or (q.min(axis=0) > hi).any():
            continue
        pts = [(float(x), float(y)) for x, y in q]
        h = hull2d(pts)
        if h and abs(area2(h)) > 1e-14:
            sp = set(p for p, s_ in zip(pts, sharp[i][m[i]]) if s_)
            out.append((h, int(ids[i]), [2 if p in sp else 0 for p in h]))
    return out


def closedSingle(me):
    # a single element (one start worm) with its hairline slot closed: the sides dropped, the rims
    # welded. as a tool the slot would cut with its walls. a temporary mesh
    bm = bmesh.new()
    bm.from_mesh(me)
    lim = math.pi - SLOT
    side = [f for f in bm.faces if f.material_index == CLS_PLAIN and
            all(abs(math.atan2(v.co.y, v.co.x)) > lim for v in f.verts)]
    sset = set(side)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4 and f not in sset])
    bmesh.ops.delete(bm, geom=side, context='FACES_ONLY')
    rim = list({v for e in bm.edges if e.is_boundary for v in e.verts})
    rmax = max((math.hypot(v.co.x, v.co.y) for v in bm.verts), default=1.0)
    bmesh.ops.remove_doubles(bm, verts=rim, dist=1.2 * SLOT * rmax)
    wire = [e for e in bm.edges if not e.link_faces]
    if wire:
        bmesh.ops.delete(bm, geom=wire, context='EDGES_FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    out = bpy.data.meshes.new("LAP_closed")
    bm.to_mesh(out)
    bm.free()
    return out


def extendedTool(src, me_s, share, report, tgt=None, me_t=None):
    # the source element continued beyond both ends along its helix: with crossed axes (and a
    # worm) the flanks of the target are then cut by the flanks of the tool and not by the edges of
    # its ends. the element is cut at a level just inside each end and the section is swept on with
    # the twist of the helix (straight teeth: straight on), sharing the vertices of the cut, so the
    # seam has no edges. at most share of the length, and only as far as the target reaches.
    # a temporary mesh
    if share <= 0 or isBevel(src) or src.get("lap_face") or "lap_rbody" not in src or "lap_throat" in src \
            or src.get("lap_custom"):
        # (a worm wheel is no cylinder: its throat would not go on along the helix; an own body is
        # taken as it is)
        return None
    zs = [v.co.z for v in me_s.vertices]
    z0, z1 = min(zs), max(zs)
    w = z1 - z0
    if w <= 0:
        return None
    ext = {1.0: share * w, -1.0: share * w}
    if tgt is not None:
        # only for crossed axes (skew lines: a crossed helical pair, a worm): with intersecting axes
        # (a pinion on a face or bevel gear) the length of the pinion is part of the design
        fs, ft = gearFrame(src), gearFrame(tgt)
        a1, a2 = fs.to_3x3().col[2].normalized(), ft.to_3x3().col[2].normalized()
        c = a1.cross(a2)
        if c.length < 1e-6:
            return None
        dist = abs((ft.translation - fs.translation).dot(c.normalized()))
        if dist < 1e-4 * max(1.0, w):
            return None
    if tgt is not None and me_t is not None:
        # how far along the source axis the solid of the target (sampled as the ring between its
        # body and tip radius, turned about its axis) comes within the tip radius of the source
        M = np.array(src.matrix_world.inverted() @ tgt.matrix_world)
        tz = [v.co.z for v in me_t.vertices]
        rr = [math.hypot(v.co.x, v.co.y) for v in me_t.vertices]
        ra_s = max(math.hypot(v.co.x, v.co.y) for v in me_s.vertices)
        th = np.linspace(0, 2 * math.pi, 721)
        rho = np.linspace(min(rr), max(rr), 7)
        hh = np.linspace(min(tz), max(tz), 9)
        T, R, H = np.meshgrid(th, rho, hh, indexing='ij')
        P = np.stack([R * np.cos(T), R * np.sin(T), H], axis=-1).reshape(-1, 3)
        Q = P @ M[:3, :3].T + M[:3, 3]
        near = np.hypot(Q[:, 0], Q[:, 1]) <= ra_s + 0.02 * w
        if not near.any():
            return None
        zq = Q[near, 2]
        ext[1.0] = min(ext[1.0], max(0.0, float(zq.max()) - z1 + 0.05 * w)) if zq.max() > z1 else 0.0
        ext[-1.0] = min(ext[-1.0], max(0.0, z0 - float(zq.min()) + 0.05 * w)) if zq.min() < z0 else 0.0
    if ext[1.0] <= 0 and ext[-1.0] <= 0:
        return None
    rp = int(src["lap_teeth"]) * float(src.get("lap_module", 1.0)) / 2
    tau = math.tan(math.radians(float(src.get("lap_helix", 0.0)))) / rp
    p = 2 * math.pi / int(src["lap_teeth"])
    bm = bmesh.new()
    bm.from_mesh(me_s)
    done = []
    for zend, sgn in ((z1, 1.0), (z0, -1.0)):
        if ext[sgn] <= 0:
            continue
        ze = zend - sgn * 0.02 * w
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-7, plane_co=(0, 0, ze),
                                     plane_no=(0, 0, sgn), clear_outer=True)
        tol = 1e-6 * max(1.0, w)
        bnd = [e for e in bm.edges if e.is_boundary and abs(e.verts[0].co.z - ze) < tol
               and abs(e.verts[1].co.z - ze) < tol]
        if len(bnd) < 3:
            continue
        # walk the boundary into loops (the outline, and the bore of a closed ring); the face of every
        # edge gives its class
        nxt = {}
        for e in bnd:
            f = e.link_faces[0]
            # the boundary edge runs along its face's winding: that orientation, with the face on
            # the inner side, is kept for the new quads
            vs = list(f.verts)
            i0 = vs.index(e.verts[0])
            a_, b_ = (e.verts[0], e.verts[1]) if vs[(i0 + 1) % len(vs)] == e.verts[1] else (e.verts[1], e.verts[0])
            if a_ in nxt:
                report.append("the tool was not continued: its end section touches itself")
                bm.free()
                return None
            nxt[a_] = (b_, f.material_index)
        loops = []
        left = set(nxt)
        while left:
            start = next(iter(left))
            loop, cls, v = [], [], start
            while True:
                loop.append(v)
                left.discard(v)
                b_, mi = nxt[v]
                cls.append(mi)
                v = b_
                if v == start or v not in nxt or len(loop) > len(nxt):
                    break
            if v != start:
                report.append("the tool was not continued: its end section is not closed")
                bm.free()
                return None
            loops.append((loop, cls))
        L = ext[sgn] + 0.02 * w
        nl = max(2, int(math.ceil(abs(tau) * L / min(p / 24, math.radians(5.0)))) + 1, int(math.ceil(L / (0.25 * w))) + 1)
        far = []
        for loop, cls in loops:
            n = len(loop)
            rings = [loop]
            for k in range(1, nl):
                dz = sgn * L * k / (nl - 1)
                cs, sn = math.cos(tau * dz), math.sin(tau * dz)
                rings.append([bm.verts.new((cs * q.co.x - sn * q.co.y, sn * q.co.x + cs * q.co.y, ze + dz))
                              for q in loop])
            for k in range(nl - 1):
                A, B = rings[k], rings[k + 1]
                for i in range(n):
                    j = (i + 1) % n
                    # the old face has A[i] -> A[j] in its winding; the new face on the other side of
                    # that edge runs A[j] -> A[i]
                    f = bm.faces.new((A[j], A[i], B[i], B[j]))
                    f.material_index = cls[i]
            R = rings[-1]
            far += [bm.edges.get((R[i], R[(i + 1) % n])) for i in range(n)]
        if len(loops) == 1:
            cap = bm.faces.new(list(reversed(rings[-1])))
            cap.material_index = CLS_PLAIN
        else:
            res = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=far,
                                          normal=(0.0, 0.0, sgn))
            for f in res["geom"]:
                if isinstance(f, bmesh.types.BMFace):
                    f.material_index = CLS_PLAIN
        done.append(ext[sgn])
    if not done:
        bm.free()
        return None
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    me = bpy.data.meshes.new("LAP_tool_ext")
    bm.to_mesh(me)
    bm.free()
    report.append("tool continued by %s beyond its ends along its helix"
                  % " and ".join("%.3g" % e for e in done))
    return me


def previousSign(src, tgt):
    # the direction of the pass that made the source, when its tool sat where the target sits now
    # (a reverse pass: the same pair turning the same way) or when the target was made by this source
    if tgt.get("lap_source") == src.name and "lap_sign" in tgt:
        return float(tgt["lap_sign"])
    prev = bpy.data.objects.get(src.get("lap_source", ""))
    if prev is None or "lap_sign" not in src or int(prev.get("lap_teeth", -1)) != int(tgt["lap_teeth"]):
        return None
    d = prev.matrix_world - tgt.matrix_world
    if max(abs(d[i][j]) for i in range(4) for j in range(4)) > 1e-6 * max(1.0, tgt.matrix_world.translation.length):
        return None
    return float(src["lap_sign"])


# ---------------------------------------------------------------------------
# worm as the source of a slice imprint: a worm is a screw, so turning it by a is the same body as
# moving it along its axis by lead a / 2 pi. every section of the wheel (a plane across the wheel
# axis) holds the worm axis, so the worm's section there is a rack (on each plane its own), made
# exactly from the axial profile, and the whole motion in that plane is the rack sliding along plus
# the wheel turning: a plane rack generating a gear, level by level. the rack only needs one axial
# pitch of sliding (it repeats), and no worm mesh is cut at all
# ---------------------------------------------------------------------------

def wormProfileOf(g):
    # the stored axial profile of a worm: [(u, r)] over one axial pitch and the segment classes
    f = list(g.get("lap_profile", []))
    c = [int(x) for x in g.get("lap_profile_cls", [])]
    if len(f) < 2 or len(f) // 2 != len(c):
        return None, None
    return [(f[2 * i], f[2 * i + 1]) for i in range(len(c))], c


def setWormProfile(g, prof, cls):
    g["lap_profile"] = [float(x) for q in prof for x in q]
    g["lap_profile_cls"] = [int(c) for c in cls]


def wormProfileDeviation(g, me, prof, tol):
    # largest distance of the worm's thread points (not on its bore or end planes) from the screw of
    # its stored profile, in the axial plane: 0 for a worm made here, more once its mesh was edited
    z1 = int(g["lap_teeth"])
    mx = sizeModule(g)
    px = math.pi * mx
    lead = z1 * px * (1.0 if float(g.get("lap_helix", 0.0)) >= 0 else -1.0)
    L = lead / (2 * math.pi)
    V = np.array([tuple(v.co) for v in me.vertices])
    r = np.hypot(V[:, 0], V[:, 1])
    z = V[:, 2]
    keep = (np.abs(r - float(g.get("lap_rbody", -1.0))) > tol) & (z > z.min() + tol) & (z < z.max() - tol)
    if not keep.any():
        # no thread points at all (the mesh was replaced, e.g. by a plain cylinder)
        return float('inf')
    u0 = prof[0][0]
    u = (z[keep] - L * np.arctan2(V[keep, 1], V[keep, 0]) - u0) % px + u0
    r = r[keep]
    pts = [(pu + k * px, pr) for k in (-1, 0, 1) for pu, pr in prof] + [(prof[0][0] + 2 * px, prof[0][1])]
    A = np.array(pts[:-1])
    B = np.array(pts[1:])
    d = B - A
    ll = np.maximum((d * d).sum(axis=1), 1e-30)
    best = np.full(len(u), np.inf)
    for i in range(len(A)):
        t = np.clip(((u - A[i, 0]) * d[i, 0] + (r - A[i, 1]) * d[i, 1]) / ll[i], 0.0, 1.0)
        best = np.minimum(best, np.hypot(u - A[i, 0] - t * d[i, 0], r - A[i, 1] - t * d[i, 1]))
    dev = float(best.max())
    # the other way round: the screw of the profile must lie on the mesh (a mesh replaced by one whose
    # points happen to lie on the tip cylinder passes the first test)
    tree = BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices for p in me.polygons])
    zmin, zmax = float(z.min()), float(z.max())
    p = 2 * math.pi / z1
    for i in range(8):
        t = -p / 2 + p * (i + 0.5) / 8
        for k in range(-40, 41):
            for pu, pr in prof:
                zz = pu + k * px + L * t
                if zmin + px / 4 < zz < zmax - px / 4:
                    hit = tree.find_nearest(Vector((pr * math.cos(t), pr * math.sin(t), zz)))
                    if hit[0] is not None:
                        dev = max(dev, hit[3])
    return dev


def rackFrame(src, tgt, zs, zt, sign):
    # the worm at rest in the wheel frame: its matrix, the wheel axis and the direction to the wheel
    # centre in worm coordinates (both across the worm axis), the worm origin in the wheel frame
    P0 = relative(src, tgt, zs, zt, sign, 0.0)
    R = P0.to_3x3()
    Ri = R.inverted()
    e_h = Ri @ Vector((0.0, 0.0, 1.0))
    c = P0.translation.copy()
    e_t = Ri @ Vector((-c.x, -c.y, 0.0))
    e_t -= Vector((0, 0, 1)) * e_t.z
    e_t -= e_h * e_t.dot(e_h)
    return P0, e_h.normalized(), e_t.normalized(), c


def rackBranch(prof, pcls, lead, px, h, e_h, e_t, zlen, mx):
    # the near side (toward the wheel) of the worm's section by the plane at the distance h from
    # its axis, the plane holding the axis and e_t: points in worm coordinates, one per sample of
    # the profile repeated along zlen (about z = 0) and a pitch more on both sides; per segment its
    # class and the surface normal (worm coordinates); the index of the first point of every pitch
    # (at the deepest point of the profile, where the rack may be cut off)
    L = lead / (2 * math.pi)
    rs = [r for u, r in prof]
    if max(rs) <= abs(h):
        return None
    i0 = int(np.argmin(rs))
    pr = prof[i0:] + [(u + px, r) for u, r in prof[:i0]]
    pc = pcls[i0:] + pcls[:i0]
    reach = zlen / 2 + abs(lead) / 2 + 2 * px
    k0 = int(math.floor((-reach - pr[0][0]) / px))
    k1 = int(math.ceil((reach - pr[0][0]) / px))
    ah = abs(h)
    step = 0.03 * mx

    def point(u, r):
        t = math.sqrt(max(r * r - h * h, 0.0))
        v = e_h * h + e_t * t
        th = math.atan2(v.y, v.x)
        return (v.x, v.y, u + L * th), t, th
    P, SC, SN, starts = [], [], [], []
    np_ = len(pr)
    for kk in range(k0, k1 + 1):
        starts.append(len(P))
        for i in range(np_):
            (ua, ra), (ub, rb) = pr[i], (pr[i + 1] if i + 1 < np_ else (pr[0][0] + px, pr[0][1]))
            ua += kk * px
            ub += kk * px
            # pieces split where the radius passes the plane distance (the section of the thread
            # starts or ends there: the side of the plane is a square root)
            cuts = [0.0, 1.0]
            if (ra - ah) * (rb - ah) < 0:
                cuts.insert(1, (ah - ra) / (rb - ra))
            for a0, a1 in zip(cuts[:-1], cuts[1:]):
                ra0, ra1 = ra + (rb - ra) * a0, ra + (rb - ra) * a1
                (_, t0, th0), (_, t1, th1) = point(ua + (ub - ua) * a0, ra0), point(ua + (ub - ua) * a1, ra1)
                d = max(abs(ub - ua) * (a1 - a0), abs(ra1 - ra0), abs(t1 - t0), abs(L * (th1 - th0)))
                n = max(1, int(math.ceil(d / step)))
                start_edge = abs(ra0 - ah) < 1e-12 and ra1 > ah
                end_edge = abs(ra1 - ah) < 1e-12 and ra0 > ah
                for q in range(n):
                    s_ = q / n
                    if start_edge:
                        s_ = s_ * s_
                    elif end_edge:
                        s_ = 1 - (1 - s_) * (1 - s_)
                    a = a0 + (a1 - a0) * s_
                    u, r = ua + (ub - ua) * a, ra + (rb - ra) * a
                    xyz, t, th = point(u, r)
                    P.append(xyz)
                    SC.append(pc[i])
                    # normal of the screw surface of this profile segment at the point
                    if abs(ub - ua) > 1e-12 * px:
                        rp = (rb - ra) / (ub - ua)
                        du = Vector((rp * math.cos(th), rp * math.sin(th), 1.0))
                    else:
                        du = Vector((math.cos(th), math.sin(th), 0.0))
                    dth = Vector((-r * math.sin(th), r * math.cos(th), L))
                    SN.append(tuple(du.cross(dth)))
    starts.append(len(P))
    xyz, _, _ = point(pr[0][0] + (k1 + 1) * px, pr[0][1])
    P.append(xyz)
    return np.array(P), SC, SN, starts


def rackPoses(src, tgt, zs, zt, sign, n, lead, px):
    # per step k: the worm moved along its axis (in place of its turn, modulo one pitch) and the
    # wheel turned by 2 pi k / n, as the matrix worm coordinates -> wheel frame
    P0 = relative(src, tgt, zs, zt, sign, 0.0)
    out = []
    for k in range(n):
        beta = 2 * math.pi * k / n
        alpha = sign * (zt / float(zs)) * beta
        sh = -(lead * alpha / (2 * math.pi)) % px
        out.append(np.array(rotZ(-beta) @ P0 @ Matrix.Translation((0.0, 0.0, sh))))
    return out


def resampleLoop(lp, kinds, h, half=None):
    # a closed outline with a point every h at most (the old points kept); kinds per segment go to
    # every new point of the segment. segments on a sector side (polar angle +-half) stay whole
    P, K = [], []
    n = len(lp)

    def onSide(q):
        return half is not None and abs(abs(math.atan2(q[1], q[0])) - half) < 1e-5
    for i in range(n):
        a, b = lp[i], lp[(i + 1) % n]
        m = 1 if onSide(a) and onSide(b) else max(1, int(math.ceil(math.dist(a, b) / h)))
        for q in range(m):
            t = q / m
            P.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            K.append(kinds[i])
    return np.array(P), K


def deformSection(loop, attrs, polys, info, posl, clear, h, motion, zval, half, box=None, nper=None):
    # test mode "press": one exact subtraction, at the position of the largest overlap; then every
    # other position only presses the points of the outline deeper, each along its own fixed ray -
    # the inward normal of that first outline - until it is out of the source section. (pressing
    # along the normal of the pressing source edge plows: a source edge moving along the outline
    # drags the points with it.) at the end the pressed points go clear deeper along their rays
    # (backlash). points on the sector sides (polar angle +-half) stay. the points keep their order:
    # the outline changes its topology once. per point: (0 untouched / 1 by a working edge / 2 by
    # another, step)
    if not polys:
        P, K = resampleLoop(loop, [(0, -1)] * len(loop), h)
        return P, K
    S = np.array(loop)
    by_pos = {}
    for key, poly in polys:
        by_pos.setdefault(key[0], []).append((key, poly))
    best, best_n = None, -1
    for pi, group in by_pos.items():
        cnt = 0
        for key, poly in group:
            cnt += int(insidePoly(S, np.array(poly)).sum())
        if cnt > best_n:
            best, best_n = pi, cnt
    lp, at = loop, attrs
    if best_n > 0:
        # with the positions one target tooth earlier and later: they cut the neighbour elements at
        # the same place, so the first outline goes on the same way across both sector sides
        kb = posl[best][0]
        tpl = [kp for pi, g in by_pos.items() for kp in g
               if posl[pi][0] == kb or (nper and posl[pi][0] in (kb - nper, kb + nper))]
        lp, at = subtract2d(loop, attrs, tpl, 0.0)
        if not lp:
            raise LapError("the imprint removed a whole section of the element")
    if area2(lp) < 0:
        lp, at = lp[::-1], at[::-1][1:] + at[::-1][:1]
    kinds = []
    for a in at:
        if a[0] == 'S':
            (pi, tris, pid), seg = a[1], a[2]
            kinds.append((1 if info[pid][0][seg] else 2, posl[pi][0]))
        else:
            kinds.append((0, -1))
    P, K = resampleLoop(lp, kinds, h, half)
    n = len(P)
    # the rays: inward normals (the outline runs counter clockwise: inward = left of the tangent)
    Tg = np.roll(P, -1, axis=0) - np.roll(P, 1, axis=0)
    tl = np.maximum(np.hypot(Tg[:, 0], Tg[:, 1]), 1e-30)
    R = np.column_stack([-Tg[:, 1] / tl, Tg[:, 0] / tl])
    ang = np.arctan2(P[:, 1], P[:, 0])
    # points on the sector sides slide along them (radially inward), so that a cut crossing a side
    # shortens it the same way on both sides of the element
    side = np.abs(np.abs(ang) - half) < 1e-5
    rr = np.maximum(np.hypot(P[:, 0], P[:, 1]), 1e-30)
    R[side] = -P[side] / rr[side][:, None]
    frozen = np.zeros(len(P), dtype=bool)
    pressed = np.array([k[0] > 0 for k in K])
    order = sorted(range(len(polys)), key=lambda q: posl[polys[q][0][0]][0])
    for q in order:
        key, poly = polys[q]
        wk = list(info[key[2]][0])
        A = np.array(poly)
        if area2(poly) < 0:
            A = A[::-1]
            wk = wk[::-1][1:] + wk[::-1][:1]
        lo_, hi_ = A.min(axis=0), A.max(axis=0)
        near = np.nonzero((P[:, 0] >= lo_[0]) & (P[:, 0] <= hi_[0]) & (P[:, 1] >= lo_[1]) & (P[:, 1] <= hi_[1])
                          & ~frozen)[0]
        if not len(near):
            continue
        X = P[near]
        inside = insidePoly(X, A)
        if not inside.any():
            continue
        near = near[inside]
        X = P[near]
        Rr = R[near]
        B = np.roll(A, -1, axis=0)
        D = B - A
        # the farthest crossing of the ray with the source outline (the point leaves the source
        # there for good; a ray through two teeth would stop in the gap - taken as the last exit)
        den = Rr[:, 0:1] * D[None, :, 1] - Rr[:, 1:2] * D[None, :, 0]
        wx = A[None, :, 0] - X[:, None, 0]
        wy = A[None, :, 1] - X[:, None, 1]
        with np.errstate(divide='ignore', invalid='ignore'):
            tr = (wx * D[None, :, 1] - wy * D[None, :, 0]) / den
            sr = (wx * Rr[:, 1:2] - wy * Rr[:, 0:1]) / den
        ok = (np.abs(den) > 1e-15) & (tr > 0) & (sr >= 0) & (sr <= 1)
        # the first exit: the crossings sorted, the first one leaves the source
        tr = np.where(ok, tr, np.inf)
        je = np.argmin(tr, axis=1)
        tmin = tr[np.arange(len(near)), je]
        good = np.isfinite(tmin)
        idx = near[good]
        P[idx] = X[good] + Rr[good] * tmin[good][:, None]
        pressed[idx] = True
        k = posl[key[0]][0]
        for ii, jj in zip(idx, je[good]):
            K[ii] = (1 if wk[jj] else 2, k)
    if clear > 0:
        P[pressed & ~frozen] += R[pressed & ~frozen] * clear
    return P, K


def resampleTopUniform(top, cls, m, met):
    # a tooth side (h, phi) as m points evenly along its length (metric met), the class of every new
    # segment from the old segment at its middle
    XY = np.array([met(h, f) for h, f in top])
    seg = np.hypot(*(XY[1:] - XY[:-1]).T)
    acc = np.concatenate([[0.0], np.cumsum(seg)])
    L = acc[-1]
    if L <= 0:
        return top, cls
    s = np.linspace(0.0, L, m)
    H = np.interp(s, acc, [q[0] for q in top])
    F = np.interp(s, acc, [q[1] for q in top])
    mid = 0.5 * (s[1:] + s[:-1])
    si = np.clip(np.searchsorted(acc, mid) - 1, 0, len(cls) - 1)
    return [(float(a), float(b)) for a, b in zip(H, F)], [cls[i] for i in si]


def imprintSlices(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, nlev, smooth, report,
                  family='AUTO', remesh=False, simple=True, clearance=0.25, extend=0.5, deform=None):
    t0 = time.time()
    zs = int(src["lap_teeth"])
    zt = int(tgt["lap_teeth"])
    m_t = sizeModule(tgt)
    sphere = isBevel(tgt)
    me_s = gearMesh(src)
    me_t = gearMesh(tgt)
    # ramps only at edges sharper than RAMP_CREASE_DEG: a lapped source has many facets on its
    # smooth envelopes, and between two positions they leave only a scallop of about step^2
    me_c = closedSingle(me_s) if zs == 1 else None
    me_x = extendedTool(src, me_c or me_s, extend, report, tgt, me_t)
    # a worm thread is a strongly twisted surface: its facets may meet at some 20 degrees, its real
    # edges (tip and root corners) at about 70
    crease = WORM_CREASE_DEG if src.get("lap_worm") else RAMP_CREASE_DEG
    V_s, E_s, TE_s, TV_s, N_s, SP_s, MI_s = meshArrays(me_x or me_c or me_s, crease)
    for tmp in (me_x, me_c):
        if tmp is not None:
            bpy.data.meshes.remove(tmp)
    WK_s = np.array([working(int(c)) for c in MI_s], dtype=bool)
    any_work = bool(WK_s.any())
    if not any_work:
        WK_s[:] = True
        report.append("the source has no working faces marked (a foreign mesh?): all of it is taken as "
                      "working, only its edges cut parasitic faces")
    if simple and len(SP_s):
        # an edge between two non working faces cuts only parasitic faces, and those become simple
        # surfaces under the whole cut anyway: no ramps there
        SP_s = SP_s[WK_s[SP_s[:, 0]] | WK_s[SP_s[:, 1]]]
    # the corners of the triangles on a sharp edge (the ends of the edge shared by the pair)
    SV_s = np.zeros(TV_s.shape, dtype=bool)
    for f0, f1 in SP_s:
        sh = set(TV_s[f0]) & set(TV_s[f1])
        for f in (f0, f1):
            for j in range(3):
                if TV_s[f][j] in sh:
                    SV_s[f][j] = True
    V_t, E_t, TE_t, TV_t, N_t, SP_t, MI_t = meshArrays(me_t)
    lo3 = V_t.min(axis=0)
    hi3 = V_t.max(axis=0)
    size = float(np.linalg.norm(hi3 - lo3))
    grow = 0.01 * size
    removed = []
    if sign_mode == 'AUTO':
        tree_s = BVHTree.FromPolygons([v.co for v in me_s.vertices], [p.vertices for p in me_s.polygons])
        tree_t = BVHTree.FromPolygons([v.co for v in me_t.vertices], [p.vertices for p in me_t.polygons])
        rp_, rm_ = [], []
        fp = removedFraction(src, tgt, zs, zt, 1.0, tree_s, tree_t, me_t, size, rp_)
        fm = removedFraction(src, tgt, zs, zt, -1.0, tree_s, tree_t, me_t, size, rm_)
        sign = 1.0 if fp < fm else -1.0
        removed = rp_ if sign > 0 else rm_
        report.append("direction test: removed %.0f%% with +1, %.0f%% with -1 -> %+d"
                      % (100 * fp, 100 * fm, int(sign)))
        if min(fp, fm) > 0.8 * max(fp, fm):
            prev = previousSign(src, tgt)
            if prev is not None:
                sign = prev
                removed = rp_ if sign > 0 else rm_
                report.append("direction test unclear: %+d as in the pass that made the source" % int(sign))
            else:
                report.append("WARNING: direction test unclear, set the direction by hand")
    else:
        sign = 1.0 if sign_mode == 'PLUS' else -1.0
    # slice family: spheres for a bevel target; for a cylindrical target planes across the face
    # width (teeth cut into the rim) or cylinders about the axis (teeth cut into a face)
    z0, z1 = float(V_t[:, 2].min()), float(V_t[:, 2].max())
    rr = np.linalg.norm(V_t[:, :2], axis=1)
    r0, r1 = float(rr.min()), float(rr.max())
    if sphere:
        kind = 'SPHERE'
    elif family == 'AUTO' and tgt.get("lap_face"):
        kind = 'CYL'
    elif family in ('PLANES', 'CYLINDERS'):
        kind = 'PLANE' if family == 'PLANES' else 'CYL'
    else:
        kind = 'PLANE'
        if not tgt.get("lap_internal", False):
            if not removed:
                tree_s = BVHTree.FromPolygons([v.co for v in me_s.vertices], [p.vertices for p in me_s.polygons])
                tree_t = BVHTree.FromPolygons([v.co for v in me_t.vertices], [p.vertices for p in me_t.polygons])
                removedFraction(src, tgt, zs, zt, sign, tree_s, tree_t, me_t, size, removed)
            if removed:
                # the tooth lines of the source run along its axis; the slices go across them:
                # cylinders when that axis points radially at the cut (a face gear), else planes
                ft = gearFrame(tgt)
                e_t = elements(tgt)[0]
                c = Vector(np.mean([tuple(q) for q in removed], axis=0))   # where the cut happens
                ax = (ft.inverted().to_3x3() @ gearFrame(src).to_3x3()) @ Vector((0, 0, 1))
                rad = Vector((c[0], c[1], 0.0))
                if rad.length > 1e-12:
                    rad.normalize()
                    tan = Vector((0, 0, 1)).cross(rad)
                    if abs(ax.dot(rad)) > max(abs(ax.z), abs(ax.dot(tan))):
                        kind = 'CYL'
    sgn = 1.0
    if kind == 'SPHERE':
        l_in, l_out = float(tgt["lap_lin"]), float(tgt["lap_lout"])
        a_, b_ = l_in, l_out
        t0dir = sphereDir(math.radians(float(tgt["lap_delta"])), 0.0)
    elif kind == 'CYL':
        a_, b_ = r0, r1
        if tgt.get("lap_face"):
            sgn = 1.0 if float(tgt["lap_face"]) > 0 else -1.0
        elif removed:
            ft = gearFrame(tgt)
            e_t = elements(tgt)[0]
            zm = np.mean([q.z for q in removed])
            sgn = 1.0 if zm > 0.5 * (z0 + z1) else -1.0
    else:
        a_, b_ = z0, z1
    e = 1e-6 * (b_ - a_)
    if kind == 'PLANE' and src.get("lap_worm") and "lap_throat" in tgt:
        # a worm wheel: its tooth surfaces bend around the worm across the width; coarse sections
        # leave chords that later nick the tips of the worm lapped by this wheel
        need = int(math.ceil((b_ - a_) / (0.3 * m_t))) + 1
        if need > nlev:
            report.append("worm wheel: %d sections instead of %d (one per 0.3 module of width)" % (need, nlev))
            nlev = need
    turns_t = None
    if kind == 'PLANE' and tgt.get("lap_worm"):
        # a worm as the target: its thread turns fast along the axis, so the sections are as dense as
        # its starter (at most 6 degrees of twist apart) and joined along the thread
        tau_t = math.tan(math.radians(float(tgt.get("lap_helix", 0.0)))) / (zt * float(tgt["lap_module"]) / 2)
        need = int(math.ceil(abs(tau_t) * (b_ - a_) / min(2 * math.pi / zt / 24, math.radians(6.0)))) + 1
        if need > nlev:
            report.append("worm target: %d sections instead of %d (along the thread)" % (need, nlev))
            nlev = need
    levels = [a_ + (b_ - a_) * k / (nlev - 1) for k in range(nlev)]
    deform_on = deform is not None and kind == 'PLANE'
    if deform is not None and not deform_on:
        report.append("press mode only for plane sections: the exact cut is used")
    if deform_on:
        simple = False
        report.append("test mode press: one subtraction at the largest overlap, then the outline only pressed "
                      "out of the source by %.3g (%.3g more at the ends)" % (deform[0], deform[1]))
    if kind == 'PLANE' and tgt.get("lap_worm"):
        turns_t = [tau_t * lv for lv in levels]
    cut_at = [min(max(v, a_ + e), b_ - e) for v in levels]

    def projection(val):
        if kind == 'SPHERE':
            return Gnomonic(t0dir, val)
        if kind == 'CYL':
            return CylProj(val, sgn)
        return Plane2d(val)
    n = zt * steps * sub * slowCycle(src, tgt, zt)[1]
    prof_s, pcls_s = wormProfileOf(src) if src.get("lap_worm") else (None, None)
    rack = kind == 'PLANE' and prof_s is not None and not tgt.get("lap_internal", False)
    if rack and _SLOW:
        rack = False
        report.append("slowed pair: the worm is turned for real, its mesh cut at every position")
    if rack:
        # the rack stands for the worm only while the worm is the screw of its profile: an edited
        # worm is turned for real (its mesh cut at every position)
        dev = wormProfileDeviation(src, me_s, prof_s, 1e-3 * sizeModule(src))
        if dev > 1e-3 * sizeModule(src):
            rack = False
            report.append("the worm mesh left the screw of its profile by %.3g (edited?): it is turned for "
                          "real, its mesh cut at every position (slow)" % dev)
    # source positions near the target element (a tooth j of the source at step k)
    # (k, matrix (4, 4), verts in the target frame, range of the level coordinate, ramp prisms)
    posl = []
    bases = [relative(src, tgt, zs, zt, sign, _TURN[0] * k / n) for k in range(n + 1)]
    lvl = levelOf(kind)
    nramp = 0
    for k in (range(0) if rack else range(n)):
        for j in range(zs):
            M = np.array(bases[k] @ rotZ(2 * math.pi * j / zs))
            Vt = V_s @ M[:3, :3].T + M[:3, 3]
            M1 = np.array(bases[k + 1] @ rotZ(2 * math.pi * j / zs))
            Vt1 = V_s @ M1[:3, :3].T + M1[:3, 3]
            lo_ = np.minimum(Vt.min(axis=0), Vt1.min(axis=0))
            hi_ = np.maximum(Vt.max(axis=0), Vt1.max(axis=0))
            if (hi_ < lo3 - grow).any() or (lo_ > hi3 + grow).any():
                continue
            # ramps: the motion from this position to the next one as convex prisms (a triangle at
            # both positions) for the faces that lead at a sharp silhouette edge; their sections
            # fill the steps a sharp edge would leave between the positions
            prisms = None
            if smooth and len(SP_s):
                mv = Vt1[TV_s].mean(axis=1) - Vt[TV_s].mean(axis=1)
                nr = N_s @ M[:3, :3].T
                cd = np.einsum("ij,ij->i", nr, mv) / np.maximum(np.linalg.norm(mv, axis=1), 1e-30)
                f0, f1 = SP_s[:, 0], SP_s[:, 1]
                sil = ((cd[f0] > NEUTRAL_COS) & (cd[f1] < -NEUTRAL_COS)) | \
                      ((cd[f1] > NEUTRAL_COS) & (cd[f0] < -NEUTRAL_COS))
                ids = np.unique(np.where(cd[f0[sil]] > 0, f0[sil], f1[sil]))
                if len(ids):
                    A = Vt[TV_s[ids]]
                    B = Vt1[TV_s[ids]]
                    B = B + (B - A) * 0.01
                    sm = SV_s[ids]
                    prisms = (np.concatenate([A, B], axis=1), ids, np.concatenate([sm, sm], axis=1))
                    nramp += len(ids)
            lv = lvl(Vt)
            vmin, vmax = float(lv.min()), float(lv.max())
            if prisms is not None:
                pl = lvl(prisms[0])
                vmin, vmax = min(vmin, float(pl.min())), max(vmax, float(pl.max()))
            posl.append((k, M, Vt, vmin, vmax, prisms))
    if rack:
        lead_s = zs * math.pi * sizeModule(src) * (1.0 if float(src.get("lap_helix", 0.0)) >= 0 else -1.0)
        px_s = math.pi * sizeModule(src)
        _, e_h, e_t, wc0 = rackFrame(src, tgt, zs, zt, sign)
        zlen_s = 2 * float(np.linalg.norm(hi3 - lo3)) + 4 * px_s
        posl = [(k, M, None, -math.inf, math.inf, None)
                for k, M in enumerate(rackPoses(src, tgt, zs, zt, sign, n, lead_s, px_s))]
        report.append("worm as a rack in every section (its turn taken as a slide along its axis): exact "
                      "sections from its axial profile, no mesh cut")
    motion = {}
    if deform_on:
        # per step: the source's previous position <- this one (for the direction a point is pressed)
        if rack:
            P0_ = relative(src, tgt, zs, zt, sign, 0.0)

            def mu(k):
                beta = 2 * math.pi * k / n
                alpha = sign * (zt / float(zs)) * beta
                return rotZ(-beta) @ P0_ @ Matrix.Translation((0.0, 0.0, -lead_s * alpha / (2 * math.pi)))
        else:
            def mu(k):
                return relative(src, tgt, zs, zt, sign, _TURN[0] * k / n)
        for k in {q[0] for q in posl}:
            motion[k] = np.array(mu(k - 1) @ mu(k).inverted())
    report.append("imprint '%s' -> '%s' (slice method, %d %s): %d -> %d teeth, ratio %.6g, %d steps of 1/%d "
                  "tooth, %d source positions near the target element, %d ramp prisms"
                  % (src.name, tgt.name, nlev, {'SPHERE': "spheres", 'PLANE': "planes across the width",
                                               'CYL': "cylinders across the face"}[kind], zs, zt, zt * _SLOW.get(tgt.name, 1) / float(zs * _SLOW.get(src.name, 1)), n,
                     steps * sub, len(posl), nramp))
    if not posl:
        raise LapError("the source never reaches the target: move the gears closer")
    cos_lim = math.cos(math.radians(limit_deg))
    worm_s, worm_t = bool(src.get("lap_worm")), bool(tgt.get("lap_worm"))
    nmain = zt * steps * slowCycle(src, tgt, zt)[1]
    results = []                  # per level: (points 2d, attrs), projection
    allk = set()
    for li, val in enumerate(cut_at):
        # the corner cache holds the source polygons of one section only (they are large)
        _corner_cache.clear()
        pr = projection(val)
        tl = sliceLoops(V_t, E_t, TE_t, kind, val)
        if not tl:
            raise LapError("a section of the target element is empty")
        Pt, trs = max(tl, key=lambda l: len(l[0]))
        loop, ok = pr.project(Pt)
        if not ok.all():
            raise LapError("the target element is too wide for the section projection")
        loop = [tuple(q) for q in loop]
        attrs = [('T', int(MI_t[t])) for t in trs]
        if area2(loop) < 0:
            loop = loop[::-1]
            attrs = attrs[::-1][1:] + attrs[::-1][:1]
        loop, attrs = dropCollinear(loop, attrs, 1e-9 * size)
        lo = np.array(loop).min(axis=0) - grow
        hi = np.array(loop).max(axis=0) + grow
        polys = []
        info = []                 # per source polygon: (working edges, corner points, points)
        rackN = None
        if rack:
            br = rackBranch(prof_s, pcls_s, lead_s, px_s, val - wc0.z, e_h, e_t, zlen_s, sizeModule(src))
            if br is not None:
                BP, BC, BN, bst = br
                rackN = np.array(BN + [(0.0, 0.0, 1.0)])
                dummy = len(BN)
                pid_pt = np.zeros(len(BP), dtype=np.int64)
                for q in range(len(bst) - 1):
                    pid_pt[bst[q]:bst[q + 1]] = q
                pid_pt[-1] = len(bst) - 2
                tb = -sizeModule(src)
                for pi, (k, M, _v, _a, _b, _p) in enumerate(posl):
                    Q = BP @ M[:3, :3].T + M[:3, 3]
                    inb = np.nonzero((Q[:, 0] >= lo[0]) & (Q[:, 0] <= hi[0]) & (Q[:, 1] >= lo[1]) & (Q[:, 1] <= hi[1]))[0]
                    if not len(inb):
                        continue
                    p0, p1 = pid_pt[inb[0]], pid_pt[inb[-1]]
                    b, e = bst[p0], bst[min(p1 + 1, len(bst) - 1)]
                    back = []
                    for idx in (e, b):
                        z_ = BP[idx, 2]
                        v = e_h * (val - wc0.z) + e_t * tb
                        back.append(np.array((v.x, v.y, z_)) @ M[:3, :3].T + M[:3, 3])
                    poly = [tuple(q[:2]) for q in Q[b:e + 1]] + [tuple(q[:2]) for q in back]
                    ea = [(-1 - j, BC[j]) for j in range(b, e)] + [(-1 - dummy, CLS_PLAIN)] * 3
                    poly, ea = clipSource(poly, ea, lo, hi, (-1 - dummy, CLS_PLAIN))
                    if not poly:
                        continue
                    tris = [a[0] for a in ea]
                    roles = [a[1] for a in ea]
                    wk, corner = sourceRoles(poly, roles, RAMP_CREASE_DEG, True)
                    polys.append(((pi, tris, len(info)), poly))
                    info.append((wk, corner, poly))
        for pi, (k, M, Vt, vmin, vmax, prisms) in enumerate([] if rack else posl):
            if vmax < val or vmin > val:
                continue
            for P, tris in sliceLoops(Vt, E_s, TE_s, kind, val):
                Q, okq = pr.project(P)
                if not okq.all():
                    continue
                if (Q.max(axis=0) < lo).any() or (Q.min(axis=0) > hi).any():
                    continue
                inside = ((Q >= lo) & (Q <= hi)).all()
                Q = [tuple(q) for q in Q]
                ea = [(int(t), CLS_FLANK if WK_s[t] else CLS_PLAIN) for t in tris]
                if not inside and not _NOCLIP:
                    # only the part near this section of the target: the rest of the source section
                    # cannot cut it, and the subtraction costs by the number of points
                    Q, ea = clipSource(Q, ea, lo, hi)
                    if not Q:
                        continue
                tl = [a[0] for a in ea]
                wk, corner = sourceRoles(Q, [a[1] for a in ea], crease, True)
                polys.append(((pi, tl, len(info)), Q))
                info.append((wk, corner, Q))
            if prisms is not None:
                # the space swept by a face at a sharp edge: works as the face does, except near the
                # path of the sharp edge
                for poly, tri, cf in prismSections(prisms, lvl, val, pr, lo, hi):
                    polys.append(((pi, [tri] * len(poly), len(info)), poly))
                    info.append(([bool(WK_s[tri])] * len(poly), cf, poly))
        if deform_on:
            de = min(val - a_, b_ - val)
            cl_ = deform[0] + deform[1] * max(0.0, 1.0 - de / max(0.1 * (b_ - a_), 1e-12))
            P_, K_ = deformSection(loop, attrs, polys, info, posl, cl_, 0.02 * m_t, motion, val, math.pi / zt, (lo, hi),
                                         steps * sub * slowCycle(src, tgt, zt)[1] // slowCycle(src, tgt, zt)[0])
            results.append(('D', [tuple(q) for q in P_], K_, pr, val))
            if _DBGPAR is not None:
                _DBGPAR.append(([tuple(q) for q in P_], [kk[0] for kk in K_]))
            continue
        lp, at = loop, attrs
        c = 0
        while c < len(polys):
            # batches of about 2500 points
            c1, nv = c, 0
            while c1 < len(polys) and (c1 == c or nv + len(polys[c1][1]) <= 2500):
                nv += len(polys[c1][1])
                c1 += 1
            lp, at = subtract2d(lp, at, polys[c:c1], 0.0)
            c = c1
            if not lp:
                raise LapError("the imprint removed a whole section of the element (wrong direction or "
                               "placement?)")
            lp, at = dropCollinear(lp, at, 1e-7 * size)
        # parasitic cuts: made by a non working face or an edge of the source, or with a normal
        # that cannot pass torque
        N = len(lp)
        par = {}
        for i in range(N):
            a = at[i]
            if a[0] != 'S':
                continue
            (pi, tris, pid), seg = a[1], a[2]
            wk, corner, poly = info[pid]
            p0, p1 = lp[i], lp[(i + 1) % N]
            if not wk[seg]:
                par[i] = 1
                continue
            if cornerCut(p0, p1, poly, corner, seg, CORNER_NEAR * m_t):
                par[i] = 2
                continue
            k, M = posl[pi][0], posl[pi][1]
            q = pr.point(0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]))
            tri_ = tris[seg] if seg < len(tris) else tris[0]
            nrm = Vector(M[:3, :3] @ (N_s[tri_] if tri_ >= 0 else rackN[-1 - tri_]))
            tt = Vector((-q.y, q.x, 0.0))
            ax = Vector(M[:3, :3] @ np.array((0.0, 0.0, 1.0)))
            ts = ax.cross(q - Vector(M[:3, 3]))
            if nrm.length < 1e-30 or tt.length < 1e-30 or ts.length < 1e-30:
                par[i] = 3
                continue
            nrm.normalize()
            # a worm passes its torque as a screw: its pressure angle is taken in the axial section
            # (the normal against its axis), not across it
            c_t = abs(nrm.z) if worm_t else transverseCos(nrm, tt, Vector((0.0, 0.0, 1.0)))
            c_s = abs(nrm.dot(ax.normalized())) if worm_s else transverseCos(nrm, ts, ax)
            if min(c_t, c_s) < cos_lim:
                par[i] = 3
            else:
                par[i] = 0
                allk.add(k // sub)
        _corner_cache.clear()
        results.append((lp, at, pr, val, par))
        if _DBGPAR is not None:
            _DBGPAR.append(([tuple(q) for q in lp], [par.get(i, -1) for i in range(len(lp))]))
    # order of the working cuts over all sections, counted from the largest gap of the turn
    ks = sorted(allk)
    kstart = 0
    if ks:
        gaps = [((ks[(i + 1) % len(ks)] - ks[i]) % nmain or nmain, i) for i in range(len(ks))]
        kstart = ks[(max(gaps)[1] + 1) % len(ks)]
    rel = [(k - kstart) % nmain for k in ks]
    kmin, kmax = (min(rel), max(rel)) if rel else (0, 0)
    data = []
    data_u = []
    npar = 0
    ncut = 0
    why = [0, 0, 0, 0]
    if kind == 'CYL':
        h_body = sgn * (z0 if sgn > 0 else z1)
        body_s = lambda h: abs(h - h_body) < 1e-6 * size
    else:
        body_s = bodyTest(tgt, sphere, m_t)
    up_s = -1 if (kind == 'PLANE' and tgt.get("lap_internal", False)) else 1
    if kind == 'CYL':
        floorOf = lambda pr: h_body + 0.25 * m_t
    else:
        floorOf = lambda pr: bodyFloor(tgt, sphere, m_t, pr.val if kind == 'SPHERE' else 1.0, up_s)
    secs = []
    if deform_on:
        kw = [kk[1] for r_ in results for kk in r_[2] if kk[0] == 1]
        k0_, k1_ = (min(kw), max(kw)) if kw else (0, 0)
        for _, lp_, K_, pr_, _v in results:
            n_ = len(lp_)
            cl_ = []
            for i in range(n_):
                kk = K_[i] if K_[i][0] else K_[(i + 1) % n_]
                if kk[0] == 0:
                    cl_.append(CLS_PLAIN)
                elif kk[0] == 2:
                    cl_.append(CLS_PARASITIC)
                    npar += 1
                else:
                    cl_.append(1 + min(BANDS - 1, int(BANDS * (kk[1] - k0_) / float(k1_ - k0_ + 1))))
                ncut += kk[0] > 0
            data.append((lp_, cl_, pr_))
        results = []
    for lp, at, pr, val, par in results:
        cls = []
        N = len(lp)
        for i in range(N):
            a = at[i]
            if a[0] != 'S':
                cls.append(a[1])
                continue
            ncut += 1
            why[par[i]] += 1
            if par[i]:
                cls.append(CLS_PARASITIC)
                npar += 1
            else:
                k = posl[a[1][0]][0]
                b = int(BANDS * ((k // sub - kstart) % nmain - kmin) / float(kmax - kmin + 1))
                cls.append(1 + min(BANDS - 1, max(0, b)))
        order = toothOrder(lp, pr, sphere, body_s, 2 * math.pi / zt)
        cls = majorityRuns(lp, cls, FLICKER * m_t, order)
        cls = filterRuns(lp, cls, FLICKER * m_t, order)
        secs.append((lp, cls, order, pr, up_s))
    if simple and len(secs) >= 3:
        # the flank ends as smooth lines over the sections (clean edges for the simple surfaces); a
        # flank may grow by at most FLICKER modules over its parasitic neighbours
        caps = [FLICKER_GROW * m_t / (lv if kind == "SPHERE" else 1.0) for lv in cut_at]
        new, changed = harmonizeFlanks(secs, caps, 3 * FLICKER * m_t)
        secs = [(lp, cls) + sec[2:] for (lp, cls), sec in zip(new, secs)]
        report.append("flank ends smoothed over the sections (%d of %d sections shortened a little)"
                      % (changed, len(secs)))
    for lp, cls, order, pr, up_ in secs:
        lp, cls = simplifyRuns(lp, cls, SIMPLIFY * m_t)
        data_u.append(mergeShort(lp, cls, 1e-5 * m_t) + (pr,))
        fl_ = floorOf(pr)
        lp, cls = reliefRuns(lp, cls, relief * m_t, 0.0, sideTest(pr, sphere, zt), clearance * m_t,
                             lambda q, pr=pr: up_s * pr.polar(q[0], q[1])[0], fl_,
                             pr.val if kind == 'SPHERE' else 1.0)
        if not lp:
            raise LapError("a section collapsed after the relief: make the relief smaller")
        lp, cls = mergeShort(lp, cls, 1e-5 * m_t)
        data.append((lp, cls, pr))
    choice = {}
    if simple:
        # the sector is chosen on the cut outlines; the relieved ones are cut to the same sector
        tops_u, tcls_u, phi0 = sectorTops(tgt, data_u, sphere and kind != 'CYL', zt, m_t, body_s, choice=choice)
    tops, tcls, phi0 = sectorTops(tgt, data, sphere and kind != 'CYL', zt, m_t, body_s, choice=choice)
    # the points of every section: corners and class changes kept, smooth runs spaced by curvature;
    # neighbouring sections are joined by the shortest triangulation between them
    if kind == 'SPHERE':
        met = lambda h, f, lv: (math.sin(h) * f * lv, h * lv)
    elif kind == 'CYL':
        met = lambda h, f, lv: (lv * f, h)
    else:
        met = lambda h, f, lv: (h * math.cos(f), h * math.sin(f))
    pins = [set() for _ in tops]
    if simple:
        up = -1 if (kind == 'PLANE' and tgt.get("lap_internal", False)) else 1
        n0 = sum(len(t) for t in tops)
        STATS.clear()
        for k in range(len(tops)):
            tops[k], tcls[k], pins[k] = simplifyTop(tops_u[k], tcls_u[k], 2 * math.pi / zt, up, m_t,
                                                    lambda h, f, lv=levels[k]: met(h, f, lv), 0.0,
                                                    (tops[k], tcls[k]), relief * m_t, clearance * m_t,
                                                    floorOf(data_u[k][2]))
        report.append("tool surfaces: tooth sides %d -> %d points (non working runs as arcs on meridians, "
                      "chamfers and walls; %d runs kept as cut)" % (n0, sum(len(t) for t in tops),
                                                                  STATS.get("runs_failed", 0)))
    if deform_on:
        # every section the same number of points, evenly along it: the sections join by quads
        lens = []
        for k in range(len(tops)):
            XY = np.array([met(h, f, levels[k]) for h, f in tops[k]])
            lens.append(float(np.hypot(*(XY[1:] - XY[:-1]).T).sum()))
        mcount = max(8, int(math.ceil(max(lens) / (0.02 * m_t))) + 1)
        for k in range(len(tops)):
            tops[k], tcls[k] = resampleTopUniform(tops[k], tcls[k], mcount,
                                                  lambda h, f, lv=levels[k]: met(h, f, lv))
        report.append("press: %d points per section, quads between the sections" % mcount)
    for k in (range(0) if deform_on else range(len(tops))):
        tops[k], tcls[k] = adaptiveTop(tops[k], tcls[k], lambda h, f, lv=levels[k]: met(h, f, lv),
                                       SIMPLIFY * m_t, 0.02 * m_t, 0.4 * m_t, pins[k])
    report.append("sections: %d cut segments, %d parasitic (%d by non working faces, %d by edges of the "
                  "source, %d by the normal; relieved by %.3g), cut in %d steps"
                  % (ncut, npar, why[1], why[2], why[3], relief * m_t, (kmax - kmin + 1) if ks else 0))
    if kind == 'SPHERE':
        me_new = bevelLoft("LAP_new", zt, levels, tops, tcls, float(tgt["lap_neck"]), float(tgt["lap_rc"]))
    elif kind == 'CYL':
        me_new = faceLoft("LAP_new", zt, levels, tops, tcls, h_body, sgn)
    else:
        me_new = spurLoft("LAP_new", zt, levels, tops, tcls, float(tgt["lap_rbody"]), turns_t, quads=deform_on)
    if remesh:
        if kind == 'SPHERE':
            place = lambda h, f, lv: sphereDir(h, f) * lv
        elif kind == 'CYL':
            place = lambda h, f, lv: Vector((lv * math.cos(f), lv * math.sin(f), sgn * h))
        else:
            place = lambda h, f, lv: Vector((h * math.cos(f), h * math.sin(f), lv))
        sz = sectionSizing(tops, levels, place, REMESH_EPS * m_t, 0.03 * m_t, 0.4 * m_t, met)
        me_new = remeshCut(me_new, m_t, report, sz, REMESH_EPS * m_t)
    if phi0:
        me_new.transform(rotZ(phi0))
        report.append("element sector turned by %.4g deg (its sides cross the teeth once)" % math.degrees(phi0))
    ob, vol = meshCheck(me_new)
    bm = bmesh.new()
    bm.from_mesh(me_new)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(me_new)
    attachMaterials(me_t)
    me_t.update()
    report.append("target element: %d faces, volume %.6g, open edges %d" % (len(me_t.polygons), vol, ob))
    if ob:
        report.append("WARNING: the element is not closed")
    report.append("done in %.1f s" % (time.time() - t0))
    tgt["lap_source"] = src.name
    tgt["lap_sign"] = int(sign)
    tgt["lap_steps"] = int(steps)
    return sign


# ---------------------------------------------------------------------------
# adaptive isotropic remeshing (botsch & kobbelt 2004, sizing after dunyach et al. 2013) of the cut
# surfaces of an element: long edges are split, short ones collapsed, edges flipped toward valence
# 6, the points smoothed along the surface and put back onto it. the target edge length follows the
# curvature: L = sqrt(6 eps / k - 3 eps^2) keeps the deviation of the triangles below eps. the
# borders of the cut surfaces (to the blank, the ends, the sector sides, between working and
# parasitic faces) stay as they are, so the element still fits its neighbours
# ---------------------------------------------------------------------------

def faceKind(f):
    c = f.material_index
    return 0 if c in (CLS_PLAIN, CLS_FLANK) else (2 if c == CLS_PARASITIC else 1)


def remeshCut(me, module, report, sizing, band, iters=5, max_faces=60000):
    # sizing: [(point, target edge length)] from the curvature of the section outlines (the profile
    # curvature dominates on gear flanks); a new point takes the length of the nearest sample
    from mathutils.kdtree import KDTree
    t0 = time.time()
    bm = bmesh.new()
    bm.from_mesh(me)
    triangulateSafe(bm)
    bm.normal_update()
    if not any(faceKind(f) for f in bm.faces) or not sizing:
        bm.free()
        return me
    ref = BVHTree.FromBMesh(bm)
    kd = KDTree(len(sizing))
    for i, (co, l) in enumerate(sizing):
        kd.insert(co, i)
    kd.balance()

    def target(co):
        _, idx, _ = kd.find(co)
        return sizing[idx][1]

    def inside(e):
        # an edge of the cut surfaces that may change: two faces of the same cut kind
        lf = e.link_faces
        if len(lf) != 2:
            return False
        k0 = faceKind(lf[0])
        return k0 != 0 and k0 == faceKind(lf[1])

    def frozenSet():
        fz = set()
        for e in bm.edges:
            if not inside(e):
                fz.add(e.verts[0])
                fz.add(e.verts[1])
        return fz

    L = {v: target(v.co) for v in bm.verts}
    stats = [0, 0, 0]
    for it in range(iters):
        # split long edges
        if len(bm.faces) < max_faces:
            for e in [e for e in bm.edges if inside(e)]:
                if not e.is_valid:
                    continue
                a, b = e.verts
                lt = 0.5 * (L.get(a) or target(a.co)) + 0.5 * (L.get(b) or target(b.co))
                if e.calc_length() <= 4.0 / 3.0 * lt:
                    continue
                ne, nv = bmesh.utils.edge_split(e, a, 0.5)
                L[nv] = target(nv.co)
                for f in list(nv.link_faces):
                    vs = list(f.verts)
                    if len(vs) == 4:
                        bmesh.utils.face_split(f, nv, vs[(vs.index(nv) + 2) % 4])
                stats[0] += 1
        # collapse short edges
        bm.normal_update()
        fz = frozenSet()
        for e in [e for e in bm.edges if inside(e)]:
            if not e.is_valid or not inside(e):
                continue
            a, b = e.verts
            lt = 0.5 * (L.get(a) or target(a.co)) + 0.5 * (L.get(b) or target(b.co))
            if e.calc_length() >= 4.0 / 5.0 * lt:
                continue
            fa, fb = a in fz, b in fz
            if fa and fb:
                continue
            keep, gone = (a, b) if fa else ((b, a) if fb else (a, b))
            pos = keep.co.copy() if (fa or fb) else (a.co + b.co) * 0.5
            na = {x.other_vert(a) for x in a.link_edges}
            nb = {x.other_vert(b) for x in b.link_edges}
            if len(na & nb) != 2:
                continue
            ok = True
            for v in (a, b):
                for x in v.link_edges:
                    w = x.other_vert(v)
                    if w is not a and w is not b and (w.co - pos).length > 4.0 / 3.0 * lt:
                        ok = False
                        break
                if not ok:
                    break
                for f in v.link_faces:
                    if e in f.edges:
                        continue
                    c = [pos if w is v else w.co for w in f.verts]
                    nn = (c[1] - c[0]).cross(c[2] - c[0])
                    if nn.length < 1e-24 or nn.dot(f.normal) <= 0.2 * nn.length:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            lk = L.get(keep) or target(keep.co)
            bmesh.ops.pointmerge(bm, verts=[keep, gone], merge_co=pos)
            if keep.is_valid:
                L[keep] = lk
            stats[1] += 1
        # flip toward valence 6 (4 on the borders), only between nearly coplanar triangles
        bm.normal_update()
        fz = frozenSet()
        for e in [e for e in bm.edges if inside(e)]:
            if not e.is_valid or not inside(e):
                continue
            f0, f1 = e.link_faces
            if len(f0.verts) != 3 or len(f1.verts) != 3 or f0.normal.dot(f1.normal) < math.cos(math.radians(10)):
                continue
            a, b = e.verts
            c = [w for w in f0.verts if w is not a and w is not b][0]
            d = [w for w in f1.verts if w is not a and w is not b][0]
            if bm.edges.get((c, d)) is not None:
                continue
            wa, wb, wc, wd = (4 if v in fz else 6 for v in (a, b, c, d))
            va, vb, vc, vd = len(a.link_edges), len(b.link_edges), len(c.link_edges), len(d.link_edges)
            before = abs(va - wa) + abs(vb - wb) + abs(vc - wc) + abs(vd - wd)
            after = abs(va - 1 - wa) + abs(vb - 1 - wb) + abs(vc + 1 - wc) + abs(vd + 1 - wd)
            if after >= before:
                continue
            n1 = (a.co - c.co).cross(d.co - c.co)
            n2 = (d.co - c.co).cross(b.co - c.co)
            if n1.dot(f0.normal) <= 0 or n2.dot(f0.normal) <= 0:
                continue
            if bmesh.utils.edge_rotate(e, False) is not None:
                stats[2] += 1
        # smooth and keep the points within band of the original surface: the section surface
        # between two sections is only piecewise flat (thin triangles with scattered normals), so
        # the points are not put exactly back onto it but anywhere closer than band
        bm.normal_update()
        fz = frozenSet()
        moves = []
        for v in bm.verts:
            if v in fz or not v.link_edges:
                continue
            nbr = [x.other_vert(v).co for x in v.link_edges]
            cen = sum(nbr, Vector()) / len(nbr)
            moves.append((v, v.co + 0.5 * (cen - v.co)))
        for v, p in moves:
            loc, nor, idx, dist = ref.find_nearest(p)
            if loc is not None and dist > band:
                p = loc + (p - loc) * (band / dist)
            v.co = p
            L[v] = target(v.co)
    ok = all(e.is_manifold for e in bm.edges)
    # deviation: points of the original surface against the new one
    new_tree = BVHTree.FromBMesh(bm)
    # (measured on the working faces: the relieved parasitic faces vary by up to the relief depth
    # from one section to the next, and there the smoothing is wanted)
    ds = []
    old = bmesh.new()
    old.from_mesh(me)
    for v in old.verts:
        if not v.link_faces or any(faceKind(f) != 1 for f in v.link_faces):
            continue
        loc, nor, idx, dist = new_tree.find_nearest(v.co)
        if dist is not None:
            ds.append(dist)
    old.free()
    ds = np.array(ds) if ds else np.zeros(1)
    dev = float(ds.max())
    dev99 = float(np.percentile(ds, 99))
    if not ok:
        bm.free()
        report.append("WARNING: remeshing skipped (the mesh would not stay closed)")
        return me
    out = bpy.data.meshes.new(me.name)
    bm.to_mesh(out)
    bm.free()
    report.append("remeshed the cut surfaces: %d splits, %d collapses, %d flips, %d -> %d faces, "
                  "deviation of the working faces from the section surface: 99%% of the points within %.2g "
                  "modules, largest %.2g, %.1f s"
                  % (stats[0], stats[1], stats[2], len(me.polygons), len(out.polygons), dev99 / module,
                     dev / module, time.time() - t0))
    attachMaterials(out)
    bpy.data.meshes.remove(me)
    return out


def sectionSizing(tops, levels, place, eps, lmin, lmax, met):
    # target edge lengths at the points of the section outlines from their curvature (circle
    # through the neighbours in the section metric): L = sqrt(6 eps / k - 3 eps^2)
    out = []
    for top, lv in zip(tops, levels):
        M = [met(h, f, lv) for h, f in top]
        for k in range(len(top)):
            if 0 < k < len(top) - 1:
                a, b, c = M[k - 1], M[k], M[k + 1]
                la, lb, lc = math.dist(a, b), math.dist(b, c), math.dist(a, c)
                cr = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
                kap = 2 * cr / max(la * lb * lc, 1e-30)
                u = ((b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])) / max(la * lb, 1e-30)
                if u < math.cos(math.radians(20)):
                    kap = 0.0                  # a corner: a feature, not curvature
            else:
                kap = 0.0
            if kap > 1e-12:
                q = 6 * eps / kap - 3 * eps * eps
                L = math.sqrt(q) if q > 0 else lmin
            else:
                L = lmax
            out.append((place(top[k][0], top[k][1], lv), min(lmax, max(lmin, L))))
    # neighbouring samples along an outline differ by at most 30%
    for _ in range(4):
        for i in range(1, len(out)):
            a, b = out[i - 1][1], out[i][1]
            if a > 1.3 * b:
                out[i - 1] = (out[i - 1][0], 1.3 * b)
            elif b > 1.3 * a:
                out[i] = (out[i][0], 1.3 * a)
    return out


def imprint3d(context, src, tgt, steps_per_tooth, sign_mode, smooth, report):
    t0 = time.time()
    zs = int(src["lap_teeth"])
    zt = int(tgt["lap_teeth"])
    checkRotary(src)
    checkRotary(tgt)
    checkVersion(src)
    checkVersion(tgt)
    if gearMesh(src) == gearMesh(tgt):
        raise LapError("source and target share the element mesh")
    me_s = toolMesh(src)
    try:
        return imprintWith(context, src, tgt, me_s, steps_per_tooth, sign_mode, smooth, report, t0)
    finally:
        bpy.data.meshes.remove(me_s)


def imprintWith(context, src, tgt, me_s, steps_per_tooth, sign_mode, smooth, report, t0):
    zs = int(src["lap_teeth"])
    zt = int(tgt["lap_teeth"])
    me_t = gearMesh(tgt)
    e_t = elements(tgt)[0]
    blo, bhi = meshBox(me_t)
    size = float(np.linalg.norm(bhi - blo))
    tree_s = BVHTree.FromPolygons([v.co for v in me_s.vertices], [p.vertices for p in me_s.polygons])
    tree_t = BVHTree.FromPolygons([v.co for v in me_t.vertices], [p.vertices for p in me_t.polygons])
    ft = gearFrame(tgt)
    to_frame = ft.inverted() @ e_t.matrix_world
    if sign_mode == 'AUTO':
        fp = removedFraction(src, tgt, zs, zt, 1.0, tree_s, tree_t, me_t, size)
        fm = removedFraction(src, tgt, zs, zt, -1.0, tree_s, tree_t, me_t, size)
        sign = 1.0 if fp < fm else -1.0
        report.append("direction test: removed %.0f%% with +1, %.0f%% with -1 -> %+d"
                      % (100 * fp, 100 * fm, int(sign)))
        if min(fp, fm) > 0.8 * max(fp, fm):
            report.append("WARNING: direction test unclear, set the direction by hand")
    else:
        sign = 1.0 if sign_mode == 'PLUS' else -1.0
    # target element box in the target frame, grown by the motion of one step
    corners = np.array([tuple(to_frame @ Vector(c)) for c in e_t.bound_box])
    lo = corners.min(axis=0)
    hi = corners.max(axis=0)
    n = zt * steps_per_tooth * slowCycle(src, tgt, zt)[1]
    # n + 1 positions: the last one is the full turn (the source teeth are shifted there, so the
    # interval before it must end at beta = 2 pi and not wrap to position 0)
    rels = [relative(src, tgt, zs, zt, sign, _TURN[0] * k / n) for k in range(n + 1)]
    # a source tooth is in mesh with the target element when any of its vertices comes into the
    # element box grown by the longest edge (so faces crossing the box are caught too)
    sv, stris, spairs = triangles(me_s)
    step_move = 0.0
    touch = {}
    for k in range(n):
        for j in range(zs):
            m = rels[k] @ rotZ(2 * math.pi * j / zs)
            c = npApply(m, sv)
            tmin = np.minimum.reduce([c[stris[:, 0]], c[stris[:, 1]], c[stris[:, 2]]])
            tmax = np.maximum.reduce([c[stris[:, 0]], c[stris[:, 1]], c[stris[:, 2]]])
            if np.any(np.all((tmax >= lo) & (tmin <= hi), axis=1)):
                touch.setdefault(j, set()).add(k)
                c1 = npApply(rels[k + 1] @ rotZ(2 * math.pi * j / zs), sv)
                step_move = max(step_move, float(np.linalg.norm(c1 - c, axis=1).max()))
    npos = sum(len(v) for v in touch.values())
    report.append("imprint '%s' -> '%s': %d -> %d teeth, ratio %.6g, %d steps (1/%d tooth), "
                  "%d positions of source teeth in mesh with the target element"
                  % (src.name, tgt.name, zs, zt, zt * _SLOW.get(tgt.name, 1) / float(zs * _SLOW.get(src.name, 1)), n, steps_per_tooth, npos))
    if not npos:
        raise LapError("the source never reaches the target: move the gears closer")
    glo = lo - step_move
    ghi = hi + step_move
    tools = []
    for j, ks in touch.items():
        for k in ks:
            tools.append((me_s, ft @ rels[k] @ rotZ(2 * math.pi * j / zs)))
    if smooth:
        verts, tris, pairs = sv, stris, spairs
        min_thick = 1e-5 * size
        min_area = (1e-3 * size) ** 2
        prisms = []
        for j, ks in touch.items():
            rj = rotZ(2 * math.pi * j / zs)
            for k in sorted({(k - 1) % n for k in ks} | ks):
                pr = rampPrisms(verts, tris, pairs, rels[k] @ rj, rels[k + 1] @ rj, glo, ghi, min_area)
                if pr is not None:
                    prisms += splitPieces(pr, min_thick)
                    bpy.data.meshes.remove(pr)
        nprism = len(prisms)
        packs = packDisjoint(prisms)
        for pm in packs:
            tools.append((pm, ft))
        report.append("smooth sweep: %d positions plus %d prisms (in %d disjoint packs) for the motion "
                      "between them" % (npos, nprism, len(packs)))
    nf = sum(len(t[0].polygons) for t in tools)
    if nf > MAX_TOOL_FACES:
        for me, mm in tools:
            if me is not me_s and me.users == 0:
                bpy.data.meshes.remove(me)
        raise LapError("%d tool faces, too heavy: use fewer steps per tooth or a simpler source" % nf)
    ob0, vol0 = meshCheck(me_t)
    # ramps are subtracted one by one: a ramp may cross itself slightly at the border of its
    # forward patch (chords instead of arcs); alone that is harmless, in a batch union it is not
    res = booleanChecked(context, me_t, e_t.matrix_world, tools, report)
    for me, mm in tools:
        if me is not me_s and me.users == 0:
            bpy.data.meshes.remove(me)
    res = dropCrumbs(res)
    ob1, vol1 = meshCheck(res)
    if len(res.polygons) == 0:
        bpy.data.meshes.remove(res)
        raise LapError("the imprint removed the whole element (wrong direction or placement?)")
    # write into the shared element mesh: all teeth of the target change
    bm = bmesh.new()
    bm.from_mesh(res)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(res)
    me_t.update()
    report.append("tool faces %d; target element: volume %.6g -> %.6g, %d faces, open edges %d"
                  % (nf, vol0, vol1, len(me_t.polygons), ob1))
    if ob1:
        report.append("WARNING: the element is not closed")
    report.append("done in %.1f s" % (time.time() - t0))
    tgt["lap_source"] = src.name
    tgt["lap_sign"] = int(sign)
    tgt["lap_steps"] = int(steps_per_tooth)
    return sign


def methodOf(src, tgt):
    # which engine an imprint of this pair uses
    if src is None or tgt is None or src == tgt:
        return None
    if isRack(src) or isRack(tgt):
        return 'RACK'
    if tgt.get("lap_custom"):
        return 'MERIDIAN'
    try:
        if pairMode(src, tgt) is not None:
            return 'SECTION'
    except Exception:
        return None
    if tgt.get("lap_kind") == 'SPUR' and "lap_rbody" in tgt or tgt.get("lap_kind") == 'BEVEL':
        return 'SLICES'
    return 'BOOLEAN'


# ---------------------------------------------------------------------------
# worm as the target: a running worm repeats its axial profile along the thread (a screw), so it is
# made from one meridian section - the half plane through its axis where the wheel sits - cut by
# all positions of the wheel over one turn of the worm, exactly as a slice. one axial pitch of that
# section about the wheel's middle plane is the profile of the new worm; the element is its screw
# sweep (quads along the thread, see wormSweep). the root becomes a floor c* below the deepest cut
# with radial walls at the ends of the working flanks
# ---------------------------------------------------------------------------

def douglasPeucker(pts, tol):
    # indices of the points kept on an open polyline
    if len(pts) < 3:
        return list(range(len(pts)))
    keep = [0, len(pts) - 1]
    stack = [(0, len(pts) - 1)]
    P = np.asarray(pts, dtype=float)
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        d = P[b] - P[a]
        l = float(np.hypot(d[0], d[1]))
        Q = P[a + 1:b] - P[a]
        if l > 0:
            dist = np.abs(Q[:, 0] * d[1] - Q[:, 1] * d[0]) / l
        else:
            dist = np.hypot(Q[:, 0], Q[:, 1])
        i = int(np.argmax(dist))
        if dist[i] > tol:
            keep.append(a + 1 + i)
            stack += [(a, a + 1 + i), (a + 1 + i, b)]
    return sorted(set(keep))


def wormProfile(chain, ccls, zc, px, r_tip, bore, mx, clearance, report):
    # one axial pitch of the lapped meridian outline (chain [(r, z)] from the bottom end to the top
    # end, ccls per segment) about zc, cut in the middle of tip lands: [(u, r)] and classes
    n = len(chain)
    kind = lambda c: 'W' if working(c) else ('P' if c == CLS_PARASITIC else 'O')
    # the pitch about the wheel's middle plane, cut on tip lands (points near the tip radius)
    tipseg = [i for i in range(n - 1) if chain[i][0] > r_tip - 0.1 * mx and chain[i + 1][0] > r_tip - 0.1 * mx]
    zA = None
    if tipseg:
        mids = [0.5 * (chain[i][1] + chain[i + 1][1]) for i in tipseg]
        for zm in sorted(mids, key=lambda q: abs(q + px / 2 - zc)):
            if abs(zm + px / 2 - zc) > px / 2:
                break
            if any(min(chain[i][1], chain[i + 1][1]) - 1e-9 <= zm + px <= max(chain[i][1], chain[i + 1][1]) + 1e-9
                   for i in tipseg):
                zA = zm
                break
    if zA is None:
        zA = zc - px / 2
        report.append("worm: no uncut tip land to start the pitch at, cut at the wheel's middle plane")

    def crossing(zv):
        best = None
        for i in range(n - 1):
            (r0, z0), (r1, z1) = chain[i], chain[i + 1]
            if (z0 - zv) * (z1 - zv) <= 0 and z0 != z1:
                t = (zv - z0) / (z1 - z0)
                r = r0 + (r1 - r0) * t
                if best is None or r > best[0]:
                    best = (r, i, t)
        return best
    ca, cb = crossing(zA), crossing(zA + px)
    if ca is None or cb is None or cb[1] < ca[1]:
        raise LapError("the lapped worm has no whole axial pitch: make the worm longer")
    pts = [(ca[0], zA)] + [chain[i] for i in range(ca[1] + 1, cb[1] + 1)] + [(cb[0], zA + px)]
    cl = [ccls[i] for i in range(ca[1], cb[1] + 1)]
    # short working runs among parasitic ones (and the other way round) follow their neighbours
    lmin = FLICKER * mx
    for _ in range(3):
        runs = []
        i = 0
        while i < len(cl):
            j = i
            while j + 1 < len(cl) and kind(cl[j + 1]) == kind(cl[i]):
                j += 1
            runs.append((i, j))
            i = j + 1
        changed = False
        for r_, (i, j) in enumerate(runs):
            if r_ == 0 or r_ == len(runs) - 1:
                continue
            ln = sum(math.dist(pts[q], pts[q + 1]) for q in range(i, j + 1))
            kp, kn, k0 = kind(cl[runs[r_ - 1][0]]), kind(cl[runs[r_ + 1][0]]), kind(cl[i])
            if ln < lmin and kp == kn and kp != k0 and 'O' not in (kp, k0):
                new = cl[runs[r_ - 1][0]]
                for q in range(i, j + 1):
                    cl[q] = new
                changed = True
        if not changed:
            break
    # the root: a floor c* below the deepest cut, radial walls at the ends of the flanks
    rs = [q[0] for q in pts]
    imin = int(np.argmin(rs))
    wl = [i for i in range(min(imin, len(cl))) if kind(cl[i]) == 'W']
    wr = [i for i in range(imin, len(cl)) if kind(cl[i]) == 'W']
    if wl and wr:
        a, b = wl[-1] + 1, wr[0]              # points: end of the left flank, start of the right one
        r_floor = max(bore + 0.25 * mx, rs[imin] - clearance * mx)
        (ra_, za), (rb_, zb) = pts[a], pts[b]
        inner = pts[a:b + 1]
        if za < zb and all(za - 1e-9 <= z <= zb + 1e-9 and r >= r_floor - 1e-9 for r, z in inner):
            pts = pts[:a + 1] + [(r_floor, za), (r_floor, zb)] + pts[b:]
            cl = cl[:a] + [CLS_PARASITIC] * 3 + cl[b:]
        else:
            report.append("worm: the root was left as cut (it reaches past the ends of the flanks)")
    # fewer points: every run of one kind (working, parasitic, uncut) simplified on its own; a kept
    # segment takes the step class of the longest cut segment it covers
    out, oc = [pts[0]], []
    i = 0
    while i < len(cl):
        j = i
        while j + 1 < len(cl) and kind(cl[j + 1]) == kind(cl[i]):
            j += 1
        run = pts[i:j + 2]
        keep = douglasPeucker([(z, r) for r, z in run], 1e-3 * mx)
        for q0, q1 in zip(keep[:-1], keep[1:]):
            out.append(run[q1])
            best = max(range(q0, q1), key=lambda q: math.dist(run[q], run[q + 1]))
            oc.append(cl[i + best])
        i = j + 1
    prof = [(z, r) for r, z in out[:-1]]
    return prof, oc


def simplifySection(poly, vf, tris, wk, onbox, tol):
    # a closed source section with fewer points: runs between fixed points (corners, changes of the
    # working flag, the ends of the edges along the clip box) simplified by Douglas-Peucker; a kept
    # edge takes the triangle and flag of the first edge it covers
    n = len(poly)
    if n < 8 or tol <= 0:
        return poly, vf, tris, wk
    fixed = [i for i in range(n) if vf[i] or wk[i] != wk[i - 1] or onbox[i] or onbox[i - 1]]
    if not fixed:
        fixed = [0]
    keep = []
    for q, a in enumerate(fixed):
        b = fixed[(q + 1) % len(fixed)]
        L = (b - a) % n or n
        run = [poly[(a + i) % n] for i in range(L + 1)]
        ks = douglasPeucker(run, tol)
        keep += [(a + i) % n for i in ks[:-1]]
    if len(keep) < 3 or len(keep) == n:
        return poly, vf, tris, wk
    return ([poly[i] for i in keep], [vf[i] for i in keep], [tris[i] for i in keep], [wk[i] for i in keep])


def trimTool(src, tgt, zs, zt, sign, me, r_t, z0, z1, size, report):
    # the part of the source along its axis that can ever come near the target (every point turns
    # on a circle about the source axis; the target lies within r_t and z0 .. z1 about its own axis,
    # whatever its turn): the source is cut by two planes across its axis just outside that part
    # and the cuts are closed. a long worm cutting a thin disc keeps only its middle. a temporary
    # mesh, or None when nothing would go
    V = np.array([tuple(v.co) for v in me.vertices])
    if len(V) < 4:
        return None
    M0 = np.array(relative(src, tgt, zs, zt, sign, 0.0))
    marg = 0.02 * size
    reach = np.zeros(len(V), dtype=bool)
    for a in np.linspace(0.0, 2 * math.pi, 72, endpoint=False):
        c, s_ = math.cos(a), math.sin(a)
        Va = np.c_[c * V[:, 0] - s_ * V[:, 1], s_ * V[:, 0] + c * V[:, 1], V[:, 2]]
        P = Va @ M0[:3, :3].T + M0[:3, 3]
        reach |= (np.hypot(P[:, 0], P[:, 1]) <= r_t + marg) & (P[:, 2] >= z0 - marg) & (P[:, 2] <= z1 + marg)
    if not reach.any():
        return None
    bm = bmesh.new()
    bm.from_mesh(me)
    el = max((e.calc_length() for e in bm.edges), default=0.0)
    h0 = float(V[reach, 2].min()) - el - marg
    h1 = float(V[reach, 2].max()) + el + marg
    zmin, zmax = float(V[:, 2].min()), float(V[:, 2].max())
    if h0 <= zmin + 0.05 * (zmax - zmin) and h1 >= zmax - 0.05 * (zmax - zmin):
        bm.free()
        return None
    if h0 > zmin:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-9 * size,
                               plane_co=(0.0, 0.0, h0), plane_no=(0.0, 0.0, 1.0), clear_inner=True)
    if h1 < zmax:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-9 * size,
                               plane_co=(0.0, 0.0, h1), plane_no=(0.0, 0.0, 1.0), clear_outer=True)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        res = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
        for f in res.get("faces", []):
            f.material_index = CLS_PLAIN
    if any(e.is_boundary for e in bm.edges):
        bm.free()
        return None
    out = bpy.data.meshes.new("LAP_trim")
    bm.to_mesh(out)
    report.append("tool cut to the part that can reach the target: %.4g .. %.4g of %.4g .. %.4g along its axis, "
                  "%d of %d faces" % (max(h0, zmin), min(h1, zmax), zmin, zmax, len(bm.faces), len(me.polygons)))
    bm.free()
    return out


def imprintWorm(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, report, clearance=0.25,
                extend=0.5):
    t0 = time.time()
    zs = int(src["lap_teeth"])
    zt = int(tgt["lap_teeth"])
    mx = sizeModule(tgt)
    px = math.pi * mx
    me_s = gearMesh(src)
    me_t = gearMesh(tgt)
    zz = [v.co.z for v in me_t.vertices]
    zlo, zhi = min(zz), max(zz)
    r_tip = max(math.hypot(v.co.x, v.co.y) for v in me_t.vertices)
    bore = float(tgt["lap_rbody"])
    size = math.hypot(2 * r_tip, zhi - zlo)
    if sign_mode == 'AUTO':
        sign = previousSign(src, tgt)
        if sign is not None:
            report.append("direction %+d as in the pass that made the source" % int(sign))
        else:
            tree_s = BVHTree.FromPolygons([v.co for v in me_s.vertices], [p.vertices for p in me_s.polygons])
            tree_t = BVHTree.FromPolygons([v.co for v in me_t.vertices], [p.vertices for p in me_t.polygons])
            fp = removedFraction(src, tgt, zs, zt, 1.0, tree_s, tree_t, me_t, size)
            fm = removedFraction(src, tgt, zs, zt, -1.0, tree_s, tree_t, me_t, size)
            sign = 1.0 if fp < fm else -1.0
            report.append("direction test: removed %.0f%% with +1, %.0f%% with -1 -> %+d"
                          % (100 * fp, 100 * fm, int(sign)))
            if min(fp, fm) > 0.8 * max(fp, fm):
                report.append("WARNING: direction test unclear, set the direction by hand")
    else:
        sign = 1.0 if sign_mode == 'PLUS' else -1.0
    me_x = extendedTool(src, me_s, extend, report, tgt, me_t)
    me_c = trimTool(src, tgt, zs, zt, sign, me_x if me_x is not None else me_s, r_tip, zlo, zhi, size, report)
    V_s, E_s, TE_s, TV_s, N_s, SP_s, MI_s = meshArrays(me_c if me_c is not None else
                                                       (me_x if me_x is not None else me_s), RAMP_CREASE_DEG)
    for me_ in (me_x, me_c):
        if me_ is not None:
            bpy.data.meshes.remove(me_)
    WK_s = np.array([working(int(c)) for c in MI_s], dtype=bool)
    if not WK_s.any():
        WK_s[:] = True
    slow = _SLOW.get(src.name, 1)
    slow_t = _SLOW.get(tgt.name, 1)
    # the tool comes back to the same place after one turn of the worm, or after N turns (while the
    # wheel moves by slow_t teeth); the positions are as dense per turn and per tooth as without
    ncyc, fac = slowCycle(src, tgt, zt)
    n = zt * steps * sub * 4 * fac
    turn = _TURN[0]

    custom = bool(tgt.get("lap_custom"))
    if custom:
        TA = [(np.array(el.matrix_basis), meshArrays(el.data)) for el in elements(tgt)]

    def targetSection(t):
        # an own target body: its outline on the meridian half plane at t (the section with the
        # plane, clipped to r >= 0), the largest loop
        best = None
        R = np.array(rotZ(-t))
        for Mb, A in TA:
            M = R @ Mb
            Vt_ = A[0] @ M[:3, :3].T + M[:3, 3]
            for P, _tr in sliceLoops(Vt_[:, [0, 2, 1]], A[1], A[2], 'PLANE', 0.0):
                Q = [tuple(q) for q in P[:, :2]]
                out = []
                for i in range(len(Q)):
                    a, b = Q[i], Q[(i + 1) % len(Q)]
                    if a[0] >= 0:
                        out.append((max(a[0], 0.0), a[1]))
                    if (a[0] >= 0) != (b[0] >= 0):
                        f = a[0] / (a[0] - b[0])
                        out.append((0.0, a[1] + (b[1] - a[1]) * f))
                if len(out) >= 3:
                    ar = area2(out)
                    if best is None or abs(ar) > abs(best[0]):
                        best = (ar, out)
        if best is None:
            raise LapError("the target body does not reach the meridian half plane at %.1f deg"
                           % math.degrees(t))
        ar, out = best
        return dropCollinear(out if ar > 0 else out[::-1], [('T', CLS_PLAIN)] * len(out), 1e-9 * size)[0]

    lo = np.array((bore - mx, zlo - mx))
    hi = np.array((r_tip + mx, zhi + mx))
    simp = 0.0 * mx           # source sections simplified by this much (Douglas-Peucker)
    lo2, hi2 = lo - 0.25 * mx, hi + 0.25 * mx
    posl = []                 # (step, matrix source element -> target frame) per source position
    zc_ = [None]

    el_s = float(np.linalg.norm(V_s[E_s[:, 0]] - V_s[E_s[:, 1]], axis=1).max()) if len(E_s) else 0.0

    def gather(ts):
        # the source sections on the meridian half planes at the angles ts: every source position
        # is placed once and cut only by the meridians it reaches (its angular range about the
        # target axis); the sections are clipped to the box about the target section.
        # per meridian: [(tag, polygon)] and [(working edges, corner flags, polygon)]
        polys = [[] for _ in ts]
        info = [[] for _ in ts]
        tarr = np.array(ts)
        cs_, sn_ = np.cos(tarr), np.sin(tarr)
        for k in range(n):
            base = relative(src, tgt, zs, zt, sign, turn * k / n)
            for j in range(zs):
                M0 = np.array(base @ rotZ(2 * math.pi * j / zs))
                if zc_[0] is None:
                    zc_[0] = float(M0[2, 3])
                V0 = V_s @ M0[:3, :3].T + M0[:3, 3]
                rr = np.hypot(V0[:, 0], V0[:, 1])
                # (a long triangle comes closer to the axis than its corners: less its longest edge)
                if V0[:, 2].max() < lo[1] or V0[:, 2].min() > hi[1] or rr.min() - el_s > hi[0]:
                    continue
                # the meridians this position reaches
                far = rr > 1e-9 * size
                if not far.any():
                    continue
                ph = np.arctan2(V0[:, 1], V0[:, 0])
                c0 = math.atan2(float(np.sin(ph[far]).sum()), float(np.cos(ph[far]).sum()))
                dph = (ph - c0 + math.pi) % (2 * math.pi) - math.pi
                a0, a1 = float(dph[far].min()), float(dph[far].max())
                cross_axis = False
                if rr.min() - el_s <= 0:
                    # does a triangle pass the axis (its projection across the axis holds it)?
                    X_, Y_ = V0[TV_s, 0], V0[TV_s, 1]
                    c0_ = X_[:, 0] * Y_[:, 1] - Y_[:, 0] * X_[:, 1]
                    c1_ = X_[:, 1] * Y_[:, 2] - Y_[:, 1] * X_[:, 2]
                    c2_ = X_[:, 2] * Y_[:, 0] - Y_[:, 2] * X_[:, 0]
                    cross_axis = bool((((c0_ >= 0) & (c1_ >= 0) & (c2_ >= 0)) |
                                       ((c0_ <= 0) & (c1_ <= 0) & (c2_ <= 0))).any())
                if not far.all() or a1 - a0 > 1.5 * math.pi or cross_axis:
                    # the source passes the axis: all meridians, whole sections
                    hit = np.arange(len(ts))
                    tmin = tmax = None
                else:
                    # angular range of every triangle about the target axis: a meridian is crossed
                    # only by the triangles whose range holds it
                    dT = dph[TV_s]
                    tmin, tmax = dT.min(axis=1), dT.max(axis=1)
                    dt = (tarr - c0 + math.pi) % (2 * math.pi) - math.pi
                    hit = np.nonzero((dt >= a0 - 1e-9) & (dt <= a1 + 1e-9))[0]
                if tmin is not None:
                    dtl = ((tarr - c0 + math.pi) % (2 * math.pi) - math.pi)
                if not len(hit):
                    continue
                pi_ = len(posl)
                posl.append((k, M0))
                for jm in hit:
                    c_, s_ = cs_[jm], sn_[jm]
                    Vr = np.empty_like(V0)
                    Vr[:, 0] = c_ * V0[:, 0] + s_ * V0[:, 1]
                    Vr[:, 1] = V0[:, 2]
                    Vr[:, 2] = -s_ * V0[:, 0] + c_ * V0[:, 1]
                    if tmin is None:
                        loops_ = sliceLoops(Vr, E_s, TE_s, 'PLANE', 0.0)
                    else:
                        cand = np.nonzero((tmin <= dtl[jm]) & (tmax >= dtl[jm]))[0]
                        loops_ = sliceSub(Vr, E_s, TE_s, cand)
                    for P, tris in loops_:
                        Q = P[:, :2]
                        if (Q.max(axis=0) < lo).any() or (Q.min(axis=0) > hi).any() or Q[:, 0].min() < 0:
                            continue
                        # points outside the box: of a run on the same side only its ends are kept (the
                        # chord stays on that side), then the exact clip
                        code = np.where(Q[:, 0] < lo2[0], 1, np.where(Q[:, 0] > hi2[0], 2,
                                        np.where(Q[:, 1] < lo2[1], 3, np.where(Q[:, 1] > hi2[1], 4, 0))))
                        kp = (code == 0) | (code != np.roll(code, 1)) | (code != np.roll(code, -1))
                        if not kp.all():
                            ix = np.nonzero(kp)[0]
                            if len(ix) < 3:
                                continue
                            Q = Q[ix]
                            tris = [tris[i] for i in ix]
                        Ql = [tuple(q) for q in Q]
                        wk, corner = sourceRoles(Ql, [CLS_FLANK if WK_s[t_] else CLS_PLAIN for t_ in tris],
                                                 RAMP_CREASE_DEG, True)
                        poly2, vf2, e2 = clipBoxAttr(Ql, corner, list(zip(tris, wk)), lo, hi)
                        if not poly2:
                            continue
                        tr2 = [e[0] if e is not None else tris[0] for e in e2]
                        wk2 = [bool(e[1]) if e is not None else False for e in e2]
                        poly2, vf2, tr2, wk2 = simplifySection(poly2, vf2, tr2, wk2, [e is None for e in e2],
                                                               simp)
                        polys[jm].append(((pi_, tr2, len(info[jm])), poly2))
                        info[jm].append((wk2, vf2, poly2))
        return polys, info

    def meridian(t, G=None):
        # the meridian half plane at the angle t of the worm, turned onto y = 0, x > 0; section
        # coordinates (r, z). returns the outer outline from the bottom end at the bore to the top
        # end at the bore, its segment classes, the parasitic counts and the wheel's middle plane
        if G is None:
            pp, ii = gather([t])
            G = (pp[0], ii[0])
        polys, info = G
        zc = zc_[0]
        Rt = np.array(rotZ(-t))
        if not polys:
            raise LapError("the source never reaches the worm: move the gears closer")
        if custom:
            lp = targetSection(t)
            rin = min(q[0] for q in lp)
        else:
            lp = [(bore, zlo), (r_tip, zlo), (r_tip, zhi), (bore, zhi)]
            rin = bore
        at = [('T', CLS_PLAIN)] * len(lp)
        z_in = [q[1] for q in lp if abs(q[0] - rin) < 1e-6 * size]
        zi0, zi1 = min(z_in), max(z_in)
        c = 0
        while c < len(polys):
            c1, nv = c, 0
            while c1 < len(polys) and (c1 == c or (nv + len(polys[c1][1]) <= 2500 and c1 - c < NPOLY)):
                nv += len(polys[c1][1])
                c1 += 1
            lp, at = subtract2d(lp, at, polys[c:c1], 0.0)
            c = c1
            if not lp:
                raise LapError("the imprint removed the whole worm section (wrong direction or placement?)")
            lp, at = dropCollinear(lp, at, 1e-7 * size)
        _corner_cache.clear()
        cos_lim = math.cos(math.radians(limit_deg))
        N = len(lp)
        cls = []
        why = [0, 0, 0, 0]
        for i in range(N):
            a = at[i]
            if a[0] != 'S':
                cls.append(a[1])
                continue
            (pi, tris, pid), seg = a[1], a[2]
            wk, corner, poly = info[pid]
            p0, p1 = lp[i], lp[(i + 1) % N]
            k, M = posl[pi]
            M = Rt @ M
            par = 0
            if not wk[seg]:
                par = 1
            elif cornerCut(p0, p1, poly, corner, seg, CORNER_NEAR * mx):
                par = 2
            else:
                q = Vector((0.5 * (p0[0] + p1[0]), 0.0, 0.5 * (p0[1] + p1[1])))
                nrm = Vector(M[:3, :3] @ N_s[tris[seg] if seg < len(tris) else tris[0]])
                ax = Vector(M[:3, :3] @ np.array((0.0, 0.0, 1.0)))
                ts = ax.cross(q - Vector(M[:3, 3]))
                if nrm.length < 1e-30 or ts.length < 1e-30:
                    par = 3
                else:
                    nrm.normalize()
                    # the worm passes torque as a screw: its pressure angle is taken in the axial section
                    if min(abs(nrm.z), transverseCos(nrm, ts, ax)) < cos_lim:
                        par = 3
            why[par] += 1
            cls.append(CLS_PARASITIC if par else 1 + min(BANDS - 1, int(BANDS * k / float(n))))
        # the outer outline from the bottom end at the bore to the top end at the bore
        tol = 1e-6 * size
        ib = next((i for i in range(N) if abs(lp[i][0] - rin) < tol and abs(lp[i][1] - zi0) < tol), None)
        it = next((i for i in range(N) if abs(lp[i][0] - rin) < tol and abs(lp[i][1] - zi1) < tol), None)
        if ib is None or it is None:
            raise LapError("the wheel cut into the bore or the corners of the worm section")
        idx = [(ib + q) % N for q in range(((it - ib) % N) + 1)]
        chain = [lp[i] for i in idx]
        ccls = [cls[i] for i in idx[:-1]]
        return chain, ccls, why, zc

    chain, ccls, why, zc = meridian(0.0)
    # a screw (cylindrical worm) has on every meridian the same outline, shifted by the lead; a wheel
    # of another pitch or a globoid pair does not: then every meridian is cut on its own
    p = 2 * math.pi / zt
    lead = zt * px
    C0 = np.array(chain)
    ch1 = chain if custom else meridian(p / 4)[0]
    P1 = np.array(ch1)
    dev = 0.0
    win = np.abs(C0[:, 1] - zc) < px
    r_root = float(C0[win, 0].min()) if win.any() else bore
    if len(P1) > 1:
        for sg in (1.0, -1.0):
            Q = P1 - np.array((0.0, sg * px / 4))
            # about the wheel's middle plane, where its teeth cut the whole thread (towards the ends
            # the throat of a worm wheel trims the tips differently on every meridian)
            # the root left out too: the tips of a worm wheel sweep a globoid there, which the floor
            # below the flanks replaces anyway
            sel = (Q[:, 0] > r_root + 0.3 * mx) & (np.abs(Q[:, 1] - zc) < 0.75 * px)
            d = curveDeviation(Q[sel], C0) if sel.any() else float('inf')
            dev = d if sg > 0 else min(dev, d)
    # a worm cut back by its own wheel stays within a few hundredths of a module (facets, steps);
    # a wheel of a foreign pitch or shape leaves it by a large part of the module
    if not custom and slow == 1 and slow_t == 1 and dev <= 0.25 * mx:
        prof, pcls = wormProfile(chain, ccls, zc, px, r_tip, bore, mx, clearance, report)
        report.append("imprint '%s' -> worm '%s' (meridian section, %d positions of the wheel over one turn "
                      "of the worm): %d cut segments, %d parasitic (%d by non working faces, %d by edges of the "
                      "source, %d by the normal); profile of one axial pitch: %d points"
                      % (src.name, tgt.name, n, sum(why), why[1] + why[2] + why[3], why[1], why[2], why[3],
                         len(prof)))
        me_new = wormSweep("LAP_new", zt, mx, prof, pcls, zlo, zhi, bore)
        setWormProfile(tgt, prof, pcls)
        tgt["lap_globoid"] = 0
        tgt["lap_slow"] = [1, 1]
    else:
        # meridians meridian_step apart at most (2 deg)
        step = float(getattr(getattr(context.scene, "lap", None), "meridian_step", 2.0))
        nm = max(int(math.ceil(360.0 / zt / step)), 24 * slow_t)
        if custom:
            report.append("own target body: every one of %d meridians per element cut on its own" % nm)
        elif (slow, slow_t) != (1, 1):
            report.append("worm: slowed pair, every one of %d meridians per start cut on its own" % nm)
        else:
            report.append("worm: the meridian outlines are no screw (a quarter start apart they differ by %.3g "
                          "after the shift by the lead): globoid, every one of %d meridians per start cut on "
                          "its own" % (dev, nm))
        chains = []
        tol = 0.005 * mx
        # a slowed target repeats slow_t times per element (its sectors are the same): only the
        # meridians of one repeat are cut, the others are their copies (not for an own body that is
        # not the same under that turn)
        nrep = int(slow_t)
        if nrep > 1 and custom:
            for tq in (0.1, 0.37, 0.71):
                A_ = np.array(targetSection(-p / 2 + p * tq))
                B_ = np.array(targetSection(-p / 2 + p * tq + p / nrep))
                if len(A_) < 2 or len(B_) < 2 or max(curveDeviation(A_, np.vstack([B_, B_[:1]])),
                                                     curveDeviation(B_, np.vstack([A_, A_[:1]]))) > 1e-6 * size:
                    nrep = 1
                    break
        if nrep > 1:
            nm = nrep * int(math.ceil(nm / float(nrep)))
            report.append("the target repeats %d times per element: %d of %d meridians cut, the others copied"
                          % (nrep, nm // nrep, nm))
        nms = nm // nrep
        tl = [-p / 2 + p * jm / nm for jm in range(nms)]
        GP, GI = gather(tl)
        for jm in range(nms):
            t = tl[jm]
            ch, cc, w_, _ = meridian(t, (GP[jm], GI[jm]))
            for q in range(4):
                why[q] += w_[q]
            out, oc = [ch[0]], []
            i = 0
            while i < len(cc):
                j = i
                while j + 1 < len(cc) and (working(cc[j + 1]) == working(cc[i])
                                           and (cc[j + 1] == CLS_PARASITIC) == (cc[i] == CLS_PARASITIC)):
                    j += 1
                run = ch[i:j + 2]
                keep = douglasPeucker(run, tol)
                for q0, q1 in zip(keep[:-1], keep[1:]):
                    out.append(run[q1])
                    best = max(range(q0, q1), key=lambda q: math.dist(run[q], run[q + 1]))
                    oc.append(cc[i + best])
                i = j + 1
            chains.append((t, out, oc))
        if nrep > 1:
            chains = [(t + r * p / nrep, o_, c_) for r in range(nrep) for t, o_, c_ in chains]
        # the last meridian is the first one of the next start: the same outline, so the elements
        # meet exactly
        chains.append((p / 2, chains[0][1], chains[0][2]))
        me_new = globoidLoft("LAP_new", zt, chains)
        for k in ("lap_profile", "lap_profile_cls"):
            if k in tgt:
                del tgt[k]
        tgt["lap_globoid"] = 1
        tgt["lap_slow"] = [int(slow), int(slow_t)]
        report.append("imprint '%s' -> %s '%s' (%d positions of the source over %s of the target "
                      "on each meridian): %d cut segments, %d parasitic; up to %d points per meridian, "
                      "triangles"
                      % (src.name, "globoid worm" if tgt.get("lap_worm") else "own body", tgt.name, n,
                         "one turn" if ncyc == 1 else "%d turns" % ncyc, sum(why),
                         why[1] + why[2] + why[3],
                         max(len(c[1]) for c in chains)))
    ob, vol = meshCheck(me_new)
    bm = bmesh.new()
    bm.from_mesh(me_new)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(me_new)
    attachMaterials(me_t)
    me_t.update()
    report.append("target element: %d faces, volume %.6g, open edges %d" % (len(me_t.polygons), vol, ob))
    if ob:
        report.append("WARNING: the element is not closed")
    report.append("done in %.1f s" % (time.time() - t0))
    tgt["lap_source"] = src.name
    tgt["lap_sign"] = int(sign)
    tgt["lap_steps"] = int(steps)
    return sign



# ---------------------------------------------------------------------------
# rotation to translation: a rack and a cylindrical gear on parallel directions (rack z = gear
# axis). a rack tool cuts a gear in the section method above (the rack moves by the rolling radius
# per radian); a gear tool cuts a rack here: one section of the rack element (one pitch, its sides
# in the middle of the spaces), cut by all positions of the gear rolling over it, then extruded
# along the width, shifted along the rack by the helix of the tool
# ---------------------------------------------------------------------------

def elWorld(el):
    # the world matrix of an element from its parent (matrix_world may not be updated yet)
    return el.parent.matrix_world @ el.matrix_parent_inverse @ el.matrix_basis


def rackBlankProfile(m):
    pl = math.pi * m
    return [(-pl / 2, m), (pl / 2, m)]


def rackOutlineMesh(name, lp, cls, levels, shifts):
    # the outline (x, y) extruded through the levels (z), every level shifted along x; quads along
    # the width, the outline as the end caps
    if area2(lp) < 0:
        lp = lp[::-1]
        cls = cls[::-1][1:] + cls[::-1][:1]
    bm = bmesh.new()
    rows = [[bm.verts.new((x + sh, y, z)) for x, y in lp] for z, sh in zip(levels, shifts)]
    n = len(lp)
    for k in range(len(levels) - 1):
        A, B = rows[k], rows[k + 1]
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((A[i], A[j], B[j], B[i]))
            f.material_index = cls[i]
    for row in (rows[0], rows[-1]):
        f = bm.faces.new(row)
        f.material_index = CLS_PLAIN
    return finishMesh(bm, name)


def rackBlank(context, src, n, report):
    # smooth rack blank under a cylindrical tool: pitch line on the pitch circle of the tool,
    # n pitches of the tool's transverse pitch, the width of the tool
    checkRotary(src, "a rack blank")
    if src.get("lap_kind") != 'SPUR' or src.get("lap_internal") or src.get("lap_worm") or src.get("lap_face"):
        raise LapError("a rack blank needs an external cylindrical gear as the tool")
    zs = int(src["lap_teeth"])
    m = float(src["lap_module"])
    me_s = gearMesh(src)
    vz = [v.co.z for v in me_s.vertices]
    w = max(vz) - min(vz)
    rp = zs * m / 2
    mat = gearFrame(src) @ Matrix.Translation((0.0, -rp, 0.5 * (max(vz) + min(vz))))
    r = rackGear(context, n, m, w, 2.0 * m, 0.0, False, mat, blank=True)
    report.append("rack blank '%s': %d pitches of %.4g under '%s' (pitch line on its pitch circle)"
                  % (r.name, n, math.pi * m, src.name))
    return r


def gearBlankOverRack(context, src, z, report):
    # smooth gear blank over a rack tool: its pitch circle on the pitch line, axis = rack z
    if not isRack(src):
        raise LapError("the tool is not a rack")
    m = float(src["lap_module"])
    rp = z * m / 2
    w = float(src["lap_width"])
    mat = gearFrame(src) @ Matrix.Translation((0.0, rp, 0.0))
    g = spurGear(context, z, m, w, False, False, defaultBore(z, m), mat)
    report.append("gear blank '%s': %d teeth over the rack '%s' (pitch circle on its pitch line)"
                  % (g.name, z, src.name))
    return g


def imprintRackTarget(context, src, tgt, steps, sub, sign_mode, limit_deg, report, clearance=0.25):
    t0 = time.time()
    if src.get("lap_kind") != 'SPUR' or src.get("lap_internal") or src.get("lap_worm") or src.get("lap_face"):
        raise LapError("a rack is cut by an external cylindrical gear")
    zs = int(src["lap_teeth"])
    m = float(tgt["lap_module"])
    pl = math.pi * m
    v = zs * pl / (2 * math.pi)                   # rack travel per radian of the tool
    els = elements(tgt)
    el0 = els[0]
    me_s, me_t = gearMesh(src), gearMesh(tgt)
    if me_s == me_t:
        raise LapError("source and target share the element mesh")
    E = elWorld(el0)
    Ei = E.inverted()
    fs = gearFrame(src)
    dirx = gearFrame(tgt).to_3x3() @ Vector((1.0, 0.0, 0.0))
    rel0 = Ei @ fs
    ez = (rel0.to_3x3() @ Vector((0, 0, 1))).z
    if abs(abs(ez) - 1.0) > 1e-7:
        raise LapError("the gear axis must run across the rack (along its z)")
    vt = [p.co.z for p in me_t.vertices]
    vs = [p.co.z for p in me_s.vertices]
    zt0, zt1, zs0, zs1 = min(vt), max(vt), min(vs), max(vs)
    mid_t = 0.5 * (zt0 + zt1) + 1e-7 * (zt1 - zt0)
    e0 = rel0.to_translation().z
    herring = bool(src.get("lap_herring", False))
    if herring:
        mid_t += 1e-3 * (zt1 - zt0)
    mid_s = (mid_t - e0) / ez
    if not zs0 < mid_s < zs1:
        raise LapError("the gear does not reach the middle of the rack width")
    if herring and abs((0.5 * (zt0 + zt1) - e0) / ez) > 1e-5 * (zs1 - zs0):
        raise LapError("a herringbone tool must have its apex in the middle plane of the rack")
    pts_t, cls_t = sectionLoop(me_t, False, mid_t)
    pts_s, cls_s = sectionLoop(me_s, False, mid_s)
    P_s = np.array([tuple(q) for q in pts_s])
    own = P_s[:, :2]
    keep = collinearKeep([tuple(q) for q in own], 1e-9 * float(np.ptp(own, axis=0).max()))
    P_s = P_s[keep]
    own = [tuple(own[i]) for i in keep]
    role_s = [cls_s[i] for i in keep]
    any_work = any(working(c) for c in role_s)
    wk_s, corner_s = sourceRoles(own, role_s, RAMP_CREASE_DEG, any_work)
    loop = [(q[0], q[1]) for q in pts_t]
    attrs = [('T', c) for c in cls_t]
    loop, attrs = dropCollinear(loop, attrs, 1e-9 * float(np.ptp(np.array(loop), axis=0).max()))
    if area2(loop) < 0:
        loop = loop[::-1]
        attrs = attrs[::-1][1:] + attrs[::-1][:1]
    lo, hi = np.array(loop).min(axis=0), np.array(loop).max(axis=0)
    size = float(np.linalg.norm(hi - lo))
    glo, ghi = lo - 0.01 * size, hi + 0.01 * size
    R_s = max(q.co.xy.length for q in me_s.vertices)
    xc0 = (Ei @ fs.to_translation()).x
    L = R_s + pl
    dstep = 2 * math.pi / zs / (steps * sub)

    def positions(sign):
        # the tool rolls along the rack: turned by a it moves by -sign v a (in the rack frame)
        a0, a1 = (xc0 - L) / (sign * v), (xc0 + L) / (sign * v)
        if a0 > a1:
            a0, a1 = a1, a0
        n = int(math.ceil((a1 - a0) / dstep)) + 1
        out, info, frames = [], [], {}
        for k in range(n):
            a = a0 + k * dstep
            base = Ei @ Matrix.Translation(-dirx * (sign * v * a)) @ fs @ rotZ(a) @ fs.inverted() @ src.matrix_world
            frames[k] = mat4np(base)
            for j in range(zs):
                M = mat4np(base @ rotZ(2 * math.pi * j / zs))
                Q = P_s @ M[:3, :3].T + M[:3, 3]
                Q = Q[:, :2]
                if (Q.max(axis=0) < glo).any() or (Q.min(axis=0) > ghi).any():
                    continue
                poly, vf, ew = clipBoxAttr(list(map(tuple, Q.tolist())), corner_s, wk_s, glo, ghi)
                if poly:
                    out.append((len(info), poly))
                    info.append((k, [bool(w) for w in ew], vf, poly))
        return out, frames, info, n

    def run(sign):
        pos, frames, info, n = positions(sign)
        lp, at = list(loop), list(attrs)
        for c in range(0, len(pos), CHUNK):
            lp, at = subtract2d(lp, at, pos[c:c + CHUNK], 0.0)
            if not lp:
                break
            lp, at = dropCollinear(lp, at, 1e-7 * size)
        return lp, at, pos, frames, info, n

    if sign_mode == 'AUTO':
        res, keepres = {}, {}
        for sg in (1.0, -1.0):
            r_ = run(sg)
            res[sg] = abs(area2(r_[0])) if r_[0] else 0.0
            keepres[sg] = r_
        sign = 1.0 if res[1.0] >= res[-1.0] else -1.0
        a0_ = abs(area2(loop))
        report.append("direction test: section keeps %.0f%% with +1, %.0f%% with -1 -> %+d"
                      % (100 * res[1.0] / a0_, 100 * res[-1.0] / a0_, int(sign)))
        lp, at, pos, frames, info, n = keepres[sign]
    else:
        sign = 1.0 if sign_mode == 'PLUS' else -1.0
        lp, at, pos, frames, info, n = run(sign)
    if not lp:
        raise LapError("the imprint removed the whole rack element (wrong direction or placement?)")
    report.append("imprint '%s' -> rack '%s' (section method, rolling): %d teeth, rack travel %.4g per turn, %d steps "
                  "of 1/%d tooth, %d tool positions near the element"
                  % (src.name, tgt.name, zs, 2 * math.pi * v, n, steps * sub, len(pos)))
    cut = [i for i, a in enumerate(at) if a[0] == 'S']
    if not cut:
        report.append("WARNING: the tool did not reach the rack")
    cos_lim = math.cos(math.radians(limit_deg))
    N = len(lp)
    par = {}
    n_edge = n_corner = 0
    for i in cut:
        k, ew, vf, poly = info[at[i][1]]
        sg = at[i][2]
        p0, p1 = lp[i], lp[(i + 1) % N]
        if not ew[sg]:
            par[i] = True
            n_edge += 1
            continue
        if cornerCut(p0, p1, poly, vf, sg, CORNER_NEAR * m):
            par[i] = True
            n_corner += 1
            continue
        F = frames[k]
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        nrm = Vector((d.y, -d.x, 0.0))
        if nrm.length < 1e-30:
            par[i] = True
            continue
        nrm.normalize()
        u = Vector((0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.0))
        w = u - Vector((F[0, 3], F[1, 3], 0.0))
        ts = Vector((-w.y, w.x, 0.0))
        axs = Vector(F[:3, :3] @ np.array((0.0, 0.0, 1.0)))
        ct = transverseCos(nrm, Vector((1.0, 0.0, 0.0)), Vector((0.0, 0.0, 1.0)))
        cs = transverseCos(nrm, ts, axs)
        par[i] = min(ct, cs) < cos_lim
    ks = sorted(set(info[at[i][1]][0] // sub for i in cut if not par[i]))
    kmin, kmax = (min(ks), max(ks)) if ks else (0, 0)
    cls = []
    for i in range(N):
        a = at[i]
        if a[0] != 'S':
            cls.append(a[1])
        elif par[i]:
            cls.append(CLS_PARASITIC)
        else:
            b = int(BANDS * (info[a[1]][0] // sub - kmin) / float(kmax - kmin + 1))
            cls.append(1 + min(BANDS - 1, max(0, b)))
    report.append("cut edges: %d, parasitic %d (%d cut by non working faces, %d by corners of the tool)"
                  % (len(cut), sum(1 for c in cls if c == CLS_PARASITIC), n_edge, n_corner))
    cls = majorityRuns(lp, cls, FLICKER * m)
    lp, cls = simplifyRuns(lp, cls, SIMPLIFY * m)
    lp, cls = mergeShort(lp, cls, 1e-5 * m)
    # root clearance: the tip of the tool reaches only its addendum; the cut below the lowest
    # working point (the path of the tool tip: the root and its fillet) goes down by c m
    ywk = [lp[i][1] for i in range(len(lp)) if working(cls[i]) or working(cls[i - 1])]
    nlow = 0
    if ywk and clearance > 0:
        yw = min(ywk)
        ybody = min(q[1] for q in loop)
        cut_pt = [cls[i] == CLS_PARASITIC or cls[i - 1] == CLS_PARASITIC for i in range(len(lp))]
        out = []
        for i, (x, y) in enumerate(lp):
            if cut_pt[i] and y < yw - 1e-9 * m and not (working(cls[i]) or working(cls[i - 1])):
                y = max(y - clearance * m, ybody + 0.1 * m)
                nlow += 1
            out.append((x, y))
        lp = out
    # along the width: the tool turned by d cuts the section shifted by sign v d
    tau_s = math.tan(math.radians(float(src.get("lap_helix", 0.0)))) / (zs * float(src["lap_module"]) / 2)
    shape = twistShape(herring)
    if abs(tau_s) > 1e-12:
        mid0 = 0.5 * (zt0 + zt1) if herring else mid_t
        levels = [zt0, 0.5 * (zt0 + zt1), zt1] if herring else [zt0, zt1]
        k_ = RACK_CUT * sign * v * tau_s / ez
        shifts = [k_ * (shape(zk - mid0) - shape(mid_t - mid0)) for zk in levels]
        helix_t = math.degrees(math.atan(k_))
    else:
        levels, shifts, helix_t = [zt0, zt1], [0.0, 0.0], 0.0
    me_new = rackOutlineMesh("LAP_new", lp, cls, levels, shifts)
    ob, vol = meshCheck(me_new)
    bm = bmesh.new()
    bm.from_mesh(me_new)
    bm.to_mesh(me_t)
    bm.free()
    bpy.data.meshes.remove(me_new)
    attachMaterials(me_t)
    me_t.update()
    tgt["lap_helix"] = helix_t
    tgt["lap_herring"] = herring and abs(helix_t) > 1e-9
    tgt["lap_source"] = src.name
    tgt["lap_sign"] = int(sign)
    tgt["lap_steps"] = int(steps)
    report.append("outline: %d points, root clearance %.3g (%d points lowered); helix %.4g deg%s"
                  % (len(lp), clearance * m, nlow, helix_t, ", herringbone" if tgt["lap_herring"] else ""))
    report.append("target element: %d faces, volume %.6g, open edges %d" % (len(me_t.polygons), vol, ob))
    if ob:
        report.append("WARNING: the element is not closed")
    report.append("done in %.1f s" % (time.time() - t0))
    return sign


def imprintRack(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, report, simple, clearance):
    if isRack(src) and isRack(tgt):
        raise LapError("two racks do not roll on each other")
    if tgt.get("lap_custom") or tgt.get("lap_worm") or src.get("lap_worm") or src.get("lap_custom"):
        raise LapError("rack lapping works with cylindrical gears only")
    checkVersion(src)
    checkVersion(tgt)
    if isRack(tgt):
        return imprintRackTarget(context, src, tgt, steps, sub, sign_mode, limit_deg, report, clearance)
    if tgt.get("lap_kind") != 'SPUR' or tgt.get("lap_internal") or tgt.get("lap_face"):
        raise LapError("a rack cuts an external cylindrical gear")
    rel = gearFrame(tgt).inverted() @ gearFrame(src)
    if abs(abs((rel.to_3x3() @ Vector((0, 0, 1))).z) - 1.0) > 1e-7:
        raise LapError("the rack must run across the gear axis (its z along the axis)")
    if gearMesh(src) == gearMesh(tgt):
        raise LapError("source and target share the element mesh")
    helical = abs(float(src.get("lap_helix", 0.0))) > 1e-9 or abs(float(tgt.get("lap_helix", 0.0))) > 1e-9
    if src.get("lap_herring") and not helical:
        pass
    return imprint2d(context, src, tgt, 'HELICAL' if helical else 'SPUR', steps, sub, sign_mode, limit_deg, relief,
                     report, simple, clearance)



def _imprint(context, src, tgt, steps, sub, sign_mode, smooth, limit_deg, relief, report, slices=16,
            family='AUTO', remesh=False, simple=True, clearance=0.25, extend=0.5, deform=None, slow=(1, 1)):
    # slow = (wheel, worm): both turned that many times slower than their teeth say; only their
    # quotient counts (4 and 3: the wheel turns 3/4 as fast relative to the worm)
    ks, kt = int(slow[0]), int(slow[1])
    g = math.gcd(ks, kt)
    ks, kt = ks // g, kt // g
    if isRack(src) or isRack(tgt):
        if (ks, kt) != (1, 1):
            raise LapError("with a rack the ratio is fixed by the pitches (no slowdown)")
        return imprintRack(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, report, simple, clearance)
    if (ks, kt) != (1, 1):
        zs_, zt_ = int(src["lap_teeth"]), int(tgt["lap_teeth"])
        # the target comes out the same after a turn by 2 pi / o (o = zt kt / gcd(ks, zt)). every
        # element of the target must be the same, so o must be a multiple of zt: gcd(ks, zt) = 1.
        # otherwise the target really gets o teeth: a worm is rebuilt with o starts (its elements
        # are made new anyway), the same kinematics then read: wheel slowed ks / g, worm not slowed
        g = math.gcd(ks, zt_)
        o = zt_ * kt // g
        Rphys = Fraction(zt_ * kt, zs_ * ks)          # tool turns per blank turn
        if g > 1 and not tgt.get("lap_worm"):
            raise LapError("with this ratio the blank gets %d teeth, not %d (its teeth would differ): make the "
                           "blank with %d teeth" % (o, zt_, o))
        if tgt.get("lap_worm") and o != zt_:
            report.append("the thread repeats %d times per turn: worm '%s' rebuilt from %d to %d starts "
                          "(elements); the ratio is kept as %d : %d turns"
                          % (o, tgt.name, zt_, o, Rphys.numerator, Rphys.denominator))
            setStarts(tgt, o)
            ps_ = getattr(context.scene, "lap", None)
            if ps_ is not None:
                ps_.ratio_auto = False
                ps_.ratio_tool, ps_.ratio_blank = Rphys.numerator, Rphys.denominator
                ps_.blank_slow = 1
            zt_, ks, kt = o, ks // g, 1
        _SLOW.clear()
        _SLOW[src.name] = ks
        _SLOW[tgt.name] = kt
        a_, b_ = zs_ * ks, zt_ * kt
        g_ = math.gcd(a_, b_)
        report.append("ratio: the tool turns %d : %d per turn of the blank (not as the teeth say); one cycle = "
                      "%d turn(s) of the blank" % (b_ // g_, a_ // g_, ks // math.gcd(ks, zt_)))
        try:
            return imprint(context, src, tgt, steps, sub, sign_mode, smooth, limit_deg, relief, report, slices,
                           family, remesh, simple, clearance, extend, deform)
        finally:
            _SLOW.clear()
    checkRotary(src)
    checkRotary(tgt)
    checkVersion(src)
    checkVersion(tgt)
    if gearMesh(src) == gearMesh(tgt):
        raise LapError("source and target share the element mesh")
    mode = pairMode(src, tgt)
    if (src.get("lap_herring") or tgt.get("lap_herring")) and mode not in ('HELICAL', 'BEVEL'):
        raise LapError("herringbone gears are made only on parallel axes (section method)")
    if abs(float(src.get("lap_spiral", 0.0))) > 1e-9 and mode != 'BEVEL':
        raise LapError("a spiral bevel source only for a bevel target with the same apex (section method)")
    if mode is not None:
        return imprint2d(context, src, tgt, mode, steps, sub, sign_mode, limit_deg, relief, report, simple,
                         clearance)
    if tgt.get("lap_custom"):
        return imprintWorm(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, report, clearance, extend)
    if methodOf(src, tgt) == 'SLICES' and tgt.get("lap_worm") and not src.get("lap_worm"):
        return imprintWorm(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, report, clearance, extend)
    if methodOf(src, tgt) == 'SLICES':
        return imprintSlices(context, src, tgt, steps, sub, sign_mode, limit_deg, relief, slices, smooth, report,
                             family, remesh, simple, clearance, extend, deform)
    report.append("boolean method (the target is not a gear of this add-on)")
    return imprint3d(context, src, tgt, steps, sign_mode, smooth, report)


# ---------------------------------------------------------------------------
# print offset (bakeOffset, made when the gear is created) and printable copy (the pieces joined only):
# the outline moved into the material in the layer plane. a 3d printer lays about a line's worth of material too much on every wall (the
# slicer's "horizontal expansion"); the copy is made that much smaller so the printed part comes
# out at the nominal size. the gear is assumed to lie on an end face (its axis = the print z):
# every point moves only across the axis, so that each wall - flank, tip, root, bore, mantle -
# moves by the offset along its horizontal normal, and the end faces stay where they are
# ---------------------------------------------------------------------------

def writeStlBinary(path, tris, header=b"gear_lapping"):
    # tris: (n, 3, 3) float array, counter clockwise seen from outside
    import struct
    T = np.asarray(tris, dtype=np.float64)
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ln = np.linalg.norm(N, axis=1)
    N = N / np.where(ln > 0, ln, 1.0)[:, None]
    rec = np.zeros(len(T), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"] = N
    rec["v"] = T
    with open(path, "wb") as f:
        f.write(header[:80].ljust(80, b" "))
        f.write(struct.pack("<I", len(T)))
        f.write(rec.tobytes())


def imprint(*args, **kw):
    # the lapping works on closed sectors: the pieces are open at their sides, the sides are put back for the
    # time of the operation (engineMode) and taken out of the result again
    with engineMode():
        return _imprint(*args, **kw)


def closedParts(bm, m):
    # a mesh cut into closed parts: split where more than two faces meet an edge (walls of parts
    # joined by hand), then the connected pieces, each with its holes closed. [bmesh]
    multi = [e for e in bm.edges if len(e.link_faces) > 2]
    if multi:
        bmesh.ops.split_edges(bm, edges=multi)
    bm.verts.ensure_lookup_table()
    comp = {}
    seen = set()
    parts = []
    for f0 in bm.faces:
        if f0 in seen:
            continue
        stack, faces = [f0], []
        seen.add(f0)
        while stack:
            f = stack.pop()
            faces.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        stack.append(g)
        nb = bmesh.new()
        vm = {}
        for f in faces:
            vs = []
            for v in f.verts:
                if v not in vm:
                    vm[v] = nb.verts.new(v.co)
                vs.append(vm[v])
            try:
                nb.faces.new(vs).material_index = f.material_index
            except ValueError:
                pass
        bmesh.ops.remove_doubles(nb, verts=list(nb.verts), dist=1e-6 * m)
        bnd = [e for e in nb.edges if e.is_boundary]
        if bnd:
            bmesh.ops.holes_fill(nb, edges=bnd, sides=0)
        bmesh.ops.recalc_face_normals(nb, faces=list(nb.faces))
        vol = nb.calc_volume(signed=True)
        if vol < 0:
            bmesh.ops.reverse_faces(nb, faces=list(nb.faces))
        if abs(vol) < 1e-6 * m ** 3 or any(e.is_boundary for e in nb.edges):
            # a sheet (the leftover of a wall between parts) or a piece that stays open: no solid
            nb.free()
            continue
        # a hair (2e-4 m) thicker: neighbouring parts overlap instead of touching across a gap of
        # rounding errors, so that the union merges them
        nb.normal_update()
        for v in nb.verts:
            v.co += v.normal * (2e-4 * m)
        parts.append(nb)
    return parts


def joinedSolid(gear, report):
    # all element objects of the gear (whatever they hold: the linked sector meshes, or a mesh the
    # user joined by hand) in the gear's frame, united into one solid by the boolean modifier
    # (manifold solver): the walls where two parts meet vanish, and where their outlines differ a
    # little (a step at a sector side) the union is still exact. normals out. [bmesh]
    m = sizeModule(gear)
    inv = gear.matrix_world.inverted()
    pieces = []
    for el in gear.children:
        if el.type != 'MESH':
            continue
        if el.get("lap_seat") and "lap_seat_z0" in gear:
            pieces += closedParts(seatSolidBM(gear, True), m)
            continue
        bm = bmesh.new()
        bm.from_mesh(el.data)
        bm.transform(inv @ el.matrix_world)
        pieces += closedParts(bm, m)
        bm.free()
    if not pieces:
        raise LapError("the gear has no mesh parts")
    coll = bpy.data.collections.new("LAP_export_tmp")
    bpy.context.scene.collection.children.link(coll)
    objs = []
    try:
        for i, nb in enumerate(pieces):
            me = bpy.data.meshes.new("LAP_part_%d" % i)
            nb.to_mesh(me)
            nb.free()
            ob = bpy.data.objects.new(me.name, me)
            coll.objects.link(ob)
            objs.append(ob)
        base = objs[0]
        if len(objs) > 1:
            others = bpy.data.collections.new("LAP_export_ops")
            coll.children.link(others)
            for ob in objs[1:]:
                coll.objects.unlink(ob)
                others.objects.link(ob)
            mod = base.modifiers.new("union", 'BOOLEAN')
            mod.operation = 'UNION'
            mod.operand_type = 'COLLECTION'
            mod.collection = others
            mod.solver = 'MANIFOLD'
            others.hide_viewport = False
        dg = bpy.context.evaluated_depsgraph_get()
        ev = base.evaluated_get(dg)
        bm = bmesh.new()
        bm.from_mesh(ev.to_mesh())
        ev.to_mesh_clear()
    finally:
        for ob in objs:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            if me.users == 0:
                bpy.data.meshes.remove(me)
        for c in list(coll.children):
            bpy.data.collections.remove(c)
        bpy.data.collections.remove(coll)
    # triangles, points on the same spot joined (the union may keep twins along its seams); then the
    # slivers it may leave where parts meet (edges of 1e-5 m, faces of no area, more than two faces at
    # an edge) collapsed there only, the clean rest stays as it is
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6 * m)
    for _ in range(4):
        bad = [e for e in bm.edges if len(e.link_faces) != 2]
        if not bad:
            break
        vs = {v for e in bad for v in e.verts}
        near = {e2 for v in vs for e2 in v.link_edges}
        bmesh.ops.dissolve_degenerate(bm, dist=1e-4 * m, edges=list(near))
        vs = [v for v in bm.verts if v.is_valid and any(len(e.link_faces) != 2 for e in v.link_edges)]
        if vs:
            bmesh.ops.remove_doubles(bm, verts=vs, dist=1e-4 * m)
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        res = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
        report.append("export: %d open edges closed by %d faces" % (len(bnd), len(res["faces"])))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    # loose bits of no volume (a pair of triangles on one spot) go: pieces far smaller than the rest
    seen = set()
    comps = []
    for f0 in bm.faces:
        if f0 in seen:
            continue
        stack, faces = [f0], []
        seen.add(f0)
        while stack:
            f = stack.pop()
            faces.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        stack.append(g)
        comps.append(faces)
    if len(comps) > 1:
        big = max(len(c) for c in comps)
        drop = [f for c in comps if len(c) < 0.001 * big and
                sum(f.calc_area() for f in c) < 1e-6 * m * m for f in c]
        if drop:
            bmesh.ops.delete(bm, geom=drop, context='FACES')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    report.append("export: %d closed parts united (manifold boolean)" % len(pieces))
    return bm


COLLAPSE_ROUNDS = 4          # rounds of collapsing the short edges of faces the offset turned over
COLLAPSE_LEN = 2.5           # such an edge is shorter than this many offsets


def repairSolid(bm, m, rounds=4):
    # the few defects the union can leave where neighbouring parts meet: edges of more than two
    # faces (a fin) and small holes, all within a hair. around each defect the points closer than
    # 2e-3 m are welded, degenerate faces dissolved, zero area faces removed, holes of up to 8
    # edges closed; repeated while it helps. returns the number of defects found at first
    def defects():
        return [e for e in bm.edges if len(e.link_faces) != 2]
    bad = defects()
    n0 = len(bad)
    for _ in range(rounds):
        if not bad:
            break
        vs = list({v for e in bad for v in e.verts} | {w for e in bad for v in e.verts for f in v.link_faces
                                                        for w in f.verts})
        bmesh.ops.remove_doubles(bm, verts=vs, dist=2e-3 * m)
        vs = [v for v in vs if v.is_valid]
        eds = list({e for v in vs for e in v.link_edges})
        if eds:
            bmesh.ops.dissolve_degenerate(bm, dist=1e-4 * m, edges=eds)
        fz = [f for f in {f for v in vs if v.is_valid for f in v.link_faces} if f.calc_area() < (1e-4 * m) ** 2]
        if fz:
            bmesh.ops.delete(bm, geom=fz, context='FACES_ONLY')
        loose = [e for e in bm.edges if not e.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='EDGES')
        lv = [v for v in bm.verts if not v.link_edges]
        if lv:
            bmesh.ops.delete(bm, geom=lv, context='VERTS')
        # a fin: two faces on the same points (or facing each other) on an edge of more than two
        fin = set()
        for e in bm.edges:
            if len(e.link_faces) > 2:
                fs = list(e.link_faces)
                for i in range(len(fs)):
                    for j in range(i + 1, len(fs)):
                        if set(fs[i].verts) == set(fs[j].verts) or fs[i].normal.dot(fs[j].normal) < -0.999:
                            fin.update((fs[i], fs[j]))
        if fin:
            bmesh.ops.delete(bm, geom=list(fin), context='FACES_ONLY')
        bnd = [e for e in bm.edges if e.is_boundary]
        if bnd:
            res = bmesh.ops.holes_fill(bm, edges=bnd, sides=8)
            tri = [f for f in res.get("faces", []) if len(f.verts) > 3]
            if tri:
                bmesh.ops.triangulate(bm, faces=tri)
        bad = defects()
    ng = [f for f in bm.faces if len(f.verts) > 3]
    if ng:
        bmesh.ops.triangulate(bm, faces=ng)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return n0


DEBUG_CHAMFER = False
CHAMFER_STATS = {'done': 0, 'left': 0}   # the rims chamfered / left without, since the last reset (for the panel)
CHAMFER_FLAT = 0.9           # a loop of the rim of an end plane is chamfered if the faces beyond it lean enough from
                             # the plane (|normal z| below this): a cone nearly as flat as the plane has no foot


def endPlanes(bm, ends='BOTH', tol=None):
    # the faces of the two end planes of the solid, the axis being z: flat, facing out along the axis, every point in
    # the lowest (LOW) or the highest (HIGH) plane (within tol: the seams of a union leave a plane a hair uneven).
    # returns {'LOW': set, 'HIGH': set}, the z of both
    bm.normal_update()
    zs = [v.co.z for v in bm.verts]
    out = {'LOW': set(), 'HIGH': set()}
    if not zs:
        return out, 0.0, 0.0
    lo, hi = min(zs), max(zs)
    if tol is None:
        tol = 1e-4 * max(hi - lo, 1e-9) + 1e-7
    for f in bm.faces:
        nz = f.normal.z
        if ends in ('BOTH', 'LOW') and nz < -0.9995 and all(v.co.z < lo + tol for v in f.verts):
            out['LOW'].add(f)
        elif ends in ('BOTH', 'HIGH') and nz > 0.9995 and all(v.co.z > hi - tol for v in f.verts):
            out['HIGH'].add(f)
    return out, lo, hi


def bedRing(planes, others=()):
    # the edges of the rim of the flat faces: those with a face of another kind beyond them (a face that is nearly
    # in the plane too, a sliver of the union, is none)
    skip = set(planes) | set(others)
    ring = []
    for f in planes:
        for e in f.edges:
            if len(e.link_faces) != 2:
                continue
            g = e.link_faces[0] if e.link_faces[1] is f else e.link_faces[1]
            if g in skip or abs(g.normal.z) > 0.9995:
                continue
            ring.append(e)
    return list(set(ring))


def loopLean(loop, planes):
    # how flat the faces beyond a loop of the rim lie, |normal z| on average (1: in the plane, 0: a wall)
    tot = 0.0
    for e in loop:
        g = e.link_faces[0] if e.link_faces[0] not in planes else e.link_faces[1]
        tot += abs(g.normal.z)
    return tot / max(len(loop), 1)


def selfHits(bm, limit=20000, slab=None, inside=False):
    # the triangles that cut each other without sharing a point, as a set of pairs named by the places of their
    # centres (so the hits of a mesh can be compared before and after a change of a part of it).
    # slab [(z0, z1), ...]: only the triangles that reach into one of these ranges of heights are looked at (the chamfer
    # changes nothing outside of them, and the big meshes of many teeth take their time); inside: only those that lie
    # wholly in a range (after the cut at the height of the chamfer nothing above it has moved)
    # (the points and the triangles come out of a mesh made of the bmesh, in one go: the loops over the bmesh in python
    # took longer than the search)
    me = bpy.data.meshes.new("LAP_hits")
    try:
        bm.to_mesh(me)
        V = np.empty(len(me.vertices) * 3, dtype=np.float32)
        me.vertices.foreach_get("co", V)
        V = V.reshape(-1, 3).astype(np.float64)
        me.calc_loop_triangles()
        P = np.empty(len(me.loop_triangles) * 3, dtype=np.int32)
        me.loop_triangles.foreach_get("vertices", P)
        P = P.reshape(-1, 3).astype(np.int64)
    finally:
        bpy.data.meshes.remove(me)
    if not len(P):
        return set()
    if slab is not None:
        z = V[P][:, :, 2]
        lo_, hi_ = z.min(axis=1), z.max(axis=1)
        keep = np.zeros(len(P), dtype=bool)
        for z0, z1 in slab:
            keep |= ((lo_ >= z0) & (hi_ <= z1)) if inside else ((hi_ >= z0) & (lo_ <= z1))
        P = P[keep]
        if not len(P):
            return set()
    tree = BVHTree.FromPolygons(V.tolist(), P.tolist(), epsilon=0.0)
    # the pairs that touch in a point or an edge (neighbours) are left out in one go
    pr = np.array(tree.overlap(tree), dtype=np.int64).reshape(-1, 2)
    pr = pr[pr[:, 0] < pr[:, 1]]
    if len(pr):
        A_, B_ = P[pr[:, 0]], P[pr[:, 1]]
        pr = pr[~(A_[:, :, None] == B_[:, None, :]).any(axis=(1, 2))]
    keys = set()
    if not len(pr):
        return keys
    cen = np.rint(V[P].sum(axis=1) * 3e5).astype(np.int64)
    for i, j in pr.tolist():
        ki, kj = tuple(cen[i].tolist()), tuple(cen[j].tolist())
        keys.add((ki, kj) if ki <= kj else (kj, ki))
        if len(keys) >= limit:
            break
    return keys


def hitPlace(pair):
    # where a pair of cutting triangles is (the middle of their centres; the keys are 3e5 times the sum of three points)
    return Vector([(a + b) / (2.0 * 3e5 * 3.0) for a, b in zip(pair[0], pair[1])])


def hitTree(hits):
    # the places of the hits of a mesh in a tree (None: no hits)
    if not hits:
        return None
    tree = mathutils.kdtree.KDTree(len(hits))
    for i, p in enumerate(hits):
        tree.insert(hitPlace(p), i)
    tree.balance()
    return tree


def newHitCount(h1, hits0, tree0, radius):
    # the triangles cutting each other that were not there before and are not near one that was (a mesh may have a few
    # already, the thin tooth tips of a bevel gear; the chamfer moves some and the cut splits some in two)
    fresh = h1 - hits0
    if tree0 is None:
        return len(fresh)
    return sum(1 for p in fresh if not tree0.find_range(hitPlace(p), radius))


def ringLoops(ring):
    # the rim edges in connected loops
    par = {}

    def find(v):
        while par.setdefault(v, v) is not v:
            par[v] = par[par[v]]
            v = par[v]
        return v
    for e in ring:
        a, b = find(e.verts[0]), find(e.verts[1])
        if a is not b:
            par[a] = b
    groups = {}
    for e in ring:
        groups.setdefault(find(e.verts[0]), []).append(e)
    return list(groups.values())


def outlineTree(edges):
    # the segments of an outline (the xy of its edges) with a tree of their middles, for the distance of a place to it
    es = [ed for ed in edges if ed.is_valid]
    segA = np.array([(ed.verts[0].co.x, ed.verts[0].co.y) for ed in es]).reshape(-1, 2)
    segB = np.array([(ed.verts[1].co.x, ed.verts[1].co.y) for ed in es]).reshape(-1, 2)
    n = len(segA)
    tree = mathutils.kdtree.KDTree(max(n, 1))
    for i in range(n):
        tree.insert(Vector((0.5 * (segA[i][0] + segB[i][0]), 0.5 * (segA[i][1] + segB[i][1]), 0.0)), i)
    tree.balance()
    lmax = float(np.hypot(*(segB - segA).T).max()) if n else 0.0
    return segA, segB, tree, lmax


def outlineDist(ot, q, reach):
    # the distance of the place q (x, y) to the outline when it is below reach, else a number above it
    segA, segB, tree, lmax = ot
    cand = [i for _, i, _ in tree.find_range(Vector((float(q[0]), float(q[1]), 0.0)), reach + 0.5 * lmax)]
    if not cand:
        return reach + 1.0
    A_, B_ = segA[cand], segB[cand]
    ab = B_ - A_
    t = np.clip(((np.asarray(q) - A_) * ab).sum(axis=1) / np.maximum((ab * ab).sum(axis=1), 1e-30), 0.0, 1.0)
    dd = np.hypot(*(A_ + ab * t[:, None] - np.asarray(q)).T)
    return float(dd.min())


def nearInner(bm, loop, plane, ring_all, e):
    # the points inside the flat faces (on no rim) nearer to the outline of this loop than e: after the chamfer they
    # would lie outside the moved outline (the seams of a union leave such points a hair from the outline). they are
    # dissolved: the flat faces round such a point become one flat face, nothing of the shape is lost.
    # returns the number of points dissolved
    rimv = {v for ed in ring_all if ed.is_valid for v in ed.verts}
    inner = {v for f in plane if f.is_valid for v in f.verts} - rimv
    if not inner:
        return 0
    ot = outlineTree(loop)
    near = [v for v in inner if outlineDist(ot, (v.co.x, v.co.y), 1.05 * e) < 1.05 * e]
    if not near:
        return 0
    bmesh.ops.dissolve_verts(bm, verts=near, use_face_split=False, use_boundary_tear=False)
    return len(near)


def insideEvenOdd(P, A, B):
    # which of the points P (n, 2) lie inside the outline made of the edges A -> B (m, 2) (every loop of it, the holes
    # too): the crossing number of a ray to +x is odd
    out = np.zeros(len(P), dtype=bool)
    ay, by = A[:, 1][None, :], B[:, 1][None, :]
    dx = (B[:, 0] - A[:, 0])[None, :]
    with np.errstate(divide='ignore', invalid='ignore'):
        slope = dx / (by - ay)
    for s0 in range(0, len(P), 256):
        p = P[s0:s0 + 256]
        x, y = p[:, 0:1], p[:, 1:2]
        cond = (ay > y) != (by > y)
        xi = A[:, 0][None, :] + (y - ay) * slope
        out[s0:s0 + 256] = (np.sum(cond & (x < xi), axis=1) % 2) == 1
    return out


def weldClose(bm, verts, dist, flat=False):
    # points that lie within dist of each other become one point (the one with the lowest place in the list stays);
    # flat: only the distance across the axis counts (points of one plane that differ by a hair in height).
    # the clusters are found here: blender 4.5 remove_doubles leaves part of the pairs in one pass, even points on
    # one spot (a pass of dist 1e-6 left a third of 1096 pairs, a second one with 2e-6 the rest)
    vs = [v for v in verts if v.is_valid]
    if len(vs) < 2:
        return 0

    def at(v):
        return (v.co.x, v.co.y, 0.0) if flat else v.co
    kd = mathutils.kdtree.KDTree(len(vs))
    for i, v in enumerate(vs):
        kd.insert(at(v), i)
    kd.balance()
    parent = list(range(len(vs)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, v in enumerate(vs):
        for _co, j, _d in kd.find_range(at(v), dist):
            if j != i:
                a, b = find(i), find(j)
                if a != b:
                    parent[max(a, b)] = min(a, b)
    tm = {}
    for i, v in enumerate(vs):
        r = find(i)
        if r != i:
            tm[v] = vs[r]
    if tm:
        bmesh.ops.weld_verts(bm, targetmap=tm)
    return len(tm)


def refillPlane(bm, z_end, tol, sgn, welded=False):
    # the flat faces of an end plane made anew from their outline: with the rim moved, an old triangle (a long one that
    # runs close along the outline) can lie across the moved outline. the points of the outline (the outer loop and
    # the holes) are triangulated again by a constrained delaunay triangulation, the triangles inside the outline
    # kept; the faces point out of the solid as the old ones did (sgn: the side of the band, the plane faces the
    # other way). returns True when done, False when the outline cannot be filled (nothing is changed then)
    # the faces of the plane are found by their places (the ones the merging of points made new are not the old ones,
    # a triangle turned over by the move is still one)
    faces = [f for f in bm.faces if all(abs(v.co.z - z_end) <= tol for v in f.verts)]
    if not faces:
        if DEBUG_CHAMFER:
            print("   refill: no plane faces left")
        return False
    fs = set(faces)
    bnd = list({ed for f in faces for ed in f.edges if sum(1 for g in ed.link_faces if g in fs) == 1})
    if len(bnd) < 3:
        if DEBUG_CHAMFER:
            print("   refill: outline of %d edges" % len(bnd))
        return False
    verts = list({v for ed in bnd for v in ed.verts})
    idx = {v: i for i, v in enumerate(verts)}
    pts = [Vector((v.co.x, v.co.y)) for v in verts]
    cons = [(idx[ed.verts[0]], idx[ed.verts[1]]) for ed in bnd]
    ext = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts))
    if not welded and weldClose(bm, verts, 4e-9 * ext, True):
        # points of the outline on one spot (they differ by a hair in height: the seam of a union) are one point
        # for the triangulation, and so for the solid
        bm.normal_update()
        return refillPlane(bm, z_end, tol, sgn, True)
    ov, oe, of, overts, oedges, ofaces = mgeom.delaunay_2d_cdt(pts, cons, [], 0, 1e-9 * ext, True)
    # every point of the result is a point of the outline (a new one would be a crossing of the outline with itself)
    vm = {}
    for k, orig in enumerate(overts):
        if len(orig) != 1:
            if DEBUG_CHAMFER:
                print("   refill: point %d of the triangulation comes from %d points of the outline" % (k, len(orig)))
            return False
        vm[k] = verts[orig[0]]
    A = np.array([(ed.verts[0].co.x, ed.verts[0].co.y) for ed in bnd])
    B = np.array([(ed.verts[1].co.x, ed.verts[1].co.y) for ed in bnd])
    tri = np.array([t for t in of if len(t) == 3], dtype=np.int64).reshape(-1, 3)
    V = np.array([(p[0], p[1]) for p in ov])
    inside = insideEvenOdd(V[tri].mean(axis=1), A, B)
    keep = tri[inside]
    if not len(keep):
        if DEBUG_CHAMFER:
            print("   refill: no triangle inside the outline (%d triangles)" % len(tri))
        return False
    mat = faces[0].material_index
    bmesh.ops.delete(bm, geom=faces, context='FACES')
    for t in keep:
        a, b, c = (int(k) for k in t)
        pa, pb, pc = V[a], V[b], V[c]
        cross = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
        if abs(cross) < 1e-18:
            continue
        # the normal of a counter clockwise triangle points to +z
        order = (a, b, c) if cross * (-sgn) > 0 else (a, c, b)
        try:
            f = bm.faces.new([vm[k] for k in order])
        except ValueError:
            continue
        f.material_index = mat
    return True


def chamferLoop(bm, loop, ring_all, skip, z_end, sgn, e, tol=None, refill=False):
    # one loop of the rim of an end plane chamfered by e: the walls next to it are cut at the height e, and the points
    # below the cut move across the axis into the material by e (1 - s) with s = height / e (the wall tilts 45 deg).
    # the move of a rim point comes from the walls it lies on (in a corner: the corner of the moved walls). a point
    # whose moved place lies nearer than e to the outline (the tip of a thin tooth, the end of a short edge) is not
    # on the moved outline: it goes to the nearest point that is (the chamfers of the two flanks meet there).
    # returns the rim points moved, or None
    # the plane of the loop itself (the coordinates are single floats: the planes of two loops can differ by a bit)
    z_end = sum(v.co.z for ed in loop for v in ed.verts) / (2.0 * len(loop))
    # the slack of the heights: the cut ring is single floats too, a few units of the last place off the cut plane
    eps = 1e-6 * e + 3e-7 * max(abs(z_end) + e, 1.0)
    seen, stack = set(), []
    for ed in loop:
        for g in ed.link_faces:
            if g not in skip and g not in seen:
                seen.add(g)
                stack.append(g)
    while stack:
        f = stack.pop()
        for ed in f.edges:
            for g in ed.link_faces:
                if g in seen or g in skip:
                    continue
                if min(sgn * (v.co.z - z_end) for v in g.verts) < e - eps:
                    seen.add(g)
                    stack.append(g)
    z_cut = z_end + sgn * e
    geom = list(seen) + list({ed for f in seen for ed in f.edges}) + list({v for f in seen for v in f.verts})
    bmesh.ops.bisect_plane(bm, geom=geom, dist=eps, plane_co=(0.0, 0.0, z_cut), plane_no=(0.0, 0.0, 1.0),
                           use_snap_center=False, clear_outer=False, clear_inner=False)
    bm.normal_update()
    ring_v = {v for ed in loop if ed.is_valid for v in ed.verts}
    # the band again after the cut: the faces from the rim up to the cut ring
    band, stack = set(), []
    for v in ring_v:
        for g in v.link_faces:
            if g not in skip and g not in band and \
                    max(sgn * (w.co.z - z_end) for w in g.verts) <= e + eps:
                band.add(g)
                stack.append(g)
    while stack:
        f = stack.pop()
        for ed in f.edges:
            for g in ed.link_faces:
                if g in band or g in skip:
                    continue
                if max(sgn * (w.co.z - z_end) for w in g.verts) <= e + eps:
                    band.add(g)
                    stack.append(g)
    sval = {}
    for f in band:
        for v in f.verts:
            sval[v] = max(0.0, sgn * (v.co.z - z_end) / e)
    # the move of every point of the band from its walls
    raw = {}
    for v, s_ in sval.items():
        if s_ >= 1.0 - 1e-6:
            continue
        A = np.zeros((2, 2))
        b = np.zeros(2)
        for f in v.link_faces:
            if f in skip:
                continue
            n = f.normal
            sx = math.hypot(n.x, n.y)
            if sx < 0.05:
                continue
            nx = np.array((n.x, n.y))
            w = f.calc_area() * sx
            A += w * np.outer(nx, nx)
            b += w * (-e * sx) * nx
        tr = A[0, 0] + A[1, 1]
        d = np.zeros(2) if tr <= 0 else np.linalg.solve(A + 1e-6 * tr * np.eye(2), b)
        ln = float(np.hypot(d[0], d[1]))
        if ln > 4 * e:
            d *= 4 * e / ln
        raw[v] = d
    rim = [v for v in {w for ed in loop if ed.is_valid for w in ed.verts} if v in raw]
    if len({v for ed in loop if ed.is_valid for v in ed.verts} - set(rim)):
        # a point of the loop that no wall of the band reaches: not a clean rim, left as it is
        if DEBUG_CHAMFER:
            print("   loop has points outside the band: left out")
        return None
    if DEBUG_CHAMFER:
        ss = sorted(sval[v] for v in raw)
        print("   z_end %.9g, s of the moved points %.3g .. %.3g, loop z %.9g .. %.9g" % (
            z_end, ss[0] if ss else -1, ss[-1] if ss else -1,
            min(v.co.z for ed in loop for v in ed.verts), max(v.co.z for ed in loop for v in ed.verts)))
    # the outline all the loops of this plane make, for the distance of a moved place to it
    ot = outlineTree(ring_all)
    # the order of the rim points along the loop(s)
    nxt = {}
    for ed in loop:
        a, b_ = ed.verts
        nxt.setdefault(a, []).append(b_)
        nxt.setdefault(b_, []).append(a)
    pos = {v: np.array((v.co.x + raw[v][0], v.co.y + raw[v][1])) for v in rim}

    def dist_ok(v):
        return outlineDist(ot, pos[v], e + 0.5 * ot[3]) >= 0.985 * e
    good = {v: dist_ok(v) for v in rim}
    # edges that turned round: both ends not on the moved outline
    for _ in range(6):
        changed = False
        for ed in loop:
            a, b_ = ed.verts
            if a not in pos or b_ not in pos:
                continue
            t = np.array((b_.co.x - a.co.x, b_.co.y - a.co.y))
            if float(np.dot(pos[b_] - pos[a], t)) < -1e-9 * e:
                if good[a] or good[b_]:
                    good[a] = good[b_] = False
                    changed = True
        if not changed:
            break
    n_bad = sum(1 for v in rim if not good[v])
    if DEBUG_CHAMFER:
        print("   loop: %d rim points, %d off the moved outline, band %d faces, %d points moved, e %.3g" % (
            len(rim), n_bad, len(band), len(raw), e))
    if n_bad == len(rim):
        return None
    if n_bad:
        # walk the loop: a point that is not on the moved outline takes the place of the nearest one that is
        order = []
        done = set()
        for v0 in rim:
            if v0 in done:
                continue
            ch = [v0]
            done.add(v0)
            prev, cur = None, v0
            while True:
                nb = [w for w in nxt.get(cur, []) if w is not prev and w not in done]
                if not nb:
                    break
                prev, cur = cur, nb[0]
                ch.append(cur)
                done.add(cur)
            order.append(ch)
        for ch in order:
            n = len(ch)
            if DEBUG_CHAMFER:
                miss = [v for v in ch if v not in good]
                if miss:
                    print("   !! chain of %d with %d points outside the rim set: s %s, in raw %s, z-z_end %s, nfaces %s" % (
                        n, len(miss), [round(sval.get(v, -1), 4) for v in miss[:5]], [v in raw for v in miss[:5]],
                        [round(v.co.z - z_end, 6) for v in miss[:5]], [len(v.link_faces) for v in miss[:5]]))
                    for v in miss[:3]:
                        print("      point", tuple(round(c, 5) for c in v.co))
                        for f in v.link_faces:
                            print("         face skip %s band %s seen %s nz %.4f nverts %d zrel %s" % (
                                f in skip, f in band, f in seen, f.normal.z, len(f.verts),
                                [round(sgn * (w.co.z - z_end), 5) for w in f.verts][:8]))
            if not any(good[v] for v in ch):
                continue
            # the nearest good point of each (cyclic distance along the chain, which is closed when its ends meet):
            # two passes round the chain, one each way
            near_f, near_b = [None] * n, [None] * n
            last = None
            for k in range(2 * n):
                if good[ch[k % n]]:
                    last = k
                if k >= n and last is not None:
                    near_f[k - n] = (k - last, last % n)
            last = None
            for k in range(2 * n - 1, -1, -1):
                if good[ch[k % n]]:
                    last = k
                if k < n and last is not None:
                    near_b[k] = (last - k, last % n)
            for i, v in enumerate(ch):
                if good[v]:
                    continue
                cand = [c for c in (near_f[i], near_b[i]) if c is not None]
                pos[v] = pos[ch[min(cand)[1]]]
    move = {v: (pos[v] - np.array((v.co.x, v.co.y))) if v in pos else None for v in raw}
    # the points above the rim: the move of the point below, less by the height
    byS = sorted((v for v in raw if v not in pos), key=lambda w: sval[w])
    mv = {v: move[v] for v in rim}
    sv = {v: 0.0 for v in rim}
    for v in byS:
        best, bs = None, -1.0
        for ed in v.link_edges:
            u = ed.other_vert(v)
            if u in mv and sv[u] < sval[v] - 1e-9:
                dz = abs(u.co.z - v.co.z) / max(ed.calc_length(), 1e-12)
                if dz > bs:
                    best, bs = u, dz
        if best is not None:
            mv[v] = mv[best] / max(1.0 - sv[best], 1e-9) * (1.0 - sval[v])
        else:
            mv[v] = raw[v] * (1.0 - sval[v])
        sv[v] = sval[v]
    for v, d in mv.items():
        if v in pos:
            v.co.x, v.co.y = float(pos[v][0]), float(pos[v][1])
        else:
            v.co.x += float(d[0])
            v.co.y += float(d[1])
    # rim points that now lie on one spot are one point
    moved = [v for v in rim if v.is_valid]
    if n_bad:
        weldClose(bm, moved, max(1e-7 * e, 1e-6))
    bm.normal_update()
    if refill and tol:
        if not refillPlane(bm, z_end, tol, sgn):
            return None
        bm.normal_update()
    q = 1e-6
    keys = {(round(v.co.x / q), round(v.co.y / q), round(v.co.z / q)) for v in moved if v.is_valid}
    return len(rim), n_bad, keys


def bmRestore(bm, snap):
    # the content of the bmesh bm replaced by that of its copy snap (which is freed); every reference into bm is void
    me = bpy.data.meshes.new("LAP_chamfer_keep")
    snap.to_mesh(me)
    snap.free()
    bm.clear()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)


def triangulateEnds(bm, ends, tol_z):
    # the flat faces of the end planes that are still n-gons (made where points a hair inside the outline were
    # dissolved) into triangles. blender's own triangulation can leave an edge of four faces on such a face (the points
    # of a union seam lie a hair apart, a diagonal then lies on an edge that is there already): it is checked, and then
    # the plane is filled anew by the constrained delaunay triangulation of its outline, checked as well. nothing is
    # kept that is worse than before. returns a note for the report ('' when all went well)
    pl, lo, hi = endPlanes(bm, ends, tol_z)
    ng = [f for side in pl for f in pl[side] if len(f.verts) > 3]
    if not ng:
        return ""

    def broken():
        return sum(1 for e in bm.edges if not e.is_manifold)
    n0 = broken()
    v0 = bm.calc_volume(signed=True)
    snap = bm.copy()
    bmesh.ops.triangulate(bm, faces=ng, quad_method='BEAUTY', ngon_method='BEAUTY')
    if broken() <= n0:
        snap.free()
        return ""
    bmRestore(bm, snap)
    snap = bm.copy()
    ok = True
    for side, sgn in (('LOW', 1.0), ('HIGH', -1.0)):
        pl, lo, hi = endPlanes(bm, ends, tol_z)
        if any(len(f.verts) > 3 for f in pl[side]):
            if not refillPlane(bm, lo if side == 'LOW' else hi, tol_z, sgn):
                ok = False
                break
            bm.normal_update()
    if ok and broken() <= n0 and abs(bm.calc_volume(signed=True) - v0) <= 1e-6 * abs(v0) + 1e-9:
        snap.free()
        return ""
    bmRestore(bm, snap)
    return "an end face is left with n-gons (they cannot be triangulated cleanly)"


def chamferBed(bm, c, report, name="", ends='BOTH', hair=0.0):
    # a chamfer c on every rim of the two end planes of the solid (a part can lie either way): the first layers that
    # the bed squashes wider ("elephant foot") then stay inside the nominal outline, and the bore keeps its size.
    # all of: the outline of the teeth, the bore, the hole of a shaft seat, hubs; for a bevel gear the back plane.
    # every loop of a rim on its own, checked afterwards: closed as before, no triangle cutting another; else a
    # smaller chamfer for that loop, at last none (the solid stays whole). returns the number of loops chamfered
    if c <= 0:
        return 0
    zs_ = [v.co.z for v in bm.verts]
    # an end plane may be uneven by a hair (the seams of a union, "hair" = 2e-4 of the module, the parts being grown
    # by it): by up to 3 hairs, or 2 % of the chamfer, at most a third of the chamfer
    tol_z = max(1e-4 * (max(zs_) - min(zs_)) + 1e-7, 0.02 * c, 3.0 * hair) if zs_ else 1e-7
    tol_z = min(tol_z, c / 3.0)
    planes, lo, hi = endPlanes(bm, ends, tol_z)
    if not (planes['LOW'] or planes['HIGH']):
        return 0
    open0 = sum(1 for e in bm.edges if not e.is_manifold)
    # (only where the chamfer works: a range of 2 chamfers at each end plane that is to be done)
    hits0 = selfHits(bm, slab=[(lo - 0.5 * c, lo + 1.5 * c) for _ in (0,) if planes['LOW']] +
                     [(hi - 1.5 * c, hi + 0.5 * c) for _ in (0,) if planes['HIGH']])
    height = hi - lo
    q = 1e-6

    tree0 = hitTree(hits0)

    def newHits(h1):
        return newHitCount(h1, hits0, tree0, 2.5 * c)

    def key(v):
        return (round(v.co.x / q), round(v.co.y / q), round(v.co.z / q))

    def ringOf(side):
        pl, lo_, hi_ = endPlanes(bm, ends, tol_z)
        other = pl['HIGH' if side == 'LOW' else 'LOW']
        return pl[side], other, bedRing(pl[side], other), (lo_ if side == 'LOW' else hi_)

    notes = []
    n_done = 0
    done = set()
    for side, sgn in (('LOW', 1.0), ('HIGH', -1.0)):
        if not planes[side]:
            continue
        for _ in range(500):
            pl, other, ring, z_end = ringOf(side)
            loops = [lp for lp in ringLoops(ring) if key(lp[0].verts[0]) not in done]
            if not loops:
                break
            lp = max(loops, key=len)
            orig = {key(v) for ed in lp for v in ed.verts}
            n_edges = len(lp)
            got = None
            if n_edges < 3:
                # a scrap of a rim (a sliver of the union): no outline to move
                done |= orig
                continue
            if loopLean(lp, set(pl) | set(other)) > CHAMFER_FLAT:
                # the face beyond leans only a little from the plane (a cone, a sphere nearly flat): no foot to cut
                done |= orig
                continue
            # the sizes from c down; at each first with the old triangles of the plane, then with the plane filled anew
            for cc, refill in [(x, rf) for x in (c, 0.7 * c, 0.5 * c, 0.35 * c, 0.25 * c) for rf in (False, True)]:
                if cc > 0.4 * height:
                    continue
                snap = bm.copy()
                try:
                    if nearInner(bm, lp, pl, ring, cc):
                        # points a hair inside the outline were dissolved: the faces of the plane are new
                        pl, other, ring, z_end = ringOf(side)
                        again = [l_ for l_ in ringLoops(ring) if key(l_[0].verts[0]) in orig]
                        lp = again[0] if again else None
                    r = chamferLoop(bm, lp, ring, set(pl) | set(other), z_end, sgn, cc, tol_z, refill) \
                        if lp is not None else None
                except (ValueError, ReferenceError, RuntimeError, LookupError, ArithmeticError) as ex:
                    r = None
                    if DEBUG_CHAMFER:
                        import traceback
                        traceback.print_exc()
                ok = r is not None
                if ok:
                    o1 = sum(1 for e in bm.edges if not e.is_manifold)
                    v1 = bm.calc_volume(signed=True)
                    # triangles cutting each other: none that are new
                    # (the move happens between the end plane and the cut ring, nothing above it changes)
                    slab = [(z_end - 0.5 * cc, z_end + 1.1 * cc) if sgn > 0 else (z_end - 1.1 * cc, z_end + 0.5 * cc)]
                    h1 = selfHits(bm, slab=slab, inside=True) if (o1 <= open0 and v1 > 0) else None
                    nnew = newHits(h1) if h1 is not None else -1
                    ok = h1 is not None and nnew == 0
                    if DEBUG_CHAMFER:
                        print("   check: open %d (was %d), volume %.4g, hits %s (were %d), new %d" % (
                            o1, open0, v1, "-" if h1 is None else len(h1), len(hits0), nnew))
                if DEBUG_CHAMFER:
                    print("chamferBed %s loop of %d edges, try %.3g%s: %s" % (
                        side, n_edges, cc, " refilled" if refill else "", ("ok %s" % (r[:2],)) if ok else "no"))
                if ok:
                    snap.free()
                    got = (cc, r, refill)
                    break
                bmRestore(bm, snap)
                pl, other, ring, z_end = ringOf(side)
                again = [l_ for l_ in ringLoops(ring) if key(l_[0].verts[0]) in orig]
                if not again:
                    break
                lp = again[0]
            done |= orig
            if got is not None:
                n_done += 1
                done |= got[1][2]
                notes.append("%s loop of %d edges: %.3g%s%s" % (
                    side.lower(), n_edges, got[0], (", %d points of thin tips merged" % got[1][1]) if got[1][1] else "",
                    ", end face triangulated anew" if got[2] else ""))
            else:
                CHAMFER_STATS['left'] += 1
                notes.append("%s loop of %d edges: left out" % (side.lower(), n_edges))
    CHAMFER_STATS['done'] += n_done
    if notes:
        report.append("chamfer %.3g of '%s': %s" % (c, name, "; ".join(notes)))
    # the flat faces that were joined where points a hair inside the outline were dissolved: triangles again
    note = triangulateEnds(bm, ends, tol_z)
    if note:
        report.append("note: " + note)
    bm.normal_update()
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    return n_done


def exportGearStl(context, gear, path, offset, report, chamfer=0.0, ends='BOTH'):
    # the gear as one solid for a slicer, in the gear's own frame (axis = z). with the print offset
    # the printable copy is made first (it needs the gear's own linked sector elements)
    # a sprocket or pulley always goes the printable copy way (its sectors weld cleanly there), also at offset 0
    els0 = elements(gear)
    # the pieces are open at their sides: a gear with its own linked elements is always joined by the printable copy
    use_pc = (not isRack(gear) and not gear.get("lap_part") and len(els0) == int(gear["lap_teeth"])
              and len({e.data.name for e in els0}) == 1) or bool(offset)
    if use_pc:
        els = elements(gear)
        if len(els) != int(gear["lap_teeth"]) or len({e.data.name for e in els}) != 1:
            raise LapError("the print offset needs the gear's own linked elements (not joined by hand): "
                           "export without it")
        ob = printCopy(context, gear, offset, report, chamfer, ends)
        tmp = bpy.data.objects.new("LAP_tmp", None)
        context.collection.objects.link(tmp)
        tmp.matrix_world = ob.matrix_world.copy()
        ob.parent = tmp
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = Matrix.Identity(4)
        tmp["lap_teeth"] = 1
        tmp["lap_module"] = sizeModule(gear)
        bm = joinedSolid(tmp, report)
        me = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.objects.remove(tmp, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    else:
        bm = joinedSolid(gear, report)
    nfix = repairSolid(bm, sizeModule(gear))
    if nfix:
        report.append("export: %d defect(s) of the union repaired" % nfix)
    if not use_pc:
        chamferBed(bm, chamfer, report, gear.name, ends, 2e-4 * sizeModule(gear))
        overhangCheck(bm, report, gear.name, chamfer)
    ng = [f for f in bm.faces if len(f.verts) > 3]
    if ng:
        # the chamfer leaves quads (and a flat face joined from several): an stl has triangles
        bmesh.ops.triangulate(bm, faces=ng, quad_method='BEAUTY', ngon_method='BEAUTY')
    open_e = sum(1 for e in bm.edges if e.is_boundary)
    multi = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    tris = np.array([[tuple(v.co) for v in f.verts] for f in bm.faces])
    vol = bm.calc_volume(signed=True)
    bm.free()
    writeStlBinary(path, tris)
    report.append("stl '%s': %d triangles, volume %.6g, open edges %d, edges of more than two faces %d"
                  % (path, len(tris), vol, open_e, multi))
    if open_e or multi:
        report.append("WARNING: the solid is not clean (open or shared edges): check it in the slicer")
    return len(tris)


def anyPrintCopy(context, g, offset, report, chamfer=0.0, ends='BOTH'):
    # a gear: its printable copy with the offset; a rack (or another part that does not turn): the
    # joined solid, without the offset
    if isGear(g) and not isRack(g) and not g.get("lap_part"):
        return printCopy(context, g, offset, report, chamfer, ends)
    bm = joinedSolid(g, report)
    repairSolid(bm, sizeModule(g))
    chamferBed(bm, chamfer, report, g.name, ends, 2e-4 * sizeModule(g))
    if offset > 0:
        report.append("note: '%s' does not turn (a rack, a part): no print offset, copied as it is" % g.name)
    mesh = bpy.data.meshes.new(g.name + "_print")
    bm.to_mesh(mesh)
    bm.free()
    attachMaterials(mesh)
    ob = bpy.data.objects.new(g.name + "_print", mesh)
    (g.users_collection[0] if g.users_collection else context.collection).objects.link(ob)
    ob.matrix_world = gearFrame(g)
    report.append("printable copy '%s' (joined solid, %d faces)" % (ob.name, len(mesh.polygons)))
    return ob


def offsetDisplacement(bm, offset, gear):
    # the move across the axis of every point of the joined solid for the print offset: per point d with
    # d . n_f = -offset |n_f,xy| for its faces (least squares, weighted by area and slope): walls move by
    # offset, corners to the corner of the moved walls, points on the end faces slide with their walls.
    # returns D (n, 2), ok (which points move), big (how many were held to 4 offsets), n_old (face normals)
    bm.verts.index_update()
    A = np.zeros((len(bm.verts), 2, 2))
    b = np.zeros((len(bm.verts), 2))
    n_old = {}
    for f in bm.faces:
        n = f.normal
        nxy = np.array((n.x, n.y))
        s_xy = float(np.linalg.norm(nxy))
        n_old[f.index] = n.copy()
        if s_xy < 1e-6:
            continue
        w = f.calc_area() * s_xy
        for v in f.verts:
            A[v.index] += w * np.outer(nxy, nxy)
            b[v.index] += w * (-offset * s_xy) * nxy
    tr = A[:, 0, 0] + A[:, 1, 1]
    reg = 1e-6 * tr[:, None, None] * np.eye(2)[None] + 1e-300 * np.eye(2)[None]
    ok = tr > 0
    D = np.zeros((len(bm.verts), 2))
    D[ok] = np.linalg.solve(A[ok] + reg[ok], b[ok][..., None])[..., 0]
    # a point between walls meeting at a very sharp angle would move far: at most 4 offsets
    ln = np.linalg.norm(D, axis=1)
    big = ln > 4 * abs(offset)
    D[big] *= (4 * abs(offset) / ln[big])[:, None]
    if isBevel(gear):
        # the rim ends of a bevel gear are spheres about the apex, triangulated with points
        # inside: those points follow the outline of the teeth smoothly (harmonic mean of their
        # neighbours) instead of their own sloping faces, so no triangle of the ends turns over
        radii = (float(gear["lap_lin"]), float(gear["lap_lout"]))

        def onCap(f):
            return any(all(abs(v.co.length - r_) < 1e-6 * r_ for v in f.verts) for r_ in radii)
        capf = set(f.index for f in bm.faces if onCap(f))
        inner = [v for v in bm.verts if v.link_faces and all(f.index in capf for f in v.link_faces)]
        if inner:
            nb = {v.index: [e.other_vert(v).index for e in v.link_edges] for v in inner}
            idx = [v.index for v in inner]
            for _ in range(200):
                Dn = D.copy()
                for i in idx:
                    Dn[i] = D[nb[i]].mean(axis=0)
                D = Dn
            ok[idx] = True
    return D, ok, big, n_old


def detectSides(me, z, m):
    # the polygons of a closed element mesh that are sector sides (they lie inside the gear once the elements
    # are joined). plain faces in one half plane through the axis whose partner is one pitch further (or,
    # for a single element, the slot); twisted sectors (helical, herringbone): a side is a face whose copy
    # turned by one pitch is a face of the element too. only for freshly made meshes
    V = np.array([tuple(v.co) for v in me.vertices])
    PH = np.arctan2(V[:, 1], V[:, 0])
    cand = {}
    for p_ in me.polygons:
        ph = PH[list(p_.vertices)]
        if p_.material_index == CLS_PLAIN and np.ptp(np.unwrap(ph)) < 1e-6:
            cand[p_.index] = float(np.unwrap(ph).mean())
    pitch = 2 * math.pi / z
    angs = np.array(list(cand.values())) if cand else np.zeros(0)
    ptol = 1e-5

    def isSide(a):
        if z == 1:
            return abs(abs((a + math.pi) % (2 * math.pi) - math.pi) - math.pi) < 2 * SLOT
        d = (angs - a) % (2 * math.pi)
        return bool((np.abs(d - pitch) < ptol).any() or (np.abs(d - (2 * math.pi - pitch)) < ptol).any())
    twins = set()
    if z > 1:
        tol = 1e-5 * max(m, 1e-9)
        key = {}
        polys = list(me.polygons)
        for p_ in polys:
            if len(p_.vertices) < 3:
                continue
            c_ = V[list(p_.vertices)].mean(axis=0)
            key.setdefault((round(c_[0] / tol / 50), round(c_[1] / tol / 50), round(c_[2] / tol / 50)), []).append(p_)
        for sg in (1.0, -1.0):
            cs, sn = math.cos(sg * pitch), math.sin(sg * pitch)
            for p_ in polys:
                P = V[list(p_.vertices)]
                R = np.stack([cs * P[:, 0] - sn * P[:, 1], sn * P[:, 0] + cs * P[:, 1], P[:, 2]], axis=1)
                c_ = R.mean(axis=0)
                k0 = (round(c_[0] / tol / 50), round(c_[1] / tol / 50), round(c_[2] / tol / 50))
                for dk in [(i, j, l) for i in (-1, 0, 1) for j in (-1, 0, 1) for l in (-1, 0, 1)]:
                    for q_ in key.get((k0[0] + dk[0], k0[1] + dk[1], k0[2] + dk[2]), ()):
                        if q_.index == p_.index or len(q_.vertices) != len(p_.vertices):
                            continue
                        Qv = V[list(q_.vertices)]
                        d_ = np.linalg.norm(R[:, None, :] - Qv[None, :, :], axis=2).min(axis=1)
                        if d_.max() < 50 * tol:
                            twins.add(p_.index)
                            twins.add(q_.index)
    return sorted({p_.index for p_ in me.polygons if (p_.index in cand and isSide(cand[p_.index])) or p_.index in twins})


def meshIsOpen(me):
    # True when the mesh has boundary edges (an element without its sector sides)
    if not len(me.edges):
        return False
    cnt = np.zeros(len(me.edges), dtype=np.int64)
    li = np.empty(len(me.loops), dtype=np.int64)
    me.loops.foreach_get("edge_index", li)
    np.add.at(cnt, li, 1)
    return bool((cnt == 1).any())


def stripSides(me, z, m):
    # the sector sides ('meridian faces') taken out of a fresh element mesh: the pieces are open at their sides,
    # the elements meet there once they are joined. nothing is changed when the open rims do not fit each other
    # (every point of a rim must have its partner one pitch further). returns the number of faces taken out
    if meshIsOpen(me):
        return 0
    sides = detectSides(me, z, m)
    if not sides:
        return 0
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.faces[i] for i in sides], context='FACES_ONLY')
    wire = [e for e in bm.edges if not e.link_faces]
    if wire:
        bmesh.ops.delete(bm, geom=wire, context='EDGES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bnd = list({v for e in bm.edges if e.is_boundary for v in e.verts})
    if not bnd:
        bm.free()
        return 0
    if z > 1:
        tol = 1e-4 * max(m, 1e-9)
        pitch = 2 * math.pi / z
        kd = mathutils.kdtree.KDTree(len(bnd))
        for i, v in enumerate(bnd):
            kd.insert(v.co, i)
        kd.balance()
        for v in bnd:
            ok_ = False
            for sg in (1.0, -1.0):
                c_, s_ = math.cos(sg * pitch), math.sin(sg * pitch)
                q = Vector((c_ * v.co.x - s_ * v.co.y, s_ * v.co.x + c_ * v.co.y, v.co.z))
                if kd.find(q)[2] < tol:
                    ok_ = True
                    break
            if not ok_:
                bm.free()
                return 0
    bm.to_mesh(me)
    bm.free()
    attachMaterials(me)
    me.update()
    return len(sides)


_ENG = {'on': False, 'cache': {}}


def closedTemp(me, z, m):
    # a closed copy of an open element mesh (each rim closed by a face), for the operations that need a closed
    # sector: the sections of the lapping, the boolean tools. the sides are taken out again afterwards
    t = me.copy()
    t.name = me.name + ".closed"
    bm = bmesh.new()
    bm.from_mesh(t)
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        res = bmesh.ops.holes_fill(bm, edges=bnd, sides=0)
        nf = res["faces"]
        for f in nf:
            f.material_index = CLS_PLAIN
        bmesh.ops.triangulate(bm, faces=nf, quad_method='BEAUTY', ngon_method='BEAUTY')
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        if bm.calc_volume(signed=True) < 0:
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.to_mesh(t)
    bm.free()
    return t


def meshSnapshot(me):
    V = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", V)
    return (len(me.vertices), len(me.polygons), float(np.round(V, 9).sum()), float(np.abs(np.round(V, 9)).sum()))


class engineMode:
    # while it is on, gearMesh() of a rotary gear gives a closed copy of its element mesh (sector sides put back);
    # what the operation changed is written back into the real mesh with the sides taken out again
    def __enter__(self):
        self.outer = _ENG['on']
        if not self.outer:
            _ENG['on'] = True
            _ENG['cache'] = {}
        return self

    def __exit__(self, et, ev, tb):
        if self.outer:
            return False
        _ENG['on'] = False
        cache, _ENG['cache'] = _ENG['cache'], {}
        for key, (me, t, snap, z, m) in cache.items():
            try:
                if et is None and me.name in bpy.data.meshes and meshSnapshot(t) != snap:
                    bm = bmesh.new()
                    bm.from_mesh(t)
                    bm.to_mesh(me)
                    bm.free()
                    attachMaterials(me)
                    me.update()
                    stripSides(me, z, m)
            finally:
                if t.name in bpy.data.meshes:
                    bpy.data.meshes.remove(t)
        return False


def joinGearBM(gear, what="joining"):
    # all the elements of a rotary gear as one welded bmesh, in the gear frame. the element mesh is open at its
    # sector sides (nothing is taken out of it here, whatever the user did to it): the copies are only welded on
    # their rims. a closed element mesh (an older gear, the sides still in it): its sector sides are left out
    checkRotary(gear, what)
    checkVersion(gear)
    z = int(gear["lap_teeth"])
    me = gearMesh(gear)
    m = sizeModule(gear)
    V = np.array([tuple(v.co) for v in me.vertices])
    sides = set()
    if not meshIsOpen(me):
        stored = me.get("lap_sides")
        if stored is not None and all(0 <= int(i) < len(me.polygons) for i in stored):
            sides = set(int(i) for i in stored)
        else:
            sides = set(detectSides(me, z, m))
    F, MI = [], []
    for p_ in me.polygons:
        if p_.index in sides:
            continue
        F.append(list(p_.vertices))
        MI.append(p_.material_index)
    STATS["sides"] = sorted(sides)
    bm = bmesh.new()
    for k in range(z):
        c, s_ = math.cos(2 * math.pi * k / z), math.sin(2 * math.pi * k / z)
        Vk = np.stack([c * V[:, 0] - s_ * V[:, 1], s_ * V[:, 0] + c * V[:, 1], V[:, 2]], axis=1)
        vs = [bm.verts.new(tuple(q)) for q in Vk]
        for f, mi in zip(F, MI):
            try:
                bm.faces.new([vs[i] for i in f]).material_index = mi
            except ValueError:
                pass
    # the elements meet on their sector sides: weld
    wd = 1e-4 * m
    if z == 1:
        # the hairline slot of a single element closed
        wd = max(wd, 1.2 * SLOT * max(math.hypot(v.co.x, v.co.y) for v in bm.verts))
        # the end faces of a single element are rings cut by the slot: triangles, so that closing
        # the slot joins them edge to edge
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    rim = list({v for e in bm.edges if e.is_boundary for v in e.verts})
    bmesh.ops.remove_doubles(bm, verts=rim, dist=wd)
    if offsetOf(gear):
        # points the print offset of the pieces took to one place (the ends of a profile edge shorter than the
        # offset): welded, the faces between them vanish
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6 * m)
        for _ in range(8):
            # (Blender 4.5 leaves some pairs after one pass)
            zv = list({v for e in bm.edges if e.calc_length() < 1e-9 * max(m, 1.0) for v in e.verts})
            if not zv:
                break
            bmesh.ops.remove_doubles(bm, verts=zv, dist=1e-6 * m)
        ze = [e for e in bm.edges if e.calc_length() < 1e-9 * max(m, 1.0)]
        if ze:
            bmesh.ops.collapse(bm, edges=ze, uvs=False)
            bmesh.ops.dissolve_degenerate(bm, dist=1e-9 * max(m, 1.0), edges=list(bm.edges))
    wire = [e for e in bm.edges if not e.link_faces]
    if wire:
        bmesh.ops.delete(bm, geom=wire, context='EDGES_FACES')
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.verts.index_update()
    bm.faces.index_update()
    # normals are left as they are unless the faces disagree (two faces of an edge running the same way)
    badn = 0
    for e in bm.edges:
        if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert:
            badn += 1
    if badn:
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
    bm.normal_update()
    return bm, m, z


def printCopy(context, gear, offset, report, chamfer=0.0, ends='BOTH'):
    # the printable copy: the elements joined into one closed solid (the shaft seat united with it), then the
    # chamfer of the end planes against the elephant foot (chamferBed; 0 = none). nothing else: no offset (it sits
    # in the pieces from their creation, bakeOffset), no repair of the pieces, no face of them taken out - the
    # gear itself is never touched, the chamfer is in the copy only
    bm, m, z = joinGearBM(gear, "the printable copy")
    if offset and gear.get("lap_offset") is None:
        report.append("WARNING: '%s' has no print offset in its pieces (the printable copy does not make it): "
                      "use 'Apply print offset' on the gear" % gear.name)
    if seatChild(gear) is not None and "lap_seat_z0" in gear:
        # the shaft seat ring (grown into the body) united with the teeth
        sb = seatSolidBM(gear, True)
        nb = bmUnion(bm, sb, m)
        sb.free()
        bm.free()
        bm = nb
        if any(len(e.link_faces) != 2 for e in bm.edges):
            # a hairline fin where the seam of the seat ring meets a tooth root (seen with Blender 4.5)
            repairSolid(bm, m)
        report.append("shaft seat %s united with '%s'" % (gear.get("lap_seat_shape"), gear.name))
    open_edges = sum(1 for e in bm.edges if not e.is_manifold)
    vol0 = bm.calc_volume(signed=True)
    nch = 0
    if chamfer > 0:
        if open_edges:
            report.append("WARNING: '%s': no chamfer, the joined mesh is not closed (%d open edges)"
                          % (gear.name, open_edges))
        else:
            nch = chamferBed(bm, chamfer, report, gear.name, ends, 2e-4 * m)
    vol1 = bm.calc_volume(signed=True)
    # a new copy never replaces an older one: blender numbers the name (.001, .002, ...)
    mesh = bpy.data.meshes.new(gear.name + "_print")
    bm.to_mesh(mesh)
    bm.free()
    attachMaterials(mesh)
    ob = bpy.data.objects.new(gear.name + "_print", mesh)
    name = ob.name
    (gear.users_collection[0] if gear.users_collection else context.collection).objects.link(ob)
    ob.matrix_world = gearFrame(gear)
    report.append("printable copy '%s': %d teeth joined, %d faces, print offset in the pieces %.4g, chamfer %s, "
                  "volume %.6g -> %.6g, open edges %d" % (name, z, len(mesh.polygons), offsetOf(gear),
                                                          ("%.3g on %d edges" % (chamfer, nch)) if nch else "none",
                                                          vol0, vol1, open_edges))
    if open_edges:
        report.append("WARNING: the joined mesh is not closed (%d open edges)" % open_edges)
    return ob


def openEdgesOfJoin(gear):
    bm, m, z = joinGearBM(gear, "the check of the joined pieces")
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


def bakeOffset(context, gear, offset, report):
    # the print offset in the pieces, so that the joined pieces stay a closed solid: first with points that a
    # short profile edge takes to one place merged (a clean result for most gears); when the joined pieces are
    # torn by that (a tooth tip narrower than the offset on a lapped gear), the offset again without the merging
    # (points that cannot move the whole way stay behind, faces turned over are selected for the hand)
    if not offset:
        return False
    try:
        open0 = openEdgesOfJoin(gear)
    except LapError:
        open0 = 0
    n_rep = len(report)
    ok = bakeOffsetOnce(context, gear, offset, report, True)
    if not ok:
        return False
    try:
        open1 = openEdgesOfJoin(gear)
    except LapError:
        return ok
    if open1 > open0:
        restoreNominal(gear, [])
        dropBaked(gear)
        del report[n_rep:]
        report.append("note: '%s': merging the points of a pinched tip tore the joined pieces (%d open edges): "
                      "the offset again without it" % (gear.name, open1 - open0))
        ok = bakeOffsetOnce(context, gear, offset, report, False)
        if ok:
            open2 = openEdgesOfJoin(gear)
            if open2 > open0:
                report.append("WARNING: '%s': the joined pieces have %d open edges at points that could not "
                              "move: correct them by hand" % (gear.name, open2 - open0))
    return ok


def bakeOffsetOnce(context, gear, offset, report, merge=True):
    # the print offset made in the pieces: every wall of the sector mesh (flanks, tips, roots, bore) moved into
    # the material across the axis by offset, so that what is drawn is what the printer should get, and
    # the pieces can be corrected by hand (one mesh, all sectors follow). the move is worked out on the joined
    # solid (neighbouring sectors give every point on a sector side its walls) and then taken back by
    # the points of the sector mesh; its topology stays. the nominal shape is kept (lap_nominal) for
    # 'restore'. returns True when done
    if not offset:
        return False
    try:
        bm, m, z = joinGearBM(gear, "the print offset")
    except LapError as e:
        report.append("note: '%s' has no print offset (%s)" % (gear.name, e))
        return False
    me = gearMesh(gear)
    if me.get("lap_offset") is not None:
        bm.free()
        report.append("note: '%s': its pieces carry the print offset %.4g already (restore the nominal shape "
                      "first to change it)" % (gear.name, float(me["lap_offset"])))
        return False
    sides = list(STATS.get("sides", []))
    pre = [v.co.copy() for v in bm.verts]
    D, ok, big, n_old = offsetDisplacement(bm, offset, gear)
    # a profile edge shorter than the offset next to a convex corner turns over (in 2d it would just vanish):
    # the two ends of such an edge are taken to one point (the topology of the sector mesh must stay: the
    # points lie on each other, the printable copy welds them), a few rounds; a point whose face still
    # turns over then moves only as far as it can (its move halved until no face turns)
    nvj = len(pre)
    bm.verts.ensure_lookup_table()
    cls = list(range(nvj))

    def find(i):
        while cls[i] != i:
            cls[i] = cls[cls[i]]
            i = cls[i]
        return i
    pos = np.array([(pre[i].x + (D[i, 0] if ok[i] else 0.0), pre[i].y + (D[i, 1] if ok[i] else 0.0)) for i in range(nvj)])

    def place():
        groups = {}
        for i in range(nvj):
            groups.setdefault(find(i), []).append(i)
        for r_, mem in groups.items():
            q = pos[mem].mean(axis=0) if len(mem) > 1 else pos[mem[0]]
            for i in mem:
                bm.verts[i].co.x, bm.verts[i].co.y = float(q[0]), float(q[1])
                pos[i] = q
        bm.normal_update()
    bevel_g = isBevel(gear)
    place()
    merged = 0
    for it in range(COLLAPSE_ROUNDS if merge else 0):
        bad = [f for f in bm.faces if f.calc_area() > 1e-14 and f.normal.dot(n_old[f.index]) < 0]
        if not bad:
            break
        n_new = 0
        for f in bad:
            for e in f.edges:
                u, w = e.verts
                d_ = pos[u.index] - pos[w.index]
                dz = abs(pre[u.index].z - pre[w.index].z)
                ln = math.hypot(d_[0], d_[1])
                if ln < COLLAPSE_LEN * abs(offset) and (bevel_g or dz < 0.5 * math.sqrt(ln * ln + dz * dz) + 1e-12):
                    ru, rw = find(u.index), find(w.index)
                    if ru != rw:
                        cls[ru] = rw
                        n_new += 1
        if not n_new:
            break
        merged += n_new
        # the class stands where the mean of its points' moved places is
        place()
    scale = np.ones(nvj)
    limited = set()
    for it in range(16):
        bad = [f for f in bm.faces if f.calc_area() > 1e-14 and f.normal.dot(n_old[f.index]) < 0]
        if not bad:
            break
        for f in bad:
            for v in f.verts:
                scale[v.index] *= 0.5 if it < 14 else 0.0
                limited.add(v.index)
        # damped places: toward the point of rest
        for i in range(nvj):
            q = pos[i] * scale[i] + np.array((pre[i].x, pre[i].y)) * (1.0 - scale[i])
            bm.verts[i].co.x, bm.verts[i].co.y = float(q[0]), float(q[1])
        bm.normal_update()
    final = np.array([(v.co.x, v.co.y) for v in bm.verts])
    D = final - np.array([(p_.x, p_.y) for p_ in pre])
    ok = np.ones(nvj, dtype=bool)
    nlim = len(limited)
    centers = [sum((pre[v.index] for v in f.verts), Vector()) / len(f.verts) for f in bm.faces
               if any(v.index in limited for v in f.verts)]
    bm.free()
    # the move of the points of the sector mesh: those of the joined solid at the same place
    kd = mathutils.kdtree.KDTree(len(pre))
    for i, p_ in enumerate(pre):
        kd.insert(p_, i)
    kd.balance()
    nv = len(me.vertices)
    V = np.empty(nv * 3)
    me.vertices.foreach_get("co", V)
    V = V.reshape(-1, 3)
    rmax = float(np.hypot(V[:, 0], V[:, 1]).max())
    tol = 1e-3 * m
    if z == 1:
        tol = max(tol, 3 * 1.2 * SLOT * rmax)
    Dv = np.zeros((nv, 2))
    lost = 0
    for i in range(nv):
        co, j, d = kd.find(Vector(V[i]))
        if d > tol:
            lost += 1
        elif ok[j]:
            Dv[i] = D[j]
    if z > 1:
        # a point on a sector side and its partner on the side of the next sector are one point of the joined
        # solid: the same move (turned by a pitch), whatever the rounding of the mesh and of the smoothing
        pitch = 2 * math.pi / z
        c_, s_ = math.cos(pitch), math.sin(pitch)
        R = np.stack([c_ * V[:, 0] - s_ * V[:, 1], s_ * V[:, 0] + c_ * V[:, 1], V[:, 2]], axis=1)
        kv = mathutils.kdtree.KDTree(nv)
        for i in range(nv):
            kv.insert(Vector(V[i]), i)
        kv.balance()
        for j in range(nv):
            co, i, d = kv.find(Vector(R[j]))
            if d < 0.1 * tol and i != j:
                avg = 0.5 * (Dv[i] + np.array((c_ * Dv[j][0] - s_ * Dv[j][1], s_ * Dv[j][0] + c_ * Dv[j][1])))
                Dv[i] = avg
                Dv[j] = np.array((c_ * avg[0] + s_ * avg[1], -s_ * avg[0] + c_ * avg[1]))
    W = V.copy()
    W[:, 0] += Dv[:, 0]
    W[:, 1] += Dv[:, 1]
    # what the move will be kept for 'restore'
    nom = me.copy()
    nom.name = me.name + ".nominal"
    nom.use_fake_user = True
    me.vertices.foreach_set("co", W.reshape(-1))
    if sides:
        me["lap_sides"] = sides
    # the faces that turned over: selected in the sector mesh, for the hand
    for p_ in me.polygons:
        p_.select = False
    marked = 0
    if centers:
        pk = mathutils.kdtree.KDTree(len(me.polygons))
        for p_ in me.polygons:
            pk.insert(Vector(V[list(p_.vertices)].mean(axis=0)), p_.index)
        pk.balance()
        for c in centers:
            for k in range(z):
                a_ = -2 * math.pi * k / z
                q = Vector((math.cos(a_) * c.x - math.sin(a_) * c.y, math.sin(a_) * c.x + math.cos(a_) * c.y, c.z))
                co, idx, d = pk.find(q)
                if d < 50 * tol:
                    me.polygons[idx].select = True
                    marked += 1
                    break
    me.update()
    me["lap_offset"] = float(offset)
    gear["lap_offset"] = float(offset)
    gear["lap_nominal"] = nom.name
    seatRebuild(gear)
    report.append("print offset %.4g made in the pieces of '%s' (%d points of the sector mesh moved, nominal shape "
                  "kept as '%s')" % (offset, gear.name, nv - lost, nom.name))
    if lost:
        report.append("WARNING: '%s': %d points of the sector mesh found no partner in the joined solid and stay"
                      % (gear.name, lost))
    if nlim:
        report.append("WARNING: '%s': %d points could not move the whole offset (a wall thinner than twice the "
                      "offset: tip, root, chamfer); %d faces of the sector mesh at them are selected - correct them "
                      "by hand (edit mode of any element, all sectors follow) or use a smaller offset"
                      % (gear.name, nlim, marked))
    if int(big.sum()):
        report.append("WARNING: '%s': %d points between very sharp corners moved only 4 offsets"
                      % (gear.name, int(big.sum())))
    return True


def swapToNominal(gear):
    # the pieces of a gear that carries a print offset, put into their nominal shape for a while (the lapping
    # cuts with the real tooth shape, the offset is made again in the result); returns what restoreSwapped needs
    nm = gear.get("lap_nominal")
    nom = bpy.data.meshes.get(nm) if nm else None
    me = gearMesh(gear)
    if nom is None or len(nom.vertices) != len(me.vertices):
        return None
    cur = np.empty(len(me.vertices) * 3)
    me.vertices.foreach_get("co", cur)
    A = np.empty(len(nom.vertices) * 3)
    nom.vertices.foreach_get("co", A)
    me.vertices.foreach_set("co", A)
    me.update()
    return (me, cur)


def restoreSwapped(sw):
    if sw is None:
        return
    me, cur = sw
    if len(me.vertices) * 3 == len(cur):
        me.vertices.foreach_set("co", cur)
        me.update()


def dropBaked(gear):
    # the markers of a print offset in the pieces, after the pieces were made new (the lapping)
    me = gearMesh(gear)
    for k in ("lap_offset", "lap_sides"):
        if k in me:
            del me[k]
        if k in gear:
            del gear[k]
    nm = gear.get("lap_nominal")
    if nm:
        nom = bpy.data.meshes.get(nm)
        if nom is not None:
            bpy.data.meshes.remove(nom)
        del gear["lap_nominal"]


def restoreNominal(gear, report):
    # the pieces of the gear back to the shape before the print offset (hand corrections of the points are
    # lost with it; the mesh must have the same points)
    nm = gear.get("lap_nominal")
    nom = bpy.data.meshes.get(nm) if nm else None
    me = gearMesh(gear)
    if nom is None or len(nom.vertices) != len(me.vertices):
        report.append("WARNING: '%s': no nominal shape to restore (the points of the mesh changed)" % gear.name)
        return False
    A = np.empty(len(nom.vertices) * 3)
    nom.vertices.foreach_get("co", A)
    me.vertices.foreach_set("co", A)
    me.update()
    for k in ("lap_offset", "lap_sides"):
        if k in me:
            del me[k]
        if k in gear:
            del gear[k]
    seatRebuild(gear)
    report.append("'%s': the pieces are back in the nominal shape" % gear.name)
    return True


def bakeNew(context, objs, report):
    # the print offset (scene setting) in the pieces of every new gear
    off = float(context.scene.lap.print_offset)
    n = 0
    if not off:
        return 0
    for o in objs:
        for g in [o] + list(o.children_recursive):
            if isGear(g) and not g.get("lap_part") and not isRack(g) and elements(g):
                try:
                    if bakeOffset(context, g, off, report):
                        n += 1
                except Exception as e:
                    report.append("WARNING: '%s': the print offset failed (%s)" % (g.name, e))
    return n


def gearsOfSelection(context):
    # the gears to work on: the active gear, or all gears of the active pair
    act = context.active_object
    if act is not None and "lap_pair_no" in act:
        return [c for c in act.children_recursive if isGear(c) and not c.get("lap_part") and not isRack(c)]
    g = gearOfActive(context)
    return [g] if g is not None else []


# ---------------------------------------------------------------------------
# user interface
# ---------------------------------------------------------------------------

def pollGear(self, obj):
    return isGear(obj)


class LAP_Props(bpy.types.PropertyGroup):
    teeth: bpy.props.IntProperty(name="Teeth", default=20, min=1, max=1000)
    module: bpy.props.FloatProperty(name="Module", default=1.5, min=0.001, precision=4,
                                    description="1.5 for fdm with a 0.4 nozzle: the tip land about two lines, "
                                                "two perimeters a side up to 3/4 of the tooth height")
    kind: bpy.props.EnumProperty(name="Type", items=(
        ('SPUR', "Cylindrical", "parallel axes"),
        ('BEVEL', "Bevel pair", "intersecting axes: both gears are created at once"),
        ('WORM', "Worm pair", "crossed axes at 90 deg: worm (source) and wheel blank (target) at once")),
        default='SPUR')
    worm_starts: bpy.props.IntProperty(name="Starts", default=1, min=1, max=12,
                                       description="number of threads of the worm; one element per start")
    worm_q: bpy.props.FloatProperty(name="Diameter factor q", default=10.0, min=4.0, max=40.0, precision=2,
                                    description="pitch diameter of the worm in axial modules; the lead angle "
                                                "is atan(starts / q)")
    worm_length: bpy.props.FloatProperty(name="Worm length (0 = auto)", default=0.0, min=0.0,
                                         description="auto: the outer diameter of the wheel")
    wheel_tol: bpy.props.FloatProperty(name="Wheel mesh tolerance", default=0.01, min=0.001, max=0.1, precision=3,
                                       description="allowed chord deviation of the worm wheel mesh, in modules; "
                                                   "flat flanks get sparse, fillets stay dense. Sections are "
                                                   "dropped at twice this value")
    width: bpy.props.FloatProperty(name="Face width", default=6.0, min=0.001,
                                   description="along the axis; for bevel gears along the cone, from the large end")
    shaft: bpy.props.FloatProperty(name="Shaft angle", default=90.0, min=1.0, max=179.0,
                                   description="angle between the axes of the bevel pair")
    shape: bpy.props.EnumProperty(name="Element", items=(
        ('TOOTH', "Starter tooth", "involute starter tooth to reshape"),
        ('SMOOTH', "Smooth blank", "plain sector of the tip circle")), default='TOOTH')
    bore: bpy.props.FloatProperty(name="Bore radius (0 = auto)", default=0.0, min=0.0,
                                  description="cylindrical bore; bevel gears: it runs up to the rim")
    mate_teeth: bpy.props.IntProperty(name="Mating teeth", default=30, min=1, max=1000)
    std_mate: bpy.props.BoolProperty(name="With mating gear", default=False,
                                     description="cylindrical: make the external mate too, with its own starter "
                                                 "teeth, in mesh (opposite hand for helical teeth)")
    helix: bpy.props.FloatProperty(name="Helix angle", default=0.0, min=-75.0, max=75.0,
                                   description="angle of the teeth at the pitch circle (positive: right "
                                               "hand); the module is the transverse module")
    mate_cross: bpy.props.FloatProperty(name="Crossing angle", default=0.0, min=-90.0, max=90.0,
                                        description="angle between the axes of a crossed cylindrical pair; "
                                                    "the helix angles of both gears add up to it")
    mate_internal: bpy.props.BoolProperty(name="Internal (ring)", default=False,
                                          description="ring gear; for a bevel source the pitch cone over 90 deg")
    motion: bpy.props.EnumProperty(name="Rolling", items=(
        ('ROT', "Rotation - rotation", "two gears turning about their axes"),
        ('TRANS', "Rotation - translation", "a gear turning and a rack moving along (the rack as the tool "
                                             "or as the blank)")), default='ROT')
    # tab 1: one gear
    g_kind: bpy.props.EnumProperty(name="Gear", items=(
        ('CYL', "Cylindrical", "external gear: spur, helical or herringbone"),
        ('RING', "Internal", "internal gear (ring), cut by a pinion rolling inside it"),
        ('BEVEL', "Bevel", "one bevel gear"),
        ('WORM', "Worm", "cylindrical worm"),
        ('RACK', "Rack", "straight, helical or herringbone rack")), default='CYL')
    rack_height: bpy.props.FloatProperty(name="Body under the roots (0 = 2 modules)", default=0.0, min=0.0,
                                         description="height of the rack body below the tooth roots")
    herring: bpy.props.BoolProperty(name="Herringbone", default=False,
                                    description="two halves of opposite hand meeting in the middle plane "
                                                "(chevron); the helix angle is that of the upper half")
    g_delta: bpy.props.FloatProperty(name="Pitch cone angle", default=45.0, min=5.0, max=85.0,
                                     description="half angle of the pitch cone of the bevel gear")
    cutter_teeth: bpy.props.IntProperty(name="Cutter teeth (0 = auto)", default=0, min=0, max=500,
                                        description="internal gear: teeth of the pinion that cuts it (auto: about "
                                                    "half, at least 10 fewer than the ring)")
    ring_rim: bpy.props.FloatProperty(name="Rim radius (0 = auto)", default=0.0, min=0.0,
                                      description="outer radius of the ring (auto: 3.5 modules outside the "
                                                  "pitch circle)")
    # tab 2: pairs
    pr_kind: bpy.props.EnumProperty(name="Pair", items=(
        ('EXT', "External", "two cylindrical gears, parallel axes"),
        ('INT', "Internal", "pinion and ring"),
        ('PLANET', "Planetary", "sun, planets and ring"),
        ('BEVEL', "Bevel", "bevel pair, intersecting axes"),
        ('WORM', "Worm", "worm and worm wheel, crossed axes"),
        ('RACK', "Rack", "pinion and rack (straight, helical, herringbone)"),
        ('WRACK', "Worm rack", "worm and a rack along its axis, the teeth wrapped around the worm"),
        ('ESCAPE', "Escapement", "swiss lever escapement: escape wheel with club teeth and the pallet fork"),
        ('GRAVITY', "Gravity esc.", "gravity escapement for a pendulum (double three-legged): locking wheel and "
                                    "two gravity arms; the impulse is the weight of the arm, not the spring"),
        ('CLOCK', "Cycloidal", "clock gearing: wheel with epicycloidal teeth driving a pinion with radial "
                               "leaves (bs 978)")), default='EXT')
    pr_bore1: bpy.props.FloatProperty(name="Bore radius 1 (0 = auto)", default=0.0, min=0.0,
                                      description="radius of the bore of the first gear (the wheel)")
    pr_bore2: bpy.props.FloatProperty(name="Bore radius 2 (0 = auto)", default=0.0, min=0.0,
                                      description="radius of the bore of the second gear (the pinion)")
    grav_arm: bpy.props.FloatProperty(name="Arm length", default=120.0, min=20.0,
                                      description="from the pendulum axis to the pads on the rod; all sizes follow")
    grav_t: bpy.props.FloatProperty(name="Plate thickness", default=3.0, min=0.5)
    grav_gap: bpy.props.FloatProperty(name="Gap between planes", default=0.4, min=0.05)
    grav_lift: bpy.props.FloatProperty(name="Lift (deg)", default=1.5, min=0.5, max=4.0,
                                       description="how far the wheel lifts an arm: the impulse is the weight of the arm "
                                                   "falling back through this angle")
    grav_unlock: bpy.props.FloatProperty(name="Unlock (deg)", default=0.8, min=0.3, max=3.0,
                                         description="how much further the pendulum carries the arm to free the wheel")
    esc_teeth: bpy.props.IntProperty(name="Escape wheel teeth", default=15, min=12, max=40)
    esc_lift: bpy.props.FloatProperty(name="Lift (deg)", default=8.5, min=4.0, max=14.0,
                                      description="fork turn during the impulse (pallet and club together)")
    esc_lock: bpy.props.FloatProperty(name="Lock (deg)", default=1.5, min=0.5, max=4.0,
                                      description="fork turn from the lock to the start of the impulse")
    esc_drop: bpy.props.FloatProperty(name="Drop (deg)", default=1.5, min=0.3, max=4.0,
                                      description="free turn of the wheel after each impulse (wheel degrees)")
    esc_draw: bpy.props.FloatProperty(name="Draw (deg)", default=12.0, min=0.0, max=20.0,
                                      description="inclination of the locking faces that pulls the pallets into the lock")
    esc_lever: bpy.props.FloatProperty(name="Lever length (0 = auto)", default=0.0, min=0.0,
                                       description="from the pallet arbor to the notch, in modules")
    esc_pin: bpy.props.FloatProperty(name="Notch width (0 = auto)", default=0.0, min=0.0,
                                     description="width of the notch for the impulse pin, in modules")
    clock_bs978: bpy.props.BoolProperty(name="BS 978 leaves", default=False,
                                        description="leaf thickness of the standard (1.05 m up to 7 leaves, else 1.25 m): "
                                                    "a large backlash, as in clocks")
    clock_backlash: bpy.props.FloatProperty(name="Backlash (modules)", default=0.05, min=0.0, max=0.9, precision=3,
                                            description="gap at the pitch circle; the pinion leaf is the rest of the "
                                                        "pitch after the wheel tooth. 0.05 m and more: no contact at "
                                                        "the handover (checked for 55:7, 84:11, 20:7, 21:5)")
    clock_fillet: bpy.props.FloatProperty(name="Root fillet (modules)", default=0.25, min=0.0, max=1.0, precision=3,
                                          description="radius of the fillets between the radial flanks and the roots "
                                                      "of wheel and pinion")
    pr_z1: bpy.props.IntProperty(name="Teeth 1", default=20, min=3, max=1000)
    pr_z2: bpy.props.IntProperty(name="Teeth 2", default=30, min=3, max=1000)
    pr_module: bpy.props.FloatProperty(name="Module", default=1.5, min=0.001, precision=4,
                                       description="1.5 for fdm with a 0.4 nozzle (see the gear tab)")
    pr_width: bpy.props.FloatProperty(name="Face width", default=6.0, min=0.001)
    pr_helix: bpy.props.FloatProperty(name="Helix angle", default=0.0, min=-45.0, max=45.0,
                                      description="helix of the first gear (the mate gets the opposite hand, an "
                                                  "internal mate the same)")
    pr_herring: bpy.props.BoolProperty(name="Herringbone", default=False)
    chev_shape: bpy.props.EnumProperty(name="Chevron", items=(
        ('V', "V", "two spirals of opposite hand meeting at the apex (a kink)"),
        ('U', "U", "the spiral angle grows smoothly from 0 at the apex: no kink")), default='V',
        description="shape of a herringbone bevel gear")
    chev_apex: bpy.props.FloatProperty(
        name="Apex offset", default=0.0, precision=3,
        description="apex of the chevron, from the middle of the face width in modules, positive toward the large "
                    "end. a heel-loaded gear is balanced about 0.2 .. 0.3 modules above the middle")
    chev_adv: bpy.props.BoolProperty(
        name="Own inner angle", default=False,
        description="V: set the spiral angle of the inner half yourself (off: the same as the outer half)")
    chev_in: bpy.props.FloatProperty(
        name="Inner angle", default=0.0, min=-60.0, max=60.0,
        description="V, with Own inner angle: spiral angle of the inner half; 0 is a straight inner half, "
                    "positive mirrors the outer half (a chevron), negative has the same hand (a spiral). The "
                    "Spiral angle is the outer half. U: the Spiral angle is the angle at the farther end")
    pr_shape: bpy.props.EnumProperty(name="Teeth", items=(
        ('TOOTH', "Teeth", "ready teeth: starter teeth, the ring cut by its pinion"),
        ('SMOOTH', "Blanks", "smooth blanks in their places")), default='TOOTH')
    pr_sun: bpy.props.IntProperty(name="Sun teeth", default=18, min=6, max=500)
    pr_planet: bpy.props.IntProperty(name="Planet teeth", default=15, min=6, max=500)
    pr_planets: bpy.props.IntProperty(name="Planets", default=3, min=1, max=12)
    # tab: chain sprockets and timing pulleys
    cb_kind: bpy.props.EnumProperty(name="Wheel", items=(
        ('CHAIN', "Sprocket", "roller chain sprocket (iso 606 / ansi)"),
        ('BELT', "Belt pulley", "timing belt pulley with flanges and hub")), default='BELT')
    cb_pair: bpy.props.BoolProperty(name="Pair of wheels", default=False,
                                    description="two wheels on parallel axes at the center distance a whole number "
                                                "of links (chain: even) or belt teeth gives")
    cb_z1: bpy.props.IntProperty(name="Teeth 1", default=20, min=7, max=400)
    cb_z2: bpy.props.IntProperty(name="Teeth 2", default=40, min=7, max=400)
    cb_chain: bpy.props.EnumProperty(name="Chain", items=tuple((k, "%s  p %g" % (k, v[0]), "roller %g, inner width %g"
                                                                % (v[1], v[2])) for k, v in CHAINS.items()) +
                                     (('CUSTOM', "Custom", "pitch, roller diameter and inner width by hand"),),
                                     default='08B')
    cb_pitch: bpy.props.FloatProperty(name="Pitch", default=12.7, min=1.0)
    cb_roller: bpy.props.FloatProperty(name="Roller diameter", default=8.51, min=0.5)
    cb_inner: bpy.props.FloatProperty(name="Inner width", default=7.75, min=0.5)
    cb_belt: bpy.props.EnumProperty(name="Belt", items=tuple((k, "%s  p %g" % (k, v[0]), "groove depth %g, width %g"
                                                              % (v[1], v[2])) for k, v in BELTS.items()),
                                    default='GT2-2')
    cb_width: bpy.props.FloatProperty(name="Belt width (0 = usual)", default=0.0, min=0.0,
                                      description="belt: the width between the flanges is this plus 1; sprocket: "
                                                  "the tooth width (0 = iso 606: 0.93 or 0.95 of the inner width)")
    cb_flange: bpy.props.BoolProperty(name="Flanges", default=True, description="belt guides on both sides")
    cb_flange_ext: bpy.props.FloatProperty(name="Flange over the teeth", default=1.5, min=0.2,
                                           description="radius of the flanges beyond the outside circle")
    cb_flange_t: bpy.props.FloatProperty(name="Flange thickness", default=1.2, min=0.4)
    cb_hub_d: bpy.props.FloatProperty(name="Hub diameter (0 = none)", default=0.0, min=0.0)
    cb_hub_len: bpy.props.FloatProperty(name="Hub length", default=6.0, min=0.5)
    cb_hub_both: bpy.props.BoolProperty(name="Hub on both sides", default=False)
    cb_bore: bpy.props.FloatProperty(name="Bore radius 1 (0 = auto)", default=0.0, min=0.0,
                                     description="auto: 2.5 (a 5 mm shaft), at most half the root radius")
    cb_bore2: bpy.props.FloatProperty(name="Bore radius 2 (0 = auto)", default=0.0, min=0.0)
    cb_dist: bpy.props.FloatProperty(name="Center distance", default=80.0, min=1.0,
                                     description="wanted; the real one follows from the whole number of links / "
                                                 "teeth (never less than the wheels need)")
    # shaft seat of new gears and fdm settings
    seat_shape: bpy.props.EnumProperty(name="Shaft seat", items=(
        ('ROUND', "Round", "a round bore of the diameter"),
        ('D', "D-shaft", "round with one flat"),
        ('SQUARE', "Square", "the size across the flats"),
        ('PENT', "Pentagon", "the size across the inscribed circle"),
        ('HEX', "Hexagon", "the size across the flats"),
        ('CROSS', "Lego cross", "lego technic axle: cross 4.8 x 1.8"),
        ('NONE', "None", "no bore: the gear is solid")), default='ROUND')
    seat_d: bpy.props.FloatProperty(name="Shaft size", default=5.0, min=0.5,
                                    description="diameter (round, d-shaft) or across the flats (polygons)")
    seat_flat: bpy.props.FloatProperty(name="Flat depth", default=0.5, min=0.05,
                                       description="d-shaft: how deep the flat cuts into the diameter")
    seat_fit: bpy.props.FloatProperty(name="Fit clearance", default=0.05, min=0.0, max=1.0, precision=3,
                                      description="the seat larger than the shaft by this much per side (the design "
                                                  "clearance; what the printer adds is the print offset of the "
                                                  "output)")
    fdm_nozzle: bpy.props.FloatProperty(name="Nozzle", default=0.4, min=0.1, max=2.0, precision=2,
                                        description="the line width is 1.125 of it")
    fdm_layer: bpy.props.FloatProperty(name="Layer height", default=0.2, min=0.04, max=1.0, precision=3,
                                       description="sets the overhang a face may have: half a line of shift per "
                                                   "layer (0.4 nozzle: 48 deg from the vertical at 0.2, 66 at 0.1, "
                                                   "37 at 0.3); used for cones under flanges and the overhang check")
    # tab 3: blanks and rolling
    ratio_auto: bpy.props.BoolProperty(name="Ratio from the teeth", default=True,
                                       description="the tool and the blank turn as their numbers of teeth say")
    ratio_tool: bpy.props.IntProperty(name="Tool turns", default=1, min=1, max=100000)
    ratio_blank: bpy.props.IntProperty(name="Blank turns", default=1, min=1, max=100000)
    blank_slow: bpy.props.IntProperty(name="Blank slowdown", default=1, min=1, max=64,
                                      description="the blank turns this many times slower still (the tool "
                                                  "faster against it): a wheel blank gets that many times the "
                                                  "teeth, a worm blank that many times the starts. more thread "
                                                  "turns on a worm: give the ratio with fewer tool turns")
    blank_od: bpy.props.FloatProperty(name="Diameter", default=12.0, min=0.001)
    blank_bore: bpy.props.FloatProperty(name="Bore radius", default=0.0, min=0.0)
    blank_len: bpy.props.FloatProperty(name="Length", default=14.0, min=0.001)
    blank_angle: bpy.props.FloatProperty(name="Axis angle", default=90.0, min=0.0, max=180.0,
                                         description="between the axes of tool and blank (0: parallel, 90: "
                                                     "crossed as a worm)")
    blank_dist: bpy.props.FloatProperty(name="Center distance", default=9.0, min=0.0)
    blank_throat: bpy.props.FloatProperty(name="Throat radius (0 = none)", default=0.0, min=0.0,
                                          description="crossed axes: the blank hollowed about the tool axis to "
                                                      "this radius (globoid blank)")
    lowpoly: bpy.props.BoolProperty(name="Low poly", default=False,
                                    description="straight flanks (two segments), straight root and tip, few "
                                                "sections: game meshes and quick previews, made in a moment")
    meridian_step: bpy.props.FloatProperty(name="Meridian step (deg)", default=2.0, min=0.25, max=10.0,
                                           description="own bodies and globoid worms as targets: the angle "
                                                       "between their meridian sections")
    source: bpy.props.PointerProperty(name="Source", type=bpy.types.Object, poll=pollGear)
    target: bpy.props.PointerProperty(name="Target", type=bpy.types.Object, poll=pollGear)
    steps: bpy.props.IntProperty(name="Steps per tooth", default=12, min=1, max=1000)
    substeps: bpy.props.IntProperty(name="Substeps", default=4, min=1, max=64,
                                    description="section method: positions between two steps (precision)")
    pressure_limit: bpy.props.FloatProperty(name="Max pressure angle", default=45.0, min=1.0, max=89.0,
                                            description="cut faces whose normal is steeper than this against "
                                                        "the turning direction of either gear pass no torque: "
                                                        "they are parasitic (magenta) and relieved")
    relief: bpy.props.FloatProperty(name="Parasitic relief", default=0.03, min=0.0, max=0.5, precision=3,
                                    description="depth of the relief of parasitic faces, in modules")
    extend: bpy.props.FloatProperty(name="Tool continued", default=0.5, min=0.0, max=3.0, precision=2,
                                    description="crossed axes (crossed helical, worm): the cylindrical source is "
                                                "continued beyond both ends along its helix as far as the target "
                                                "reaches, at most by this share of its length, so that the target "
                                                "is cut by its flanks and not by the edges of its ends")
    lap_mode: bpy.props.EnumProperty(name="Mode", items=(
        ('CUT', "Cut", "exact: every position subtracted from the sections"),
        ('PRESS', "Press (test)", "test mode, plane sections only: one subtraction at the largest overlap, "
                                  "then the points of the outline are only pressed out of the source, along "
                                  "the normal of the edge that presses them; the same number of points in "
                                  "every section, joined by quads")), default='CUT')
    press_clearance: bpy.props.FloatProperty(name="Clearance", default=0.2, min=0.0, max=5.0, precision=3,
                                             description="press mode: the points stay this far from the source "
                                                         "(scene units, usually mm; backlash without binding)")
    press_end: bpy.props.FloatProperty(name="Extra at the ends", default=0.1, min=0.0, max=5.0, precision=3,
                                       description="press mode: this much more at the end faces, fading over "
                                                   "a tenth of the width (no binding at the ends)")
    clearance: bpy.props.FloatProperty(name="Root clearance c*", default=0.25, min=0.0, max=1.0, precision=3,
                                       description="the root lies c* modules below the deepest point the mating "
                                                   "tips reach (gost 13755: 0.25, i.e. 1.25 m below the pitch "
                                                   "circle with a standard mate); also the dedendum 1 + c* of "
                                                   "the starter tooth")
    gap: bpy.props.FloatProperty(name="Clearance", default=0.2, min=-2.0, max=2.0, precision=3,
                                 description="moved into the material on the rubbing faces only (cut faces and "
                                             "flanks); bore, ends, uncut surfaces and sector sides stay. "
                                             "the gap between the pair grows by this much")
    print_delete: bpy.props.BoolProperty(name="Delete original", default=False,
                                         description="Printable Copy: delete the gear (or the whole selected pair) after "
                                                     "the copy is made")
    print_chamfer: bpy.props.FloatProperty(name="Chamfer", default=0.4, min=0.0, max=3.0, precision=2,
                                           description="45 deg chamfer on every rim of the end faces (outline of the "
                                                       "teeth, bore, shaft seat, hub) of printable copies and exported "
                                                       "STL, against the elephant foot: the first layers, squashed "
                                                       "wider by the bed, then stay inside the nominal outline. "
                                                       "A layer or two high (0.4 = two layers of 0.2); 0 = none. "
                                                       "The gear itself is never changed")
    print_ends: bpy.props.EnumProperty(name="Ends", items=(
        ('BOTH', "Both ends", "chamfer at both end faces: the gear can be printed either way up"),
        ('LOW', "Low end", "only the end face at the lowest z of the gear (its local -Z side)"),
        ('HIGH', "High end", "only the end face at the highest z of the gear (its local +Z side)")),
        default='BOTH', description="which end faces get the chamfer")
    print_status: bpy.props.StringProperty(default="", options={'HIDDEN', 'SKIP_SAVE'},
                                           description="the last result, shown in the Print block")
    print_offset: bpy.props.FloatProperty(name="Print offset", default=0.1, min=-2.0, max=2.0, precision=3,
                                          description="new gears get this clearance in their pieces: every wall "
                                                      "(flanks, tips, roots, bore) moved into the material "
                                                      "across the axis, what a 3d printer adds (scene units, "
                                                      "usually mm); 0 = none")
    slices: bpy.props.IntProperty(name="Slices", default=16, min=2, max=200,
                                  description="slice method (axes not parallel / apexes apart): sections of "
                                              "the target across its face width")
    slice_family: bpy.props.EnumProperty(name="Slices", items=(
        ('AUTO', "Auto", "planes when the source cuts the rim, cylinders when it cuts a face"),
        ('PLANES', "Across the width", "planes normal to the axis: teeth cut into the rim"),
        ('CYLINDERS', "Across the face", "cylinders about the axis: teeth cut into a face (face gear)")),
        default='AUTO')
    simple: bpy.props.BoolProperty(name="Simple non-working faces", default=True,
                                   description="replace the faces that pass no torque (tip land, tip corners, "
                                               "root) by cylinders, cones, planes and chamfers inside the old "
                                               "outline: the gear, the tool of the next pass, gets clean edges")
    remesh: bpy.props.BoolProperty(name="Remesh cut surfaces", default=False,
                                   description="slice method: rebuild the cut surfaces with even triangles "
                                               "sized by the curvature (isotropic remeshing)")
    smooth: bpy.props.BoolProperty(name="Ramps between positions", default=True,
                                   description="slice and boolean methods: the motion between two positions "
                                               "is filled at sharp edges, so the cut follows the envelope "
                                               "instead of leaving steps")
    direction: bpy.props.EnumProperty(name="Direction", items=(
        ('AUTO', "Auto", "test both directions"), ('PLUS', "+", ""), ('MINUS', "-", "")), default='AUTO')


def addGap(gear, gap, report):
    with engineMode():
        return _addGap(gear, gap, report)


def _addGap(gear, gap, report):
    # a clearance on the rubbing surfaces only: the faces that were cut or are flanks (class not
    # plain) move into the material by gap along their normal. the plain faces - bore, ends, tip
    # lands left uncut, the sector sides between the elements - stay where they are: a point on one
    # slides in its plane, a point on two of them along their edge, on three it stays
    me = gearMesh(gear)
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.normal_update()
    moving = [f for f in bm.faces if f.material_index != CLS_PLAIN]
    if not moving:
        bm.free()
        raise LapError("'%s' has no rubbing faces (no cut or flank faces): nothing to move" % gear.name)
    cos_same = math.cos(math.radians(25.0))
    disp = {}
    nfix = nslide = 0
    for v in {v for f in moving for v in f.verts}:
        nF = Vector((0.0, 0.0, 0.0))
        fn = []
        planes = []
        for f in v.link_faces:
            if f.material_index != CLS_PLAIN:
                # angle of the face at v as its weight
                lo = next(l for l in f.loops if l.vert is v)
                nF += f.normal * lo.calc_angle()
                fn.append(f.normal)
            elif f.normal.length > 0.5:
                q = f.normal
                for i, p in enumerate(planes):
                    if abs(p.normalized().dot(q)) > cos_same:
                        planes[i] = p + (q if p.dot(q) > 0 else -q)
                        break
                else:
                    planes.append(q.copy())
        if nF.length < 1e-12:
            continue
        nF.normalize()
        shell = 1.0 / max(1.0 / 3.0, min(nF.dot(q) for q in fn))
        d = -gap * shell * nF
        planes = [p.normalized() for p in planes]
        if len(planes) == 1:
            u = d - planes[0] * d.dot(planes[0])
        elif len(planes) == 2:
            u = planes[0].cross(planes[1])
        else:
            u = None if planes else d
        if u is not None and planes:
            if u.length < 1e-12:
                u = None
            else:
                u.normalize()
                c_ = u.dot(nF)
                if c_ > 0:
                    u, c_ = -u, -c_
                u = None if c_ > -0.2 else u * min(gap / -c_, 3.0 * gap)
        if u is None:
            nfix += 1
            continue
        nslide += bool(planes)
        disp[v] = u
    # a wall thinner than twice the clearance (a sharp crest between two cuts): both of its sides
    # would pass each other. such a point moves only up to 0.45 of the way to the opposite face
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    fac = {}
    for v, u in disp.items():
        L = u.length
        if L < 1e-15:
            continue
        hit = tree.ray_cast(v.co + u * (1e-6 / L), u / L, 2.2 * L)
        if hit[0] is not None and hit[2] is not None and hit[3] < 2.2 * L and \
                v not in bm.faces[hit[2]].verts:
            fac[v] = min(1.0, 0.45 * hit[3] / L)
    nthin = len(fac)
    # the sector sides are no surface: a point there and its twin on the other side (the same point
    # of the neighbouring element) must move alike, or the elements no longer meet. both moves are
    # averaged in one frame (each already lies in its side plane)
    z = int(gear["lap_teeth"])
    half = math.pi / z * ((1.0 - SLOT / (2 * math.pi)) if z == 1 else 1.0)
    span = max((max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts)) for i in range(3))
    tol = 1e-6 * span
    side = {1: [], -1: []}
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.y)
        if r < tol:
            continue
        a = math.atan2(v.co.y, v.co.x)
        for sg in (1, -1):
            if abs(a - sg * half) * r < 10 * tol:
                side[sg].append((v, r))
    kd = mathutils.kdtree.KDTree(max(1, len(side[-1])))
    for i, (w, r) in enumerate(side[-1]):
        kd.insert((r, w.co.z, 0.0), i)
    kd.balance()
    ntwin = 0
    twins = {}
    R = Matrix.Rotation(2 * half, 3, 'Z')
    Ri = R.inverted()
    for v, r in side[1]:
        if not side[-1]:
            break
        co, i, dist = kd.find((r, v.co.z, 0.0))
        w = side[-1][i][0]
        if dist > 100 * tol or (v not in disp and w not in disp):
            continue
        dv = disp.get(v, Vector((0.0, 0.0, 0.0)))
        dw = disp.get(w, Vector((0.0, 0.0, 0.0)))
        f = min(fac.get(v, 1.0), fac.get(w, 1.0))
        avg = 0.5 * (dv + R @ dw) * f
        disp[v] = avg
        disp[w] = Ri @ avg
        fac.pop(v, None)
        fac.pop(w, None)
        twins[v] = w
        twins[w] = v
        ntwin += 1
    for v, f in fac.items():
        disp[v] = disp[v] * f
    # faces that cut through others after the move (walls too thin in some other direction): the
    # points of both move half as far, a few times
    orig = {v: v.co.copy() for v in disp}
    nself = 0
    for it in range(8):
        for v, u in disp.items():
            v.co = orig[v] + u
        tree = BVHTree.FromBMesh(bm)
        bad = set()
        for i, j in tree.overlap(tree):
            fi, fj = bm.faces[i], bm.faces[j]
            if i != j and not (set(fi.verts) & set(fj.verts)):
                bad.update(v for v in fi.verts if v in disp)
                bad.update(v for v in fj.verts if v in disp)
        if not bad:
            break
        if it == 0:
            nself = len(bad)
        for v in list(bad):
            w = twins.get(v)
            if w is not None:
                bad.add(w)
        for v in bad:
            disp[v] = disp[v] * (0.5 if it < 7 else 0.0)
    else:
        for v, u in disp.items():
            v.co = orig[v] + u
    bm.to_mesh(me)
    bm.free()
    me.update()
    gear["lap_gap"] = float(gear.get("lap_gap", 0.0)) + gap
    if nthin or nself:
        report.append("WARNING: %d points on walls thinner than about twice the clearance (sharp crests): "
                      "moved less, the gap is smaller there" % (nthin + nself))
    report.append("clearance %.4g on the rubbing faces of '%s' (%d faces): %d points moved (%d of them along plain "
                  "faces), %d held by plain faces; total added %.4g"
                  % (gap, gear.name, len(moving), len(disp), nslide, nfix, gear["lap_gap"]))


def gearOfActive(context):
    o = context.active_object
    if o is None:
        return None
    if isGear(o):
        return o
    if o.parent is not None and isGear(o.parent):
        return o.parent
    return None



# ---------------------------------------------------------------------------
# placing and grouping new gears: a new gear or pair goes on the axis of the selected gear, next to
# it along the axis (its faces touching), else at the world origin. a pair gets its own empty
# ---------------------------------------------------------------------------

def anchorGear(context):
    # the selected gear; a selected pair: its output gear (the second one)
    o = context.active_object
    if o is None or not o.select_get():
        return None
    if "lap_pair_no" in o:
        g = bpy.data.objects.get(o.get("lap_out", ""))
        if g is not None and (isGear(g) or g.get("lap_part")):
            return g
        gs = [c for c in o.children_recursive if isGear(c) or c.get("lap_part")]
        return gs[-1] if gs else None
    return gearOfActive(context)


def axialRange(gear, frame_inv):
    # (min z, max z) of the gear's elements in a frame
    lo, hi = float("inf"), float("-inf")
    for el in elements(gear):
        me = el.data
        V = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", V)
        V = V.reshape(-1, 3)
        M = np.array(frame_inv @ elWorld(el))
        Z = V @ M[2, :3] + M[2, 3]
        lo, hi = min(lo, float(Z.min())), max(hi, float(Z.max()))
    return lo, hi


def newTopObjects(before):
    return [o for o in bpy.data.objects if o.name not in before and o.parent is None]


def placeNew(anchor, objs):
    # objs made about the world origin (axis = world z): onto the anchor's axis, above it
    if anchor is None:
        return
    F = gearFrame(anchor)
    lo_a, hi_a = axialRange(anchor, F.inverted())
    lo_n = min(axialRange(g, Matrix.Identity(4))[0] for g in objs if (isGear(g) or g.get("lap_part")) and elements(g))
    X = F @ Matrix.Translation((0.0, 0.0, hi_a - lo_n))
    for o in objs:
        o.matrix_world = X @ o.matrix_world


def nextPairNumber():
    return counterNext("lap_last_pair", "lap_pair_no")


def groupPair(context, objs, kind, out=None):
    # one empty for the pair (at its first gear), the gears renamed P<n>_...
    no = nextPairNumber()
    gears = [o for o in objs if isGear(o) or o.get("lap_part")]
    first = gears[0]
    e = bpy.data.objects.new("pair_%d_%s" % (no, kind), None)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = max(1.0, float(first.empty_display_size))
    e["lap_pair_no"] = no
    (first.users_collection[0] if first.users_collection else context.collection).objects.link(e)
    e.matrix_world = gearFrame(first)
    Ei = e.matrix_world.inverted()
    for o in objs:
        W = o.matrix_world.copy()
        o.parent = e
        o.matrix_parent_inverse = Ei
        o.matrix_world = W
    for g in [x for o in objs for x in [o] + list(o.children_recursive) if isGear(x) or x.get("lap_part")]:
        g["lap_pair"] = no
        renameGear(g, "P%d_%s" % (no, g.name))
    if out is not None:
        e["lap_out"] = out.name
    return e


def deleteTree(obj):
    # an object and everything below it; meshes left without users go too
    objs = [obj] + list(obj.children_recursive)
    meshes = {o.data for o in objs if o.type == 'MESH' and o.data is not None}
    for o in reversed(objs):
        bpy.data.objects.remove(o, do_unlink=True)
    for me in meshes:
        if me.users == 0:
            bpy.data.meshes.remove(me)


def removeFromPair(parent):
    # a pair empty left without gears goes too
    if parent is not None and "lap_pair_no" in parent and not any(isGear(c) for c in parent.children_recursive):
        deleteTree(parent)


def writeReport(lines, status=None):
    # the full report goes to the text GearLapping_report; the panel shows the last result: the status (lines of its
    # own) or the last line of the report, with the number of warnings
    txt = bpy.data.texts.get("GearLapping_report")
    if txt is None:
        txt = bpy.data.texts.new("GearLapping_report")
    txt.clear()
    txt.write("\n".join(lines) + "\n")
    for line in lines:
        print(line)
    try:
        nw = sum(1 for ln in lines if ln.startswith("WARNING"))
        head = status if status is not None else (lines[-1] if lines else "")
        bpy.context.scene.lap.print_status = head + (
            ("\n%d warning(s): see the text GearLapping_report" % nw) if nw else "")
    except (AttributeError, RuntimeError, TypeError, ValueError):
        pass


class LAP_OT_new(bpy.types.Operator):
    bl_idname = "lap.new_gear"
    bl_label = "New Gear"
    bl_description = ("New gear at the 3d cursor: an empty with linked tooth elements. bevel: both gears "
                      "of the pair, both empties and the cone apex in the world origin; the first is "
                      "the source, the second the target")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        z, m = ps.teeth, ps.module
        mat = context.scene.cursor.matrix.copy()
        try:
            if ps.kind == 'BEVEL':
                # the empties of both gears and the common cone apex are in the world origin
                mat = Matrix.Identity(4)
                d1, d2 = bevelAngles(z, ps.mate_teeth, ps.shaft)
                gear = newBevelGear(context, z, m, d1, ps.width, ps.shape == 'TOOTH', ps.bore, mat, ps.clearance)
                try:
                    g2, info = createMating(context, gear, ps.mate_teeth, d2 > math.pi / 2,
                                            tooth=ps.shape == 'TOOTH')
                    if ps.shape == 'TOOTH' and d2 > math.pi / 2:
                        info += " (internal: a blank, made by lapping)"
                except LapError:
                    removeGear(gear)
                    raise
                ps.source = gear
                ps.target = g2
                selectOnly(context, g2)
                self.report({'INFO'}, "%s (pitch cone %.4g deg) -> %s: %s"
                            % (gear.name, math.degrees(d1), g2.name, info))
                return {'FINISHED'}
            if ps.kind == 'WORM':
                z2 = ps.mate_teeth
                # auto: as long as the wheel's outer diameter (the throat blank d_aM2 = d2 + 2 m + 6 m / (z1 + 2))
                ln = ps.worm_length if ps.worm_length > 0 else (z2 + 2 + 6.0 / (ps.worm_starts + 2)) * m
                gear = wormGear(context, ps.worm_starts, m, ps.worm_q, ln, ps.bore, mat, ps.shape == 'TOOTH',
                                ps.clearance)
                try:
                    g2, info = createMating(context, gear, z2, False)
                    if ps.shape == 'TOOTH':
                        rep = []
                        wormWheelTeeth(context, gear, g2, rep, ps.clearance, tol=ps.wheel_tol)
                        info += "; " + rep[-1]
                except LapError:
                    removeGear(gear)
                    raise
                ps.source = gear
                ps.target = g2
                selectOnly(context, g2)
                self.report({'INFO'}, "%s (%d start(s), q %.4g, length %.4g) -> %s: %s"
                            % (gear.name, ps.worm_starts, ps.worm_q, ln, g2.name, info))
                return {'FINISHED'}
            bore = ps.bore if ps.bore > 0 else defaultBore(z, m)
            gear = spurGear(context, z, m, ps.width, ps.shape == 'TOOTH', False, bore, mat, ps.helix,
                            clearance=ps.clearance)
            if ps.std_mate:
                # the external mate with its own starter teeth, opposite hand, a tooth space facing
                z2 = ps.mate_teeth
                a = (z + z2) * m / 2
                try:
                    g2 = spurGear(context, z2, m, ps.width, ps.shape == 'TOOTH', False, defaultBore(z2, m),
                                  gearFrame(gear) @ Matrix.Translation((a, 0, 0)), -ps.helix,
                                  clearance=ps.clearance)
                except LapError:
                    removeGear(gear)
                    raise
                if ps.shape == 'TOOTH':
                    meshPhase(gear, g2, (z * m / 2, 0.0, 0.0))
                ps.source = gear
                ps.target = g2
                selectOnly(context, g2)
                self.report({'INFO'}, "%s -> %s: center distance %.4g" % (gear.name, g2.name, a))
                return {'FINISHED'}
        except LapError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        selectOnly(context, gear)
        ps.source = gear
        self.report({'INFO'}, "%s: %d linked elements (set as source)" % (gear.name, z))
        return {'FINISHED'}


class LAP_OT_mate(bpy.types.Operator):
    bl_idname = "lap.create_mating"
    bl_label = "Create Mating Gear"
    bl_description = "Smooth blank for the source, placed in mesh with it; becomes the target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if ps.source is None:
            self.report({'ERROR'}, "set the source")
            return {'CANCELLED'}
        try:
            g, info = createMating(context, ps.source, ps.mate_teeth, ps.mate_internal,
                                   0.0 if isBevel(ps.source) else ps.mate_cross)
        except LapError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        ps.target = g
        selectOnly(context, g)
        self.report({'INFO'}, "%s: %s (set as target)" % (g.name, info))
        return {'FINISHED'}


class LAP_OT_face(bpy.types.Operator):
    bl_idname = "lap.create_face"
    bl_label = "Create Face Gear"
    bl_description = ("Face gear blank for a cylindrical pinion (axes meeting at 90 deg): the pinion is "
                      "centred on the radius where it rolls without sliding; becomes the target")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if ps.source is None:
            self.report({'ERROR'}, "set the source (the pinion)")
            return {'CANCELLED'}
        try:
            g, info = faceGear(context, ps.source, ps.mate_teeth, None)
        except LapError as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        ps.target = g
        selectOnly(context, g)
        self.report({'INFO'}, "%s: %s (set as target)" % (g.name, info))
        return {'FINISHED'}


class LAP_OT_set(bpy.types.Operator):
    bl_idname = "lap.set_active"
    bl_label = "Use Active"
    bl_options = {'REGISTER', 'UNDO'}
    role: bpy.props.StringProperty()

    def execute(self, context):
        g = gearOfActive(context)
        if g is None:
            self.report({'ERROR'}, "select a gear (its empty or one of its elements)")
            return {'CANCELLED'}
        setattr(context.scene.lap, self.role, g)
        return {'FINISHED'}


class LAP_OT_swap(bpy.types.Operator):
    bl_idname = "lap.swap"
    bl_label = "Swap"
    bl_description = "Swap source and target"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        ps.source, ps.target = ps.target, ps.source
        return {'FINISHED'}


def ratioSlow(ps, src, tgt):
    # the turns of tool and blank as (source slowdown, target slowdown): the tool turns
    # zt kt / (zs ks) times per turn of the blank
    zs, zt = int(src["lap_teeth"]), int(tgt["lap_teeth"])
    R = Fraction(zt, zs) if ps.ratio_auto else Fraction(ps.ratio_tool, ps.ratio_blank)
    F = R * ps.blank_slow * Fraction(zs, zt)
    return F.denominator, F.numerator


def ratioText(ps, src, tgt):
    zs, zt = int(src["lap_teeth"]), int(tgt["lap_teeth"])
    ks, kt = ratioSlow(ps, src, tgt)
    R = Fraction(zt * kt, zs * ks)
    g = math.gcd(ks, zt)
    return R, ks // g, zt * kt // g, g


class LAP_OT_imprint(bpy.types.Operator):
    bl_idname = "lap.imprint"
    bl_label = "Imprint Source -> Target"
    bl_description = "Cut the target element by the space the source teeth sweep while the pair turns once"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        try:
            if ps.source is None or ps.target is None or ps.source == ps.target:
                raise LapError("set two different gears as source and target")
            rk = isRack(ps.source) or isRack(ps.target)
            if ps.motion == 'TRANS' and not rk:
                raise LapError("rotation to translation: the tool or the blank must be a rack")
            if ps.motion == 'ROT' and rk:
                raise LapError("a rack moves along: switch the rolling to rotation <-> translation")
            # a gear with the print offset in its pieces laps with its nominal shape; the target gets its own offset
            # again in the new pieces (the same as when the offset was made at printing: a clearance from both)
            src, tgt = ps.source, ps.target
            off_t = offsetOf(tgt) if (isGear(tgt) and not isRack(tgt)) else 0.0
            sw = swapToNominal(src) if (isGear(src) and not isRack(src) and src.get("lap_offset") is not None) else None
            sw_t = swapToNominal(tgt) if (off_t and tgt.get("lap_offset") is not None) else None
            try:
                imprint(context, src, tgt, ps.steps, ps.substeps, ps.direction, ps.smooth,
                        ps.pressure_limit, ps.relief, rep, ps.slices, ps.slice_family, ps.remesh, ps.simple,
                        ps.clearance, ps.extend,
                        (ps.press_clearance, ps.press_end) if ps.lap_mode == 'PRESS' else None,
                        (1, 1) if rk else ratioSlow(ps, src, tgt))
            finally:
                restoreSwapped(sw)
                restoreSwapped(sw_t)
            if isGear(tgt) and not isRack(tgt) and tgt.get("lap_offset") is not None:
                dropBaked(tgt)
                if off_t:
                    bakeOffset(context, tgt, off_t, rep)
                else:
                    seatRebuild(tgt)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep)
        nw = sum(1 for r in rep if r.startswith("WARNING"))
        self.report({'WARNING'} if nw else {'INFO'},
                    rep[-1] + (" (%d warnings, see GearLapping_report)" % nw if nw else ""))
        return {'FINISHED'}


def printTargets(context):
    # what the print buttons act on: the gears and parts of the active pair, else the active gear (its empty or an
    # element) or part. returns (the object that names it, [gears and parts]); (None, []) when nothing fits
    act = context.active_object
    if act is None:
        return None, []
    if "lap_pair_no" in act:
        return act, [c for c in act.children_recursive if isGear(c) or c.get("lap_part")]
    gear = gearOfActive(context)
    if gear is None:
        gear = act if act.get("lap_part") else (act.parent if act.parent is not None and
                                                act.parent.get("lap_part") else None)
    return (gear, [gear]) if gear is not None else (None, [])


def chamferNote(c, ends):
    # one line for the panel after a print action: how many rims got the chamfer
    if c <= 0:
        return "no chamfer (size 0)"
    done, left = CHAMFER_STATS['done'], CHAMFER_STATS['left']
    where = {'BOTH': "both ends", 'LOW': "low end", 'HIGH': "high end"}.get(ends, "")
    if not done and not left:
        return "chamfer %.3g (%s): no flat end face to chamfer" % (c, where)
    return "chamfer %.3g (%s): %d rim(s)%s" % (c, where, done, (", %d left without (see the report)" % left) if left else "")


class LAP_OT_print(bpy.types.Operator):
    bl_idname = "lap.print_copy"
    bl_label = "Printable Copy"
    bl_description = ("One closed mesh of all teeth of the active gear, or of every gear of the selected pair "
                      "(for STL export): the sectors joined and welded into a closed solid, the shaft seat "
                      "united, and every rim of the end faces chamfered by 'Chamfer' (against the elephant "
                      "foot). The print offset is not made here: it is in the pieces. The gears stay as they are")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        act = context.active_object
        pair = act if act is not None and "lap_pair_no" in act else None
        rep = []
        obs = []
        CHAMFER_STATS['done'] = CHAMFER_STATS['left'] = 0
        try:
            top, parts = printTargets(context)
            if pair is not None and not parts:
                raise LapError("the pair has no gears")
            if top is None:
                raise LapError("select a gear (its empty or an element), a part or a pair")
            for g in parts:
                obs.append(anyPrintCopy(context, g, ps.print_offset, rep, ps.print_chamfer, ps.print_ends))
        except LapError as e:
            for ob in obs:
                deleteTree(ob)
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        status = "%s: %s\n%s" % (
            "copies of the pair" if pair is not None else "copy",
            ", ".join("%s (%d faces)" % (o.name, len(o.data.polygons)) for o in obs),
            chamferNote(ps.print_chamfer, ps.print_ends))
        if pair is not None:
            # the copies of a pair in one empty of their own, where the pair is
            e = bpy.data.objects.new(pair.name + "_print", None)
            e.empty_display_type = 'PLAIN_AXES'
            e.empty_display_size = pair.empty_display_size
            (pair.users_collection[0] if pair.users_collection else context.collection).objects.link(e)
            e.matrix_world = pair.matrix_world.copy()
            Ei = e.matrix_world.inverted()
            for ob in obs:
                W = ob.matrix_world.copy()
                ob.parent = e
                ob.matrix_parent_inverse = Ei
                ob.matrix_world = W
            rep.append("printable copies of pair '%s' in '%s': %s" % (pair.name, e.name, ", ".join(o.name for o in obs)))
            sel = e
        else:
            sel = obs[0]
        if ps.print_delete:
            # the originals go (the copies keep their names, numbers and places)
            src = pair if pair is not None else parts[0]
            nm, parent = src.name, src.parent
            if ps.source is not None and ps.source.name in {o.name for o in [src] + list(src.children_recursive)}:
                ps.source = None
            if ps.target is not None and ps.target.name in {o.name for o in [src] + list(src.children_recursive)}:
                ps.target = None
            deleteTree(src)
            removeFromPair(parent)
            rep.append("original '%s' deleted" % nm)
            status += "\noriginal '%s' deleted" % nm
        writeReport(rep, status)
        selectOnly(context, sel)
        nw = sum(1 for r in rep if r.startswith("WARNING"))
        self.report({'WARNING'} if nw else {'INFO'}, rep[-1] + (" (%d warnings)" % nw if nw else ""))
        return {'FINISHED'}


class LAP_OT_offset(bpy.types.Operator):
    bl_idname = "lap.apply_offset"
    bl_label = "Apply print offset"
    bl_description = ("Make the print offset in the pieces (sector meshes) of the active gear or of the gears of "
                      "the active pair: every wall moves into the material by the offset. A gear that carries one "
                      "already is put back to its nominal shape first (hand corrections are lost)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        gears = gearsOfSelection(context)
        if not gears:
            self.report({'ERROR'}, "select a gear (its empty or an element) or a pair")
            return {'CANCELLED'}
        n = 0
        for g in gears:
            try:
                if g.get("lap_offset") is not None:
                    restoreNominal(g, rep)
                if g.get("lap_offset") is None and bakeOffset(context, g, float(ps.print_offset), rep):
                    n += 1
            except LapError as e:
                rep.append("ERROR: " + str(e))
        nw = sum(1 for r in rep if r.startswith("WARNING"))
        msg = ("print offset %.4g in the pieces of %d gear(s)" % (ps.print_offset, n)) if ps.print_offset else \
            "offset 0: the gear(s) are in the nominal shape"
        writeReport(rep, msg)
        self.report({'WARNING'} if nw else {'INFO'}, msg + (" (%d warnings, see the report)" % nw if nw else ""))
        return {'FINISHED'}


class LAP_OT_offset_restore(bpy.types.Operator):
    bl_idname = "lap.restore_nominal"
    bl_label = "Nominal shape"
    bl_description = "Put the pieces of the active gear (or of the gears of the pair) back to the shape without the print offset"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        n = 0
        for g in gearsOfSelection(context):
            if g.get("lap_offset") is not None and restoreNominal(g, rep):
                n += 1
        msg = "%d gear(s) back in the nominal shape" % n
        writeReport(rep, msg)
        self.report({'INFO'}, msg)
        return {'FINISHED'}


class LAP_OT_overhang(bpy.types.Operator):
    bl_idname = "lap.check_overhang"
    bl_label = "Check overhang"
    bl_description = ("Report the overhangs of the active gear (or of the gears of the pair) for the layer height "
                      "and the nozzle: faces that lean further than a layer can bear. Changes nothing")
    bl_options = {'REGISTER'}

    def execute(self, context):
        rep = []
        n = 0
        res = []
        try:
            for g in gearsOfSelection(context):
                bm, m, z = joinGearBM(g, "the overhang check")
                up, down = overhangCheck(bm, rep, g.name, 0.0) or (0.0, 0.0)
                res.append((g.name, up, down))
                bm.free()
                n += 1
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        lw, layer, th = fdmParams()
        status = "overhang (mm2, lying / upside down; layer %.3g, up to %.0f deg):\n%s" % (
            layer, th, "\n".join("%s: %.3g / %.3g" % r for r in res))
        writeReport(rep, status)
        self.report({'INFO'}, "%d gear(s) checked, see GearLapping_report" % n)
        return {'FINISHED'}


class LAP_OT_export(bpy.types.Operator):
    bl_idname = "lap.export_stl"
    bl_label = "Export STL"
    bl_description = ("The active gear (its empty or an element) as one closed solid in an STL file: the sector "
                      "sides left out, the teeth welded, holes closed, normals out, every rim of the end faces "
                      "chamfered by 'Chamfer' (the print offset is in the pieces)")
    bl_options = {'REGISTER'}
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    filter_glob: bpy.props.StringProperty(default="*.stl", options={'HIDDEN'})

    def invoke(self, context, event):
        gear = gearOfActive(context)
        if gear is None:
            self.report({'ERROR'}, "select a gear (its empty or an element)")
            return {'CANCELLED'}
        if not self.filepath:
            self.filepath = bpy.path.abspath("//") + gear.name + ".stl" if bpy.data.filepath else gear.name + ".stl"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        gear = gearOfActive(context)
        rep = []
        try:
            if gear is None:
                raise LapError("select a gear (its empty or an element)")
            path = bpy.path.ensure_ext(bpy.path.abspath(self.filepath), ".stl")
            if ps.print_offset and gear.get("lap_offset") is None and not isRack(gear) and not gear.get("lap_part"):
                rep.append("WARNING: '%s' has no print offset in its pieces: use 'Apply print offset' first" % gear.name)
            CHAMFER_STATS['done'] = CHAMFER_STATS['left'] = 0
            ntri = exportGearStl(context, gear, path, 0.0, rep, ps.print_chamfer, ps.print_ends)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep, "stl %s: %d triangles\n%s" % (bpy.path.basename(path), ntri,
                                                        chamferNote(ps.print_chamfer, ps.print_ends)))
        selectOnly(context, gear)
        nw = sum(1 for r in rep if r.startswith("WARNING"))
        self.report({'WARNING'} if nw else {'INFO'}, rep[-1] + (" (%d warnings)" % nw if nw else ""))
        return {'FINISHED'}


class LAP_OT_gap(bpy.types.Operator):
    bl_idname = "lap.add_gap"
    bl_label = "Add Clearance"
    bl_description = ("Move the rubbing faces (cut faces and flanks) of the active gear into the material by the "
                      "clearance; bore, ends, uncut surfaces and sector sides are not touched")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        gear = gearOfActive(context)
        rep = []
        try:
            if gear is None:
                raise LapError("select a gear (its empty or an element)")
            addGap(gear, ps.gap, rep)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep)
        self.report({'INFO'}, rep[-1])
        return {'FINISHED'}


def ownBlank(context, src, od, bore, length, angle_deg, dist, throat, module, report):
    # a blank of revolution placed at the tool (src): its axis turned by angle_deg about the line
    # joining the centres (0: parallel, 90: crossed), the centre dist from the tool axis. throat > 0
    # (crossed axes): the blank is hollowed about the tool axis to that radius (a globoid blank).
    # it becomes an own body of this add-on (cut on its meridian half planes)
    R = od / 2
    if R <= 0 or length <= 0:
        raise LapError("give the blank a diameter and a length")
    if bore >= R:
        raise LapError("the bore is larger than the blank")
    ang = math.radians(angle_deg)
    if throat > 0 and abs(math.sin(ang)) < 0.5:
        raise LapError("a throat only for crossed axes (angle near 90 deg)")
    nz = 97 if throat > 0 else 2
    zs = [-length / 2 + length * k / (nz - 1) for k in range(nz)]

    def rad(z):
        if throat > 0 and abs(z) < throat:
            return min(R, dist - math.sqrt(throat * throat - z * z))
        return R
    prof = [(rad(z), z) for z in zs]
    if min(r for r, z in prof) <= max(bore, 0.02 * R):
        raise LapError("the throat cuts through to the bore / axis: a smaller throat or a larger distance")
    nseg = 96
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / nseg), r * math.sin(2 * math.pi * k / nseg), z))
                      for k in range(nseg)])
    for a_, b_ in zip(rings[:-1], rings[1:]):
        for k in range(nseg):
            bm.faces.new((a_[k], a_[(k + 1) % nseg], b_[(k + 1) % nseg], b_[k]))
    if bore > 0:
        ib = [bm.verts.new((bore * math.cos(2 * math.pi * k / nseg), bore * math.sin(2 * math.pi * k / nseg), zs[0]))
              for k in range(nseg)]
        it = [bm.verts.new((bore * math.cos(2 * math.pi * k / nseg), bore * math.sin(2 * math.pi * k / nseg), zs[-1]))
              for k in range(nseg)]
        for k in range(nseg):
            k1 = (k + 1) % nseg
            bm.faces.new((rings[0][k1], rings[0][k], ib[k], ib[k1]))
            bm.faces.new((rings[-1][k], rings[-1][k1], it[k1], it[k]))
            bm.faces.new((ib[k], it[k], it[k1], ib[k1]))
    else:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("blank")
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("blank_%d" % nextNumber(), me)
    context.collection.objects.link(ob)
    ob.matrix_world = gearFrame(src) @ Matrix.Translation((dist, 0.0, 0.0)) @ Matrix.Rotation(ang, 4, 'X')
    context.view_layer.update()
    g = makeGearFrom(context, ob, 'WORM' if abs(math.sin(ang)) > 0.5 else 'WHEEL', 1, module, report)
    return g


def makeGearFrom(context, obj, kind, teeth, module, report):
    # an own body as a gear of this add-on: the active empty (its mesh children) or a mesh; the axis
    # is the local z of the empty (of the mesh). the meshes are joined into one element in the frame
    # of the empty; teeth > 1: that element is one tooth, repeated teeth times about the axis.
    # the old objects stay, hidden. as a target an own body is cut on its meridian half planes (it
    # should be a body of revolution, the blank); 'WORM' only marks it as a worm
    if isGear(obj) or (obj.parent is not None and isGear(obj.parent)):
        raise LapError("'%s' is already a gear of this add-on" % obj.name)
    if obj.type == 'EMPTY':
        empty = obj
        meshes = [c for c in obj.children if c.type == 'MESH']
        if not meshes:
            raise LapError("the empty '%s' has no mesh children" % obj.name)
    elif obj.type == 'MESH':
        loc, rot, sca = obj.matrix_world.decompose()
        empty = bpy.data.objects.new(obj.name + "_gear", None)
        empty.empty_display_type = 'SINGLE_ARROW'
        context.collection.objects.link(empty)
        empty.matrix_world = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
        meshes = [obj]
    else:
        raise LapError("select an empty with mesh children, or a mesh")
    inv = empty.matrix_world.inverted()
    bm = bmesh.new()
    for o in meshes:
        me_ = o.data.copy()
        me_.transform(inv @ o.matrix_world)
        bm.from_mesh(me_)
        bpy.data.meshes.remove(me_)
    for f in bm.faces:
        f.material_index = CLS_PLAIN
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bm.calc_volume(signed=True) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    V = np.array([tuple(v.co) for v in bm.verts])
    open_edges = sum(1 for e in bm.edges if not e.is_manifold)
    r = np.hypot(V[:, 0], V[:, 1])
    zlo, zhi = float(V[:, 2].min()), float(V[:, 2].max())
    # a hole along the axis: the middle of the axis lies outside the body (by the nearest face, so
    # that overlapping parts - two crossed bars - count as one body)
    tree = BVHTree.FromBMesh(bm)
    pm = Vector((0.0, 0.0, 0.5 * (zlo + zhi)))
    loc, nrm, idx, dist = tree.find_nearest(pm)
    solid = loc is None or (pm - loc).dot(nrm) <= 0
    me = bpy.data.meshes.new("tmp")
    bm.to_mesh(me)
    bm.free()
    attachMaterials(me)
    no = nextNumber()
    empty["lap_no"] = no
    empty["lap_teeth"] = int(teeth)
    empty["lap_module"] = float(module)
    empty["lap_width"] = zhi - zlo
    empty["lap_internal"] = False
    empty["lap_rbody"] = 0.0 if solid else float(r.min())
    empty["lap_custom"] = 1
    if kind == 'WORM':
        empty["lap_kind"] = 'SPUR'
        empty["lap_worm"] = 1.0
        empty["lap_axial_module"] = float(module)
        empty["lap_helix"] = 0.0
    else:
        empty["lap_kind"] = 'CUSTOM'
    me.name = empty.name + "_mesh"
    for k in range(teeth):
        el = bpy.data.objects.new("%s_e%03d" % (empty.name, k + 1), me)
        el["lap_index"] = k
        context.collection.objects.link(el)
        el.parent = empty
        el.matrix_parent_inverse = Matrix.Identity(4)
        el.matrix_basis = rotZ(2 * math.pi * k / teeth)
        el.lock_location = (True, True, True)
        el.lock_rotation = (True, True, True)
        el.lock_scale = (True, True, True)
    for o in meshes:
        o.hide_set(True)
        o.hide_render = True
    report.append("'%s' is now a gear: %s, %d element(s)%s, module %.4g (tolerances only), %s; the old "
                  "mesh object(s) hidden" % (empty.name, "worm" if kind == 'WORM' else "own body", teeth,
                                             "" if teeth == 1 else " (one tooth, repeated)", module,
                                             "solid" if solid else "bore %.4g" % float(r.min())))
    if open_edges:
        report.append("WARNING: the mesh is not closed (%d open edges): the imprint needs a closed body"
                      % open_edges)
    return empty


class LAP_OT_make(bpy.types.Operator):
    bl_idname = "lap.make_gear"
    bl_label = "Make Gear from Active"
    bl_description = ("Turn the active empty (with mesh children) or mesh into a gear of this add-on: the axis "
                      "is its local z. The whole body is one element; the ratio then comes from the "
                      "slowdowns (or give the number of teeth when the mesh is one tooth)")
    bl_options = {'REGISTER', 'UNDO'}
    kind: bpy.props.EnumProperty(name="Kind", items=(
        ('WHEEL', "Body / wheel", "any body; as a target it is cut on its meridian sections"),
        ('WORM', "Worm", "a body along its axis (cylinder, globoid blank); as a target cut on its meridians")),
        default='WHEEL')
    teeth: bpy.props.IntProperty(name="Teeth", default=1, min=1, max=500,
                                 description="1: the mesh is the whole body; more: the mesh is one tooth, "
                                             "repeated this many times about the axis")
    module: bpy.props.FloatProperty(name="Module", default=1.0, min=0.001,
                                    description="size of the teeth for tolerances, relief and clearance")

    def invoke(self, context, event):
        self.module = context.scene.lap.module
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        try:
            if context.active_object is None:
                raise LapError("select an empty with mesh children, or a mesh")
            g = makeGearFrom(context, context.active_object, self.kind, self.teeth, self.module, rep)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep)
        selectOnly(context, g)
        self.report({'WARNING'} if any(r.startswith("WARNING") for r in rep) else {'INFO'}, rep[0])
        return {'FINISHED'}


class LAP_OT_reverse(bpy.types.Operator):
    bl_idname = "lap.reverse_blank"
    bl_label = "Reverse: Blank Copy of Source"
    bl_description = ("Smooth copy of the source in its place; it becomes the target and the old target "
                      "the source")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if ps.source is None or ps.target is None:
            self.report({'ERROR'}, "set source and target")
            return {'CANCELLED'}
        old_src, old_tgt = ps.source, ps.target
        g = blankCopy(context, old_src)
        ps.source = old_tgt
        ps.target = g
        selectOnly(context, g)
        self.report({'INFO'}, "%s in place of %s; source %s -> target %s"
                    % (g.name, old_src.name, old_tgt.name, g.name))
        return {'FINISHED'}


def drawChevron(box, ps, z, delta, width, module):
    # the options of a herringbone bevel gear: V / U, apex offset, inner angle, the balance hint
    box.prop(ps, "chev_shape", expand=True)
    box.prop(ps, "chev_apex")
    if ps.chev_shape == 'V':
        row = box.row(align=True)
        row.prop(ps, "chev_adv", toggle=True)
        if ps.chev_adv:
            row.prop(ps, "chev_in", text="")
    try:
        l_out = z * module / 2 / math.sin(delta)
        l_in = l_out - width
        if l_in <= 0:
            return
        u = ps.chev_shape == 'U'
        col = box.column(align=True)
        lc = 0.5 * (l_in + l_out) + ps.chev_apex * module
        col.label(text="apex %.3g from the small end (%.3g modules)" % (lc - l_in, (lc - l_in) / module))
        h = [(apexBalance(l_in, l_out, k, u) - 0.5 * (l_in + l_out)) / module for k in (0.0, 1.0, 2.0)]
        col.label(text="thrust balance: offset %+.2f / %+.2f / %+.2f m (load even / toward the large end / strongly)"
                  % tuple(h))
    except (ValueError, ZeroDivisionError):
        pass


def drawSeat(box, ps, bevel=False):
    b = box.box()
    b.prop(ps, "seat_shape")
    sh = ps.seat_shape
    if sh == 'CROSS':
        b.label(text="lego technic axle: cross %.1f x %.1f" % (LEGO_D, LEGO_W))
    elif sh != 'NONE':
        b.prop(ps, "seat_d", text="Diameter" if sh in ('ROUND', 'D') else "Across flats")
        if sh == 'D':
            b.prop(ps, "seat_flat")
    if sh != 'NONE':
        b.prop(ps, "seat_fit")


def drawGap(lay, ps):
    # after the imprint: the clearance on the rubbing faces of the lapped gear (the active one)
    box = lay.box()
    box.label(text="Clearance of the lapped gear")
    row = box.row(align=True)
    row.prop(ps, "gap")
    row.operator("lap.add_gap", icon='MOD_OFFSET')


def wrapLabels(lay, text, icon='NONE', width=44, lines=6):
    # a text over several labels (a blender label does not wrap); the icon at the first line
    import textwrap
    first = True
    for part in str(text).split("\n"):
        for ln in textwrap.wrap(part, width) or [""]:
            if lines <= 0:
                return
            if first and icon != 'NONE':
                lay.label(text=ln, icon=icon)
            else:
                lay.label(text=ln)
            first = False
            lines -= 1


def offsetNote(gears):
    # what the pieces of these gears carry of the print offset
    if not gears:
        return None
    vals = sorted({round(offsetOf(g), 6) for g in gears})
    have = [v for v in vals if v]
    if not have:
        return "no print offset in the pieces yet"
    return "print offset in the pieces: %s%s" % (", ".join("%.4g" % v for v in have),
                                                  " (a gear without it)" if 0.0 in vals else "")


def drawPrint(lay, context):
    # the block under every tab: what the print buttons act on, the offset in the pieces, the chamfer of the end faces
    # against the elephant foot, the printer's line and layer (the overhang limit), the check, the copy, the STL, and the
    # last result
    ps = context.scene.lap
    box = lay.box()
    box.label(text="Print")
    top, parts = printTargets(context)
    gears = gearsOfSelection(context)
    col = box.column(align=True)
    if top is None:
        col.label(text="select a gear, a part or a pair", icon='INFO')
    else:
        col.label(text=("pair %s: %d parts" % (top.name, len(parts))) if "lap_pair_no" in top else top.name,
                  icon='OBJECT_DATA')
        note = offsetNote(gears)
        if note:
            col.label(text=note)
        if any(isRack(p) or p.get("lap_part") for p in parts):
            col.label(text="a rack or a part: no print offset, joined as it is")
    row = box.row(align=True)
    row.prop(ps, "print_offset", text="Offset")
    sub = row.row(align=True)
    sub.enabled = bool(gears)
    sub.operator("lap.apply_offset", icon='MOD_OFFSET', text="Apply")
    sub.operator("lap.restore_nominal", icon='LOOP_BACK', text="Nominal")
    row = box.row(align=True)
    row.prop(ps, "print_chamfer", text="Chamfer")
    row.prop(ps, "print_ends", text="")
    lw, layer, th = fdmParams()
    if ps.print_chamfer > 0:
        box.label(text="45 deg at every rim of the end faces: %.1f layers" % (ps.print_chamfer / max(layer, 1e-6)),
                  icon='MOD_BEVEL')
        if ps.print_chamfer < 1.5 * layer:
            box.label(text="under 1.5 layers: hardly shows in the slice", icon='ERROR')
    else:
        box.label(text="no chamfer: the first layers will flare (elephant foot)", icon='ERROR')
    row = box.row(align=True)
    row.prop(ps, "fdm_nozzle")
    row.prop(ps, "fdm_layer")
    box.label(text="line %.2f, overhang up to %.0f deg from the vertical" % (lw, th))
    col = box.column(align=True)
    sub = col.row(align=True)
    sub.enabled = bool(gears)
    sub.operator("lap.check_overhang", icon='ZOOM_ALL')
    sub = col.row(align=True)
    sub.enabled = bool(parts)
    sub.operator("lap.print_copy", icon='DUPLICATE')
    sub.prop(ps, "print_delete", text="", icon='TRASH')
    sub = col.row(align=True)
    sub.enabled = gearOfActive(context) is not None
    sub.operator("lap.export_stl", icon='EXPORT')
    if ps.print_status:
        wrapLabels(box.box(), ps.print_status, icon='INFO')


def cylInfo(col, z, m, helix):
    rp = z * m / 2
    col.label(text="pitch d %.4g, tip d %.4g, root d %.4g" % (2 * rp, 2 * rp + 2 * m, 2 * rp - 2.5 * m))
    if abs(helix) > 1e-9:
        col.label(text="normal module %.4g" % (m * math.cos(math.radians(helix))))


class LAP_OT_single(bpy.types.Operator):
    bl_idname = "lap.gear_single"
    bl_label = "Create Gear"
    bl_description = "One gear by its parameters at the 3d cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOW[0] = bool(context.scene.lap.lowpoly)
        try:
            return self.run(context)
        finally:
            _LOW[0] = False
            _SEAT[0] = None

    def run(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        anchor = anchorGear(context)
        before = {o.name for o in bpy.data.objects}
        mat = Matrix.Identity(4)
        z, m, tooth = ps.teeth, ps.module, ps.shape == 'TOOTH'
        rep = []
        _SEAT[0] = seatSpec(ps)
        try:
            if ps.g_kind == 'CYL':
                g = spurGear(context, z, m, ps.width, tooth, False, defaultBore(z, m), mat,
                             ps.helix, clearance=ps.clearance, herring=ps.herring)
                msg = "%s: %d teeth, module %.4g%s" % (g.name, z, m, ", herringbone" if g.get("lap_herring") else
                                                      (", helix %.4g deg" % ps.helix if abs(ps.helix) > 1e-9 else ""))
            elif ps.g_kind == 'RING':
                g = ringGear(context, z, m, ps.width, ps.helix, ps.herring, ps.clearance, mat, rep, ps.cutter_teeth,
                             tooth, ps.ring_rim)
                msg = "%s: internal, %d teeth%s" % (g.name, z, ("; " + rep[-1]) if rep else "")
            elif ps.g_kind == 'BEVEL':
                g = newBevelGear(context, z, m, math.radians(ps.g_delta), ps.width, tooth, seatRoundBore(), mat,
                                 ps.clearance, ps.helix, ps.herring, (ps.chev_in if ps.chev_adv and ps.chev_shape == 'V' else None) if ps.herring else None,
                                 ps.herring and ps.chev_shape == 'U', ps.chev_apex * m if ps.herring else 0.0)
                msg = "%s: bevel, pitch cone %.4g deg%s" % (g.name, ps.g_delta,
                                                           (", %s %.4g deg" % ("herringbone" if g.get("lap_herring")
                                                                               else "spiral", ps.helix))
                                                           if abs(ps.helix) > 1e-9 else "")
            elif ps.g_kind == 'RACK':
                g = rackGear(context, z, m, ps.width, ps.rack_height if ps.rack_height > 0 else 2 * m, ps.helix,
                             ps.herring, mat, ps.clearance, _LOW[0])
                msg = "%s: rack, %d teeth, length %.4g%s" % (g.name, z, z * math.pi * m, ", herringbone" if
                                                            ps.herring and abs(ps.helix) > 1e-9 else
                                                            (", helix %.4g deg" % ps.helix if abs(ps.helix) > 1e-9
                                                             else ""))
            else:
                ln = ps.worm_length if ps.worm_length > 0 else 32 * m
                g = wormGear(context, ps.worm_starts, m, ps.worm_q, ln, 0.0, mat, tooth, ps.clearance)
                msg = "%s: %d start(s), q %.4g, length %.4g" % (g.name, ps.worm_starts, ps.worm_q, ln)
            bakeNew(context, [g], rep)
            try:
                seatRings(context, [g], rep)
            except LapError:
                removeGear(g)
                raise
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        placeNew(anchor, newTopObjects(before))
        if anchor is not None:
            msg += " (on the axis of %s)" % anchor.name
        if rep:
            writeReport(rep)
        ps.source = g
        selectOnly(context, g)
        self.report({'WARNING'} if any(r.startswith("WARNING") for r in rep) else {'INFO'}, msg)
        return {'FINISHED'}


class LAP_OT_pair(bpy.types.Operator):
    bl_idname = "lap.gear_pair"
    bl_label = "Create Pair"
    bl_description = "Gears in mesh by the parameters of the pair, at the 3d cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOW[0] = bool(context.scene.lap.lowpoly)
        try:
            return self.run(context)
        finally:
            _LOW[0] = False
            _SEAT[0] = None

    def run(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        anchor = anchorGear(context)
        before = {o.name for o in bpy.data.objects}
        mat = Matrix.Identity(4)
        m, tooth = ps.pr_module, ps.pr_shape == 'TOOTH'
        rep = []
        t0 = time.time()
        _SEAT[0] = None if ps.pr_kind in ('ESCAPE', 'GRAVITY') else seatSpec(ps)
        try:
            if ps.pr_kind in ('EXT', 'INT'):
                g1, g2, a = gearPair(context, ps.pr_z1, ps.pr_z2, m, ps.pr_width, ps.pr_helix, ps.pr_herring,
                                     ps.pr_kind == 'INT', tooth, ps.clearance, mat, rep)
                msg = "%s + %s: center distance %.4g, ratio %.4g" % (g1.name, g2.name, a, ps.pr_z2 / float(ps.pr_z1))
                sel = g2
            elif ps.pr_kind == 'PLANET':
                sun, planets, ring, car, angs = planetary(context, ps.pr_sun, ps.pr_planet, ps.pr_planets, m,
                                                          ps.pr_width, ps.pr_helix, ps.pr_herring, tooth,
                                                          ps.clearance, mat, rep)
                zr = ps.pr_sun + 2 * ps.pr_planet
                g1, g2, sel = sun, ring, ring
                msg = ("planetary: sun %d, %d planets of %d, ring %d; carrier radius %.4g; ratio with the ring held "
                       "%.4g (sun to carrier)" % (ps.pr_sun, len(planets), ps.pr_planet, zr,
                                                  (ps.pr_sun + ps.pr_planet) * m / 2, 1.0 + zr / float(ps.pr_sun)))
            elif ps.pr_kind == 'CLOCK':
                g1, g2, a = clockPair(context, ps.pr_z1, ps.pr_z2, m, ps.pr_width, mat, rep, ps.clearance,
                                      None if ps.clock_bs978 else ps.clock_backlash, ps.clock_fillet,
                                      (0.0, 0.0))
                msg = rep.pop()
                sel = g2
            elif ps.pr_kind == 'BEVEL':
                g1, g2, msg = newBevelPair(context, ps.pr_z1, ps.pr_z2, m, ps.shaft, ps.pr_width, tooth, seatRoundBore(),
                                           ps.clearance, ps.pr_helix, ps.pr_herring, (ps.chev_in if ps.chev_adv and ps.chev_shape == 'V' else None) if ps.pr_herring else None,
                                           ps.pr_herring and ps.chev_shape == 'U',
                                           ps.chev_apex * m if ps.pr_herring else 0.0)
                sel = g2
            elif ps.pr_kind == 'RACK':
                g1, g2 = rackPair(context, ps.pr_z1, ps.pr_z2, m, ps.pr_width, ps.pr_helix, ps.pr_herring, mat,
                                  ps.clearance, _LOW[0])
                msg = "%s + %s: rack moves %.4g per pinion turn" % (g1.name, g2.name, ps.pr_z1 * math.pi * m)
                sel = g2
            elif ps.pr_kind == 'ESCAPE':
                g1, g2, a = escapePair(context, ps.esc_teeth, m, ps.pr_width, mat, rep, ps.esc_lock, ps.esc_lift,
                                       ps.esc_drop, ps.esc_draw, ps.esc_lever, ps.esc_pin, (ps.pr_bore1, ps.pr_bore2))
                msg = rep.pop()
                sel = g1
            elif ps.pr_kind == 'GRAVITY':
                g1, arms, des = gravityPair(context, ps.grav_arm, ps.grav_t, ps.grav_gap, mat, rep, ps.grav_lift,
                                            ps.grav_unlock, (ps.pr_bore1, ps.pr_bore2))
                g2 = arms[0]
                msg = rep.pop()
                sel = g1
            elif ps.pr_kind == 'WRACK':
                g1, g2, msg = wormRackPair(context, ps.worm_starts, m, ps.worm_q, ps.pr_z2, ps.pr_width,
                                           ps.worm_length, 0.0, mat, ps.clearance, _LOW[0])
                sel = g2
            else:
                g1, g2, msg = newWormPair(context, ps.worm_starts, m, ps.worm_q, ps.pr_z2, ps.worm_length, 0.0,
                                          tooth, ps.clearance, ps.wheel_tol, mat)
                sel = g2
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        objs = newTopObjects(before)
        bakeNew(context, objs, rep)
        try:
            seatRings(context, objs, rep)
        except LapError as e:
            for o in objs:
                deleteTree(o)
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        placeNew(anchor, objs)
        pe = groupPair(context, objs, ps.pr_kind.lower(), sel)
        rep.append(msg + " (%.1f s)" % (time.time() - t0))
        rep.append("pair %d: '%s'%s" % (int(pe["lap_pair_no"]), pe.name,
                                       (", on the axis of %s" % anchor.name) if anchor is not None else ""))
        writeReport(rep)
        ps.source, ps.target = g1, g2
        selectOnly(context, pe)
        nw = sum(1 for r in rep if r.startswith("WARNING"))
        self.report({'WARNING'} if nw else {'INFO'}, rep[-1] + (" (%d warnings, see GearLapping_report)" % nw
                                                                  if nw else ""))
        return {'FINISHED'}


class LAP_OT_delete(bpy.types.Operator):
    bl_idname = "lap.delete_gear"
    bl_label = "Delete Gear"
    bl_description = ("Delete the selected gears with all their elements (a selected pair empty: the whole pair); "
                      "printable copies stay")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        todo = []
        for o in context.selected_objects:
            if "lap_pair_no" in o:
                todo.append(o)
            elif isGear(o) or o.get("lap_part"):
                todo.append(o)
            elif o.parent is not None and (isGear(o.parent) or o.parent.get("lap_part")):
                todo.append(o.parent)
        names = []
        seen = set()
        n = 0
        for o in todo:
            try:
                nm = o.name
            except ReferenceError:
                continue
            if nm in seen:
                continue
            anc, skip = o.parent, False
            while anc is not None:
                if anc in todo:
                    skip = True
                anc = anc.parent
            if skip:
                continue
            seen.add(nm)
            parent = o.parent
            deleteTree(o)
            names.append(nm)
            n += 1
            removeFromPair(parent)
        if not n:
            self.report({'WARNING'}, "select a gear (its empty or an element) or a pair empty")
            return {'CANCELLED'}
        self.report({'INFO'}, "deleted: " + ", ".join(names))
        return {'FINISHED'}


class LAP_OT_rackblank(bpy.types.Operator):
    bl_idname = "lap.rack_blank"
    bl_label = "Blank for Rolling"
    bl_description = ("Rotation - translation: a smooth rack under a gear tool, or a smooth gear over a rack tool "
                      "(teeth / pitches from 'Blank teeth'); becomes the target")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        try:
            if ps.source is None:
                raise LapError("set the tool (source) first")
            if isRack(ps.source):
                g = gearBlankOverRack(context, ps.source, ps.mate_teeth, rep)
            else:
                g = rackBlank(context, ps.source, ps.mate_teeth, rep)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep)
        ps.target = g
        selectOnly(context, g)
        self.report({'INFO'}, rep[-1])
        return {'FINISHED'}


class LAP_OT_blank(bpy.types.Operator):
    bl_idname = "lap.own_blank"
    bl_label = "Create Own Blank"
    bl_description = ("A blank of revolution by its dimensions, placed at the tool (source): axis angle, center "
                      "distance, an optional throat about the tool axis; becomes the target")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        rep = []
        try:
            if ps.source is None:
                raise LapError("set the tool (source) first")
            g = ownBlank(context, ps.source, ps.blank_od, ps.blank_bore, ps.blank_len, ps.blank_angle, ps.blank_dist,
                         ps.blank_throat, sizeModule(ps.source), rep)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        writeReport(rep)
        ps.target = g
        selectOnly(context, g)
        self.report({'INFO'}, "%s: own blank (set as target)" % g.name)
        return {'FINISHED'}


class LAP_PT_gear(bpy.types.Panel):
    # first tab: one gear by its parameters
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gear"
    bl_label = "Gear"

    def draw(self, context):
        ps = context.scene.lap
        lay = self.layout
        box = lay.box()
        box.prop(ps, "g_kind", expand=True)
        k = ps.g_kind
        if k == 'WORM':
            box.prop(ps, "worm_starts")
            box.prop(ps, "worm_q")
            box.prop(ps, "module", text="Axial module")
            box.prop(ps, "worm_length", text="Length (0 = 32 modules)")
            box.label(text="lead angle %.2f deg, pitch d %.4g" % (math.degrees(math.atan2(ps.worm_starts, ps.worm_q)),
                                                                 ps.worm_q * ps.module))
        else:
            box.prop(ps, "teeth")
            box.prop(ps, "module", text="Module (large end)" if k == 'BEVEL' else "Module")
            box.prop(ps, "width")
            if k == 'BEVEL':
                box.prop(ps, "g_delta")
                row = box.row(align=True)
                row.prop(ps, "helix", text="Spiral angle")
                row.prop(ps, "herring", toggle=True)
                if ps.herring and abs(ps.helix) > 1e-9:
                    drawChevron(box, ps, ps.teeth, math.radians(ps.g_delta), ps.width, ps.module)
            else:
                row = box.row(align=True)
                row.prop(ps, "helix")
                row.prop(ps, "herring", toggle=True)
                if k == 'RACK':
                    box.prop(ps, "rack_height")
                    box.label(text="length %.4g, pitch %.4g" % (ps.teeth * math.pi * ps.module, math.pi * ps.module))
                else:
                    cylInfo(box.column(align=True), ps.teeth, ps.module, ps.helix)
            if k == 'RING':
                box.prop(ps, "cutter_teeth")
                box.prop(ps, "ring_rim")
        if k != 'RACK':
            box.prop(ps, "shape")
        if k not in ('RING', 'RACK'):
            drawSeat(box, ps, bevel=(k == 'BEVEL'))
        box.prop(ps, "clearance")
        box.prop(ps, "lowpoly")
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("lap.gear_single", icon='MESH_CYLINDER')
        row.operator("lap.delete_gear", text="", icon='TRASH')
        box.label(text="new: on the axis of the selected gear, next to it" if anchorGear(context) else
                  "new: at the world origin (select a gear to stack on its axis)", icon='INFO')
        drawPrint(lay, context)


class LAP_PT_pair(bpy.types.Panel):
    # second tab: gears in mesh by the parameters of the pair
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Gear Pair"
    bl_label = "Gear Pair"

    def draw(self, context):
        ps = context.scene.lap
        lay = self.layout
        box = lay.box()
        box.prop(ps, "pr_kind", expand=True)
        k = ps.pr_kind
        col = None
        if k in ('EXT', 'INT'):
            box.prop(ps, "pr_z1", text="Pinion teeth" if k == 'INT' else "Teeth 1")
            box.prop(ps, "pr_z2", text="Ring teeth" if k == 'INT' else "Teeth 2")
            box.prop(ps, "pr_module")
            box.prop(ps, "pr_width")
            row = box.row(align=True)
            row.prop(ps, "pr_helix")
            row.prop(ps, "pr_herring", toggle=True)
            col = box.column(align=True)
            a = (ps.pr_z2 - ps.pr_z1 if k == 'INT' else ps.pr_z1 + ps.pr_z2) * ps.pr_module / 2
            col.label(text="center distance %.4g, ratio %.4g" % (a, ps.pr_z2 / float(ps.pr_z1)))
            if k == 'INT' and ps.pr_z2 - ps.pr_z1 < 6:
                col.label(text="the ring needs at least 6 teeth more", icon='ERROR')
        elif k == 'PLANET':
            box.prop(ps, "pr_sun")
            box.prop(ps, "pr_planet")
            box.prop(ps, "pr_planets")
            box.prop(ps, "pr_module")
            box.prop(ps, "pr_width")
            row = box.row(align=True)
            row.prop(ps, "pr_helix")
            row.prop(ps, "pr_herring", toggle=True)
            zr = ps.pr_sun + 2 * ps.pr_planet
            col = box.column(align=True)
            col.label(text="ring %d teeth, carrier radius %.4g" % (zr, (ps.pr_sun + ps.pr_planet) * ps.pr_module / 2))
            col.label(text="ring held: sun : carrier = %.4g" % (1.0 + zr / float(ps.pr_sun)))
            if (ps.pr_sun + zr) % ps.pr_planets:
                col.label(text="(sun + ring) / planets not whole: unequal spacing", icon='ERROR')
            a = (ps.pr_sun + ps.pr_planet) * ps.pr_module / 2
            if ps.pr_planets > 1 and 2 * a * math.sin(math.pi / ps.pr_planets) <= (ps.pr_planet + 2) * ps.pr_module:
                col.label(text="the planets touch each other", icon='ERROR')
        elif k == 'CLOCK':
            box.prop(ps, "pr_z1", text="Wheel teeth")
            box.prop(ps, "pr_z2", text="Pinion leaves")
            box.prop(ps, "pr_module")
            box.prop(ps, "pr_width")
            col = box.column(align=True)
            col.label(text="ratio %d : %d = %.4g, center distance %.4g" % (ps.pr_z1, ps.pr_z2, ps.pr_z1 / float(ps.pr_z2),
                                                                        (ps.pr_z1 + ps.pr_z2) * ps.pr_module / 2))
            box.prop(ps, "clock_bs978")
            if not ps.clock_bs978:
                box.prop(ps, "clock_backlash")
            box.prop(ps, "clock_fillet")
            bl = None if ps.clock_bs978 else ps.clock_backlash
            col = box.column(align=True)
            col.label(text="leaves %.2f m thick, backlash %.2f m (the wheel drives)"
                      % (clockLeaf(ps.pr_z2, bl), math.pi / 2 - clockLeaf(ps.pr_z2, bl)))
            if bl is not None and bl < 0.05:
                col.label(text="below 0.05 m the teeth can touch at the handover", icon='ERROR')
            if ps.pr_z2 < 6:
                col.label(text="fewer than 6 leaves: rough running, check it", icon='ERROR')
        elif k == 'BEVEL':
            box.prop(ps, "pr_z1")
            box.prop(ps, "pr_z2")
            box.prop(ps, "shaft")
            box.prop(ps, "pr_module", text="Module (large end)")
            box.prop(ps, "pr_width")
            row = box.row(align=True)
            row.prop(ps, "pr_helix", text="Spiral angle")
            row.prop(ps, "pr_herring", toggle=True)
            d1, d2 = bevelAngles(ps.pr_z1, ps.pr_z2, ps.shaft)
            if ps.pr_herring and abs(ps.pr_helix) > 1e-9:
                drawChevron(box, ps, ps.pr_z1, d1, ps.pr_width, ps.pr_module)
            col = box.column(align=True)
            col.label(text="pitch cones %.2f + %.2f deg" % (math.degrees(d1), math.degrees(d2)))
            if d2 > math.pi / 2:
                col.label(text="the second gear is internal (a blank)", icon='INFO')
        elif k == 'RACK':
            box.prop(ps, "pr_z1", text="Pinion teeth")
            box.prop(ps, "pr_z2", text="Rack teeth")
            box.prop(ps, "pr_module")
            box.prop(ps, "pr_width")
            row = box.row(align=True)
            row.prop(ps, "pr_helix")
            row.prop(ps, "pr_herring", toggle=True)
            col = box.column(align=True)
            col.label(text="rack length %.4g, %.4g per pinion turn" % (ps.pr_z2 * math.pi * ps.pr_module,
                                                                      ps.pr_z1 * math.pi * ps.pr_module))
            if ps.pr_z1 < 17 and abs(ps.pr_helix) < 1e-9:
                col.label(text="fewer than 17 teeth: the rack undercuts the pinion", icon='ERROR')
        elif k == 'ESCAPE':
            box.prop(ps, "esc_teeth")
            box.prop(ps, "pr_module")
            box.prop(ps, "pr_width")
            row = box.row(align=True)
            row.prop(ps, "esc_lock")
            row.prop(ps, "esc_lift")
            row = box.row(align=True)
            row.prop(ps, "esc_drop")
            row.prop(ps, "esc_draw")
            box.prop(ps, "esc_lever")
            box.prop(ps, "esc_pin")
            row = box.row(align=True)
            row.prop(ps, "pr_bore1", text="Wheel bore r")
            row.prop(ps, "pr_bore2", text="Fork bore r")
            col = box.column(align=True)
            R = ps.esc_teeth * ps.pr_module / 2
            col.label(text="locking circle d %.4g, %.3g deg of the wheel per beat" % (2 * R, 180.0 / ps.esc_teeth))
            col.label(text="fork swings +-%.3g deg between the banking pins (not made)"
                      % ((ps.esc_lock + ps.esc_lift) / 2 + 0.5))
        elif k == 'GRAVITY':
            box.prop(ps, "grav_arm")
            row = box.row(align=True)
            row.prop(ps, "grav_t")
            row.prop(ps, "grav_gap")
            row = box.row(align=True)
            row.prop(ps, "grav_lift")
            row.prop(ps, "grav_unlock")
            row = box.row(align=True)
            row.prop(ps, "pr_bore1", text="Wheel bore r (D)")
            row.prop(ps, "pr_bore2", text="Arm bore r")
            col = box.column(align=True)
            col.label(text="wheel axis %.4g below the pendulum axis; 60 deg per beat" % (0.45 * ps.grav_arm))
            col.label(text="the pendulum must swing more than +-%.2f deg" % (ps.grav_lift + ps.grav_unlock + 0.2))
            col.label(text="arms turn about the pendulum axis (the bend of its spring)", icon='INFO')
        elif k == 'WRACK':
            box.prop(ps, "worm_starts")
            box.prop(ps, "worm_q")
            box.prop(ps, "pr_z2", text="Rack teeth")
            box.prop(ps, "pr_module", text="Axial module")
            box.prop(ps, "pr_width", text="Face width (at most 1.8 (r1 - m))")
            box.prop(ps, "worm_length")
            col = box.column(align=True)
            col.label(text="lead angle %.2f deg, %.4g per worm turn" % (
                math.degrees(math.atan2(ps.worm_starts, ps.worm_q)), ps.worm_starts * math.pi * ps.pr_module))
        else:
            box.prop(ps, "worm_starts")
            box.prop(ps, "worm_q")
            box.prop(ps, "pr_z2", text="Wheel teeth")
            box.prop(ps, "pr_module", text="Axial module")
            box.prop(ps, "worm_length")
            box.prop(ps, "wheel_tol")
            col = box.column(align=True)
            col.label(text="lead angle %.2f deg, ratio %.4g" % (math.degrees(math.atan2(ps.worm_starts, ps.worm_q)),
                                                               ps.pr_z2 / float(ps.worm_starts)))
            col.label(text="center distance %.4g" % ((ps.worm_q + ps.pr_z2) * ps.pr_module / 2))
        if k not in ('CLOCK', 'RACK', 'WRACK', 'ESCAPE', 'GRAVITY'):
            box.prop(ps, "pr_shape", expand=True)
        if k == 'CLOCK':
            box.prop(ps, "clearance", text="Root clearance (modules)")
        elif k not in ('ESCAPE', 'GRAVITY'):
            box.prop(ps, "clearance")
        if k not in ('ESCAPE', 'GRAVITY'):
            drawSeat(box, ps, bevel=(k == 'BEVEL'))
        box.prop(ps, "lowpoly")
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("lap.gear_pair", icon='MESH_CYLINDER')
        row.operator("lap.delete_gear", text="", icon='TRASH')
        box.label(text="new: on the axis of the selected gear, next to it" if anchorGear(context) else
                  "new: at the world origin (select a gear to stack on its axis)", icon='INFO')
        drawPrint(lay, context)


class LAP_OT_belt(bpy.types.Operator):
    bl_idname = "lap.belt_wheel"
    bl_label = "Create"
    bl_description = ("Sprocket or timing pulley at the world origin (on the axis of the selected gear if there is "
                      "one); a pair: two wheels at the center distance a whole number of links or belt teeth gives")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        _LOW[0] = bool(context.scene.lap.lowpoly)
        try:
            return self.run(context)
        finally:
            _LOW[0] = False
            _SEAT[0] = None

    def run(self, context):
        ps = context.scene.lap
        if context.object is not None and context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        anchor = anchorGear(context)
        before = {o.name for o in bpy.data.objects}
        mat = Matrix.Identity(4)
        kind = ps.cb_kind
        custom = None
        if kind == 'CHAIN':
            key = ps.cb_chain
            if key == 'CUSTOM':
                custom = (ps.cb_pitch, ps.cb_roller, ps.cb_inner)
                key = "custom"
        else:
            key = ps.cb_belt
        kw = dict(width=ps.cb_width, flange=ps.cb_flange and kind == 'BELT', flange_ext=ps.cb_flange_ext,
                  flange_t=ps.cb_flange_t, hub_d=ps.cb_hub_d, hub_len=ps.cb_hub_len, hub_both=ps.cb_hub_both,
                  custom=custom)
        rep = []
        t0 = time.time()
        _SEAT[0] = seatSpec(ps)
        try:
            if ps.cb_pair:
                g1, g2, msg = beltPair(context, kind, ps.cb_z1, ps.cb_z2, key, ps.cb_dist, mat, rep, 0.0, 0.0, **kw)
            else:
                g1, info, W = beltWheel(context, kind, ps.cb_z1, key, mat, 0.0, **kw)
                g2 = None
                if kind == 'CHAIN':
                    msg = "%s: %d teeth, pitch %.4g, pitch d %.4g, tip d %.4g, root d %.4g, tooth width %.4g" % (
                        g1.name, ps.cb_z1, g1["lap_pitch"], 2 * info['R'], 2 * info['tip'], 2 * info['root'], W)
                else:
                    msg = "%s: %d teeth, pitch %.4g, pitch d %.4g, outside d %.4g, between the flanges %.4g" % (
                        g1.name, ps.cb_z1, g1["lap_pitch"], info['PD'], info['OD'], W)
        except LapError as e:
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        objs = newTopObjects(before)
        bakeNew(context, objs, rep)
        try:
            seatRings(context, objs, rep)
        except LapError as e:
            for o in objs:
                deleteTree(o)
            rep.append("ERROR: " + str(e))
            writeReport(rep)
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        placeNew(anchor, objs)
        if g2 is not None:
            pe = groupPair(context, objs, "chain" if kind == 'CHAIN' else "belt", g2)
            rep.append(msg + " (%.1f s)" % (time.time() - t0))
            rep.append("pair %d: '%s'%s" % (int(pe["lap_pair_no"]), pe.name,
                                           (", on the axis of %s" % anchor.name) if anchor is not None else ""))
            ps.source, ps.target = g1, g2
            selectOnly(context, pe)
        else:
            rep.append(msg + (" (on the axis of %s)" % anchor.name if anchor is not None else ""))
            ps.source = g1
            selectOnly(context, g1)
        writeReport(rep)
        self.report({'INFO'}, rep[-1] if g2 is not None else msg)
        return {'FINISHED'}


class LAP_PT_belt(bpy.types.Panel):
    # chain sprockets and timing pulleys
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Chain & Belt"
    bl_label = "Chain & Belt"

    def draw(self, context):
        ps = context.scene.lap
        lay = self.layout
        box = lay.box()
        box.prop(ps, "cb_kind", expand=True)
        k = ps.cb_kind
        box.prop(ps, "cb_pair")
        if k == 'CHAIN':
            box.prop(ps, "cb_chain")
            if ps.cb_chain == 'CUSTOM':
                box.prop(ps, "cb_pitch")
                box.prop(ps, "cb_roller")
                box.prop(ps, "cb_inner")
                p, d1, b1 = ps.cb_pitch, ps.cb_roller, ps.cb_inner
            else:
                p, d1, b1 = CHAINS[ps.cb_chain]
        else:
            box.prop(ps, "cb_belt")
            p = BELTS[ps.cb_belt][0]
        box.prop(ps, "cb_z1", text="Teeth 1" if ps.cb_pair else "Teeth")
        if ps.cb_pair:
            box.prop(ps, "cb_z2")
            box.prop(ps, "cb_dist")
        box.prop(ps, "cb_width", text="Tooth width (0 = iso)" if k == 'CHAIN' else "Belt width (0 = usual)")
        col = box.column(align=True)
        for z in ([ps.cb_z1, ps.cb_z2] if ps.cb_pair else [ps.cb_z1]):
            if k == 'CHAIN':
                D = p / math.sin(math.pi / max(z, 3))
                ri = 0.505 * d1 + 0.069 * d1 ** (1.0 / 3.0)
                col.label(text="%d teeth: pitch d %.4g, root d %.4g" % (z, D, D - 2 * ri))
            else:
                P, h, w, form, phi, pld, bw = BELTS[ps.cb_belt]
                PD = z * P / math.pi
                col.label(text="%d teeth: pitch d %.4g, outside d %.4g" % (z, PD, PD - 2 * pld))
        if k == 'BELT':
            row = box.row(align=True)
            row.prop(ps, "cb_flange", toggle=True)
            if ps.cb_flange:
                row.prop(ps, "cb_flange_ext", text="Over teeth")
                row.prop(ps, "cb_flange_t", text="Thick")
        row = box.row(align=True)
        row.prop(ps, "cb_hub_d", text="Hub d")
        row.prop(ps, "cb_hub_len", text="Length")
        box.prop(ps, "cb_hub_both")
        drawSeat(box, ps)
        box.prop(ps, "lowpoly")
        row = box.row(align=True)
        row.scale_y = 1.3
        row.operator("lap.belt_wheel", icon='MESH_CYLINDER')
        row.operator("lap.delete_gear", text="", icon='TRASH')
        box.label(text="new: on the axis of the selected gear, next to it" if anchorGear(context) else
                  "new: at the world origin (select a gear to stack on its axis)", icon='INFO')
        if k == 'BELT':
            box.label(text="groove sizes after common open tables: print a test strip first", icon='ERROR')
        drawPrint(lay, context)


class LAP_PT_lapping(bpy.types.Panel):
    # third tab: blanks and rolling - a tool (any gear or own body), a blank, the ratio, the imprint
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lapping"
    bl_label = "Lapping"

    def draw(self, context):
        ps = context.scene.lap
        lay = self.layout
        lay.prop(ps, "motion", expand=True)
        trans = ps.motion == 'TRANS'
        box = lay.box()
        box.label(text="Tool")
        row = box.row(align=True)
        row.prop(ps, "source", text="Tool")
        row.operator("lap.set_active", text="", icon='EYEDROPPER').role = "source"
        box.operator("lap.make_gear", icon='EMPTY_SINGLE_ARROW')
        box = lay.box()
        box.label(text="Blank")
        if trans:
            col = box.column(align=True)
            rk = isRack(ps.source)
            col.label(text="smooth gear over the rack:" if rk else "smooth rack under the gear:")
            col.prop(ps, "mate_teeth", text="Gear teeth" if rk else "Rack pitches")
            col.operator("lap.rack_blank", icon='ADD')
            row = box.row(align=True)
            row.prop(ps, "target", text="Blank")
            row.operator("lap.set_active", text="", icon='EYEDROPPER').role = "target"
            box.operator("lap.swap", text="Swap Tool and Blank", icon='ARROW_LEFTRIGHT')
            box = lay.box()
            box.label(text="Rolling")
            box.label(text="Method: one section, the rack moves by the rolling radius", icon='INFO')
            if ps.source is not None and ps.target is not None and not (isRack(ps.source) or isRack(ps.target)):
                box.label(text="the tool or the blank must be a rack", icon='ERROR')
            box.prop(ps, "steps")
            box.prop(ps, "substeps")
            box.prop(ps, "pressure_limit")
            if not isRack(ps.target):
                box.prop(ps, "relief")
                box.prop(ps, "simple")
            box.prop(ps, "clearance")
            box.prop(ps, "direction")
            box.operator("lap.imprint", icon='MOD_BOOLEAN')
            drawGap(lay, ps)
            drawPrint(lay, context)
            return
        col = box.column(align=True)
        col.label(text="by teeth, in mesh with the tool:")
        col.prop(ps, "mate_teeth")
        col.prop(ps, "mate_internal")
        if ps.source is not None and not isBevel(ps.source):
            col.prop(ps, "mate_cross")
        row = col.row(align=True)
        row.operator("lap.create_mating", text="Mating Blank", icon='ADD')
        if ps.source is not None and not isBevel(ps.source):
            row.operator("lap.create_face", text="Face Blank", icon='MESH_CIRCLE')
        col = box.column(align=True)
        col.label(text="by dimensions (own body):")
        row = col.row(align=True)
        row.prop(ps, "blank_od")
        row.prop(ps, "blank_bore")
        col.prop(ps, "blank_len")
        row = col.row(align=True)
        row.prop(ps, "blank_angle")
        row.prop(ps, "blank_dist")
        col.prop(ps, "blank_throat")
        col.operator("lap.own_blank", icon='MESH_CYLINDER')
        row = box.row(align=True)
        row.prop(ps, "target", text="Blank")
        row.operator("lap.set_active", text="", icon='EYEDROPPER').role = "target"
        box.operator("lap.swap", text="Swap Tool and Blank", icon='ARROW_LEFTRIGHT')
        box = lay.box()
        box.label(text="Rolling")
        method = methodOf(ps.source, ps.target)
        if method:
            box.label(text={'SECTION': "Method: one section (exact; helical teeth twisted)",
                            'SLICES': "Method: slices across the face width",
                            'MERIDIAN': "Method: meridian sections (own body, exact)",
                            'BOOLEAN': "Method: booleans (foreign target)",
                            'RACK': "a rack: switch to rotation - translation"}[method], icon='INFO')
        box.prop(ps, "ratio_auto")
        if not ps.ratio_auto:
            row = box.row(align=True)
            row.prop(ps, "ratio_tool")
            row.prop(ps, "ratio_blank")
        box.prop(ps, "blank_slow")
        if ps.target is not None and ps.source is not None and ps.source != ps.target \
                and "lap_teeth" in ps.source and "lap_teeth" in ps.target:
            R, cyc, o, g = ratioText(ps, ps.source, ps.target)
            col = box.column(align=True)
            col.label(text="tool : blank = %d : %d turns, cycle %d blank turn(s)" % (R.numerator, R.denominator, cyc))
            zt_ = int(ps.target["lap_teeth"])
            if g > 1:
                col.label(text=("the worm is rebuilt with %d starts" if ps.target.get("lap_worm") else
                                "the blank would get %d teeth: not possible") % o, icon='ERROR')
            elif o > zt_:
                col.label(text="the blank repeats %d times per element" % (o // zt_), icon='INFO')
        if method == 'SLICES':
            box.prop(ps, "lap_mode", expand=True)
            if ps.lap_mode == 'PRESS':
                row = box.row(align=True)
                row.prop(ps, "press_clearance")
                row.prop(ps, "press_end")
        box.prop(ps, "steps")
        box.prop(ps, "substeps")
        if method == 'MERIDIAN' or (ps.target is not None and ps.target.get("lap_worm")):
            box.prop(ps, "meridian_step")
        if method == 'SLICES':
            row = box.row(align=True)
            row.prop(ps, "slices", text="Slices")
            if not isBevel(ps.target):
                row.prop(ps, "slice_family", text="")
            box.prop(ps, "remesh")
        if method == 'SLICES':
            box.prop(ps, "extend")
        if method in ('SLICES', 'BOOLEAN'):
            box.prop(ps, "smooth")
        if method != 'BOOLEAN':
            box.prop(ps, "pressure_limit")
            box.prop(ps, "relief")
            box.prop(ps, "clearance")
            box.prop(ps, "simple")
        box.prop(ps, "direction")
        box.operator("lap.imprint", icon='MOD_BOOLEAN')
        box.operator("lap.reverse_blank", icon='FILE_REFRESH')
        drawGap(lay, ps)
        drawPrint(lay, context)


CLASSES = (LAP_Props, LAP_OT_new, LAP_OT_single, LAP_OT_pair, LAP_OT_blank, LAP_OT_rackblank, LAP_OT_delete, LAP_OT_mate, LAP_OT_face, LAP_OT_set,
           LAP_OT_swap, LAP_OT_imprint, LAP_OT_reverse, LAP_OT_print, LAP_OT_offset, LAP_OT_offset_restore, LAP_OT_overhang, LAP_OT_export, LAP_OT_gap, LAP_OT_make, LAP_OT_belt,
           LAP_PT_gear, LAP_PT_pair, LAP_PT_belt, LAP_PT_lapping)


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)
    bpy.types.Scene.lap = bpy.props.PointerProperty(type=LAP_Props)


def unregister():
    del bpy.types.Scene.lap
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
