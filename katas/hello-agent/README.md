# Hello Agent

## Goal

Show that the using PydanticAI Agent with Google Gemini or Claude works and is configured correctly

## Steps

1. Run katas and select the `hello-agent` kata


## Java

brew install openjdk@21
brew tap spring-io/tap
brew install spring-boot
spring init -d=spring-ai-google-genai --groupId=com.ricardopiccoli --java-version=21 springaitest
cd springaitest
./gradlew build
./gradlew test
./gradlew bootRun
