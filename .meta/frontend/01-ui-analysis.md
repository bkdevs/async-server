# UI Analysis for Async-Server Frontend (Iced.rs)

## Overview
This document provides a comprehensive analysis of the Async desktop application UI based on screenshots, breaking down all visual elements, interactions, and patterns needed to recreate the interface using Iced.rs.

## Design System

### Color Palette
```rust
// Primary colors
const BACKGROUND_PRIMARY: Color = Color::from_rgb(0.1, 0.1, 0.1);      // #1a1a1a
const BACKGROUND_SECONDARY: Color = Color::from_rgb(0.16, 0.16, 0.16);  // #2a2a2a
const BACKGROUND_TERTIARY: Color = Color::from_rgb(0.2, 0.2, 0.2);      // #333333

// Text colors
const TEXT_PRIMARY: Color = Color::from_rgb(0.88, 0.88, 0.88);          // #e0e0e0
const TEXT_SECONDARY: Color = Color::from_rgb(0.63, 0.63, 0.63);        // #a0a0a0
const TEXT_ACCENT: Color = Color::from_rgb(0.29, 0.62, 1.0);            // #4a9eff

// Status colors
const STATUS_COMPLETED: Color = Color::from_rgb(0.29, 0.87, 0.5);       // #4ade80
const STATUS_PENDING: Color = Color::from_rgb(1.0, 0.75, 0.0);          // #ffbf00
const STATUS_ERROR: Color = Color::from_rgb(0.96, 0.26, 0.21);          // #f54338

// Interactive colors
const BUTTON_PRIMARY: Color = Color::from_rgb(0.29, 0.62, 1.0);         // #4a9eff
const BUTTON_HOVER: Color = Color::from_rgb(0.35, 0.68, 1.0);           // #5aafff
const BORDER_SUBTLE: Color = Color::from_rgb(0.3, 0.3, 0.3);            // #4d4d4d
```

### Typography Scale
```rust
const FONT_SIZE_LARGE: u16 = 24;      // Main task titles
const FONT_SIZE_MEDIUM: u16 = 18;     // Section headers
const FONT_SIZE_BODY: u16 = 14;       // Body text, descriptions
const FONT_SIZE_SMALL: u16 = 12;      // Timestamps, metadata
const FONT_SIZE_CODE: u16 = 13;       // Code snippets

const FONT_WEIGHT_BOLD: Weight = Weight::Bold;
const FONT_WEIGHT_MEDIUM: Weight = Weight::Medium;
const FONT_WEIGHT_REGULAR: Weight = Weight::Normal;
```

### Spacing System
```rust
const SPACING_XS: u16 = 4;
const SPACING_SM: u16 = 8;
const SPACING_MD: u16 = 16;
const SPACING_LG: u16 = 24;
const SPACING_XL: u16 = 32;

const BORDER_RADIUS_SM: f32 = 4.0;
const BORDER_RADIUS_MD: f32 = 8.0;
const BORDER_RADIUS_LG: f32 = 12.0;
```

## Layout Structure

### Main Application Layout
```
┌─────────────────────────────────────────────────────────────┐
│                    Window Title Bar                         │
├──────────┬──────────────────────────────────────────────────┤
│          │                Header Bar                        │
│          ├──────────────────────────────────────────────────┤
│ Sidebar  │                                                  │
│ (~250px) │              Main Content Area                   │
│          │                                                  │
│          │                                                  │
│          │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

### Sidebar Components
1. **User Profile Section** (Top)
   - Height: ~60px
   - User avatar (32x32px circle)
   - Username with dropdown indicator
   - Background: BACKGROUND_SECONDARY

2. **Navigation Menu**
   - "New task" button (full width, primary style)
   - "Inbox" section
   - "Projects" expandable section
   - "Tasks" section with current tasks

3. **Visual Hierarchy**
   - Section headers: TEXT_SECONDARY, FONT_SIZE_SMALL
   - Menu items: TEXT_PRIMARY, FONT_SIZE_BODY
   - Active item: Highlighted background, TEXT_ACCENT
   - Indentation: 16px for nested items

### Main Content Area Components

#### Header Bar
- Height: ~56px
- Background: BACKGROUND_SECONDARY
- Contains:
  - Breadcrumb navigation (left)
  - Filter tabs (center)
  - Action buttons (right)

#### Task List View
- **Status Groups**: Collapsible sections
  - Header with arrow icon and task count
  - Consistent vertical spacing (SPACING_MD)

#### Task Item Cards
- Height: ~72px per item
- Background: BACKGROUND_PRIMARY with hover state
- Layout: `[Avatar] [Content] [Metadata]`
- Border radius: BORDER_RADIUS_SM
- Margin between cards: SPACING_SM

## Component Specifications

### Task Item Card
```rust
struct TaskItem {
    id: String,
    title: String,
    assignee: User,
    status: TaskStatus,
    github_issue: Option<u32>,
    timestamp: DateTime,
    project: String,
}

// Visual structure:
// ┌─────────────────────────────────────────────────────┐
// │ [●] [Avatar] Task Title                    #123 5h  │
// │                Project Name                         │
// └─────────────────────────────────────────────────────┘
```

### Modal Dialog Structure
```rust
struct Modal {
    // Overlay: Semi-transparent background (rgba(0,0,0,0.6))
    // Container: Centered, max-width 500px
    // Background: BACKGROUND_SECONDARY
    // Border radius: BORDER_RADIUS_LG
    // Padding: SPACING_LG
}
```

### Code Diff Viewer
```rust
struct CodeDiff {
    // Side-by-side layout
    // Line numbers: TEXT_SECONDARY, FONT_SIZE_SMALL
    // Added lines: Green background tint
    // Removed lines: Red background tint
    // Syntax highlighting: Language-specific colors
}
```

## Interaction Patterns

### Navigation Flow
1. **Sidebar Navigation**
   - Click project → Load project tasks
   - Click task → Load task detail view
   - Breadcrumb navigation for deep links

2. **Task Management**
   - Create task → Modal dialog → Form submission
   - Task status → Drag & drop or context menu
   - Task detail → Full-screen view with back navigation

3. **Real-time Updates**
   - WebSocket connection for live updates
   - Optimistic UI updates
   - Toast notifications for feedback

### State Management Requirements
```rust
#[derive(Debug, Clone)]
pub enum AppState {
    Loading,
    Dashboard(DashboardState),
    TaskDetail(TaskDetailState),
    ProjectView(ProjectViewState),
    Error(String),
}

#[derive(Debug, Clone)]
pub struct DashboardState {
    projects: Vec<Project>,
    tasks: Vec<Task>,
    selected_project: Option<String>,
    filter: TaskFilter,
}
```

### Message Types
```rust
#[derive(Debug, Clone)]
pub enum Message {
    // Navigation
    NavigateToProject(String),
    NavigateToTask(String),
    ShowTaskCreation,
    
    // Task operations
    CreateTask(CreateTaskRequest),
    UpdateTaskStatus(String, TaskStatus),
    DeleteTask(String),
    
    // UI interactions
    ToggleSection(String),
    FilterTasks(TaskFilter),
    
    // API responses
    TasksLoaded(Vec<Task>),
    ProjectsLoaded(Vec<Project>),
    TaskCreated(Task),
    ApiError(String),
}
```

## API Integration Points

### Required Endpoints
1. **Authentication**: `/auth/github`
2. **Projects**: `/github/list-repos`
3. **Tasks**: `/task/create-subtasks`, `/task/chat`
4. **GitHub**: `/github/import-issues`

### Data Models
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub description: String,
    pub status: TaskStatus,
    pub project_id: String,
    pub assignee_id: Option<String>,
    pub github_issue: Option<u32>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskStatus {
    PendingInput,
    PendingReview,
    Researching,
    InProgress,
    Completed,
    Cancelled,
}
```

## Performance Considerations

### Iced.rs Specific
- Use `lazy` widgets for large lists
- Implement virtual scrolling for task lists
- Cache rendered components where possible
- Optimize font rendering for code syntax highlighting

### Memory Management
- Lazy load task details
- Pagination for large task lists
- Image caching for user avatars
- Debounce search/filter operations

## Accessibility Requirements

### Keyboard Navigation
- Tab order: Sidebar → Header → Main content
- Arrow keys for list navigation
- Enter/Space for activation
- Escape for modal dismissal

### Screen Reader Support
- Semantic HTML structure
- ARIA labels for interactive elements
- Status announcements for task updates
- Proper heading hierarchy

### Visual Accessibility
- High contrast color scheme (already dark)
- Scalable fonts (respect system font size)
- Focus indicators on all interactive elements
- Reduced motion options

## Development Phases

### Phase 1: Core Layout
- Basic window structure
- Sidebar navigation
- Header bar
- Empty states

### Phase 2: Task Management
- Task list rendering
- Task creation modal
- Basic task operations
- Status management

### Phase 3: Advanced Features
- Code diff viewer
- Real-time updates
- GitHub integration
- Search and filtering

### Phase 4: Polish
- Animations and transitions
- Error handling
- Performance optimization
- Accessibility improvements

## Testing Strategy

### Unit Tests
- Component rendering
- State management
- Message handling
- API integration

### Integration Tests
- User workflows
- Navigation paths
- Data persistence
- Error scenarios

### Visual Regression Tests
- Component screenshots
- Layout consistency
- Theme compliance
- Responsive behavior

## Notes for Implementation

1. **Iced.rs Limitations**: Limited rich text rendering - may need custom solutions for syntax highlighting
2. **WebSocket Integration**: Use `tokio-tungstenite` for real-time updates
3. **HTTP Client**: `reqwest` for API calls
4. **Image Loading**: Async image loading for avatars
5. **Configuration**: Support for API endpoint configuration
6. **Error Handling**: Graceful degradation for offline scenarios

This analysis provides the foundation for building a pixel-perfect recreation of the Async desktop application using Iced.rs while maintaining the original's functionality and user experience.