/**
 * Notifications — E2E Tests (Cypress)
 *
 * TC-N1  Supervisor uploads feedback          → student receives notification
 * TC-N2  Supervisor uploads multiple feedback → multiple notifications displayed
 * TC-N3  User opens unread notification       → status changes to read
 * TC-N4  Team member leaves group             → remaining members receive notification
 * TC-N5  Notification list is empty           → "No notifications" message displayed
 * TC-N6  Student uploads a file               → supervisor receives notification
 * TC-N7  Supervisor schedules a meeting       → all team members receive notification
 *
 * Credentials (seed_data.py):
 *   Supervisor : Hamza@just.edu.jo  / Hamza0*
 *
 * Note: The page calls /api/v1/supervisor/notifications/* (DDD context),
 *       so all intercepts use regex to match any prefix.
 */

let accessToken = ''

before(() => {
  cy.request('POST', '/api/v1/auth/login/', {
    email: 'Hamza@just.edu.jo',
    password: 'Hamza0*',
  }).then((res) => {
    accessToken = res.body.access
  })
})

// ─── Mock data ────────────────────────────────────────────────────────────────

const UNREAD_NOTIF = {
  id: 1,
  title: 'Feedback uploaded',
  message: 'Your supervisor uploaded new feedback.',
  notif_type: 'supervisor_comment',
  team_name: 'Team Alpha',
  is_read: false,
  created_at: '2026-05-24T10:00:00Z',
}

const READ_NOTIF = {
  ...UNREAD_NOTIF, id: 2, is_read: true, title: 'Meeting Scheduled',
}

// ─── Helper: visit the notifications page with auth ───────────────────────────

function visitNotifPage() {
  cy.visit('/supervisor_notifications.html', {
    onBeforeLoad(win) {
      win.localStorage.setItem('access', accessToken)
      win.localStorage.setItem('user', JSON.stringify({
        role: 'supervisor', display_name: 'Hamza Alkofahi',
      }))
    },
  })
}

// ─── TC-N1: Supervisor uploads feedback → student receives notification ────────

describe('TC-N1 | Supervisor uploads feedback → notification received', () => {

  it('notification appears in the list after feedback is uploaded', () => {
    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: [UNREAD_NOTIF],
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.notif-item').should('have.length', 1)
    cy.get('.notif-title').should('contain.text', 'Feedback uploaded')
  })

})

// ─── TC-N2: Multiple feedback notifications displayed ─────────────────────────

describe('TC-N2 | Multiple feedback notifications → all rendered', () => {

  it('all three notifications are displayed correctly', () => {
    const multipleNotifs = [
      { ...UNREAD_NOTIF, id: 1, title: 'Feedback #1' },
      { ...UNREAD_NOTIF, id: 2, title: 'Feedback #2' },
      { ...UNREAD_NOTIF, id: 3, title: 'Feedback #3' },
    ]

    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: multipleNotifs,
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.notif-item').should('have.length', 3)
    cy.contains('Feedback #1').should('exist')
    cy.contains('Feedback #2').should('exist')
    cy.contains('Feedback #3').should('exist')
  })

})

// ─── TC-N3: User opens unread notification → status changes to read ───────────

describe('TC-N3 | Unread notification opened → marked as read', () => {

  it('unread dot disappears after clicking Mark Read', () => {
    // Stateful intercept: first GET returns the unread notification,
    // every subsequent GET (triggered by loadAll after mark-read) returns the
    // same notification with is_read: true so the dot disappears.
    let fetchCount = 0
    cy.intercept('GET', /\/notifications\/(?!unread-count)/, (req) => {
      fetchCount++
      req.reply({
        statusCode: 200,
        body: fetchCount === 1
          ? [UNREAD_NOTIF]
          : [{ ...UNREAD_NOTIF, is_read: true }],
      })
    }).as('getNotifications')

    // Mark-read PATCH endpoint — matches .../notifications/1/read/
    cy.intercept('PATCH', /\/notifications\/\d+\/read\//, {
      statusCode: 200,
      body: { ...UNREAD_NOTIF, is_read: true },
    }).as('markRead')

    visitNotifPage()
    cy.wait('@getNotifications')

    // Notification must appear as unread initially
    cy.get('.notif-item.unread').should('exist')
    cy.get('.unread-dot').should('be.visible')

    // Click the Mark Read button
    cy.get('.btn-read').first().click()
    cy.wait('@markRead')

    // After loadAll() re-fetches, the unread indicator must be gone
    cy.get('.unread-dot').should('not.exist')
  })

})

// ─── TC-N4: Team member leaves → remaining members notified ──────────────────

describe('TC-N4 | Team member leaves → notification received', () => {

  it('member-left notification appears in the list', () => {
    const leaveNotif = {
      ...UNREAD_NOTIF,
      id: 4,
      title: 'Team Member Left',
      message: 'A member has left Team Alpha.',
      notif_type: 'general',
    }

    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: [leaveNotif],
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.notif-item').should('have.length', 1)
    cy.get('.notif-title').should('contain.text', 'Team Member Left')
  })

})

// ─── TC-N5: Empty notification list → message displayed ─────────────────────

describe('TC-N5 | No notifications → empty state shown', () => {

  it('"No notifications" message is visible when list is empty', () => {
    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: [],
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.empty').should('be.visible')
    cy.get('.empty').should('contain.text', 'No notifications')
  })

})

// ─── TC-N6: Student uploads a file → supervisor receives notification ─────────

describe('TC-N6 | Student uploads file → supervisor notified', () => {

  it('file-upload notification appears in the supervisor list', () => {
    const fileNotif = {
      ...UNREAD_NOTIF,
      id: 5,
      title: 'New File Uploaded',
      message: 'Student Sadeen uploaded a new file for Team Alpha.',
      notif_type: 'file_uploaded',
    }

    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: [fileNotif],
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.notif-item').should('have.length', 1)
    cy.get('.notif-title').should('contain.text', 'New File Uploaded')
    cy.get('.notif-msg').should('contain.text', 'uploaded')
  })

})

// ─── TC-N7: Supervisor schedules meeting → team members notified ─────────────

describe('TC-N7 | Supervisor schedules meeting → members notified', () => {

  it('meeting-scheduled notification appears in the list', () => {
    const meetingNotif = {
      ...UNREAD_NOTIF,
      id: 6,
      title: 'Meeting Scheduled',
      message: 'A new meeting has been scheduled for Team Alpha.',
      notif_type: 'meeting_scheduled',
    }

    cy.intercept('GET', /\/notifications\//, {
      statusCode: 200,
      body: [meetingNotif],
    }).as('getNotifications')

    visitNotifPage()
    cy.wait('@getNotifications')

    cy.get('.notif-item').should('have.length', 1)
    cy.get('.notif-title').should('contain.text', 'Meeting Scheduled')
    cy.get('.notif-meta').should('contain.text', 'meeting_scheduled')
  })

})