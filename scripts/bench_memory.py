"""Phase 1 perf gate: 1000 episodes insert+query < 100 ms total."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

# Allow direct execution: add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from robomind.core.models import Episode, Fact
from robomind.memory import cbr
from robomind.memory.store import SQLiteMemoryStore


def main() -> None:
    with TemporaryDirectory() as td:
        store = SQLiteMemoryStore(Path(td) / "bench.db")

        t0 = time.perf_counter()
        for i in range(1000):
            store.insert_episode(Episode(input=f"design arm {i} x={i} y={i*2}",
                                         intent="design.arm"))
        t_insert = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        for _ in range(50):
            store.search_episodes("arm", limit=10)
        t_query = (time.perf_counter() - t0) * 1000 / 50

        t0 = time.perf_counter()
        cbr.similar_episodes(store, "design arm reaching x y", k=3)
        t_cbr = (time.perf_counter() - t0) * 1000

        for i in range(200):
            store.insert_fact(Fact(topic="servo", fact=f"fact {i}"))

        size = (Path(td) / "bench.db").stat().st_size / 1024

        print(f"1000 episode inserts : {t_insert:6.1f} ms")
        print(f"single FTS query     : {t_query:6.2f} ms")
        print(f"CBR (single)         : {t_cbr:6.2f} ms")
        print(f"DB size              : {size:6.1f} KB")

        store.close()


if __name__ == "__main__":
    main()