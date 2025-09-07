#![allow(dead_code)]

use super::{
    client::AsyncApiClient,
    error::ApiResult,
    models::{ApiTask, ApiTaskStatus, ApiTasksResponse, CreateTaskRequest, UpdateTaskRequest},
};

impl AsyncApiClient {
    /// Fetch all tasks with optional filtering
    pub async fn get_tasks(&self) -> ApiResult<Vec<ApiTask>> {
        let response: ApiTasksResponse = self.get("tasks").await?;
        Ok(response.tasks)
    }

    /// Fetch tasks with pagination and filtering
    pub async fn get_tasks_paginated(
        &self,
        page: usize,
        per_page: usize,
        status: Option<ApiTaskStatus>,
    ) -> ApiResult<ApiTasksResponse> {
        let mut path = format!("tasks?page={}&per_page={}", page, per_page);

        if let Some(status) = status {
            path.push_str(&format!(
                "&status={}",
                serde_json::to_string(&status).unwrap().trim_matches('"')
            ));
        }

        self.get(&path).await
    }

    /// Get a specific task by ID
    pub async fn get_task(&self, task_id: &str) -> ApiResult<ApiTask> {
        self.get(&format!("tasks/{}", task_id)).await
    }

    /// Create a new task
    pub async fn create_task(&self, request: CreateTaskRequest) -> ApiResult<ApiTask> {
        self.post("tasks", &request).await
    }

    /// Update an existing task
    pub async fn update_task(
        &self,
        task_id: &str,
        request: UpdateTaskRequest,
    ) -> ApiResult<ApiTask> {
        self.patch(&format!("tasks/{}", task_id), &request).await
    }

    /// Delete a task
    pub async fn delete_task(&self, task_id: &str) -> ApiResult<()> {
        let _: serde_json::Value = self.delete(&format!("tasks/{}", task_id)).await?;
        Ok(())
    }

    /// Generate AI subtasks for a task
    pub async fn create_subtasks(&self, task_id: &str) -> ApiResult<Vec<ApiTask>> {
        let response: ApiTasksResponse = self
            .post(
                "task/create-subtasks",
                &serde_json::json!({ "task_id": task_id }),
            )
            .await?;
        Ok(response.tasks)
    }
}
