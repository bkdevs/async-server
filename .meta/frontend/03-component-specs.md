# Component Specifications for Async-Server Frontend (Iced.rs)

## Overview
This document provides detailed specifications for each UI component in the Async frontend application, including props, state, behavior, and styling requirements.

## Core Layout Components

### 1. MainApplication (`src/app.rs`)
**Purpose**: Root application component managing global state and routing

#### State
```rust
pub struct AsyncApp {
    pub state: AppState,
    pub config: Config,
    pub api_client: ApiClient,
    pub websocket: Option<WebSocket>,
    pub theme: Theme,
}

pub enum AppState {
    Loading,
    Authentication(AuthState),
    Dashboard(DashboardState),
    TaskDetail(TaskDetailState),
    Error(ErrorState),
}
```

#### Messages
```rust
pub enum Message {
    // Application lifecycle
    Initialize,
    ConfigLoaded(Config),
    ThemeChanged(Theme),
    
    // Authentication
    LoginRequested,
    LoginCompleted(Result<User, AuthError>),
    LogoutRequested,
    
    // Navigation
    NavigateTo(Route),
    NavigateBack,
    
    // Component messages
    Sidebar(SidebarMessage),
    Header(HeaderMessage),
    TaskList(TaskListMessage),
    TaskDetail(TaskDetailMessage),
    Modal(ModalMessage),
    
    // API responses
    ApiResponse(ApiResult),
    WebSocketMessage(WsMessage),
    WebSocketError(String),
}
```

#### Layout Structure
```rust
fn view(&self) -> Element<Message> {
    match &self.state {
        AppState::Loading => loading_view(),
        AppState::Authentication(auth) => auth_view(auth),
        AppState::Dashboard(dashboard) => {
            Row::new()
                .push(Sidebar::new(&dashboard.sidebar_state).map(Message::Sidebar))
                .push(
                    Column::new()
                        .push(Header::new(&dashboard.header_state).map(Message::Header))
                        .push(main_content_view(dashboard))
                )
        },
        AppState::Error(error) => error_view(error),
    }
}
```

### 2. Sidebar Component (`src/components/sidebar.rs`)
**Purpose**: Left navigation panel with projects, tasks, and user profile

#### Props/State
```rust
pub struct SidebarState {
    pub user: User,
    pub projects: Vec<Project>,
    pub current_tasks: Vec<Task>,
    pub selected_project: Option<String>,
    pub collapsed_sections: HashSet<String>,
    pub is_collapsed: bool,
}

pub enum SidebarMessage {
    UserMenuToggled,
    ProjectSelected(String),
    TaskSelected(String),
    SectionToggled(String),
    NewTaskClicked,
    CollapseToggled,
}
```

#### Visual Specifications
- **Width**: 250px (expanded), 60px (collapsed)
- **Background**: `BACKGROUND_SECONDARY` (#2a2a2a)
- **Border**: Right border with `BORDER_SUBTLE` (#4d4d4d)
- **Sections**:
  - User profile (60px height)
  - Navigation menu
  - Projects list (expandable)
  - Current tasks list

#### User Profile Section
```rust
fn user_profile_section(user: &User, expanded: bool) -> Element<SidebarMessage> {
    Container::new(
        Row::new()
            .push(Avatar::new(&user.avatar_url, 32))
            .push_maybe(if expanded {
                Some(
                    Column::new()
                        .push(Text::new(&user.name).size(14).color(TEXT_PRIMARY))
                        .push(Text::new(&user.username).size(12).color(TEXT_SECONDARY))
                )
            } else { None })
            .push_maybe(if expanded {
                Some(Icon::chevron_down())
            } else { None })
    )
    .padding(SPACING_MD)
    .style(theme::Container::Secondary)
}
```

#### Projects Section
```rust
fn projects_section(projects: &[Project], selected: Option<&str>) -> Element<SidebarMessage> {
    let mut section = Column::new()
        .push(
            Row::new()
                .push(Icon::chevron_right()) // or down if expanded
                .push(Text::new("Projects").size(12).color(TEXT_SECONDARY))
        )
        .spacing(SPACING_SM);
    
    for project in projects {
        section = section.push(
            Button::new(
                Row::new()
                    .push(Icon::folder())
                    .push(Text::new(&project.name).size(14))
            )
            .on_press(SidebarMessage::ProjectSelected(project.id.clone()))
            .style(if Some(&project.id) == selected {
                theme::Button::Selected
            } else {
                theme::Button::Ghost
            })
        );
    }
    
    section.into()
}
```

### 3. Header Component (`src/components/header.rs`)
**Purpose**: Top navigation bar with breadcrumbs, filters, and actions

#### Props/State
```rust
pub struct HeaderState {
    pub breadcrumbs: Vec<Breadcrumb>,
    pub current_filter: TaskFilter,
    pub available_filters: Vec<TaskFilter>,
    pub search_query: String,
    pub is_searching: bool,
}

pub enum HeaderMessage {
    BreadcrumbClicked(usize),
    FilterChanged(TaskFilter),
    SearchQueryChanged(String),
    SearchSubmitted,
    NewTaskClicked,
    ViewModeChanged(ViewMode),
}

pub struct Breadcrumb {
    pub label: String,
    pub route: Route,
    pub is_current: bool,
}
```

#### Visual Specifications
- **Height**: 56px
- **Background**: `BACKGROUND_SECONDARY` (#2a2a2a)
- **Border**: Bottom border with `BORDER_SUBTLE`
- **Layout**: `[Breadcrumbs] [Spacer] [Filters] [Actions]`

#### Implementation
```rust
fn view(&self, state: &HeaderState) -> Element<HeaderMessage> {
    Container::new(
        Row::new()
            .push(breadcrumb_view(&state.breadcrumbs))
            .push(horizontal_space(Length::Fill))
            .push(filter_tabs(&state.current_filter, &state.available_filters))
            .push(search_input(&state.search_query))
            .push(new_task_button())
            .align_items(Alignment::Center)
            .spacing(SPACING_MD)
    )
    .height(56)
    .padding([0, SPACING_LG])
    .style(theme::Container::Header)
}
```

## Task Management Components

### 4. TaskList Component (`src/views/task_list.rs`)
**Purpose**: Main task listing with status groups and filtering

#### Props/State
```rust
pub struct TaskListState {
    pub tasks: Vec<Task>,
    pub grouped_tasks: HashMap<TaskStatus, Vec<Task>>,
    pub expanded_groups: HashSet<TaskStatus>,
    pub selected_tasks: HashSet<String>,
    pub loading_states: HashMap<String, bool>,
    pub filter: TaskFilter,
    pub sort_order: SortOrder,
}

pub enum TaskListMessage {
    TaskClicked(String),
    TaskStatusChanged(String, TaskStatus),
    GroupToggled(TaskStatus),
    TaskSelected(String, bool),
    BulkActionRequested(BulkAction),
    SortOrderChanged(SortOrder),
    RefreshRequested,
}
```

#### Visual Specifications
- **Background**: `BACKGROUND_PRIMARY` (#1a1a1a)
- **Padding**: `SPACING_LG` all sides
- **Group spacing**: `SPACING_XL` between status groups
- **Item spacing**: `SPACING_SM` between task items

#### Status Group Component
```rust
fn status_group_view(
    status: &TaskStatus,
    tasks: &[Task],
    expanded: bool
) -> Element<TaskListMessage> {
    let header = Button::new(
        Row::new()
            .push(Icon::chevron_right().rotation(if expanded { 90.0 } else { 0.0 }))
            .push(Text::new(status.display_name()).size(16).weight(Weight::Medium))
            .push(Badge::new(&tasks.len().to_string()).style(theme::Badge::Secondary))
            .spacing(SPACING_SM)
    )
    .on_press(TaskListMessage::GroupToggled(*status))
    .style(theme::Button::GroupHeader);
    
    let mut column = Column::new().push(header).spacing(SPACING_MD);
    
    if expanded {
        for task in tasks {
            column = column.push(
                TaskItem::new(task)
                    .on_click(TaskListMessage::TaskClicked(task.id.clone()))
                    .on_status_change(TaskListMessage::TaskStatusChanged)
            );
        }
    }
    
    column.into()
}
```

### 5. TaskItem Component (`src/components/task_item.rs`)
**Purpose**: Individual task card within the task list

#### Props/State
```rust
pub struct TaskItemProps {
    pub task: Task,
    pub is_selected: bool,
    pub is_loading: bool,
    pub on_click: Option<Message>,
    pub on_status_change: Option<fn(String, TaskStatus) -> Message>,
}

pub enum TaskItemMessage {
    Clicked,
    StatusChangeRequested(TaskStatus),
    AssigneeClicked,
    GitHubIssueClicked,
    ContextMenuRequested,
}
```

#### Visual Specifications
- **Height**: 72px
- **Background**: `BACKGROUND_PRIMARY` with hover state
- **Border radius**: `BORDER_RADIUS_SM` (4px)
- **Padding**: `SPACING_MD` (16px)
- **Layout**: `[Status][Avatar][Content][Metadata]`

#### Implementation
```rust
fn view(&self, task: &Task, selected: bool) -> Element<TaskItemMessage> {
    let status_dot = StatusDot::new(task.status)
        .size(8)
        .style(theme::StatusDot::from_status(task.status));
    
    let avatar = Avatar::new(&task.assignee.avatar_url, 32)
        .on_press(TaskItemMessage::AssigneeClicked);
    
    let content = Column::new()
        .push(
            Text::new(&task.title)
                .size(14)
                .weight(Weight::Medium)
                .color(TEXT_PRIMARY)
        )
        .push(
            Text::new(&task.project_name)
                .size(12)
                .color(TEXT_SECONDARY)
        );
    
    let metadata = Column::new()
        .push(
            task.github_issue.map(|issue| 
                Button::new(Text::new(&format!("#{}", issue)))
                    .style(theme::Button::Link)
                    .on_press(TaskItemMessage::GitHubIssueClicked)
            )
        )
        .push(
            Text::new(&task.updated_at.format_relative())
                .size(12)
                .color(TEXT_SECONDARY)
        )
        .align_items(Alignment::End);
    
    Button::new(
        Row::new()
            .push(status_dot)
            .push(avatar)
            .push(content)
            .push(horizontal_space(Length::Fill))
            .push(metadata)
            .align_items(Alignment::Center)
            .spacing(SPACING_MD)
    )
    .on_press(TaskItemMessage::Clicked)
    .style(if selected {
        theme::Button::TaskItemSelected
    } else {
        theme::Button::TaskItem
    })
    .width(Length::Fill)
    .height(72)
}
```

### 6. TaskDetail Component (`src/views/task_detail.rs`)
**Purpose**: Full task view with requirements, code diffs, and comments

#### Props/State
```rust
pub struct TaskDetailState {
    pub task: Task,
    pub requirements: Vec<Requirement>,
    pub commits: Vec<Commit>,
    pub comments: Vec<Comment>,
    pub selected_diff: Option<String>,
    pub comment_draft: String,
    pub is_editing: bool,
}

pub enum TaskDetailMessage {
    BackClicked,
    EditToggled,
    RequirementAdded(String),
    RequirementUpdated(usize, String),
    DiffSelected(String),
    CommentDraftChanged(String),
    CommentSubmitted,
    ExecuteClicked,
    ReviewActionClicked(ReviewAction),
}
```

#### Visual Specifications
- **Layout**: Full-width single column
- **Max width**: 1200px (centered)
- **Sections**:
  - Header with title and actions (80px height)
  - Task description and metadata
  - Requirements list (editable)
  - Code diffs viewer
  - Comments section

#### Header Implementation
```rust
fn header_view(task: &Task) -> Element<TaskDetailMessage> {
    Container::new(
        Row::new()
            .push(
                Button::new(Icon::arrow_left())
                    .on_press(TaskDetailMessage::BackClicked)
                    .style(theme::Button::Ghost)
            )
            .push(
                Column::new()
                    .push(Text::new(&task.title).size(24).weight(Weight::Bold))
                    .push(
                        Row::new()
                            .push(Text::new(&task.project_name).color(TEXT_SECONDARY))
                            .push(task.github_issue.map(|n| Text::new(&format!("#{}", n))))
                            .spacing(SPACING_SM)
                    )
            )
            .push(horizontal_space(Length::Fill))
            .push(
                Row::new()
                    .push(Button::new("Checkout").style(theme::Button::Secondary))
                    .push(Button::new("Review").style(theme::Button::Primary))
                    .spacing(SPACING_SM)
            )
            .align_items(Alignment::Center)
            .spacing(SPACING_LG)
    )
    .padding(SPACING_LG)
    .style(theme::Container::Header)
}
```

## Modal Components

### 7. CreateTaskModal (`src/components/modals/create_task.rs`)
**Purpose**: Modal dialog for creating new tasks

#### Props/State
```rust
pub struct CreateTaskModalState {
    pub is_visible: bool,
    pub title: String,
    pub description: String,
    pub selected_project: Option<String>,
    pub projects: Vec<Project>,
    pub validation_errors: HashMap<String, String>,
    pub is_submitting: bool,
}

pub enum CreateTaskModalMessage {
    TitleChanged(String),
    DescriptionChanged(String),
    ProjectSelected(String),
    SubmitClicked,
    CancelClicked,
    Closed,
}
```

#### Visual Specifications
- **Overlay**: Semi-transparent black (rgba(0,0,0,0.6))
- **Modal size**: 500px width, auto height
- **Background**: `BACKGROUND_SECONDARY`
- **Border radius**: `BORDER_RADIUS_LG` (12px)
- **Padding**: `SPACING_XL` (32px)

#### Implementation
```rust
fn view(&self, state: &CreateTaskModalState) -> Element<CreateTaskModalMessage> {
    if !state.is_visible {
        return Container::new(Space::new(0, 0)).into();
    }
    
    let modal_content = Container::new(
        Column::new()
            .push(
                Row::new()
                    .push(Text::new("New Issue").size(20).weight(Weight::Bold))
                    .push(horizontal_space(Length::Fill))
                    .push(
                        Button::new(Icon::close())
                            .on_press(CreateTaskModalMessage::CancelClicked)
                            .style(theme::Button::Ghost)
                    )
            )
            .push(
                TextInput::new("Task title", &state.title)
                    .on_input(CreateTaskModalMessage::TitleChanged)
                    .style(theme::TextInput::Default)
            )
            .push(
                TextInput::new("Description...", &state.description)
                    .on_input(CreateTaskModalMessage::DescriptionChanged)
                    .style(theme::TextInput::Multiline)
            )
            .push(
                PickList::new(
                    &state.projects,
                    state.selected_project.as_ref(),
                    CreateTaskModalMessage::ProjectSelected
                )
                .placeholder("Select project...")
                .style(theme::PickList::Default)
            )
            .push(
                Row::new()
                    .push(horizontal_space(Length::Fill))
                    .push(
                        Button::new("Create")
                            .on_press(CreateTaskModalMessage::SubmitClicked)
                            .style(theme::Button::Primary)
                    )
                    .spacing(SPACING_MD)
            )
            .spacing(SPACING_LG)
    )
    .width(500)
    .padding(SPACING_XL)
    .style(theme::Container::Modal);
    
    // Overlay with modal
    Container::new(
        Container::new(modal_content)
            .center_x()
            .center_y()
            .width(Length::Fill)
            .height(Length::Fill)
    )
    .style(theme::Container::ModalOverlay)
    .width(Length::Fill)
    .height(Length::Fill)
}
```

## Utility Components

### 8. CodeDiff Component (`src/components/code_diff.rs`)
**Purpose**: Side-by-side code diff viewer with syntax highlighting

#### Props/State
```rust
pub struct CodeDiffProps {
    pub before: String,
    pub after: String,
    pub language: Option<String>,
    pub file_name: String,
}

pub enum CodeDiffMessage {
    LineClicked(usize, DiffSide),
    CommentAdded(usize, String),
    ScrollSynced(f32),
}

pub enum DiffSide {
    Before,
    After,
}
```

#### Visual Specifications
- **Layout**: Side-by-side panels (50% each)
- **Background**: Darker than primary (`#0f0f0f`)
- **Line numbers**: `TEXT_SECONDARY`, right-aligned, monospace
- **Added lines**: Green background tint (`rgba(74, 222, 128, 0.1)`)
- **Removed lines**: Red background tint (`rgba(245, 67, 56, 0.1)`)
- **Font**: Monospace, 13px

### 9. StatusDot Component (`src/widgets/status_dot.rs`)
**Purpose**: Colored indicator for task status

#### Props
```rust
pub struct StatusDotProps {
    pub status: TaskStatus,
    pub size: u16, // diameter in pixels
}
```

#### Implementation
```rust
impl StatusDot {
    pub fn new(status: TaskStatus) -> Self {
        Self { status, size: 8 }
    }
    
    pub fn size(mut self, size: u16) -> Self {
        self.size = size;
        self
    }
}

impl<Message> Widget<Message, Renderer> for StatusDot {
    fn draw(&self, /* params */) {
        let color = match self.status {
            TaskStatus::Completed => STATUS_COMPLETED,
            TaskStatus::PendingReview => STATUS_PENDING,
            TaskStatus::InProgress => Color::from_rgb(0.29, 0.62, 1.0), // Blue
            _ => TEXT_SECONDARY,
        };
        
        // Draw filled circle with specified color and size
    }
}
```

### 10. Avatar Component (`src/widgets/avatar.rs`)
**Purpose**: User avatar with fallback to initials

#### Props
```rust
pub struct AvatarProps {
    pub image_url: Option<String>,
    pub fallback_text: String,
    pub size: u16,
    pub on_press: Option<Message>,
}
```

## Theme System (`src/theme.rs`)

### Component Styles
```rust
pub struct Theme;

impl button::StyleSheet for Theme {
    type Style = ButtonStyle;

    fn active(&self, style: &Self::Style) -> button::Appearance {
        match style {
            ButtonStyle::Primary => button::Appearance {
                background: Some(Background::Color(BUTTON_PRIMARY)),
                text_color: Color::WHITE,
                border_radius: BORDER_RADIUS_MD.into(),
                ..Default::default()
            },
            ButtonStyle::TaskItem => button::Appearance {
                background: Some(Background::Color(BACKGROUND_PRIMARY)),
                text_color: TEXT_PRIMARY,
                border_radius: BORDER_RADIUS_SM.into(),
                ..Default::default()
            },
            // ... other button styles
        }
    }
    
    fn hovered(&self, style: &Self::Style) -> button::Appearance {
        let active = self.active(style);
        match style {
            ButtonStyle::TaskItem => button::Appearance {
                background: Some(Background::Color(BACKGROUND_SECONDARY)),
                ..active
            },
            _ => active,
        }
    }
}
```

## Responsive Design Considerations

### Breakpoints
- **Mobile**: < 768px (simplified layout)
- **Tablet**: 768px - 1024px (collapsed sidebar by default)
- **Desktop**: > 1024px (full layout)

### Adaptive Components
- Sidebar collapses to icon-only on smaller screens
- Task list switches to single column layout
- Modal dialogs become full-screen on mobile
- Touch-friendly hit targets (minimum 44px)

This specification provides the foundation for implementing each component with consistent styling, behavior, and integration patterns throughout the Async frontend application.