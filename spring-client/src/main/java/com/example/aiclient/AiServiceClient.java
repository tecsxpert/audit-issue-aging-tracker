package com.example.aiclient;

import java.net.URI;
import java.time.Duration;
import java.util.Map;
import java.util.Objects;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.lang.NonNull;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.DefaultUriBuilderFactory;

public class AiServiceClient {
    private final RestTemplate restTemplate;
    private final String baseUrl;

    public AiServiceClient(@NonNull String baseUrl) {
        Objects.requireNonNull(baseUrl, "baseUrl cannot be null");
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.restTemplate = createRestTemplate();
    }

    private RestTemplate createRestTemplate() {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout((int) Duration.ofSeconds(10).toMillis());
        requestFactory.setReadTimeout((int) Duration.ofSeconds(10).toMillis());
        RestTemplate template = new RestTemplate(requestFactory);
        template.setUriTemplateHandler(new DefaultUriBuilderFactory(this.baseUrl));
        return template;
    }

    public String describe(@NonNull String issue) {
        return callEndpoint("/describe", issue, "description");
    }

    public String recommend(@NonNull String issue) {
        return callEndpoint("/recommend", issue, "recommendations");
    }

    public String generateReport(@NonNull String issue) {
        return callEndpoint("/generate-report", issue, "report");
    }

    private String callEndpoint(String path, String issue, String fallbackMessage) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, String>> request = new HttpEntity<>(Map.of("issue", issue), headers);
            ResponseEntity<Map> response = restTemplate.exchange(path, HttpMethod.POST, request, Map.class);
            Object body = response.getBody();
            if (body instanceof Map) {
                Object responseValue = ((Map<?, ?>) body).get("response");
                return responseValue != null ? responseValue.toString() : fallbackMessage;
            }
            return fallbackMessage;
        } catch (RestClientException exception) {
            return String.format("Unable to retrieve %s from AI service: %s", fallbackMessage, exception.getMessage());
        }
    }
}
