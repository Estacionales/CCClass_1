package kr.elice.shop.shared;

import java.util.List;

public record Page<T>(List<T> content, int page, int size, long totalElements) {

    public static <T> Page<T> of(List<T> content, int page, int size, long totalElements) {
        return new Page<>(content, page, size, totalElements);
    }

    public int totalPages() {
        if (size <= 0) {
            return 0;
        }
        return (int) Math.ceil((double) totalElements / size);
    }
}
