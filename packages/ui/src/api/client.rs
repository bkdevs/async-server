#![allow(dead_code)]

use reqwest::{Client, RequestBuilder, Response};
use serde::de::DeserializeOwned;
use std::time::Duration;
use url::Url;

use super::error::{ApiError, ApiResult};

#[derive(Debug, Clone)]
pub struct AsyncApiClient {
    client: Client,
    base_url: Url,
    auth_token: Option<String>,
}

impl AsyncApiClient {
    pub fn new(base_url: &str) -> ApiResult<Self> {
        let base_url = Url::parse(base_url).map_err(|_| ApiError::Connection)?;

        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .connect_timeout(Duration::from_secs(10))
            .build()
            .map_err(|e| ApiError::Request(e.to_string()))?;

        Ok(Self {
            client,
            base_url,
            auth_token: None,
        })
    }

    pub fn with_auth_token(&mut self, token: String) {
        self.auth_token = Some(token);
    }

    fn build_request(&self, method: reqwest::Method, path: &str) -> ApiResult<RequestBuilder> {
        let url = self.base_url.join(path).map_err(|_| ApiError::Connection)?;

        let mut request = self.client.request(method, url);

        // Add auth header if token is available
        if let Some(token) = &self.auth_token {
            request = request.header("Authorization", format!("Bearer {}", token));
        }

        request = request.header("Content-Type", "application/json");

        Ok(request)
    }

    async fn send_request<T>(&self, request: RequestBuilder) -> ApiResult<T>
    where
        T: DeserializeOwned,
    {
        let response = request.send().await.map_err(|e| {
            if e.is_timeout() {
                ApiError::Timeout
            } else if e.is_connect() {
                ApiError::Connection
            } else {
                ApiError::Request(e.to_string())
            }
        })?;

        self.handle_response(response).await
    }

    async fn handle_response<T>(&self, response: Response) -> ApiResult<T>
    where
        T: DeserializeOwned,
    {
        let status = response.status();

        if status.is_success() {
            response
                .json::<T>()
                .await
                .map_err(|e| ApiError::Request(e.to_string()))
        } else if status == reqwest::StatusCode::UNAUTHORIZED {
            Err(ApiError::Authentication)
        } else if status == reqwest::StatusCode::NOT_FOUND {
            let text = response
                .text()
                .await
                .unwrap_or_else(|_| "Not found".to_string());
            Err(ApiError::NotFound(text))
        } else {
            let message = response
                .text()
                .await
                .unwrap_or_else(|_| "Unknown error".to_string());
            Err(ApiError::Server {
                status: status.as_u16(),
                message,
            })
        }
    }

    pub async fn get<T>(&self, path: &str) -> ApiResult<T>
    where
        T: DeserializeOwned,
    {
        let request = self.build_request(reqwest::Method::GET, path)?;
        self.send_request(request).await
    }

    pub async fn post<T, B>(&self, path: &str, body: &B) -> ApiResult<T>
    where
        T: DeserializeOwned,
        B: serde::Serialize,
    {
        let request = self.build_request(reqwest::Method::POST, path)?.json(body);
        self.send_request(request).await
    }

    pub async fn patch<T, B>(&self, path: &str, body: &B) -> ApiResult<T>
    where
        T: DeserializeOwned,
        B: serde::Serialize,
    {
        let request = self.build_request(reqwest::Method::PATCH, path)?.json(body);
        self.send_request(request).await
    }

    pub async fn delete<T>(&self, path: &str) -> ApiResult<T>
    where
        T: DeserializeOwned,
    {
        let request = self.build_request(reqwest::Method::DELETE, path)?;
        self.send_request(request).await
    }

    pub async fn health_check(&self) -> ApiResult<bool> {
        match self.get::<serde_json::Value>("health").await {
            Ok(_) => Ok(true),
            Err(ApiError::NotFound(_)) => Ok(true), // Some APIs don't have /health
            Err(_) => Ok(false),
        }
    }
}
