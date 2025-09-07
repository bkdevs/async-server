# Async-Server Frontend Development Overview

## Project Summary
This document provides a comprehensive overview of the Async-Server frontend development project using Iced.rs, designed to recreate the macOS desktop application interface shown in the provided screenshots.

## Quick Reference

### Project Goal
Build a cross-platform desktop application using Rust and Iced.rs that provides:
- Task management with GitHub integration
- Real-time collaboration features
- Code review and diff viewing capabilities
- Dark theme interface matching the original design

### Technology Stack
- **Framework**: Iced.rs 0.12 (GUI framework)
- **Runtime**: Tokio (async runtime)
- **HTTP Client**: reqwest (API communication)
- **WebSocket**: tokio-tungstenite (real-time updates)
- **Serialization**: serde (JSON handling)
- **Date/Time**: chrono (timestamp management)
- **Error Handling**: thiserror + anyhow

### Key Features to Implement
1. **Sidebar Navigation**
   - User profile section
   - Project tree structure
   - Active tasks list
   - Collapsible sections

2. **Main Content Area**
   - Task list with status grouping
   - Individual task detail views
   - Code diff viewer
   - Comment system

3. **Task Management**
   - Create, read, update, delete tasks
   - Status transitions (Pending → In Progress → Completed)
   - GitHub issue integration
   - Real-time updates via WebSocket

4. **Modal Dialogs**
   - New task creation
   - Task editing
   - Confirmation dialogs

## File Structure Overview

```
async-frontend/
├── src/
│   ├── main.rs              # Application entry point
│   ├── app.rs               # Main application state and logic
│   ├── config.rs            # Configuration management
│   ├── theme.rs             # Dark theme and styling
│   ├── error.rs             # Error handling
│   ├── api/                 # API integration layer
│   │   ├── mod.rs
│   │   ├── client.rs        # HTTP client setup
│   │   ├── auth.rs          # Authentication endpoints
│   │   ├── tasks.rs         # Task management endpoints
│   │   └── websocket.rs     # Real-time updates
│   ├── models/              # Data structures
│   │   ├── mod.rs
│   │   ├── task.rs          # Task models
│   │   ├── user.rs          # User models
│   │   └── project.rs       # Project models
│   ├── components/          # UI components
│   │   ├── mod.rs
│   │   ├── sidebar.rs       # Left navigation panel
│   │   ├── header.rs        # Top navigation bar
│   │   ├── task_item.rs     # Individual task card
│   │   └── code_diff.rs     # Code diff viewer
│   ├── views/               # Main view screens
│   │   ├── mod.rs
│   │   ├── dashboard.rs     # Main dashboard
│   │   └── task_detail.rs   # Task detail view
│   └── widgets/             # Custom UI widgets
│       ├── mod.rs
│       ├── button.rs        # Styled buttons
│       ├── modal.rs         # Modal dialogs
│       └── avatar.rs        # User avatars
```

## Design System Quick Reference

### Colors (Dark Theme)
```rust
// Backgrounds
BACKGROUND_PRIMARY: #1a1a1a    // Main background
BACKGROUND_SECONDARY: #2a2a2a  // Cards, sidebar
BACKGROUND_TERTIARY: #333333   // Hover states

// Text
TEXT_PRIMARY: #e0e0e0          // Main text
TEXT_SECONDARY: #a0a0a0        // Subtitles, metadata
TEXT_ACCENT: #4a9eff           // Links, actions

// Status Colors
STATUS_COMPLETED: #4ade80      // Green
STATUS_PENDING: #ffbf00        // Amber
STATUS_ERROR: #f54338          // Red
```

### Typography
- **Large Headers**: 24px, Bold (task titles)
- **Section Headers**: 18px, Medium (status groups)  
- **Body Text**: 14px, Regular (descriptions)
- **Small Text**: 12px, Regular (timestamps)
- **Code Text**: 13px, Monospace (diffs)

### Layout Measurements
- **Sidebar Width**: 250px (expanded), 60px (collapsed)
- **Header Height**: 56px
- **Task Item Height**: 72px
- **Modal Max Width**: 500px
- **Border Radius**: 4px (small), 8px (medium), 12px (large)
- **Spacing**: 4px, 8px, 16px, 24px, 32px

## Development Timeline

### Phase 1: Foundation (Week 1)
- [x] Project setup and dependencies
- [x] Basic application structure  
- [x] Theme system implementation
- [x] Core component scaffolding
- [x] Mock data integration

### Phase 2: Core Components (Week 2)  
- [ ] Sidebar navigation component
- [ ] Header bar with breadcrumbs
- [ ] Task list with status groups
- [ ] Task item cards
- [ ] Basic modal dialogs

### Phase 3: API Integration (Week 3)
- [ ] HTTP client implementation
- [ ] Authentication flow
- [ ] Task CRUD operations
- [ ] Error handling and caching
- [ ] WebSocket real-time updates

### Phase 4: Advanced Features (Week 4)
- [ ] Code diff viewer
- [ ] GitHub integration
- [ ] Task detail view
- [ ] Comment system
- [ ] Search and filtering

### Phase 5: Polish & Testing (Week 5)
- [ ] Performance optimization
- [ ] Accessibility improvements
- [ ] Cross-platform testing
- [ ] Documentation completion
- [ ] Deployment preparation

## API Endpoints Reference

### Authentication
- `POST /auth/github` - GitHub OAuth login
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Tasks
- `GET /tasks` - List tasks with filtering
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get task details
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `POST /task/create-subtasks` - Generate AI subtasks

### Projects  
- `GET /projects` - List user projects
- `GET /github/list-repos` - List GitHub repositories
- `POST /github/import-issues` - Import GitHub issues

### Real-time
- `WS /ws` - WebSocket connection for live updates

## Key Implementation Notes

### State Management
- Use enum-based state machine for different views
- Implement message passing for component communication
- Cache API responses with TTL-based invalidation
- Handle loading states and error recovery

### Performance Considerations
- Implement virtual scrolling for large task lists
- Use lazy widgets for expensive components
- Cache rendered elements where appropriate
- Optimize WebSocket message handling

### Error Handling
- Comprehensive error types with user-friendly messages
- Retry logic with exponential backoff
- Offline mode graceful degradation
- Authentication error recovery

### Testing Strategy
- Unit tests for business logic
- Integration tests for API interactions
- Component tests for UI behavior
- Performance benchmarking

## Documentation Structure

1. **[01-ui-analysis.md](./01-ui-analysis.md)** - Detailed UI component analysis from screenshots
2. **[02-development-plan.md](./02-development-plan.md)** - Project structure and development phases
3. **[03-component-specs.md](./03-component-specs.md)** - Component specifications and implementation details
4. **[04-api-integration.md](./04-api-integration.md)** - API client and data model specifications
5. **[05-implementation-guide.md](./05-implementation-guide.md)** - Step-by-step implementation checklist

## Getting Started

1. **Review the UI Analysis** - Study the visual requirements in `01-ui-analysis.md`
2. **Set Up Development Environment** - Follow setup instructions in `05-implementation-guide.md`
3. **Implement Phase 1** - Start with foundation components per development plan
4. **Follow Component Specs** - Use detailed specifications in `03-component-specs.md`
5. **Integrate with API** - Connect to backend using patterns in `04-api-integration.md`

## Success Criteria

### Functional Requirements
- [ ] All core task management workflows functional
- [ ] Real-time updates working via WebSocket
- [ ] GitHub integration for issues and repositories
- [ ] Code diff viewing with syntax highlighting
- [ ] Cross-platform compatibility (Windows, macOS, Linux)

### Performance Requirements  
- [ ] Application startup < 3 seconds
- [ ] Task list rendering < 100ms for 1000 items
- [ ] UI interactions responsive at 60fps
- [ ] Memory usage < 100MB baseline

### Quality Requirements
- [ ] 90%+ code coverage with tests
- [ ] Zero accessibility violations
- [ ] Clean error handling throughout
- [ ] Comprehensive documentation

This overview provides the roadmap and reference material needed to successfully implement the Async-Server frontend using Iced.rs, ensuring consistency with the original design while leveraging Rust's performance and safety benefits.