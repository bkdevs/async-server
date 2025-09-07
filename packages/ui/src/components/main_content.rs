use iced::{
    alignment,
    widget::{button, column, container, row, scrollable, text},
    Color, Element, Length,
};

use crate::messages::Message;
use crate::models::{Task, TaskStatus};

pub struct MainContent;

impl MainContent {
    pub fn view(tasks: &[Task], expanded_sections: &[String]) -> Element<'static, Message> {
        container(
            scrollable(
                column![
                    Self::task_section(TaskStatus::PendingReview, tasks, expanded_sections),
                    Self::task_section(TaskStatus::PendingInput, tasks, expanded_sections),
                    Self::task_section(TaskStatus::Completed, tasks, expanded_sections),
                ]
                .spacing(32),
            )
            .height(Length::Fill),
        )
        .padding(24)
        .width(Length::Fill)
        .height(Length::Fill)
        .into()
    }

    fn task_section(
        status: TaskStatus,
        tasks: &[Task],
        expanded_sections: &[String],
    ) -> Element<'static, Message> {
        let section_label = status.label();
        let is_expanded = expanded_sections.contains(&section_label.to_string());
        let tasks_for_status: Vec<_> = tasks.iter().filter(|task| task.status == status).collect();

        if tasks_for_status.is_empty() {
            return container(text("")).into();
        }

        let header = button(
            row![
                text(if is_expanded { "▼" } else { "▶" })
                    .size(12)
                    .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                text(section_label)
                    .size(16)
                    .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))),
            ]
            .spacing(8)
            .align_items(alignment::Alignment::Center),
        )
        .on_press(Message::SectionToggled(section_label.to_string()))
        .style(iced::theme::Button::Text)
        .width(Length::Fill)
        .padding([8, 0]);

        let mut content = vec![header.into()];

        if is_expanded {
            for task in tasks_for_status {
                content.push(Self::task_item_clean(task));
            }
        }

        column(content).spacing(12).into()
    }

    fn task_item_clean(task: &Task) -> Element<'static, Message> {
        let github_info = if let Some(issue) = task.github_issue {
            format!("#{}", issue)
        } else {
            "".to_string()
        };

        let task_id = task.id.clone();
        let task_title = task.title.clone();
        let task_assignee = task.assignee.clone();
        let task_time_ago = task.time_ago.clone();
        let task_status = task.status.clone();

        button(
            row![
                // Status dot
                text("●")
                    .size(8)
                    .style(iced::theme::Text::Color(task_status.dot_color())),
                // User avatar placeholder
                container(text("👤"))
                    .width(24)
                    .height(24)
                    .center_x()
                    .center_y(),
                // Task content
                column![
                    text(task_title)
                        .size(14)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))),
                    text(task_assignee)
                        .size(12)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                ]
                .spacing(2),
                // Spacer
                container(text("")).width(Length::Fill),
                // Right side metadata
                column![
                    row![
                        if !github_info.is_empty() {
                            text("🔗").size(12)
                        } else {
                            text("")
                        },
                        text(github_info)
                            .size(12)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6)))
                    ]
                    .spacing(4),
                    text(task_time_ago)
                        .size(12)
                        .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6)))
                ]
                .spacing(2)
                .align_items(alignment::Alignment::End)
            ]
            .spacing(12)
            .align_items(alignment::Alignment::Center),
        )
        .on_press(Message::TaskClicked(task_id))
        .width(Length::Fill)
        .style(iced::theme::Button::Text)
        .padding([12, 8])
        .into()
    }
}
