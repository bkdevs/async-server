use iced::{
    alignment,
    widget::{button, column, container, row, text},
    Color, Element, Length,
};

use crate::messages::Message;

pub struct Sidebar;

impl Sidebar {
    pub fn view(selected_project: &str) -> Element<'static, Message> {
        container(
            column![
                // User profile section
                container(
                    row![
                        container(text("👤"))
                            .width(24)
                            .height(24)
                            .center_x()
                            .center_y(),
                        text("bkdevs")
                            .size(14)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))),
                        text("▼")
                            .size(12)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                    ]
                    .spacing(8)
                    .align_items(alignment::Alignment::Center)
                )
                .padding([16, 20]),
                // New task button
                container(
                    button(text("📝 New task").size(14))
                        .on_press(Message::NewTaskClicked)
                        .width(Length::Fill)
                        .style(iced::theme::Button::Primary)
                        .padding([10, 16])
                )
                .padding([0, 20, 16, 20]),
                // Inbox
                container(
                    button(
                        row![
                            text("📥").size(14),
                            text("Inbox")
                                .size(14)
                                .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9)))
                        ]
                        .spacing(8)
                        .align_items(alignment::Alignment::Center)
                    )
                    .on_press(Message::InboxClicked)
                    .width(Length::Fill)
                    .style(iced::theme::Button::Text)
                    .padding([6, 16])
                )
                .padding([0, 20, 20, 20]),
                // Projects section
                container(
                    column![
                        text("Projects")
                            .size(12)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                        column![
                            Self::project_item("📁", "async_app", "async_app", selected_project),
                            Self::project_item(
                                "📁",
                                "async-internal",
                                "async-internal",
                                selected_project
                            ),
                            Self::project_item(
                                "📁",
                                "async-desktop",
                                "async-desktop",
                                selected_project
                            ),
                            Self::project_item(
                                "📁",
                                "async-agent",
                                "async-agent",
                                selected_project
                            ),
                        ]
                        .spacing(4)
                    ]
                    .spacing(8)
                )
                .padding([0, 20, 20, 20]),
                // Tasks section
                container(
                    column![
                        text("Tasks")
                            .size(12)
                            .style(iced::theme::Text::Color(Color::from_rgb(0.6, 0.6, 0.6))),
                        column![
                            Self::sidebar_task_item("Make creating and following a..."),
                            Self::sidebar_task_item("Make the title truncate in the..."),
                            Self::sidebar_task_item("Migrate the credentials to env..."),
                        ]
                        .spacing(4)
                    ]
                    .spacing(8)
                )
                .padding([0, 20]),
            ]
            .spacing(0),
        )
        .width(250)
        .height(Length::Fill)
        .into()
    }

    fn project_item(
        icon: &str,
        name: &str,
        id: &str,
        selected_project: &str,
    ) -> Element<'static, Message> {
        let is_selected = selected_project == id;
        let text_color = if is_selected {
            iced::theme::Text::Color(Color::from_rgb(0.3, 0.6, 1.0))
        } else {
            iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))
        };

        button(
            row![text(icon).size(14), text(name).size(14).style(text_color)]
                .spacing(8)
                .align_items(alignment::Alignment::Center),
        )
        .on_press(Message::ProjectClicked(id.to_string()))
        .width(Length::Fill)
        .style(iced::theme::Button::Text)
        .padding([6, 16])
        .into()
    }

    fn sidebar_task_item(title: &str) -> Element<'static, Message> {
        button(
            row![
                text("•")
                    .size(14)
                    .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9))),
                text(title)
                    .size(13)
                    .style(iced::theme::Text::Color(Color::from_rgb(0.9, 0.9, 0.9)))
            ]
            .spacing(8)
            .align_items(alignment::Alignment::Center),
        )
        .on_press(Message::TaskClicked(title.to_string()))
        .width(Length::Fill)
        .style(iced::theme::Button::Text)
        .padding([6, 16])
        .into()
    }
}
