# PoC 02 — PyQt6 + QScintilla Hello Editor

```bash
uv run python poc/02_editor_hello/run.py
```

생성물:

- `poc/02_editor_hello/artifacts/editor_hello.png`
- `poc/02_editor_hello/artifacts/editor_saved_copy.py`

Acceptance evidence:

- `editor_hello.png` 에서 QScintilla 위젯, Python 렉서 하이라이팅, 줄 번호/폴딩 마진을 확인할 수 있다.
- `editor_saved_copy.py` 로 파일 저장 경로가 동작함을 남긴다.
- 상태바의 cursor 텍스트는 커서 아래 식별자 좌표/텍스트 추적을 보여준다.
