package kr.elice.library.acceptance;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import kr.elice.library.platform.LibraryApplication;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

/**
 * 도서관 수용기준 테스트입니다. 이 테스트가 실습의 채점기이자 멱등성의 근거입니다.
 *
 * <p>모든 호출은 앞단 컨트롤러(라우터 경유)를 통과합니다. 그래서 migration.properties
 * 가 legacy 를 가리키든 new 를 가리키든, 또는 모듈별로 섞여 있든, 같은 수용기준을
 * 통과해야 합니다. 전환 전(legacy)과 후(new) 모두 이 테스트가 green 이어야 합니다.</p>
 */
@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = LibraryApplication.class)
class LibraryAcceptanceTest {

    @Autowired
    private WebApplicationContext wac;

    private MockMvc mvc;
    private final ObjectMapper om = new ObjectMapper();

    @BeforeEach
    void setUp() {
        this.mvc = MockMvcBuilders.webAppContextSetup(wac).build();
    }

    private JsonNode postJson(String url, String body, HttpStatus expect) throws Exception {
        MvcResult res = mvc.perform(post(url).contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().is(expect.value())).andReturn();
        String content = res.getResponse().getContentAsString();
        return content.isEmpty() ? om.createObjectNode() : om.readTree(content);
    }

    private String newMember(String name) throws Exception {
        return postJson("/members", "{\"name\":\"%s\"}".formatted(name), HttpStatus.CREATED).get("id").asText();
    }

    private String newBook(String title) throws Exception {
        return postJson("/books", "{\"title\":\"%s\"}".formatted(title), HttpStatus.CREATED).get("id").asText();
    }

    private void borrow(String memberId, String bookId, int daysUntilDue, HttpStatus expect) throws Exception {
        postJson("/loans", "{\"memberId\":\"%s\",\"bookId\":\"%s\",\"daysUntilDue\":%d}"
                .formatted(memberId, bookId, daysUntilDue), expect);
    }

    @Test
    @DisplayName("정상 흐름: 회원·도서를 만들고 대출·반납이 동작한다")
    void healthyFlow() throws Exception {
        String m = newMember("김회원");
        String b = newBook("클린 아키텍처");
        JsonNode loan = postJson("/loans", "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(m, b),
                HttpStatus.CREATED);
        assertThat(loan.get("memberId").asText()).isEqualTo(m);
        postJson("/loans/" + loan.get("id").asText() + "/return", "", HttpStatus.OK);
    }

    @Test
    @DisplayName("AC-1: 대출 한도 5권을 넘기면 여섯 번째 대출이 거부된다")
    void ac1_loanLimit() throws Exception {
        String m = newMember("한도회원");
        for (int i = 1; i <= 5; i++) {
            borrow(m, newBook("책" + i), 14, HttpStatus.CREATED);
        }
        // 여섯 번째는 한도 초과로 거부
        JsonNode fail = postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(m, newBook("책6")),
                HttpStatus.CONFLICT);
        assertThat(fail.get("code").asText()).isEqualTo("LOAN_LIMIT_EXCEEDED");
    }

    @Test
    @DisplayName("AC-2: 연체 중인 회원은 새 대출이 거부된다")
    void ac2_overdueBlocks() throws Exception {
        String m = newMember("연체회원");
        // 기한이 지난(연체) 대출 한 건을 보유 (daysUntilDue 음수)
        borrow(m, newBook("연체된 책"), -3, HttpStatus.CREATED);
        // 정상 대출 시도 → 연체로 거부
        JsonNode fail = postJson("/loans",
                "{\"memberId\":\"%s\",\"bookId\":\"%s\"}".formatted(m, newBook("새 책")),
                HttpStatus.CONFLICT);
        assertThat(fail.get("code").asText()).isEqualTo("OVERDUE_EXISTS");
    }
}