/**
 * Discussion Scheduling — E2E Tests (Cypress)
 *
 * TC-1  Schedule without exam conflicts  → meeting created successfully
 * TC-2  Schedule when exam conflict exists → scheduling blocked
 * TC-3  Fair distribution across teams   → no conflicts between teams
 *
 * Credentials (seed_data.py):
 *   Supervisor : Hamza@just.edu.jo  / Hamza0*
 *
 * Note: The page uses /api/v1/supervisor/* endpoints (DDD context),
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

const MOCK_SLOT = {
  id: 1, date: '2026-06-15', start_time: '09:00:00',
  end_time: '12:00:00', mode: 'Both', is_open: true,
  created_at: '2026-05-24T10:00:00Z',
}

const MOCK_MEETING = {
  id: 1, supervisor_name: 'Hamza Alkofahi', team_name: 'Team Alpha',
  date: '2026-06-15', time: '09:00:00', meeting_type: 'Online',
  topic: 'Project progress review', created_at: '2026-05-24T10:00:00Z',
}

const MOCK_TEAMS = [
  { id: 1, name: 'Team Alpha', status: 'active' },
  { id: 2, name: 'Team Nova',  status: 'active' },
]

// ─── Helper: visit the scheduling page with auth ──────────────────────────────

function visitSchedulePage() {
  cy.visit('/supervisor_schedule_discussions.html', {
    onBeforeLoad(win) {
      win.localStorage.setItem('access', accessToken)
      win.localStorage.setItem('user', JSON.stringify({
        role: 'supervisor', display_name: 'Hamza Alkofahi',
      }))
    },
  })
}

// ─── TC-1: Schedule without exam conflicts ────────────────────────────────────

describe('TC-1 | Schedule without exam conflicts → meeting created', () => {

  it('page loads with slots and meetings sections', () => {
    cy.intercept('GET', /\/slots\//, { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [MOCK_MEETING] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    visitSchedulePage()

    cy.contains('Schedule Discussions').should('exist')
  })

  it('supervisor adds an availability slot successfully', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    // Intercept the POST to any slots endpoint
    cy.intercept('POST', /\/slots\//, {
      statusCode: 201, body: MOCK_SLOT,
    }).as('addSlot')

    visitSchedulePage()

    cy.get('input[name="date"], #slot-date').first().type('2026-06-15')
    cy.get('input[name="start_time"], #slot-start').first().type('09:00')
    cy.get('input[name="end_time"], #slot-end').first().type('12:00')
    cy.get('select[name="mode"], #slot-mode').first().select('Both')
    cy.get('button').contains(/add slot|save slot/i).click()

    cy.wait('@addSlot').its('response.statusCode').should('eq', 201)
  })

  it('booking a meeting shows success message', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    cy.intercept('POST', /\/meetings\/book\/|\/book\//, {
      statusCode: 201, body: MOCK_MEETING,
    }).as('bookMeeting')

    visitSchedulePage()

    cy.get('select[name="team_id"], #book-team').first().select('Team Alpha')
    cy.get('select[name="meeting_type"], #book-type').first().select('Online')
    cy.get('button').contains(/book|schedule/i).first().click()

    cy.wait('@bookMeeting').its('response.statusCode').should('eq', 201)

    cy.get('.flash-ok, .flash').should('be.visible')
  })

  it('booked meeting appears in the meetings list', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [MOCK_MEETING] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    visitSchedulePage()

    cy.contains('Team Alpha').should('exist')
    cy.contains('2026-06-15').should('exist')
  })

})

// ─── TC-2: Exam conflict → scheduling blocked ─────────────────────────────────

describe('TC-2 | Exam conflict exists → scheduling blocked', () => {

  it('error message shown when booking falls on exam date', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    cy.intercept('POST', /\/meetings\/book\/|\/book\//, {
      statusCode: 400,
      body: { error: 'Cannot schedule on exam day (2026-06-15) for this team.' },
    }).as('bookFail')

    visitSchedulePage()

    cy.get('select[name="team_id"], #book-team').first().select('Team Alpha')
    cy.get('select[name="meeting_type"], #book-type').first().select('Online')
    cy.get('button').contains(/book|schedule/i).first().click()

    cy.wait('@bookFail')
    cy.get('.flash-err, .flash').should('be.visible').and('contain.text', 'exam')
  })

  it('error message shown when no availability slots exist', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    cy.intercept('POST', /\/meetings\/book\/|\/book\//, {
      statusCode: 400,
      body: { error: 'No available slot found for the requested mode.' },
    }).as('bookFail')

    visitSchedulePage()

    cy.get('select[name="team_id"], #book-team').first().select('Team Alpha')
    cy.get('select[name="meeting_type"], #book-type').first().select('Online')
    cy.get('button').contains(/book|schedule/i).first().click()

    cy.wait('@bookFail')
    cy.get('.flash-err, .flash').should('be.visible').and('contain.text', 'slot')
  })

})

// ─── TC-3: Fair distribution across teams ─────────────────────────────────────

describe('TC-3 | Fair distribution → no conflicts between teams', () => {

  it('both teams appear in the meetings list after balanced booking', () => {
    const twoMeetings = [
      { ...MOCK_MEETING, id: 1, team_name: 'Team Alpha', date: '2026-06-15', time: '09:00:00' },
      { ...MOCK_MEETING, id: 2, team_name: 'Team Nova',  date: '2026-06-16', time: '09:00:00' },
    ]

    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: twoMeetings })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    visitSchedulePage()

    cy.contains('Team Alpha').should('exist')
    cy.contains('Team Nova').should('exist')
  })

  it('fairness error shown when one team has too many meetings', () => {
    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: [] })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    cy.intercept('POST', /\/meetings\/book\/|\/book\//, {
      statusCode: 400,
      body: { error: 'Fair distribution: schedule a team with fewer meetings first.' },
    }).as('fairFail')

    visitSchedulePage()

    cy.get('select[name="team_id"], #book-team').first().select('Team Alpha')
    cy.get('select[name="meeting_type"], #book-type').first().select('Online')
    cy.get('button').contains(/book|schedule/i).first().click()

    cy.wait('@fairFail')
    cy.get('.flash-err, .flash').should('be.visible').and('contain.text', 'Fair')
  })

  it('two meetings at different times have no time conflict', () => {
    const meetings = [
      { ...MOCK_MEETING, id: 1, team_name: 'Team Alpha', time: '09:00:00' },
      { ...MOCK_MEETING, id: 2, team_name: 'Team Nova',  time: '09:30:00' },
    ]

    cy.intercept('GET', /\/slots\//,   { statusCode: 200, body: [MOCK_SLOT] })
    cy.intercept('GET', /\/meetings\//, { statusCode: 200, body: meetings })
    cy.intercept('GET', /\/teams\//,   { statusCode: 200, body: MOCK_TEAMS })

    visitSchedulePage()

    cy.contains('09:00').should('exist')
    cy.contains('09:30').should('exist')
  })

})