/* ==========================================================================
   StudyTrack — script.js
   Plain JavaScript (ES6+). No libraries, no build tools.

   Structure:
   1.  Constants and app state
   2.  LocalStorage helpers
   3.  Date and time helpers
   4.  Small utilities
   5.  Calculations (hours, progress, weekly stats, streak)
   6.  Rendering (dashboard, sessions, tasks, analytics)
   7.  Sessions: add / edit / delete
   8.  Tasks: add / toggle / delete
   9.  Filters and search
   10. Settings: target, theme, demo data, reset
   11. Navigation
   12. Start the app
   ========================================================================== */

'use strict';

/* ---------- 1. CONSTANTS AND APP STATE ---------- */

const STORAGE_KEYS = {
    sessions: 'studySessions',
    tasks: 'tasks',
    target: 'dailyTarget',
    theme: 'theme'
};

const DEFAULT_TARGET = 9;
const SUBJECTS = ['Java / DSA', 'Aptitude', 'English', 'College Work', 'Web Development', 'Other'];
const PRIORITIES = ['Low', 'Medium', 'High'];
const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

// Application data. Loaded from LocalStorage when the app starts.
let studySessions = [];
let tasks = [];
let dailyTarget = DEFAULT_TARGET;

// Id of the session currently being edited (null when adding a new one).
let editingSessionId = null;

// Timer id for the toast message.
let toastTimer = null;

/* Short helper so the code below stays readable. */
function $(id) {
    return document.getElementById(id);
}

/* ---------- 2. LOCALSTORAGE HELPERS ---------- */

/**
 * Reads a value from LocalStorage and parses it.
 * Returns the fallback when the key is missing or the stored value is broken.
 */
function readStorage(key, fallback) {
    try {
        const raw = localStorage.getItem(key);
        if (raw === null) {
            return fallback;
        }
        return JSON.parse(raw);
    } catch (error) {
        console.warn('Could not read "' + key + '" from LocalStorage.', error);
        return fallback;
    }
}

function writeStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.warn('Could not save "' + key + '" to LocalStorage.', error);
        showToast('Saving failed. Your browser storage may be full or blocked.');
    }
}

/** Loads every piece of data and cleans out anything invalid. */
function loadData() {
    const storedSessions = readStorage(STORAGE_KEYS.sessions, []);
    studySessions = Array.isArray(storedSessions) ? storedSessions.filter(isValidSession) : [];

    const storedTasks = readStorage(STORAGE_KEYS.tasks, []);
    tasks = Array.isArray(storedTasks) ? storedTasks.filter(isValidTask) : [];

    const storedTarget = Number(readStorage(STORAGE_KEYS.target, DEFAULT_TARGET));
    dailyTarget = isValidTarget(storedTarget) ? storedTarget : DEFAULT_TARGET;
}

function saveData() {
    writeStorage(STORAGE_KEYS.sessions, studySessions);
    writeStorage(STORAGE_KEYS.tasks, tasks);
    writeStorage(STORAGE_KEYS.target, dailyTarget);
}

function isValidSession(session) {
    return Boolean(session) &&
        typeof session === 'object' &&
        typeof session.id === 'string' &&
        typeof session.subject === 'string' &&
        typeof session.topic === 'string' &&
        isISODate(session.date) &&
        isTimeString(session.startTime) &&
        isTimeString(session.endTime) &&
        typeof session.duration === 'number' &&
        session.duration > 0;
}

function isValidTask(task) {
    return Boolean(task) &&
        typeof task === 'object' &&
        typeof task.id === 'string' &&
        typeof task.title === 'string' &&
        typeof task.subject === 'string' &&
        PRIORITIES.indexOf(task.priority) !== -1 &&
        typeof task.completed === 'boolean';
}

function isValidTarget(value) {
    return typeof value === 'number' && isFinite(value) && value > 0 && value <= 24;
}

/* ---------- 3. DATE AND TIME HELPERS ---------- */

/**
 * Dates are stored as plain calendar strings ("2026-09-19") and are always
 * built from local date parts, so no timezone shifting can happen.
 */
function toISODate(dateObject) {
    const year = dateObject.getFullYear();
    const month = String(dateObject.getMonth() + 1).padStart(2, '0');
    const day = String(dateObject.getDate()).padStart(2, '0');
    return year + '-' + month + '-' + day;
}

function todayISO() {
    return toISODate(new Date());
}

/** Turns "2026-09-19" into a local Date at midnight. */
function parseISODate(isoString) {
    const parts = isoString.split('-');
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
}

function addDays(dateObject, amount) {
    const copy = new Date(dateObject.getFullYear(), dateObject.getMonth(), dateObject.getDate());
    copy.setDate(copy.getDate() + amount);
    return copy;
}

function isISODate(value) {
    return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value);
}

function isTimeString(value) {
    return typeof value === 'string' && /^\d{2}:\d{2}$/.test(value);
}

/** "19:30" -> 1170 minutes since midnight. */
function timeToMinutes(timeString) {
    const parts = timeString.split(':');
    return Number(parts[0]) * 60 + Number(parts[1]);
}

/** Hours between two times, rounded to two decimals. */
function calculateDuration(startTime, endTime) {
    const minutes = timeToMinutes(endTime) - timeToMinutes(startTime);
    return Math.round((minutes / 60) * 100) / 100;
}

function formatLongDate(dateObject) {
    return dateObject.toLocaleDateString(undefined, {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    });
}

function formatShortDate(isoString) {
    return parseISODate(isoString).toLocaleDateString(undefined, {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

/** Monday of the week that contains the given date. */
function startOfWeek(dateObject) {
    const day = dateObject.getDay();          // 0 = Sunday
    const shift = day === 0 ? -6 : 1 - day;   // move back to Monday
    return addDays(dateObject, shift);
}

/* ---------- 4. SMALL UTILITIES ---------- */

function createId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

/** Escapes text before it goes into innerHTML. */
function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/** 2 -> "2 hrs", 1.5 -> "1.5 hrs", 1 -> "1 hr" */
function formatHours(hours) {
    const rounded = Math.round(hours * 100) / 100;
    const text = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
    return text + (rounded === 1 ? ' hr' : ' hrs');
}

function showToast(message) {
    const toast = $('toast');
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
        toast.hidden = true;
    }, 2800);
}

function showError(elementId, message) {
    const element = $(elementId);
    element.textContent = message;
    element.hidden = false;
}

function hideError(elementId) {
    const element = $(elementId);
    element.textContent = '';
    element.hidden = true;
}

/* ---------- 5. CALCULATIONS ---------- */

/** Total study hours for one calendar date. */
function calculateStudyHours(isoDate) {
    return studySessions.reduce(function (total, session) {
        return session.date === isoDate ? total + session.duration : total;
    }, 0);
}

function calculateTotalHours() {
    return studySessions.reduce(function (total, session) {
        return total + session.duration;
    }, 0);
}

/** Progress for today, capped at 100%. */
function calculateProgress() {
    if (!isValidTarget(dailyTarget)) {
        return 0;
    }
    const percent = (calculateStudyHours(todayISO()) / dailyTarget) * 100;
    return Math.min(100, Math.round(percent));
}

/** Hours for each day of the current week, Monday to Sunday. */
function calculateWeeklyStats() {
    const monday = startOfWeek(new Date());
    const week = [];

    for (let index = 0; index < 7; index++) {
        const day = addDays(monday, index);
        const iso = toISODate(day);
        week.push({
            label: WEEKDAY_LABELS[index],
            date: iso,
            hours: calculateStudyHours(iso),
            isToday: iso === todayISO()
        });
    }
    return week;
}

/** Hours per subject, biggest first. Subjects with no time are skipped. */
function calculateSubjectTotals() {
    const totals = {};

    studySessions.forEach(function (session) {
        totals[session.subject] = (totals[session.subject] || 0) + session.duration;
    });

    return Object.keys(totals)
        .map(function (subject) {
            return { subject: subject, hours: totals[subject] };
        })
        .sort(function (a, b) {
            return b.hours - a.hours;
        });
}

/**
 * Counts consecutive days with at least one session, ending today.
 * If nothing was studied today but yesterday was studied, the streak
 * is still counted from yesterday so the day is not lost yet.
 */
function calculateStreak() {
    if (studySessions.length === 0) {
        return 0;
    }

    const studiedDates = {};
    studySessions.forEach(function (session) {
        studiedDates[session.date] = true;
    });

    const today = new Date();
    let cursor = today;

    if (!studiedDates[toISODate(today)]) {
        cursor = addDays(today, -1);
        if (!studiedDates[toISODate(cursor)]) {
            return 0;
        }
    }

    let streak = 0;
    while (studiedDates[toISODate(cursor)]) {
        streak++;
        cursor = addDays(cursor, -1);
    }
    return streak;
}

function countCompletedTasks() {
    return tasks.filter(function (task) {
        return task.completed;
    }).length;
}

/* ---------- 6. RENDERING ---------- */

function renderAll() {
    renderDashboard();
    renderSessions();
    renderTasks();
    renderAnalytics();
}

function renderGreeting() {
    const now = new Date();
    const hour = now.getHours();
    let greeting = 'Good Evening';

    if (hour < 12) {
        greeting = 'Good Morning';
    } else if (hour < 17) {
        greeting = 'Good Afternoon';
    }

    $('dashboardHeading').textContent = greeting + ', Student 👋';
    $('todayDate').textContent = formatLongDate(now);
}

function renderDashboard() {
    const today = todayISO();
    const todayHours = calculateStudyHours(today);
    const progress = calculateProgress();
    const completedTasks = countCompletedTasks();
    const todaySessionCount = studySessions.filter(function (session) {
        return session.date === today;
    }).length;

    $('statTodayHours').textContent = formatHours(todayHours);
    $('statSessionCount').textContent = todaySessionCount === 0
        ? 'No sessions logged today'
        : todaySessionCount + (todaySessionCount === 1 ? ' session today' : ' sessions today');

    $('statTarget').textContent = formatHours(dailyTarget);
    $('statProgress').textContent = progress + '%';

    const remaining = Math.max(0, dailyTarget - todayHours);
    $('statRemaining').textContent = remaining === 0
        ? 'Target reached. Well done.'
        : formatHours(remaining) + ' left today';

    $('statTasksRatio').textContent = completedTasks + ' / ' + tasks.length;
    $('statTasksHint').textContent = tasks.length === 0
        ? 'No tasks added yet'
        : (tasks.length - completedTasks) + ' still pending';

    // Progress bar
    const roundedToday = Math.round(todayHours * 100) / 100;
    $('progressText').textContent = roundedToday + ' / ' + dailyTarget + ' hours';
    $('progressFill').style.width = progress + '%';
    $('progressBar').setAttribute('aria-valuenow', String(progress));

    if (todayHours === 0) {
        $('progressCaption').textContent = 'Log your first session to start today\u2019s progress.';
    } else if (progress >= 100) {
        $('progressCaption').textContent = 'You hit your daily target. Anything else today is a bonus.';
    } else {
        $('progressCaption').textContent = 'You are ' + progress + '% of the way to today\u2019s target.';
    }

    // Streak chip
    const streak = calculateStreak();
    $('streakChip').textContent = streak === 0
        ? '🔥 No streak yet'
        : '🔥 ' + streak + (streak === 1 ? ' Day Study Streak' : ' Day Study Streak');
}

/** Returns the sessions that match the current search and filters, newest first. */
function filterSessions() {
    const searchTerm = $('searchInput').value.trim().toLowerCase();
    const subjectFilter = $('filterSubject').value;
    const dateFilter = $('filterDate').value;

    return studySessions
        .filter(function (session) {
            const matchesSearch = searchTerm === '' ||
                session.topic.toLowerCase().includes(searchTerm) ||
                session.subject.toLowerCase().includes(searchTerm);
            const matchesSubject = subjectFilter === '' || session.subject === subjectFilter;
            const matchesDate = dateFilter === '' || session.date === dateFilter;
            return matchesSearch && matchesSubject && matchesDate;
        })
        .sort(function (a, b) {
            // Newest date first, then latest start time first.
            if (a.date !== b.date) {
                return a.date < b.date ? 1 : -1;
            }
            return timeToMinutes(b.startTime) - timeToMinutes(a.startTime);
        });
}

function renderSessions() {
    const visibleSessions = filterSessions();
    const tableBody = $('sessionTableBody');
    const table = $('sessionTable');
    const emptyState = $('sessionEmpty');

    tableBody.innerHTML = '';

    $('sessionSummary').textContent = visibleSessions.length +
        (visibleSessions.length === 1 ? ' session' : ' sessions') +
        (visibleSessions.length !== studySessions.length ? ' of ' + studySessions.length : '');

    if (visibleSessions.length === 0) {
        table.hidden = true;
        emptyState.hidden = false;
        emptyState.textContent = studySessions.length === 0
            ? 'No study sessions yet. Add your first session to start tracking your progress.'
            : 'No sessions match your search. Try a different subject or date.';
        return;
    }

    table.hidden = false;
    emptyState.hidden = true;

    visibleSessions.forEach(function (session) {
        const row = document.createElement('tr');
        row.innerHTML =
            '<td data-label="Date">' + escapeHtml(formatShortDate(session.date)) + '</td>' +
            '<td data-label="Subject"><span class="tag">' + escapeHtml(session.subject) + '</span></td>' +
            '<td data-label="Topic">' + escapeHtml(session.topic) + '</td>' +
            '<td data-label="Start">' + escapeHtml(session.startTime) + '</td>' +
            '<td data-label="End">' + escapeHtml(session.endTime) + '</td>' +
            '<td data-label="Duration">' + escapeHtml(formatHours(session.duration)) + '</td>' +
            '<td class="cell-actions">' +
                '<button class="button button-outline button-small" type="button" data-edit-session="' + session.id + '">Edit</button>' +
                '<button class="button button-ghost button-small" type="button" data-delete-session="' + session.id + '">Delete</button>' +
            '</td>';
        tableBody.appendChild(row);
    });
}

function renderTasks() {
    const list = $('taskList');
    const emptyState = $('taskEmpty');
    const completed = countCompletedTasks();

    $('statTotalTasks').textContent = String(tasks.length);
    $('statDoneTasks').textContent = String(completed);
    $('statPendingTasks').textContent = String(tasks.length - completed);

    list.innerHTML = '';

    if (tasks.length === 0) {
        emptyState.hidden = false;
        return;
    }
    emptyState.hidden = true;

    // Pending tasks first, then completed ones.
    const sortedTasks = tasks.slice().sort(function (a, b) {
        return Number(a.completed) - Number(b.completed);
    });

    sortedTasks.forEach(function (task) {
        const item = document.createElement('li');
        item.className = 'task-item' + (task.completed ? ' is-done' : '');
        item.innerHTML =
            '<button class="task-check" type="button" data-toggle-task="' + task.id + '" ' +
                'aria-pressed="' + task.completed + '" ' +
                'aria-label="' + (task.completed ? 'Mark as pending: ' : 'Mark as completed: ') + escapeHtml(task.title) + '">✓</button>' +
            '<div class="task-body">' +
                '<p class="task-title">' + escapeHtml(task.title) + '</p>' +
                '<div class="task-meta">' +
                    '<span class="tag">' + escapeHtml(task.subject) + '</span>' +
                    '<span class="priority priority-' + task.priority.toLowerCase() + '">' + escapeHtml(task.priority) + '</span>' +
                    '<span>' + (task.completed ? 'Completed' : 'Pending') + '</span>' +
                '</div>' +
            '</div>' +
            '<button class="button button-ghost button-small" type="button" data-delete-task="' + task.id + '">Delete</button>';
        list.appendChild(item);
    });
}

function renderAnalytics() {
    renderWeeklyChart();
    renderSubjectDistribution();
    renderAnalyticsStats();
}

function renderWeeklyChart() {
    const week = calculateWeeklyStats();
    const chart = $('weeklyChart');
    const emptyState = $('weeklyEmpty');
    const maxHours = Math.max.apply(null, week.map(function (day) { return day.hours; }));

    const monday = startOfWeek(new Date());
    $('weeklyRange').textContent = formatShortDate(toISODate(monday)) + ' – ' +
        formatShortDate(toISODate(addDays(monday, 6)));

    chart.innerHTML = '';

    if (maxHours === 0) {
        chart.hidden = true;
        emptyState.hidden = false;
        return;
    }

    chart.hidden = false;
    emptyState.hidden = true;

    week.forEach(function (day) {
        // Bar height is a percentage of the tallest bar of the week.
        const heightPercent = maxHours === 0 ? 0 : (day.hours / maxHours) * 100;
        const column = document.createElement('div');
        column.className = 'chart-column';
        column.innerHTML =
            '<span class="chart-value">' + (day.hours > 0 ? Math.round(day.hours * 10) / 10 + 'h' : '0') + '</span>' +
            '<div class="chart-bar' + (day.hours === 0 ? ' is-empty' : '') + (day.isToday ? ' is-today' : '') + '" ' +
                'style="height:' + Math.max(heightPercent, day.hours > 0 ? 4 : 1) + '%" ' +
                'title="' + day.label + ': ' + formatHours(day.hours) + '"></div>' +
            '<span class="chart-label">' + day.label + '</span>';
        chart.appendChild(column);
    });
}

function renderSubjectDistribution() {
    const totals = calculateSubjectTotals();
    const list = $('subjectList');
    const emptyState = $('subjectEmpty');

    list.innerHTML = '';

    if (totals.length === 0) {
        emptyState.hidden = false;
        return;
    }
    emptyState.hidden = true;

    const maxHours = totals[0].hours;

    totals.forEach(function (entry) {
        const widthPercent = (entry.hours / maxHours) * 100;
        const item = document.createElement('li');
        item.innerHTML =
            '<div class="subject-row-head">' +
                '<span>' + escapeHtml(entry.subject) + '</span>' +
                '<span class="subject-hours">' + escapeHtml(formatHours(entry.hours)) + '</span>' +
            '</div>' +
            '<div class="progress-track">' +
                '<div class="progress-fill" style="width:' + widthPercent + '%"></div>' +
            '</div>';
        list.appendChild(item);
    });
}

function renderAnalyticsStats() {
    const totalHours = calculateTotalHours();
    const subjectTotals = calculateSubjectTotals();

    // Average is per day actually studied, so empty days do not distort it.
    const studyDays = {};
    studySessions.forEach(function (session) {
        studyDays[session.date] = true;
    });
    const dayCount = Object.keys(studyDays).length;
    const average = dayCount === 0 ? 0 : totalHours / dayCount;
    const streak = calculateStreak();

    $('statTotalHours').textContent = formatHours(totalHours);
    $('statAvgHours').textContent = formatHours(average);
    $('statTopSubject').textContent = subjectTotals.length === 0 ? '—' : subjectTotals[0].subject;
    $('statTasksDone').textContent = String(countCompletedTasks());
    $('statStreak').textContent = streak + (streak === 1 ? ' day' : ' days');
}

/* ---------- 7. SESSIONS: ADD / EDIT / DELETE ---------- */

/** Reads the session form and returns { valid, data, message }. */
function readSessionForm() {
    const subject = $('sessionSubject').value;
    const topic = $('sessionTopic').value.trim();
    const date = $('sessionDate').value;
    const startTime = $('sessionStart').value;
    const endTime = $('sessionEnd').value;

    if (!subject) {
        return { valid: false, message: 'Choose a subject for this session.' };
    }
    if (topic === '') {
        return { valid: false, message: 'Add a topic so you know what you studied.' };
    }
    if (!isISODate(date)) {
        return { valid: false, message: 'Pick the date of the session.' };
    }
    if (!isTimeString(startTime) || !isTimeString(endTime)) {
        return { valid: false, message: 'Enter both a start time and an end time.' };
    }
    if (timeToMinutes(endTime) <= timeToMinutes(startTime)) {
        return { valid: false, message: 'End time must be later than start time.' };
    }

    return {
        valid: true,
        data: {
            subject: subject,
            topic: topic,
            date: date,
            startTime: startTime,
            endTime: endTime,
            duration: calculateDuration(startTime, endTime)
        }
    };
}

function handleSessionSubmit(event) {
    event.preventDefault();
    const result = readSessionForm();

    if (!result.valid) {
        showError('sessionError', result.message);
        return;
    }
    hideError('sessionError');

    if (editingSessionId) {
        updateStudySession(editingSessionId, result.data);
    } else {
        addStudySession(result.data);
    }
}

function addStudySession(data) {
    const session = {
        id: createId(),
        subject: data.subject,
        topic: data.topic,
        date: data.date,
        startTime: data.startTime,
        endTime: data.endTime,
        duration: data.duration
    };

    studySessions.push(session);
    saveData();
    resetSessionForm();
    renderAll();
    showToast('Session added: ' + formatHours(session.duration) + ' of ' + session.subject + '.');
}

/** Fills the form so the user can change an existing session. */
function editStudySession(id) {
    const session = studySessions.find(function (item) {
        return item.id === id;
    });
    if (!session) {
        showToast('That session no longer exists.');
        return;
    }

    editingSessionId = id;
    $('sessionSubject').value = session.subject;
    $('sessionTopic').value = session.topic;
    $('sessionDate').value = session.date;
    $('sessionStart').value = session.startTime;
    $('sessionEnd').value = session.endTime;

    $('sessionFormHeading').textContent = 'Edit session';
    $('sessionSubmitBtn').textContent = 'Save changes';
    $('sessionCancelBtn').hidden = false;
    hideError('sessionError');
    updateDurationPreview();

    showPage('dashboard');
    $('sessionSubject').focus();
}

function updateStudySession(id, data) {
    const session = studySessions.find(function (item) {
        return item.id === id;
    });
    if (!session) {
        resetSessionForm();
        return;
    }

    session.subject = data.subject;
    session.topic = data.topic;
    session.date = data.date;
    session.startTime = data.startTime;
    session.endTime = data.endTime;
    session.duration = data.duration;

    saveData();
    resetSessionForm();
    renderAll();
    showToast('Session updated.');
}

function deleteStudySession(id) {
    const session = studySessions.find(function (item) {
        return item.id === id;
    });
    if (!session) {
        return;
    }

    const confirmed = window.confirm('Delete this session?\n\n' + session.subject + ' — ' + session.topic +
        '\n' + formatShortDate(session.date) + ', ' + formatHours(session.duration) + '\n\nThis cannot be undone.');
    if (!confirmed) {
        return;
    }

    studySessions = studySessions.filter(function (item) {
        return item.id !== id;
    });

    // If the deleted session was open in the form, close edit mode.
    if (editingSessionId === id) {
        resetSessionForm();
    }

    saveData();
    renderAll();
    showToast('Session deleted.');
}

/** Clears the form and leaves edit mode. */
function resetSessionForm() {
    editingSessionId = null;
    $('sessionForm').reset();
    $('sessionDate').value = todayISO();
    $('sessionFormHeading').textContent = 'Quick add session';
    $('sessionSubmitBtn').textContent = 'Add session';
    $('sessionCancelBtn').hidden = true;
    hideError('sessionError');
    updateDurationPreview();
}

/** Live duration preview under the time inputs. */
function updateDurationPreview() {
    const startTime = $('sessionStart').value;
    const endTime = $('sessionEnd').value;
    const output = $('sessionDuration');

    if (!isTimeString(startTime) || !isTimeString(endTime)) {
        output.textContent = '—';
        return;
    }

    const duration = calculateDuration(startTime, endTime);
    output.textContent = duration > 0 ? formatHours(duration) : 'End must be after start';
}

/* ---------- 8. TASKS ---------- */

function handleTaskSubmit(event) {
    event.preventDefault();

    const title = $('taskTitle').value.trim();
    const subject = $('taskSubject').value;
    const priority = $('taskPriority').value;

    if (title === '') {
        showError('taskError', 'Give the task a short title.');
        return;
    }
    if (!subject) {
        showError('taskError', 'Choose a subject for this task.');
        return;
    }

    hideError('taskError');
    addTask(title, subject, priority);
}

function addTask(title, subject, priority) {
    tasks.push({
        id: createId(),
        title: title,
        subject: subject,
        priority: PRIORITIES.indexOf(priority) === -1 ? 'Medium' : priority,
        completed: false,
        createdAt: todayISO()
    });

    saveData();
    $('taskForm').reset();
    $('taskPriority').value = 'Medium';
    renderTasks();
    renderDashboard();
    renderAnalyticsStats();
    showToast('Task added.');
}

function toggleTask(id) {
    const task = tasks.find(function (item) {
        return item.id === id;
    });
    if (!task) {
        return;
    }

    task.completed = !task.completed;
    saveData();
    renderTasks();
    renderDashboard();
    renderAnalyticsStats();
}

function deleteTask(id) {
    const task = tasks.find(function (item) {
        return item.id === id;
    });
    if (!task) {
        return;
    }

    const confirmed = window.confirm('Delete this task?\n\n' + task.title + '\n\nThis cannot be undone.');
    if (!confirmed) {
        return;
    }

    tasks = tasks.filter(function (item) {
        return item.id !== id;
    });

    saveData();
    renderTasks();
    renderDashboard();
    renderAnalyticsStats();
    showToast('Task deleted.');
}

/* ---------- 9. SETTINGS: TARGET, THEME, DEMO DATA, RESET ---------- */

function handleTargetSubmit(event) {
    event.preventDefault();
    const value = Number($('targetInput').value);

    if (!isValidTarget(value)) {
        showError('targetError', 'Enter a target between 0.5 and 24 hours.');
        return;
    }

    hideError('targetError');
    dailyTarget = value;
    writeStorage(STORAGE_KEYS.target, dailyTarget);
    renderDashboard();
    showToast('Daily target set to ' + formatHours(dailyTarget) + '.');
}

function updateTheme(theme) {
    const chosen = theme === 'dark' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', chosen);
    writeStorage(STORAGE_KEYS.theme, chosen);
    $('lightThemeBtn').setAttribute('aria-pressed', String(chosen === 'light'));
    $('darkThemeBtn').setAttribute('aria-pressed', String(chosen === 'dark'));
}

/** Adds clearly labelled sample data so the app is easy to try out. */
function loadDemoData() {
    const confirmed = window.confirm('Add demo sessions and tasks to your current data?');
    if (!confirmed) {
        return;
    }

    const today = new Date();
    const demoSessions = [
        { offset: 0, subject: 'Java / DSA', topic: 'Arrays and two pointers (demo)', startTime: '09:00', endTime: '11:30' },
        { offset: 0, subject: 'Web Development', topic: 'CSS grid practice (demo)', startTime: '14:00', endTime: '16:00' },
        { offset: 1, subject: 'Aptitude', topic: 'Time and work problems (demo)', startTime: '18:00', endTime: '20:00' },
        { offset: 1, subject: 'Java / DSA', topic: 'Linked lists (demo)', startTime: '10:00', endTime: '12:30' },
        { offset: 2, subject: 'English', topic: 'Reading comprehension (demo)', startTime: '08:00', endTime: '09:30' },
        { offset: 3, subject: 'College Work', topic: 'DBMS assignment (demo)', startTime: '15:00', endTime: '18:00' },
        { offset: 4, subject: 'Web Development', topic: 'JavaScript DOM practice (demo)', startTime: '19:00', endTime: '21:30' }
    ];

    demoSessions.forEach(function (item) {
        const date = toISODate(addDays(today, -item.offset));
        studySessions.push({
            id: createId(),
            subject: item.subject,
            topic: item.topic,
            date: date,
            startTime: item.startTime,
            endTime: item.endTime,
            duration: calculateDuration(item.startTime, item.endTime)
        });
    });

    const demoTasks = [
        { title: 'Solve 5 array problems (demo)', subject: 'Java / DSA', priority: 'High', completed: true },
        { title: 'Revise percentages (demo)', subject: 'Aptitude', priority: 'Medium', completed: true },
        { title: 'Build a responsive navbar (demo)', subject: 'Web Development', priority: 'High', completed: false },
        { title: 'Read one editorial (demo)', subject: 'English', priority: 'Low', completed: false }
    ];

    demoTasks.forEach(function (item) {
        tasks.push({
            id: createId(),
            title: item.title,
            subject: item.subject,
            priority: item.priority,
            completed: item.completed,
            createdAt: todayISO()
        });
    });

    saveData();
    renderAll();
    showToast('Demo data loaded. Use "Reset all data" to remove it.');
}

function resetAllData() {
    const confirmed = window.confirm('Reset all data?\n\nThis clears every study session and task, and sets the daily target back to ' +
        DEFAULT_TARGET + ' hours. This cannot be undone.');
    if (!confirmed) {
        return;
    }

    studySessions = [];
    tasks = [];
    dailyTarget = DEFAULT_TARGET;

    try {
        localStorage.removeItem(STORAGE_KEYS.sessions);
        localStorage.removeItem(STORAGE_KEYS.tasks);
        localStorage.removeItem(STORAGE_KEYS.target);
    } catch (error) {
        console.warn('Could not clear LocalStorage.', error);
    }

    $('targetInput').value = DEFAULT_TARGET;
    $('searchInput').value = '';
    $('filterSubject').value = '';
    $('filterDate').value = '';
    updateTheme('light');
    resetSessionForm();
    renderAll();
    showPage('dashboard');
    showToast('All data has been reset.');
}

/* ---------- 10. NAVIGATION ---------- */

function showPage(pageName) {
    const pages = document.querySelectorAll('.page');
    pages.forEach(function (page) {
        const isTarget = page.id === 'page-' + pageName;
        page.hidden = !isTarget;
        page.classList.toggle('is-active', isTarget);
    });

    document.querySelectorAll('.nav-link').forEach(function (link) {
        const isTarget = link.dataset.page === pageName;
        link.classList.toggle('is-active', isTarget);
        if (isTarget) {
            link.setAttribute('aria-current', 'page');
        } else {
            link.removeAttribute('aria-current');
        }
    });

    closeMobileNav();
    window.scrollTo({ top: 0, behavior: 'auto' });
}

function openMobileNav() {
    $('sidebar').classList.add('is-open');
    $('navOverlay').hidden = false;
    $('menuButton').setAttribute('aria-expanded', 'true');
}

function closeMobileNav() {
    $('sidebar').classList.remove('is-open');
    $('navOverlay').hidden = true;
    $('menuButton').setAttribute('aria-expanded', 'false');
}

/* ---------- 11. EVENT LISTENERS ---------- */

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(function (link) {
        link.addEventListener('click', function () {
            showPage(link.dataset.page);
        });
    });

    $('menuButton').addEventListener('click', function () {
        if ($('sidebar').classList.contains('is-open')) {
            closeMobileNav();
        } else {
            openMobileNav();
        }
    });

    $('navOverlay').addEventListener('click', closeMobileNav);

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            closeMobileNav();
        }
    });

    $('goToFormBtn').addEventListener('click', function () {
        showPage('dashboard');
        $('sessionSubject').focus();
    });

    // Session form
    $('sessionForm').addEventListener('submit', handleSessionSubmit);
    $('sessionCancelBtn').addEventListener('click', resetSessionForm);
    $('sessionStart').addEventListener('change', updateDurationPreview);
    $('sessionEnd').addEventListener('change', updateDurationPreview);

    // Session list actions (one listener for all rows)
    $('sessionTableBody').addEventListener('click', function (event) {
        const editButton = event.target.closest('[data-edit-session]');
        const deleteButton = event.target.closest('[data-delete-session]');

        if (editButton) {
            editStudySession(editButton.dataset.editSession);
        } else if (deleteButton) {
            deleteStudySession(deleteButton.dataset.deleteSession);
        }
    });

    // Search and filters
    $('searchInput').addEventListener('input', renderSessions);
    $('filterSubject').addEventListener('change', renderSessions);
    $('filterDate').addEventListener('change', renderSessions);
    $('clearFiltersBtn').addEventListener('click', function () {
        $('searchInput').value = '';
        $('filterSubject').value = '';
        $('filterDate').value = '';
        renderSessions();
    });

    // Tasks
    $('taskForm').addEventListener('submit', handleTaskSubmit);
    $('taskList').addEventListener('click', function (event) {
        const toggleButton = event.target.closest('[data-toggle-task]');
        const deleteButton = event.target.closest('[data-delete-task]');

        if (toggleButton) {
            toggleTask(toggleButton.dataset.toggleTask);
        } else if (deleteButton) {
            deleteTask(deleteButton.dataset.deleteTask);
        }
    });

    // Settings
    $('targetForm').addEventListener('submit', handleTargetSubmit);
    $('lightThemeBtn').addEventListener('click', function () {
        updateTheme('light');
    });
    $('darkThemeBtn').addEventListener('click', function () {
        updateTheme('dark');
    });
    $('demoDataBtn').addEventListener('click', loadDemoData);
    $('resetDataBtn').addEventListener('click', resetAllData);
}

/* ---------- 12. START THE APP ---------- */

function initializeApp() {
    loadData();

    const savedTheme = readStorage(STORAGE_KEYS.theme, 'light');
    updateTheme(savedTheme === 'dark' ? 'dark' : 'light');

    $('targetInput').value = dailyTarget;
    $('sessionDate').value = todayISO();

    setupEventListeners();
    renderGreeting();
    renderAll();
}

document.addEventListener('DOMContentLoaded', initializeApp);
