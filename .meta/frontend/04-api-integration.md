# API Integration Specifications for Async-Server Frontend

## Overview
This document defines the API integration layer for the Async frontend application, including HTTP client setup, endpoint definitions, data models, and error handling patterns.

## API Client Architecture

### Base Client Configuration
```rust
use reqwest::{Client, Method, RequestBuilder, Response};
use serde::{Deserialize, Serialize};
use std::time::Duration;
use tokio::time::timeout;
use url::Url;

#[derive(Clone)]
pub struct ApiClient {
    client: Client,
    base_url: Url,
    auth_token: Option<String>,
    timeout: Duration,
}

impl ApiClient {
    pub fn new(base_url: &str) -> Result<Self, ApiError> {
        let client = Client::builder()
            .timeout(Duration::from_secs(30))
            .user_agent("async-desktop/1.0.0")
            .build()
            .map_err(ApiError::ClientCreation)?;
            
        Ok(Self {
            client,
            base_url: Url::parse(base_url).map_err(|_| ApiError::InvalidBaseUrl)?,
            auth_token: None,
            timeout: Duration::from_secs(30),
        })
    }
    
    pub fn with_auth_token(mut self, token: String) -> Self {
        self.auth_token = Some(token);
        self
    }
    
    async fn execute_request<T>(&self, request: RequestBuilder) -> Result<T, ApiError>
    where
        T: for<'de> Deserialize<'de>,
    {
        let mut request = request;
        
        if let Some(token) = &self.auth_token {
            request = request.bearer_auth(token);
        }
        
        let response = timeout(self.timeout, request.send())
            .await
            .map_err(|_| ApiError::Timeout)?
            .map_err(ApiError::Request)?;
            
        self.handle_response(response).await
    }
    
    async fn handle_response<T>(&self, response: Response) -> Result<T, ApiError>
    where
        T: for<'de> Deserialize<'de>,
    {
        let status = response.status();
        
        if status.is_success() {
            response.json().await.map_err(ApiError::Deserialization)
        } else {
            let error_body = response.text().await.unwrap_or_default();
            Err(ApiError::Http {
                status: status.as_u16(),
                message: error_body,
            })
        }
    }
}
```

### Error Handling
```rust
#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error("Failed to create HTTP client: {0}")]
    ClientCreation(reqwest::Error),
    
    #[error("Invalid base URL")]
    InvalidBaseUrl,
    
    #[error("Request timeout")]
    Timeout,
    
    #[error("HTTP request failed: {0}")]
    Request(reqwest::Error),
    
    #[error("HTTP error {status}: {message}")]
    Http { status: u16, message: String },
    
    #[error("Failed to deserialize response: {0}")]
    Deserialization(reqwest::Error),
    
    #[error("Authentication required")]
    AuthRequired,
    
    #[error("Invalid authentication token")]
    AuthInvalid,
    
    #[error("Network error: {0}")]
    Network(String),
}

impl ApiError {
    pub fn is_auth_error(&self) -> bool {
        matches!(self, ApiError::AuthRequired | ApiError::AuthInvalid) ||
        matches!(self, ApiError::Http { status: 401 | 403, .. })
    }
    
    pub fn is_network_error(&self) -> bool {
        matches!(self, ApiError::Network(_) | ApiError::Timeout | ApiError::Request(_))
    }
    
    pub fn user_message(&self) -> String {
        match self {
            ApiError::AuthRequired | ApiError::AuthInvalid => 
                "Please log in to continue".to_string(),
            ApiError::Timeout => 
                "Request timed out. Please check your connection".to_string(),
            ApiError::Network(_) => 
                "Network error. Please check your connection".to_string(),
            ApiError::Http { status: 404, .. } => 
                "Resource not found".to_string(),
            ApiError::Http { status: 500..=599, .. } => 
                "Server error. Please try again later".to_string(),
            _ => "An unexpected error occurred".to_string(),
        }
    }
}

pub type ApiResult<T> = Result<T, ApiError>;
```

## Data Models

### Core Domain Models
```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub username: String,
    pub email: String,
    pub avatar_url: Option<String>,
    pub name: Option<String>,
    pub github_id: Option<i64>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub github_repo: Option<String>,
    pub github_owner: Option<String>,
    pub visibility: ProjectVisibility,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProjectVisibility {
    #[serde(rename = "public")]
    Public,
    #[serde(rename = "private")]
    Private,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub description: String,
    pub status: TaskStatus,
    pub priority: TaskPriority,
    pub project_id: String,
    pub project_name: String,
    pub assignee_id: Option<String>,
    pub assignee: Option<User>,
    pub github_issue: Option<u32>,
    pub github_pr: Option<u32>,
    pub estimated_hours: Option<f32>,
    pub actual_hours: Option<f32>,
    pub due_date: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum TaskStatus {
    #[serde(rename = "pending_input")]
    PendingInput,
    #[serde(rename = "pending_review")]
    PendingReview,
    #[serde(rename = "researching")]
    Researching,
    #[serde(rename = "in_progress")]
    InProgress,
    #[serde(rename = "completed")]
    Completed,
    #[serde(rename = "cancelled")]
    Cancelled,
}

impl TaskStatus {
    pub fn display_name(&self) -> &'static str {
        match self {
            TaskStatus::PendingInput => "Pending Input",
            TaskStatus::PendingReview => "Pending Review",
            TaskStatus::Researching => "Researching",
            TaskStatus::InProgress => "In Progress",
            TaskStatus::Completed => "Completed",
            TaskStatus::Cancelled => "Cancelled",
        }
    }
    
    pub fn color(&self) -> crate::theme::Color {
        match self {
            TaskStatus::Completed => crate::theme::STATUS_COMPLETED,
            TaskStatus::InProgress => crate::theme::STATUS_IN_PROGRESS,
            TaskStatus::PendingReview | TaskStatus::PendingInput => crate::theme::STATUS_PENDING,
            TaskStatus::Researching => crate::theme::STATUS_RESEARCHING,
            TaskStatus::Cancelled => crate::theme::STATUS_ERROR,
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum TaskPriority {
    #[serde(rename = "low")]
    Low,
    #[serde(rename = "medium")]
    Medium,
    #[serde(rename = "high")]
    High,
    #[serde(rename = "urgent")]
    Urgent,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Subtask {
    pub id: String,
    pub task_id: String,
    pub title: String,
    pub description: String,
    pub status: TaskStatus,
    pub order_index: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Comment {
    pub id: String,
    pub task_id: String,
    pub author: User,
    pub content: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Commit {
    pub id: String,
    pub task_id: String,
    pub sha: String,
    pub message: String,
    pub author: String,
    pub files_changed: Vec<FileChange>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileChange {
    pub filename: String,
    pub status: FileChangeStatus,
    pub additions: u32,
    pub deletions: u32,
    pub patch: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum FileChangeStatus {
    #[serde(rename = "added")]
    Added,
    #[serde(rename = "modified")]
    Modified,
    #[serde(rename = "removed")]
    Removed,
    #[serde(rename = "renamed")]
    Renamed,
}
```

### Request/Response Models
```rust
#[derive(Debug, Serialize)]
pub struct CreateTaskRequest {
    pub title: String,
    pub description: String,
    pub project_id: String,
    pub priority: Option<TaskPriority>,
    pub assignee_id: Option<String>,
    pub due_date: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct CreateTaskResponse {
    pub task: Task,
}

#[derive(Debug, Serialize)]
pub struct UpdateTaskRequest {
    pub title: Option<String>,
    pub description: Option<String>,
    pub status: Option<TaskStatus>,
    pub priority: Option<TaskPriority>,
    pub assignee_id: Option<String>,
    pub due_date: Option<DateTime<Utc>>,
}

#[derive(Debug, Serialize)]
pub struct TaskFilter {
    pub project_id: Option<String>,
    pub assignee_id: Option<String>,
    pub status: Option<Vec<TaskStatus>>,
    pub priority: Option<Vec<TaskPriority>>,
    pub search_query: Option<String>,
    pub created_after: Option<DateTime<Utc>>,
    pub created_before: Option<DateTime<Utc>>,
}

#[derive(Debug, Deserialize)]
pub struct TaskListResponse {
    pub tasks: Vec<Task>,
    pub total_count: u32,
    pub page: u32,
    pub per_page: u32,
}

#[derive(Debug, Serialize)]
pub struct GitHubAuthRequest {
    pub code: String,
    pub state: String,
}

#[derive(Debug, Deserialize)]
pub struct GitHubAuthResponse {
    pub access_token: String,
    pub user: User,
    pub expires_in: u64,
}

#[derive(Debug, Deserialize)]
pub struct GitHubRepository {
    pub id: i64,
    pub name: String,
    pub full_name: String,
    pub description: Option<String>,
    pub private: bool,
    pub html_url: String,
    pub clone_url: String,
}

#[derive(Debug, Deserialize)]
pub struct RepositoryListResponse {
    pub repositories: Vec<GitHubRepository>,
}
```

## API Endpoints

### Authentication Endpoints
```rust
impl ApiClient {
    pub async fn github_auth(&self, code: &str, state: &str) -> ApiResult<GitHubAuthResponse> {
        let request = GitHubAuthRequest {
            code: code.to_string(),
            state: state.to_string(),
        };
        
        let url = self.base_url.join("/auth/github")?;
        let req = self.client.post(url).json(&request);
        
        self.execute_request(req).await
    }
    
    pub async fn refresh_token(&self, refresh_token: &str) -> ApiResult<GitHubAuthResponse> {
        let url = self.base_url.join("/auth/refresh")?;
        let req = self.client.post(url)
            .json(&serde_json::json!({ "refresh_token": refresh_token }));
        
        self.execute_request(req).await
    }
    
    pub async fn logout(&self) -> ApiResult<()> {
        let url = self.base_url.join("/auth/logout")?;
        let req = self.client.post(url);
        
        self.execute_request::<serde_json::Value>(req).await?;
        Ok(())
    }
}
```

### Task Management Endpoints
```rust
impl ApiClient {
    pub async fn list_tasks(&self, filter: &TaskFilter) -> ApiResult<TaskListResponse> {
        let url = self.base_url.join("/tasks")?;
        let req = self.client.get(url).query(&filter);
        
        self.execute_request(req).await
    }
    
    pub async fn get_task(&self, task_id: &str) -> ApiResult<Task> {
        let url = self.base_url.join(&format!("/tasks/{}", task_id))?;
        let req = self.client.get(url);
        
        self.execute_request(req).await
    }
    
    pub async fn create_task(&self, request: &CreateTaskRequest) -> ApiResult<CreateTaskResponse> {
        let url = self.base_url.join("/tasks")?;
        let req = self.client.post(url).json(request);
        
        self.execute_request(req).await
    }
    
    pub async fn update_task(&self, task_id: &str, request: &UpdateTaskRequest) -> ApiResult<Task> {
        let url = self.base_url.join(&format!("/tasks/{}", task_id))?;
        let req = self.client.patch(url).json(request);
        
        self.execute_request(req).await
    }
    
    pub async fn delete_task(&self, task_id: &str) -> ApiResult<()> {
        let url = self.base_url.join(&format!("/tasks/{}", task_id))?;
        let req = self.client.delete(url);
        
        self.execute_request::<serde_json::Value>(req).await?;
        Ok(())
    }
    
    pub async fn create_subtasks(&self, task_id: &str) -> ApiResult<Vec<Subtask>> {
        let url = self.base_url.join(&format!("/task/create-subtasks"))?;
        let req = self.client.post(url)
            .json(&serde_json::json!({ "task_id": task_id }));
        
        #[derive(Deserialize)]
        struct SubtasksResponse {
            subtasks: Vec<Subtask>,
        }
        
        let response: SubtasksResponse = self.execute_request(req).await?;
        Ok(response.subtasks)
    }
}
```

### Project Management Endpoints
```rust
impl ApiClient {
    pub async fn list_projects(&self) -> ApiResult<Vec<Project>> {
        let url = self.base_url.join("/projects")?;
        let req = self.client.get(url);
        
        #[derive(Deserialize)]
        struct ProjectsResponse {
            projects: Vec<Project>,
        }
        
        let response: ProjectsResponse = self.execute_request(req).await?;
        Ok(response.projects)
    }
    
    pub async fn get_project(&self, project_id: &str) -> ApiResult<Project> {
        let url = self.base_url.join(&format!("/projects/{}", project_id))?;
        let req = self.client.get(url);
        
        self.execute_request(req).await
    }
    
    pub async fn create_project_from_repo(&self, repo_id: i64) -> ApiResult<Project> {
        let url = self.base_url.join("/projects/from-repo")?;
        let req = self.client.post(url)
            .json(&serde_json::json!({ "repository_id": repo_id }));
        
        self.execute_request(req).await
    }
}
```

### GitHub Integration Endpoints
```rust
impl ApiClient {
    pub async fn list_repositories(&self) -> ApiResult<RepositoryListResponse> {
        let url = self.base_url.join("/github/list-repos")?;
        let req = self.client.get(url);
        
        self.execute_request(req).await
    }
    
    pub async fn import_issues(&self, project_id: &str) -> ApiResult<Vec<Task>> {
        let url = self.base_url.join("/github/import-issues")?;
        let req = self.client.post(url)
            .json(&serde_json::json!({ "project_id": project_id }));
        
        #[derive(Deserialize)]
        struct ImportResponse {
            imported_tasks: Vec<Task>,
        }
        
        let response: ImportResponse = self.execute_request(req).await?;
        Ok(response.imported_tasks)
    }
    
    pub async fn create_pull_request(&self, task_id: &str) -> ApiResult<u32> {
        let url = self.base_url.join("/github/create-pull-request")?;
        let req = self.client.post(url)
            .json(&serde_json::json!({ "task_id": task_id }));
        
        #[derive(Deserialize)]
        struct PrResponse {
            pull_request_number: u32,
        }
        
        let response: PrResponse = self.execute_request(req).await?;
        Ok(response.pull_request_number)
    }
}
```

## WebSocket Integration

### WebSocket Client
```rust
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use futures_util::{SinkExt, StreamExt};

#[derive(Debug, Clone)]
pub struct WebSocketClient {
    url: String,
    auth_token: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WebSocketMessage {
    TaskUpdated(Task),
    TaskCreated(Task),
    TaskDeleted(String),
    CommentAdded(Comment),
    SubtaskCompleted(String),
    Error(String),
    Ping,
    Pong,
}

impl WebSocketClient {
    pub fn new(url: &str) -> Self {
        Self {
            url: url.to_string(),
            auth_token: None,
        }
    }
    
    pub fn with_auth_token(mut self, token: String) -> Self {
        self.auth_token = Some(token);
        self
    }
    
    pub async fn connect(&self) -> Result<WebSocketStream, WebSocketError> {
        let mut url = self.url.clone();
        
        if let Some(token) = &self.auth_token {
            url.push_str(&format!("?token={}", token));
        }
        
        let (ws_stream, _) = connect_async(url).await
            .map_err(WebSocketError::Connection)?;
            
        Ok(WebSocketStream::new(ws_stream))
    }
}

pub struct WebSocketStream {
    stream: tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>,
}

impl WebSocketStream {
    fn new(stream: tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>) -> Self {
        Self { stream }
    }
    
    pub async fn next_message(&mut self) -> Result<Option<WebSocketMessage>, WebSocketError> {
        while let Some(msg) = self.stream.next().await {
            match msg.map_err(WebSocketError::Protocol)? {
                Message::Text(text) => {
                    let ws_msg: WebSocketMessage = serde_json::from_str(&text)
                        .map_err(WebSocketError::Deserialization)?;
                    return Ok(Some(ws_msg));
                },
                Message::Close(_) => return Ok(None),
                Message::Ping(data) => {
                    self.stream.send(Message::Pong(data)).await
                        .map_err(WebSocketError::Protocol)?;
                },
                _ => continue,
            }
        }
        Ok(None)
    }
    
    pub async fn send_message(&mut self, message: &WebSocketMessage) -> Result<(), WebSocketError> {
        let text = serde_json::to_string(message)
            .map_err(WebSocketError::Serialization)?;
        
        self.stream.send(Message::Text(text)).await
            .map_err(WebSocketError::Protocol)
    }
    
    pub async fn close(&mut self) -> Result<(), WebSocketError> {
        self.stream.send(Message::Close(None)).await
            .map_err(WebSocketError::Protocol)
    }
}

#[derive(Debug, thiserror::Error)]
pub enum WebSocketError {
    #[error("Connection failed: {0}")]
    Connection(tokio_tungstenite::tungstenite::Error),
    
    #[error("Protocol error: {0}")]
    Protocol(tokio_tungstenite::tungstenite::Error),
    
    #[error("Serialization error: {0}")]
    Serialization(serde_json::Error),
    
    #[error("Deserialization error: {0}")]
    Deserialization(serde_json::Error),
}
```

## Caching Strategy

### In-Memory Cache
```rust
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use std::time::{Duration, Instant};

#[derive(Clone)]
pub struct ApiCache {
    tasks: Arc<RwLock<HashMap<String, (Task, Instant)>>>,
    projects: Arc<RwLock<HashMap<String, (Project, Instant)>>>,
    task_lists: Arc<RwLock<HashMap<String, (Vec<Task>, Instant)>>>,
    ttl: Duration,
}

impl ApiCache {
    pub fn new(ttl: Duration) -> Self {
        Self {
            tasks: Arc::new(RwLock::new(HashMap::new())),
            projects: Arc::new(RwLock::new(HashMap::new())),
            task_lists: Arc::new(RwLock::new(HashMap::new())),
            ttl,
        }
    }
    
    pub fn get_task(&self, task_id: &str) -> Option<Task> {
        let cache = self.tasks.read().ok()?;
        let (task, cached_at) = cache.get(task_id)?;
        
        if cached_at.elapsed() < self.ttl {
            Some(task.clone())
        } else {
            None
        }
    }
    
    pub fn set_task(&self, task: Task) {
        if let Ok(mut cache) = self.tasks.write() {
            cache.insert(task.id.clone(), (task, Instant::now()));
        }
    }
    
    pub fn invalidate_task(&self, task_id: &str) {
        if let Ok(mut cache) = self.tasks.write() {
            cache.remove(task_id);
        }
    }
    
    pub fn clear(&self) {
        if let Ok(mut tasks) = self.tasks.write() {
            tasks.clear();
        }
        if let Ok(mut projects) = self.projects.write() {
            projects.clear();
        }
        if let Ok(mut task_lists) = self.task_lists.write() {
            task_lists.clear();
        }
    }
}
```

## Error Recovery Patterns

### Retry Logic
```rust
use tokio::time::{sleep, Duration};

pub struct RetryConfig {
    pub max_attempts: u32,
    pub base_delay: Duration,
    pub max_delay: Duration,
    pub backoff_factor: f64,
}

impl Default for RetryConfig {
    fn default() -> Self {
        Self {
            max_attempts: 3,
            base_delay: Duration::from_millis(100),
            max_delay: Duration::from_secs(10),
            backoff_factor: 2.0,
        }
    }
}

pub async fn retry_with_backoff<F, T, E>(
    mut operation: F,
    config: &RetryConfig,
) -> Result<T, E>
where
    F: FnMut() -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<T, E>> + Send>>,
    E: std::fmt::Debug,
{
    let mut attempts = 0;
    let mut delay = config.base_delay;
    
    loop {
        attempts += 1;
        
        match operation().await {
            Ok(result) => return Ok(result),
            Err(error) => {
                if attempts >= config.max_attempts {
                    return Err(error);
                }
                
                sleep(delay).await;
                delay = std::cmp::min(
                    Duration::from_secs_f64(delay.as_secs_f64() * config.backoff_factor),
                    config.max_delay,
                );
            }
        }
    }
}
```

## Usage Examples

### Task Operations
```rust
// Initialize API client
let client = ApiClient::new("http://localhost:8889")?
    .with_auth_token(auth_token);

// Create a new task
let create_request = CreateTaskRequest {
    title: "Fix user authentication bug".to_string(),
    description: "Users are unable to log in with GitHub OAuth".to_string(),
    project_id: "project-123".to_string(),
    priority: Some(TaskPriority::High),
    assignee_id: None,
    due_date: None,
};

let response = client.create_task(&create_request).await?;
println!("Created task: {}", response.task.id);

// List tasks with filtering
let filter = TaskFilter {
    project_id: Some("project-123".to_string()),
    status: Some(vec![TaskStatus::PendingReview, TaskStatus::InProgress]),
    ..Default::default()
};

let tasks = client.list_tasks(&filter).await?;
println!("Found {} tasks", tasks.tasks.len());

// Update task status
let update_request = UpdateTaskRequest {
    status: Some(TaskStatus::Completed),
    ..Default::default()
};

let updated_task = client.update_task(&response.task.id, &update_request).await?;
println!("Task status updated to: {:?}", updated_task.status);
```

### WebSocket Integration
```rust
// Connect to WebSocket for real-time updates
let ws_client = WebSocketClient::new("ws://localhost:8889/ws")
    .with_auth_token(auth_token);

let mut stream = ws_client.connect().await?;

// Listen for updates
tokio::spawn(async move {
    while let Ok(Some(message)) = stream.next_message().await {
        match message {
            WebSocketMessage::TaskUpdated(task) => {
                println!("Task updated: {}", task.title);
                // Update UI state
            },
            WebSocketMessage::TaskCreated(task) => {
                println!("New task created: {}", task.title);
                // Add to task list
            },
            WebSocketMessage::Error(error) => {
                eprintln!("WebSocket error: {}", error);
            },
            _ => {}
        }
    }
});
```

This API integration specification provides a comprehensive foundation for connecting the Async frontend to the backend services, with proper error handling, caching, and real-time updates.