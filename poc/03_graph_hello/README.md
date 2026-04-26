# PoC 03 — QGraphicsView Hello Graph

```bash
uv run python poc/03_graph_hello/run.py
```

생성물:

- `poc/03_graph_hello/artifacts/graph_hello.png`

Acceptance evidence:

- `graph_hello.png` 에 3개 컨테이너 노드, 5개 멤버 노드, 실선 오렌지/점선 블루 엣지, 회색 해치 unsolved 노드가 함께 저장된다.
- `src/sourcetrail_remake/ui/graph/view.py` 의 wheel/middle-drag 구현으로 zoom/pan 상호작용을 확인할 수 있다.
