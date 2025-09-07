# AGILE Implementation Guide - Day 1 Focus

## 🚀 DAY 1 MISSION: "Hello Async" in 2 Hours

### Goal: Working Desktop App You Can Demo

**Success Criteria:**
- [ ] `cargo run` opens a window
- [ ] Window says "Hello Async"
- [ ] Dark background like the screenshots
- [ ] Window can be closed
- [ ] Looks professional enough to show stakeholders

---

## SPRINT 1 - DAY 1 IMPLEMENTATION

### Step 1: Create Project (15 minutes)

```bash
# Create the project
cargo new async-frontend --name async-frontend
cd async-frontend

# Initialize git
git init
echo "target/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
```

### Step 2: Minimal Cargo.toml (10 minutes)

Replace `Cargo.toml` with:

```toml
[package]
name = "async-frontend"
version = "0.1.0"
edition = "2021"

[dependencies]
iced = { version = "0.12", features = ["advanced"] }
```

**Test it works:**
```bash
cargo check  # MUST succeed
```

### Step 3: Hello World App (30 minutes)

Replace `src/main.rs` with:

```rust
use iced::{
    widget::{container, text},
    Application, Command, Element, Length, Settings, Theme,
};

#[derive(Debug, Clone)]
pub enum Message {}

pub struct AsyncApp;

impl Application for AsyncApp {
    type Message = Message;
    type Theme = Theme;
    type Executor = iced::executor::Default;
    type Flags = ();

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (AsyncApp, Command::none())
    }

    fn title(&self) -> String {
        "Async".to_string()
    }

    fn update(&mut self, _message: Message) -> Command<Message> {
        Command::none()
    }

    fn view(&self) -> Element<Message> {
        container(
            text("Hello Async")
                .size(32)
                .style(iced::Color::WHITE)
        )
        .width(Length::Fill)
        .height(Length::Fill)
        .center_x()
        .center_y()
        .style(|_theme| container::Appearance {
            background: Some(iced::Background::Color(iced::Color::from_rgb(0.1, 0.1, 0.1))),
            ..Default::default()
        })
        .into()
    }

    fn theme(&self) -> Theme {
        Theme::Dark
    }
}

fn main() -> iced::Result {
    AsyncApp::run(Settings {
        window: iced::window::Settings {
            size: (1200, 800),
            ..Default::default()
        },
        ..Settings::default()
    })
}
```

**Test it works:**
```bash
cargo run  # MUST open a dark window with "Hello Async"
```

### Step 4: Make it Look Professional (30 minutes)

Update the `view()` method to look more like the real app:

```rust
fn view(&self) -> Element<Message> {
    use iced::widget::{row, column};
    
    let sidebar = container(
        column![
            text("bkdevs").size(16).style(iced::Color::WHITE),
            text("").height(20), // spacer
            text("Projects").size(14).style(iced::Color::from_rgb(0.6, 0.6, 0.6)),
            text("• async-desktop").size(14).style(iced::Color::WHITE),
            text("").height(20), // spacer
            text("Tasks").size(14).style(iced::Color::from_rgb(0.6, 0.6, 0.6)),
            text("• Create new task").size(14).style(iced::Color::WHITE),
        ]
        .padding(20)
    )
    .width(250)
    .height(Length::Fill)
    .style(|_theme| container::Appearance {
        background: Some(iced::Background::Color(iced::Color::from_rgb(0.16, 0.16, 0.16))),
        ..Default::default()
    });

    let header = container(
        text("Dashboard").size(18).style(iced::Color::WHITE)
    )
    .width(Length::Fill)
    .height(60)
    .padding(20)
    .style(|_theme| container::Appearance {
        background: Some(iced::Background::Color(iced::Color::from_rgb(0.16, 0.16, 0.16))),
        ..Default::default()
    });

    let main_content = container(
        text("Tasks will appear here...")
            .size(16)
            .style(iced::Color::from_rgb(0.6, 0.6, 0.6))
    )
    .width(Length::Fill)
    .height(Length::Fill)
    .center_x()
    .center_y()
    .style(|_theme| container::Appearance {
        background: Some(iced::Background::Color(iced::Color::from_rgb(0.1, 0.1, 0.1))),
        ..Default::default()
    });

    row![
        sidebar,
        column![header, main_content]
    ]
    .into()
}
```

**Test it works:**
```bash
cargo run  # MUST look like a real task management app
```

### Step 5: Add Basic Interaction (25 minutes)

Add a working button:

```rust
#[derive(Debug, Clone)]
pub enum Message {
    ButtonPressed,
}

pub struct AsyncApp {
    button_count: u32,
}

impl Application for AsyncApp {
    // ... same type definitions ...

    fn new(_flags: ()) -> (Self, Command<Message>) {
        (AsyncApp { button_count: 0 }, Command::none())
    }

    fn update(&mut self, message: Message) -> Command<Message> {
        match message {
            Message::ButtonPressed => {
                self.button_count += 1;
                Command::none()
            }
        }
    }

    fn view(&self) -> Element<Message> {
        use iced::widget::{row, column, button};
        
        // ... same sidebar code ...

        let main_content = container(
            column![
                text(format!("Button pressed {} times", self.button_count))
                    .size(16)
                    .style(iced::Color::WHITE),
                text("").height(20),
                button("New Task")
                    .on_press(Message::ButtonPressed)
                    .style(|theme, status| button::Appearance {
                        background: Some(iced::Background::Color(iced::Color::from_rgb(0.29, 0.62, 1.0))),
                        text_color: iced::Color::WHITE,
                        border: iced::Border::with_radius(4),
                        ..button::primary(theme, status)
                    })
            ]
        )
        .width(Length::Fill)
        .height(Length::Fill)
        .center_x()
        .center_y()
        .style(|_theme| container::Appearance {
            background: Some(iced::Background::Color(iced::Color::from_rgb(0.1, 0.1, 0.1))),
            ..Default::default()
        });

        row![
            sidebar,
            column![header, main_content]
        ]
        .into()
    }
}
```

**Test it works:**
```bash
cargo run  # Button must work, counter must increment
```

---

## DAY 1 SUCCESS CHECKLIST

- [ ] App opens without errors
- [ ] Dark theme matches screenshots  
- [ ] Sidebar shows projects and tasks
- [ ] Header shows "Dashboard"
- [ ] Main area has working button
- [ ] Button interaction works (counter updates)
- [ ] App looks professional (could demo to client)
- [ ] Code is clean and readable
- [ ] `git commit -m "Day 1: Working Async desktop app"`

---

## DAY 2 SPRINT GOALS

### Morning (2 hours): Theme System
- [ ] Extract colors to constants
- [ ] Create proper theme module
- [ ] Match exact colors from screenshots
- [ ] Add hover states to buttons

### Afternoon (2 hours): Better Layout
- [ ] Proper spacing and padding
- [ ] Add icons (simple Unicode for now)
- [ ] Sidebar profile section with avatar placeholder
- [ ] Header breadcrumbs placeholder

**Day 2 Success**: App looks identical to screenshots (but still with placeholder content)

---

## AGILE DEVELOPMENT PRINCIPLES

### Every Day Must Deliver:
1. **Working Software** - App must run without crashes
2. **Visible Progress** - New feature user can see/use
3. **Demo Ready** - Always ready to show stakeholders
4. **Clean Code** - Readable, maintainable, no hacks
5. **Git Commit** - Progress saved and documented

### When Things Go Wrong:
- **Stuck for 1 hour?** → Ask for help
- **Feature too complex?** → Break it smaller
- **Iced.rs problem?** → Find simpler approach
- **Running behind?** → Cut scope, not quality

### Growth Strategy:
- **Week 1**: Static UI that looks perfect
- **Week 2**: Add real data (hardcoded first)
- **Week 3**: Connect to API
- **Week 4**: Add advanced features
- **Always**: Keep the app working and demoable

---

## TECHNICAL DEBT RULES

### Allowed Technical Debt:
- [ ] Hardcoded values (fix in next sprint)
- [ ] Copy-pasted code (refactor when 3+ copies)
- [ ] TODO comments (if tracked in backlog)
- [ ] Simple error handling (improve incrementally)

### Forbidden Technical Debt:
- ❌ Crashes or panics
- ❌ Broken features
- ❌ Non-compiling code
- ❌ Performance problems

---

## SUCCESS METRICS

### Day 1 Success:
- ✅ Stakeholder can see working app
- ✅ Team confidence in approach
- ✅ Technical foundation solid
- ✅ Clear path to Day 2

### Week 1 Success:
- ✅ App looks indistinguishable from original
- ✅ All major UI components present
- ✅ Smooth interactions and animations
- ✅ Ready for real data integration

### Project Success:
- ✅ Users choose our app over alternatives
- ✅ Performance better than web version
- ✅ Cross-platform compatibility
- ✅ Community adoption and contributions

This AGILE approach ensures you have a **working, impressive application from Day 1** that grows in capability every single day. No waterfall planning - just working software that gets better continuously! 🚀