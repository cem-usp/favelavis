# cubo_svg.py
import math
import numpy as np
import svgwrite

# ========= PROJEÇÃO =========
# Oblíqua "cabinet": XZ é a face frontal (y=0 sem distorção).
# Linhas de profundidade (eixo Y) recuam com ângulo theta e escala lambda.
def project_oblique(p, theta_deg=45.0, lam=0.5, scale=160, ox=150, oy=120):
    x, y, z = p
    th = math.radians(theta_deg)
    u = x + lam * y * math.cos(th)      # eixo X horizontal; Y recua p/ direita
    v = z - lam * y * math.sin(th)      # eixo Z "pra cima"; Y inclina o topo
    # manda pro viewport (escala e translada; inverte Y p/ SVG subir)
    return (ox + scale*u, oy - scale*v)

# (Alternativa isométrica ortográfica — se quiser trocar:)
def project_isometric(p, scale=140, ox=150, oy=120):
    ax = math.radians(35.26438968)
    ay = math.radians(45.0)
    Rx = np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
    Ry = np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
    x,y,z = p
    v3 = np.array([x,y,z])
    X = Ry @ (Rx @ v3)
    u,v = X[0], X[2]  # "drop Z" → uso (x,z) p/ tela
    return (ox + scale*u, oy - scale*v)

# ========= GEOMETRIA DO CUBO =========
# Cubo unitário: 0..1 em cada eixo
O   = (0,0,0)
X   = (1,0,0)
Y   = (0,1,0)
Z   = (0,0,1)
XY  = (1,1,0)
XZ  = (1,0,1)
YZ  = (0,1,1)
XYZ = (1,1,1)

# Faces (cada uma com 4 vértices em ordem CCW)
# Face frontal (XZ): y=0
FACE_XZ = [ O, X, XZ, Z ]
# Face direita (paralela a YZ): x=1
FACE_YZ = [ X, XY, XYZ, XZ ]
# Face superior (paralela a XY): z=1
FACE_XY = [ Z, XZ, XYZ, YZ ]

def proj_face(face, proj):
    return [proj(p) for p in face]

# ========= TRANSFORMAÇÃO AFIM: QUADRADO LOCAL 0..1 → PARALelogramo DA FACE =========
def svg_matrix_from_face(poly2d):
    # poly2d: [p0, p1, p2, p3] CCW; e1 = p1 - p0; e2 = p3 - p0
    p0, p1, p2, p3 = poly2d
    e1x, e1y = (p1[0]-p0[0], p1[1]-p0[1])
    e2x, e2y = (p3[0]-p0[0], p3[1]-p0[1])
    a,b,c,d,e,f = e1x, e1y, e2x, e2y, p0[0], p0[1]
    return f"matrix({a:.4f} {b:.4f} {c:.4f} {d:.4f} {e:.4f} {f:.4f})"

# ========= LETRAS COMO "SÓ LINHAS" EM COORDENADAS LOCAIS (0..1) =========
def glyph_F():
    # haste + dois traços; tudo em [0..1]
    return [
        (0.35,0.20, 0.35,0.85),
        (0.25,0.20, 0.70,0.20),
        (0.30,0.50, 0.62,0.50),
    ]

def glyph_plus():
    return [
        (0.50,0.25, 0.50,0.75),
        (0.25,0.50, 0.75,0.50),
    ]

def glyph_t():
    return [
        (0.25,0.35, 0.75,0.35),
        (0.50,0.35, 0.50,0.80),
    ]

def add_glyph(dwg, poly2d, segments, stroke="currentColor", stroke_width=2, margin=0.10, scale_local=0.80):
    # mapeia (u,v) locais → (x,y) da face via <g transform="matrix(...)">
    mat = svg_matrix_from_face(poly2d)
    g = dwg.g(fill="none", stroke=stroke, stroke_width=stroke_width,
              stroke_linecap="round", stroke_linejoin="round",
              transform=mat)
    for (x1,y1,x2,y2) in segments:
        u1, v1 = margin + scale_local*x1, margin + scale_local*y1
        u2, v2 = margin + scale_local*x2, margin + scale_local*y2
        g.add(dwg.line(start=(u1,v1), end=(u2,v2)))
    dwg.add(g)

# ========= DESENHO =========
def main():
    proj = project_oblique  # (ou troque para project_isometric)
    dwg = svgwrite.Drawing("cubo.svg", size=("300","220"), viewBox="0 0 300 220")

    stroke = "currentColor"

    # Projeta faces
    poly_xz = proj_face(FACE_XZ, proj)
    poly_yz = proj_face(FACE_YZ, proj)
    poly_xy = proj_face(FACE_XY, proj)

    # Arestas das 3 faces (só linhas)
    for poly in (poly_xz, poly_yz, poly_xy):
        dwg.add(dwg.polygon(points=poly, fill="none", stroke=stroke, stroke_width=2))

    # Linhas de união (opcionais) para dar leitura espacial
    # (diagonais internas entre faces adjacentes)
    # p3 de XZ conecta com p0 de XY etc.
    # (mantive mínimo para não poluir)
    
    # Letras "coladas" às faces:
    add_glyph(dwg, poly_xz, glyph_F(), stroke_width=2)     # F na face XZ (frontal)
    add_glyph(dwg, poly_yz, glyph_t(), stroke_width=2)     # t na face YZ (direita)
    add_glyph(dwg, poly_xy, glyph_plus(), stroke_width=2)  # + no topo XY

    # Trilhos de movimento (linhas paralelas ao eixo X)
    # ao longo da aresta vertical esquerda da face XZ: (x=0,y=0,z in [0,1])
    def P(z): return proj((0,0,z))
    # três linhas com comprimentos decrescentes e opacidade crescente (rastro)
    for z, L, alpha in [(0.25, 28, 0.35), (0.55, 20, 0.55), (0.80, 12, 0.75)]:
        cx, cy = P(z)
        x1, x2 = cx - 34, cx - 34 + L
        dwg.add(dwg.line(start=(x1,cy), end=(x2,cy),
                         stroke=stroke, stroke_width=2,
                         opacity=alpha, stroke_linecap="round"))

    dwg.save()
    print("OK → gerado: cubo.svg")

if __name__ == "__main__":
    main()
