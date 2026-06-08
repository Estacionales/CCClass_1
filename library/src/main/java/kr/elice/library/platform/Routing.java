package kr.elice.library.platform;

import java.util.Map;

/**
 * 라우팅 공통 규약입니다. 모듈 모드(legacy|new)와 종류(Book·Member·Loan)로 빈 이름을
 * 만들어 활성 구현을 고릅니다.
 *
 * <p>빈 이름 규약은 "{legacy|new}{Kind}Service" 입니다. 예를 들어 도서의 신규 구현은
 * newBookService 입니다. 신규 구현 클래스 이름을 NewBookService 로 두면 스프링 기본
 * 빈 이름이 newBookService 가 되어 자동으로 선택됩니다.</p>
 */
final class Routing {

    private Routing() {}

    static <T> T pick(Map<String, T> impls, String mode, String kind) {
        boolean toNew = "new".equalsIgnoreCase(mode == null ? "" : mode.trim());
        String beanName = (toNew ? "new" : "legacy") + kind + "Service";
        T impl = impls.get(beanName);
        if (impl == null) {
            throw new IllegalStateException(
                    kind + " 모듈이 " + (toNew ? "new" : "legacy") + " 로 지정됐지만 '" + beanName
                    + "' 빈이 없습니다. springboot 패키지에 " + (toNew ? "New" : "Legacy") + kind
                    + "Service 를 만들어 주세요.");
        }
        return impl;
    }
}
