use iced::{Application, Command, Element, Settings, Size, Theme};

use crate::api;
use crate::components::{Header, MainContent, Sidebar};
use crate::messages::Message;
use crate::models::{Task, TaskFilter, TaskStatus};

pub struct AsyncApp {
    pub selected_project: String,
    pub current_filter: TaskFilter,
    pub expanded_sections: Vec<String>,
    pub tasks: Vec<Task>,
    pub api_client: api::AsyncApiClient,
    pub is_loading: bool,
    pub error_message: Option<String>,
}

impl Application for AsyncApp {
    type Message = Message;
    type Theme = Theme;
    type Executor = iced::executor::Default;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        // Initialize with comprehensive mock data as fallback
        let tasks = vec![
            Task {
                id: "1".to_string(),
                title: "Make creating and following a task instant".to_string(),
                assignee: "pybae".to_string(),
                status: TaskStatus::PendingReview,
                github_issue: Some(184),
                time_ago: "5 hours ago".to_string(),
            },
            Task {
                id: "2".to_string(),
                title: "Make the title truncate in the app breadcrumbs if it's too long"
                    .to_string(),
                assignee: "pybae".to_string(),
                status: TaskStatus::PendingInput,
                github_issue: Some(192),
                time_ago: "10 minutes ago".to_string(),
            },
            Task {
                id: "3".to_string(),
                title: "Show some badge in the review button when comments are queued".to_string(),
                assignee: "pybae".to_string(),
                status: TaskStatus::Completed,
                github_issue: None,
                time_ago: "9 hours ago".to_string(),
            },
            Task {
                id: "4".to_string(),
                title: "Ensure that escape only ever navigates up".to_string(),
                assignee: "pybae".to_string(),
                status: TaskStatus::Completed,
                github_issue: None,
                time_ago: "9 hours ago".to_string(),
            },
            Task {
                id: "5".to_string(),
                title: "Make clicking on the \"Inbox\" in task title navigate back to Inbox"
                    .to_string(),
                assignee: "pybae".to_string(),
                status: TaskStatus::Completed,
                github_issue: None,
                time_ago: "9 hours ago".to_string(),
            },
        ];

        // Try to create API client for the backend server
        let api_client = api::AsyncApiClient::new("http://localhost:8000").unwrap_or_else(|_| {
            // Fallback URL if localhost doesn't work
            api::AsyncApiClient::new("http://127.0.0.1:8000").unwrap()
        });

        (
            AsyncApp {
                selected_project: "async-desktop".to_string(),
                current_filter: TaskFilter::All,
                expanded_sections: vec![
                    "Pending Review".to_string(),
                    "Pending Input".to_string(),
                    "Completed".to_string(),
                ],
                tasks,
                api_client,
                is_loading: false,
                error_message: None,
            },
            // Start by attempting to load tasks from API
            Command::perform(async {}, |_| Message::LoadTasks),
        )
    }

    fn title(&self) -> String {
        "Async - Task Management".to_string()
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::ProjectClicked(project) => {
                self.selected_project = project;
                Command::none()
            }
            Message::TaskClicked(_task_id) => {
                println!("Task clicked - would navigate to detail view");
                Command::none()
            }
            Message::SectionToggled(section) => {
                if self.expanded_sections.contains(&section) {
                    self.expanded_sections.retain(|s| s != &section);
                } else {
                    self.expanded_sections.push(section);
                }
                Command::none()
            }
            Message::NewTaskClicked => {
                println!("New task - would open modal");
                Command::none()
            }
            Message::FilterChanged(filter) => {
                self.current_filter = filter;
                Command::none()
            }
            Message::InboxClicked => {
                println!("Inbox clicked");
                Command::none()
            }
            Message::RefreshClicked => Command::perform(async {}, |_| Message::LoadTasks),
            Message::LoadTasks => {
                if !self.is_loading {
                    self.is_loading = true;
                    self.error_message = None;
                    let client = self.api_client.clone();

                    Command::perform(
                        async move { client.get_tasks().await },
                        Message::TasksLoaded,
                    )
                } else {
                    Command::none()
                }
            }
            Message::TasksLoaded(result) => {
                self.is_loading = false;
                match result {
                    Ok(api_tasks) => {
                        self.tasks = api_tasks.into_iter().map(|task| task.into()).collect();
                        self.error_message = None;
                        println!("Loaded {} tasks from API", self.tasks.len());
                    }
                    Err(error) => {
                        self.error_message = Some(format!("Failed to load tasks: {}", error));
                        println!("Failed to load tasks: {}", error);
                        // Keep existing mock data as fallback
                    }
                }
                Command::none()
            }
        }
    }

    fn view(&self) -> Element<'_, Message> {
        use iced::widget::{column, row};

        row![
            Sidebar::view(&self.selected_project),
            column![
                Header::view(
                    &self.selected_project,
                    self.current_filter,
                    self.is_loading,
                    &self.error_message
                ),
                MainContent::view(&self.tasks, &self.expanded_sections)
            ]
        ]
        .into()
    }

    fn theme(&self) -> Theme {
        Theme::Dark
    }
}

pub fn run() -> iced::Result {
    AsyncApp::run(Settings {
        window: iced::window::Settings {
            size: Size::new(1200.0, 800.0),
            min_size: Some(Size::new(900.0, 600.0)),
            ..Default::default()
        },
        ..Settings::default()
    })
}
