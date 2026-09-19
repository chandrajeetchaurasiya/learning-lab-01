# StudyTrack

**Plan. Track. Improve.**

A study tracker for students, built with plain HTML, CSS and JavaScript. Log your study sessions, keep a task list, set a daily target and watch your weekly progress. Everything is saved in your own browser, so the app works offline and nothing is uploaded anywhere.

---

## Features

- **Dashboard** with a greeting, today's date, and four live statistics: today's study hours, daily target, progress percentage and completed tasks.
- **Daily progress bar** that fills toward your target and stops at 100%.
- **Quick add session** form with subject, topic, date, start time and end time. Duration is calculated for you and shown live while you type.
- **Validation** for empty fields, missing times, and end times that are not after the start time, with plain-language messages.
- **Session list** in a table that turns into stacked cards on small screens, sorted newest first, with edit and delete (delete asks for confirmation).
- **Search and filters** by topic, subject and date, applied live as you type.
- **Tasks** with subject, priority (Low / Medium / High), completed and pending states, strikethrough on completion, delete, and total / completed / pending counts.
- **Analytics**: a bar chart of the current week (Monday to Sunday) drawn with CSS, subject distribution bars, total hours, average hours per study day, most studied subject, completed tasks and current streak.
- **Study streak** counted from the actual dates you recorded sessions on.
- **Settings**: change the daily target, switch between light and dark mode, load demo data, and reset everything.
- **Empty states** in every section instead of blank space.
- **Responsive** from 320px phones up to large desktop screens, with keyboard-accessible controls and visible focus rings.

---

## Technologies Used

- HTML5 (semantic elements, labelled form controls, ARIA where it helps)
- CSS3 (custom properties for theming, Flexbox, Grid, media queries)
- Vanilla JavaScript (ES6+)
- Browser LocalStorage

No frameworks, no libraries, no build step.

---

## Project Structure

```text
study-tracker/
│
├── index.html      Page structure and all five sections
├── style.css       Theme variables, layout, components, responsive rules
├── script.js       Data handling, calculations, rendering, events
└── README.md       This file
```

---

## How to Run

1. Put `index.html`, `style.css` and `script.js` in the same folder.
2. Double-click `index.html`, or right-click it and open it with Chrome, Edge or Firefox.

In VS Code:

1. Open the `study-tracker` folder (**File → Open Folder**).
2. Open `index.html`.
3. Press **Ctrl + Shift + P → Open with Live Server**, or just open the file directly from your file manager.

No server, no installation and no internet connection are required.

---

## How LocalStorage Works

The app saves four keys in your browser:

| Key | What it stores |
| --- | --- |
| `studySessions` | Array of session objects |
| `tasks` | Array of task objects |
| `dailyTarget` | Your target in hours |
| `theme` | `"light"` or `"dark"` |

A session looks like this:

```javascript
{
    id: "m1k2j3abc",
    subject: "Java / DSA",
    topic: "Arrays",
    date: "2026-09-19",
    startTime: "19:00",
    endTime: "21:00",
    duration: 2
}
```

Every record gets its own unique `id`, so editing and deleting never depend on array positions. Dates are stored as plain calendar strings built from local date parts, which avoids the timezone shift you get from `toISOString()`. On startup the app checks the stored data and ignores anything that does not have the expected shape, so a corrupted value cannot break the page.

Data stays in one browser on one device. Clearing your browser data, or using private browsing, removes it.

---

## Future Improvements

- Export and import data as a JSON file
- Monthly view and longer-term trends
- Session notes and focus ratings
- Due dates and reminders for tasks
- Per-subject weekly targets

---

## Author

Built as a portfolio project for learning front-end development with HTML, CSS and JavaScript.
