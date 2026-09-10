"""Original Haldane quadrature kernel, extracted without formula changes."""
import numpy as np

T2 = 1.0 / 3.0

DC = 3 * np.sqrt(3) * T2

MEASURE = 2 / (3 * np.sqrt(3))

B1 = np.array([2 * np.pi / np.sqrt(3), -2 * np.pi / 3])

B2 = np.array([0, 4 * np.pi / 3])

DELTA = np.array([[0, 1], [-np.sqrt(3) / 2, -.5], [np.sqrt(3) / 2, -.5]])

RHO = np.array([DELTA[1] - DELTA[2], DELTA[2] - DELTA[0], DELTA[0] - DELTA[1]])

def components(k):
    kd, kr = k @ DELTA.T, k @ RHO.T
    d = np.stack([np.cos(kd).sum(-1), -np.sin(kd).sum(-1),
                  -2 * T2 * np.sin(kr).sum(-1)], axis=-1)
    dx = np.stack([-np.sin(kd) @ DELTA[:, 0],
                   -np.cos(kd) @ DELTA[:, 0],
                   -2 * T2 * np.cos(kr) @ RHO[:, 0]], axis=-1)
    dy = np.stack([-np.sin(kd) @ DELTA[:, 1],
                   -np.cos(kd) @ DELTA[:, 1],
                   -2 * T2 * np.cos(kr) @ RHO[:, 1]], axis=-1)
    return d, dx, dy

class Mesh:
    def __init__(self, n, shift=.5):
        self.n, self.shift = n, shift
        u, v = np.meshgrid((np.arange(n) + shift) / n,
                           (np.arange(n) + shift) / n, indexing="ij")
        k = u.ravel()[:, None] * B1 + v.ravel()[:, None] * B2
        d, dx, dy = components(k)
        cross = np.cross(dx, dy)
        self.r2 = d[:, 0] ** 2 + d[:, 1] ** 2
        self.z0 = d[:, 2]
        self.dot0 = np.sum(d * cross, axis=1)
        self.cross_z = cross[:, 2]

    def geometry(self, g):
        mass = DC * g
        E = np.sqrt(self.r2 + (self.z0 + mass) ** 2)
        if E.min() < 1e-13:
            raise ValueError("Mesh hits a degeneracy: use a shifted mesh, not regularization.")
        # Im[<1|Hx|2><2|Hy|1>]/(2E) = -d.(dx cross dy)/(2E^2).
        W = -(self.dot0 + mass * self.cross_z) / (2 * E ** 2)
        return E, W

    def moments(self, g, temperatures):
        E, W = self.geometry(g)
        result = []
        for T in temperatures:
            if T == 0:
                q = np.ones_like(E)
                P = q
            else:
                q = np.tanh(E / (2 * T))
                P = (1 + q * q) / 2
            I = MEASURE * np.mean(q * W)
            M = MEASURE * np.mean(P * W)
            U = MEASURE * np.mean((q if T == 0 else q * np.tanh(E / T)) * W)
            D = MEASURE * np.mean((.5 * (1 - q) ** 2) * W)
            np.testing.assert_allclose(M - I, D, atol=2e-15, rtol=2e-12)
            result.append([I, M, U, D])
        return np.array(result)

    def chern(self, g):
        E, W = self.geometry(g)
        # Omega_text = 2B = W/E; C_text = 2*pi int[dk] Omega_text.
        return 2 * np.pi * MEASURE * np.mean(W / E)

def eigenvector_check():
    rng = np.random.default_rng(43872)
    k = rng.random((256, 1)) * B1 + rng.random((256, 1)) * B2
    d, dx, dy = components(k)
    d[:, 2] += DC * 1.013
    pauli = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]])
    H = np.einsum("na,aij->nij", d, pauli)
    Hx = np.einsum("na,aij->nij", dx, pauli)
    Hy = np.einsum("na,aij->nij", dy, pauli)
    eps, V = np.linalg.eigh(H)
    hx = np.einsum("nai,nab,nbj->nij", V.conj(), Hx, V)
    hy = np.einsum("nai,nab,nbj->nij", V.conj(), Hy, V)
    direct = np.imag(hx[:, 0, 1] * hy[:, 1, 0]) / (eps[:, 1] - eps[:, 0])
    E = np.linalg.norm(d, axis=1)
    analytic = -np.sum(d * np.cross(dx, dy), axis=1) / (2 * E ** 2)
    np.testing.assert_allclose(analytic, direct, atol=2e-13, rtol=2e-12)
    h = 1e-5
    finite_dx = (components(k + [h, 0])[0] - components(k - [h, 0])[0]) / (2 * h)
    np.testing.assert_allclose(dx, finite_dx, atol=1e-9, rtol=1e-8)
    return float(np.max(np.abs(analytic - direct)))
