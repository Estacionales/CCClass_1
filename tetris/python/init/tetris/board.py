"""테트리스 보드의 줄 삭제 규칙(AC-3·AC-4) 핵심 도메인입니다.

보드는 위에서 아래로 쌓인 행 리스트이며(index 0 = 맨 위), 각 행은 칸 튜플입니다(0=빈칸, 1=채움).
"""


def is_full(row):
    """한 줄의 모든 칸이 채워졌는지 판정합니다."""
    return all(cell == 1 for cell in row)


def clear_full_lines(rows, width):
    """AC-3·AC-4: 가득 찬 줄을 지우고 윗줄을 내립니다. (새 보드, 지운 줄 수) 를 돌려줍니다.

    TODO(T2·T3) 명세대로 구현하세요.
      - 힌트 T2: is_full(row) 로 각 줄이 가득 찼는지 판정합니다.
      - 힌트 T3: 가득 찬 줄을 빼고, 뺀 수만큼 맨 앞(위)에 빈 줄을 넣어 윗줄을 내립니다.
    """
    raise NotImplementedError("TODO: clear_full_lines 를 구현하세요")
