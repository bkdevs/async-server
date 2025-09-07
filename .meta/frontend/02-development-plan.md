# AGILE Development Plan for Async-Server Frontend (Iced.rs)

## AGILE Principles Applied

🎯 **Working Software from Day 1**  
🔄 **Iterative Development with 2-day sprints**  
📈 **Incremental Feature Growth**  
🚀 **Always Deployable**  
👥 **User Feedback Driven**  

## Project Structure (Minimal, Expandable)

```
async-frontend/
├── Cargo.toml              # Minimal deps, add as needed
├── src/
│   ├── main.rs            # Hello World → Full App
│   ├── app.rs             # Core loop, grows with features
│   └── lib.rs             # Export what we need
└── .env                   # Config from day 1
```

**Growing structure as we add features:**
- Day 3: Add `theme.rs` when we style
- Day 5: Add `api/` when we connect backend  
- Week 2: Add `components/` when UI grows
- Week 3: Add complex structures as needed

## SPRINT-BASED DEVELOPMENT (2-day sprints)

### 🚀 SPRINT 1 (Day 1-2): "Hello Async"
**DELIVERABLE**: Runnable desktop app with basic window

**Day 1 Morning** (2 hours)
```bash
cargo new async-frontend
cd async-frontend
# Add minimal Cargo.toml
cargo run  # MUST WORK!
```

**Day 1 Goals**:
- [ ] Empty Iced window opens ✅ WORKING APP
- [ ] Dark background color
- [ ] Window title "Async"
- [ ] Proper window size (1200x800)
- [ ] Can close window

**Day 2 Goals**:
- [ ] Add "Hello Async" text in center ✅ STILL WORKING
- [ ] Basic theme colors loaded
- [ ] Simple button that does nothing (but looks good)
- [ ] Logging setup (tracing)

**DEMO**: Show working desktop app to stakeholders

---

### 🎨 SPRINT 2 (Day 3-4): "Make it Look Right"
**DELIVERABLE**: App looks like the screenshots (empty but styled)

**Day 3 Goals**:
- [ ] Dark theme matching screenshots ✅ WORKING APP
- [ ] Sidebar area (empty, just colored rectangle)
- [ ] Header area (empty, just colored rectangle)  
- [ ] Main content area (empty)
- [ ] Proper layout structure

**Day 4 Goals**:
- [ ] Sidebar has user profile placeholder ✅ STILL WORKING
- [ ] Header has breadcrumb placeholder
- [ ] "Projects" and "Tasks" text in sidebar
- [ ] Basic typography (fonts, sizes)

**DEMO**: App looks like the real thing (but empty)

---

### 📝 SPRINT 3 (Day 5-6): "Mock Data Everywhere"  
**DELIVERABLE**: App shows fake tasks, looks completely real

**Day 5 Goals**:
- [ ] Hard-coded mock tasks in sidebar ✅ WORKING APP
- [ ] Hard-coded mock tasks in main area
- [ ] Task status dots (green, orange, etc.)
- [ ] Timestamps (fake but realistic)

**Day 6 Goals**:
- [ ] Task items clickable ✅ STILL WORKING
- [ ] Status groups (Pending Review, Completed, etc.)
- [ ] Hover effects on tasks
- [ ] GitHub issue numbers (#184, etc.)

**DEMO**: Fully functional-looking app with fake data

---

### 🔌 SPRINT 4 (Day 7-8): "Real Data Connection"
**DELIVERABLE**: App connects to real backend API

**Day 7 Goals**:
- [ ] HTTP client setup ✅ WORKING APP
- [ ] Connect to localhost:8889
- [ ] Load ONE real task from API
- [ ] Show real task in UI
- [ ] Handle connection errors gracefully

**Day 8 Goals**:
- [ ] Load ALL tasks from API ✅ STILL WORKING  
- [ ] Replace ALL mock data with real data
- [ ] Loading states while fetching
- [ ] Error states if API down

**DEMO**: Real data from backend in beautiful UI

---

### ✨ SPRINT 5 (Day 9-10): "Create Tasks"
**DELIVERABLE**: Can create new tasks

**Day 9 Goals**:
- [ ] "New Task" button works ✅ WORKING APP
- [ ] Simple modal dialog opens
- [ ] Text input for task title
- [ ] "Create" button (doesn't work yet)

**Day 10 Goals**:
- [ ] Create button calls API ✅ STILL WORKING
- [ ] New task appears in list immediately
- [ ] Modal closes after creation
- [ ] Success feedback to user

**DEMO**: End-to-end task creation workflow

---

### 🔄 SPRINT 6 (Day 11-12): "Real-time Updates"
**DELIVERABLE**: Tasks update live when changed elsewhere

**Day 11 Goals**:
- [ ] WebSocket connection to backend ✅ WORKING APP
- [ ] Receive task update messages
- [ ] Update UI when task changes
- [ ] Handle connection drops

**Day 12 Goals**:  
- [ ] Optimistic UI updates ✅ STILL WORKING
- [ ] Retry failed operations
- [ ] Show connection status
- [ ] Smooth animations for changes

**DEMO**: Multi-user real-time collaboration

---

### 📋 SPRINT 7 (Day 13-14): "Task Management"
**DELIVERABLE**: Full task lifecycle management

**Day 13 Goals**:
- [ ] Click task to see details ✅ WORKING APP
- [ ] Task detail view (basic)  
- [ ] Back button to task list
- [ ] Edit task title inline

**Day 14 Goals**:
- [ ] Change task status (dropdown) ✅ STILL WORKING
- [ ] Delete tasks (with confirmation)
- [ ] Assign tasks to users
- [ ] Due dates and priorities

**DEMO**: Complete task management workflows

---

### 🎯 SPRINT 8 (Day 15-16): "GitHub Integration" 
**DELIVERABLE**: GitHub repos and issues integrated

**Day 15 Goals**:
- [ ] List GitHub repositories ✅ WORKING APP
- [ ] Import issues from GitHub
- [ ] Show GitHub issue numbers
- [ ] Link to GitHub issue pages

**Day 16 Goals**:
- [ ] Create GitHub issues from tasks ✅ STILL WORKING
- [ ] Sync task status with issue status  
- [ ] Show commit references
- [ ] Basic code diff viewer

**DEMO**: Seamless GitHub workflow integration

---

## CONTINUOUS INTEGRATION APPROACH

### Every Day Requirements:
- [ ] `cargo run` MUST work
- [ ] App opens without crashes
- [ ] Previous features still work
- [ ] New feature demonstrated to team
- [ ] Code committed to version control

### Every Sprint Requirements:
- [ ] Demo to stakeholders
- [ ] User feedback collected
- [ ] Next sprint planned based on feedback
- [ ] Performance acceptable (< 3sec startup)
- [ ] No memory leaks

## TECHNICAL DEBT MANAGEMENT

### Refactor Triggers:
- **File > 200 lines** → Split into modules
- **Function > 50 lines** → Break down  
- **Copy-paste code** → Extract common patterns
- **Hard-coded values** → Move to config
- **Slow performance** → Profile and optimize

### Architecture Evolution:
```rust
// Day 1: Everything in main.rs
fn main() { /* simple app */ }

// Day 3: Split into modules
mod app; mod theme;

// Day 7: Add API layer  
mod api; mod models;

// Day 11: Add state management
mod state; mod messages;
```

## RISK MITIGATION

### Daily Risks:
- **Iced.rs learning curve** → Start simple, grow complexity
- **API connection issues** → Always have fallback mock data
- **Complex UI requirements** → Break into smallest possible pieces
- **Performance problems** → Profile early, optimize incrementally

### Technical Spikes (when stuck):
- **Max 4 hours research** on any blocker
- **Always produce working code** even if hacky
- **Document limitations** for future sprints
- **Get help from community** (Iced.rs Discord, etc.)

## SUCCESS METRICS

### Daily Success:
- ✅ App runs without crashes
- ✅ New feature visible to users
- ✅ Team can demo progress
- ✅ Code quality maintained

### Sprint Success:
- ✅ Stakeholder demo completed
- ✅ User feedback incorporated
- ✅ Technical debt managed
- ✅ Performance targets met

### Release Success:
- ✅ All core workflows functional
- ✅ Real users can accomplish tasks
- ✅ Stable performance under load
- ✅ Positive user feedback

## ADAPTIVE PLANNING

### Velocity Tracking:
- **Sprint 1**: Establish baseline velocity
- **Sprint 2-3**: Adjust story points based on actual completion
- **Sprint 4+**: Predict completion dates with confidence

### Scope Flexibility:
- **Core Features** (Must Have): Task CRUD, GitHub sync
- **Important Features** (Should Have): Real-time updates, code diffs  
- **Nice Features** (Could Have): Advanced filtering, bulk operations
- **Future Features** (Won't Have): AI assistance, mobile app

### Feedback Integration:
- **Daily**: Team feedback on technical approach
- **Sprint**: Stakeholder feedback on features
- **Release**: User feedback on overall experience

This AGILE approach ensures we have a **working, demoable application from Day 1** that grows in capability every single day. No more waterfall nonsense - we build real value incrementally! 🚀