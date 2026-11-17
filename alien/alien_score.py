import json, sys, random, itertools, statistics as st
import numpy as np
# pool <atoms.json> <communities.json> [n=50] | add <pool.json> <communities.json> <neighbors.json>
# fuse <pool.json> <coherence.json> [beta=0.7] | div <final.json>
# atoms.json: [{"id":"A1","name":"..."}]   communities.json: {"community": {"A1":1.0,"A7":0.5}}
# coherence.json: {"A1|A4|A9": 4}   final.json: [["A1","A4","A9"], ...]
cmd = sys.argv[1]
def avail(S, comms, m):
    reach = sorted((sum(r.get(a, 0) for a in S) / len(S) for r in comms.values()), reverse=True)
    return st.median(reach[:m])
if cmd == "pool":
    atoms = [a["id"] for a in json.load(open(sys.argv[2]))]
    comms = json.load(open(sys.argv[3])); n = int(sys.argv[4]) if len(sys.argv) > 4 else 50
    m = min(5, max(1, len(comms) // 2))
    tri = sorted(((avail(S, comms, m), S) for S in itertools.combinations(atoms, 3)))
    cut = int(len(tri) * 0.3); low, rest = tri[:cut], tri[cut:]
    random.seed(0); random.shuffle(low); random.shuffle(rest)
    use, pool, cap = {}, [], max(3, -(-3 * n // len(atoms)) + 1)
    def take(src, k):
        got = 0
        for A, S in src:
            if got >= k: break
            if all(use.get(a, 0) < cap for a in S):
                pool.append((A, S)); got += 1
                for a in S: use[a] = use.get(a, 0) + 1
    take(low, int(n * 0.7)); take(rest, n - len(pool))
    out = [{"atoms": list(S), "key": "|".join(S), "A": round(A, 3)} for A, S in pool]
    json.dump(out, open("pool.json", "w"), indent=1)
    print(f"{len(tri)} triples scored, m={m}; wrote {len(out)} to pool.json")
elif cmd == "add":
    pool = json.load(open(sys.argv[2])); comms = json.load(open(sys.argv[3]))
    m = min(5, max(1, len(comms) // 2)); have = {p["key"] for p in pool}
    for S in json.load(open(sys.argv[4])):
        S = sorted(S, key=lambda a: int(a[1:])); k = "|".join(S)
        if k not in have: pool.append({"atoms": S, "key": k, "A": round(avail(S, comms, m), 3)}); have.add(k)
        print(f'{k}  A={avail(S, comms, m):.2f}')
    json.dump(pool, open(sys.argv[2], "w"), indent=1)
elif cmd == "fuse":
    pool = json.load(open(sys.argv[2])); C = json.load(open(sys.argv[3]))
    beta = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
    pool = [p for p in pool if p["key"] in C]
    z = lambda v: (np.array(v) - np.mean(v)) / (np.std(v) or 1)
    zc, zu = z([C[p["key"]] for p in pool]), z([-p["A"] for p in pool])
    for p, c, u in zip(pool, zc, zu):
        p["C"] = C[p["key"]]; p["F"] = round((1 - beta) * c + beta * u, 3)
    keep = sorted([p for p in pool if p["C"] >= 3], key=lambda p: -p["F"])
    for p in keep[:15]: print(f'{p["F"]:+.2f}  C={p["C"]}  A={p["A"]:.2f}  {p["key"]}')
elif cmd == "div":
    S = [set(s) for s in json.load(open(sys.argv[2]))]; n = len(S)
    K = np.array([[len(a & b) / len(a | b) for b in S] for a in S])
    lam = np.linalg.eigvalsh(K / n); lam = lam[lam > 1e-12]
    flat = [a for s in S for a in s]; p = np.array([flat.count(a) for a in set(flat)]) / len(flat)
    near = sum(any(len(S[i] & S[j]) >= 2 for j in range(n) if j != i) for i in range(n))
    print(f"Vendi={np.exp(-(lam*np.log(lam)).sum()):.2f}/{n}  eff_atoms={np.exp(-(p*np.log(p)).sum()):.1f}  near_dup={near}/{n}")
