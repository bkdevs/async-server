use crate::api;
use crate::models::TaskFilter;

#[derive(Debug, Clone)]
pub enum Message {
    ProjectClicked(String),
    TaskClicked(String),
    SectionToggled(String),
    NewTaskClicked,
    FilterChanged(TaskFilter),
    InboxClicked,
    TasksLoaded(Result<Vec<api::ApiTask>, api::ApiError>),
    LoadTasks,
    RefreshClicked,
}
