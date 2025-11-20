package com.ricardopiccoli.ja;

import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.evaluation.RelevancyEvaluator;
import org.springframework.ai.document.Document;
import org.springframework.ai.evaluation.EvaluationRequest;
import org.springframework.ai.evaluation.EvaluationResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class HelloTest {
    private static final Logger LOG = LoggerFactory.getLogger(HelloTest.class);

    @Autowired
    private Hello hello;

    @Autowired
    private ChatClient.Builder chatClientBuilder;

    @Test
    void testThatHelloWorks() {
        var response = hello.sayHello("Ricardo");
        Assertions.assertThat(response).isNotNull();
        var text = response.getResult().getOutput().getText();
        LOG.info(text);
        Assertions.assertThat(text).isNotNull();
        Assertions.assertThat(text.trim()).isEqualTo("Hello Ricardo");
    }

    @Test
    void testHelloEvaluation() {
        String prompt = "Ricardo";
        var response = hello.sayHello(prompt);
        Assertions.assertThat(response).isNotNull();
        EvaluationRequest evaluationRequest = new EvaluationRequest(
                prompt,
                List.of(Document.builder().text("Hello Ricardo").build()), //TODO learn how to instruct the evaluator
                response.getResult().getOutput().getText()
        );
        RelevancyEvaluator evaluator = new RelevancyEvaluator(chatClientBuilder);
        EvaluationResponse evaluationResponse = evaluator.evaluate(evaluationRequest);
        LOG.info("Evaluation response: {}", evaluationResponse);
        assertThat(evaluationResponse.isPass()).isTrue();
    }
}
