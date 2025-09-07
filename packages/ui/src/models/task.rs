use iced::Color;

#[derive(Debug, Clone)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub assignee: String,
    pub status: TaskStatus,
    pub github_issue: Option<u32>,
    pub time_ago: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TaskStatus {
    PendingReview,
    PendingInput,
    Completed,
}

impl TaskStatus {
    pub fn label(&self) -> &'static str {
        match self {
            TaskStatus::PendingReview => "Pending Review",
            TaskStatus::PendingInput => "Pending Input",
            TaskStatus::Completed => "Completed",
        }
    }

    pub fn dot_color(&self) -> Color {
        match self {
            TaskStatus::Completed => Color::from_rgb(0.29, 0.87, 0.5), // Green
            TaskStatus::PendingReview => Color::from_rgb(1.0, 0.75, 0.0), // Orange
            TaskStatus::PendingInput => Color::from_rgb(1.0, 0.75, 0.0), // Orange
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum TaskFilter {
    All,
    Active,
    Archive,
}
