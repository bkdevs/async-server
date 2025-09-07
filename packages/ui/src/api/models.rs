use crate::models::{Task, TaskStatus};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiTask {
    pub id: String,
    pub title: String,
    pub description: Option<String>,
    pub status: ApiTaskStatus,
    pub assignee_id: Option<String>,
    pub assignee_name: Option<String>,
    pub github_issue: Option<u32>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub project_id: String,
    pub org_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ApiTaskStatus {
    Research,
    Planning,
    Execution,
    Review,
    Completed,
    Failed,
}

impl From<ApiTaskStatus> for TaskStatus {
    fn from(status: ApiTaskStatus) -> Self {
        match status {
            ApiTaskStatus::Research => TaskStatus::PendingInput,
            ApiTaskStatus::Planning => TaskStatus::PendingInput,
            ApiTaskStatus::Execution => TaskStatus::PendingInput,
            ApiTaskStatus::Review => TaskStatus::PendingReview,
            ApiTaskStatus::Completed => TaskStatus::Completed,
            ApiTaskStatus::Failed => TaskStatus::PendingInput,
        }
    }
}

impl From<ApiTask> for Task {
    fn from(api_task: ApiTask) -> Self {
        use chrono::prelude::*;

        let time_ago = {
            let duration = Utc::now() - api_task.updated_at;
            if duration.num_minutes() < 60 {
                format!("{} minutes ago", duration.num_minutes())
            } else if duration.num_hours() < 24 {
                format!("{} hours ago", duration.num_hours())
            } else {
                format!("{} days ago", duration.num_days())
            }
        };

        Task {
            id: api_task.id,
            title: api_task.title,
            assignee: api_task.assignee_name.unwrap_or("Unassigned".to_string()),
            status: api_task.status.into(),
            github_issue: api_task.github_issue,
            time_ago,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiProject {
    pub id: String,
    pub name: String,
    pub description: Option<String>,
    pub github_repo: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiUser {
    pub id: String,
    pub email: String,
    pub name: Option<String>,
    pub avatar_url: Option<String>,
    pub github_username: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiTasksResponse {
    pub tasks: Vec<ApiTask>,
    pub total: usize,
    pub page: usize,
    pub per_page: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateTaskRequest {
    pub title: String,
    pub description: Option<String>,
    pub project_id: String,
    pub assignee_id: Option<String>,
    pub github_issue: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateTaskRequest {
    pub title: Option<String>,
    pub description: Option<String>,
    pub status: Option<ApiTaskStatus>,
    pub assignee_id: Option<String>,
    pub github_issue: Option<u32>,
}
