package com.ricardopiccoli.ja;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.model.Generation;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.lang.Nullable;
import org.springframework.stereotype.Component;

import java.util.Optional;

@Component
public class Hello implements CommandLineRunner {
    private static final Logger LOG = LoggerFactory.getLogger(Hello.class);

    private final ChatClient chatClient;

    @Autowired
    public Hello(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder
                .defaultSystem("""
                    Don't answer any question, simply greet the caller with 'Hello' mentioning their name
                    if known, without any additional markup or syntax
                """)
                .build();
    }

    @Nullable
    public ChatResponse sayHello(String prompt) {
        return chatClient
                .prompt(prompt)
                .call()
                .chatResponse();
    }

    @Override
    public void run(String... args) throws Exception {
         var text = Optional.ofNullable(sayHello("World"))
                 .map(ChatResponse::getResult)
                 .map(Generation::getOutput)
                 .map(AssistantMessage::getText)
                 .orElse("FAIL");
        LOG.info(text);
    }
}
