package com.datasense.tetris;

import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;

/** 명세(sdd/01_planning/tetris_spec.md)의 수용기준을 통과하는 테스트입니다. */
class BoardTest {

    private static boolean[] row(int... cells) {
        boolean[] r = new boolean[cells.length];
        for (int i = 0; i < cells.length; i++) {
            r[i] = cells[i] == 1;
        }
        return r;
    }

    @Test // AC-3: 한 줄이 가득 차면 지워지고 위 블록이 내려온다
    void clearsSingleFullLine() {
        List<boolean[]> rows = new ArrayList<>(List.of(
                row(0, 0, 0),
                row(1, 0, 0),
                row(1, 1, 1)));
        Board board = new Board(3, rows);

        int cleared = board.clearFullLines();

        assertEquals(1, cleared);
        assertEquals(3, board.rows().size());
        assertArrayEquals(row(1, 0, 0), board.rows().get(2)); // 위 블록이 한 칸 내려옴
        assertArrayEquals(row(0, 0, 0), board.rows().get(0)); // 맨 위는 빈 줄
    }

    @Test // AC-4: 여러 줄이 동시에 가득 차면 함께 지워진다
    void clearsMultipleFullLines() {
        List<boolean[]> rows = new ArrayList<>(List.of(
                row(1, 0, 1),
                row(1, 1, 1),
                row(1, 1, 1)));
        Board board = new Board(3, rows);

        assertEquals(2, board.clearFullLines());
        assertArrayEquals(row(1, 0, 1), board.rows().get(2));
    }

    @Test // 가득 찬 줄이 없으면 보드는 그대로다
    void noFullLineKeepsBoard() {
        List<boolean[]> rows = new ArrayList<>(List.of(row(1, 0, 0), row(0, 1, 0)));
        Board board = new Board(3, rows);

        assertEquals(0, board.clearFullLines());
        assertEquals(2, board.rows().size());
    }
}
