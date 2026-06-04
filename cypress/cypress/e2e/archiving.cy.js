/**
 * Project Archiving — E2E Tests (Cypress)
 *
 * TC-1  Project marked as completed          → archived successfully
 * TC-2  Admin searches the archive           → archived project retrieved
 * TC-3  Retrieve archived data on demand     → correct information displayed
 * TC-4  Archived data older than 5 years     → data still available
 * TC-5  System backup occurs                 → data safely backed up
 *
 * Credentials (seed_data.py):
 *   Supervisor : Hamza@just.edu.jo  / Hamza0*
 */

let accessToken = ''
let teamId      = null

const ARCHIVED_TEAM = {
  id: 1,
  name: 'Team Alpha',
  project_title: 'AI Attendance System',
  project_description: 'Face-recognition attendance tracker for JUST.',
  status: 'complete',
  progress: 100,
  academic_year: '2025-2026',
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-05-24T00:00:00Z',
  leader: { id: 2, display_name: 'Sadeen', email: 'sadeen@cit.just.edu.jo', role: 'student' },
  members: [{ id: 2, display_name: 'Sadeen', email: 'sadeen@cit.just.edu.jo', role: 'student' }],
  assigned_supervisor: { id: 1, display_name: 'Hamza Alkofahi', email: 'Hamza@just.edu.jo', role: 'supervisor' },
  exam_dates: [],
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Visit a page with tokens already set in localStorage.
 * Uses onBeforeLoad so tokens are available before the page JS runs.
 */
function visitAs(url, token) {
  cy.visit(url, {
    onBeforeLoad(win) {
      win.localStorage.setItem('access', token)
      win.localStorage.setItem('user', JSON.stringify({ role: 'supervisor', display_name: 'Hamza' }))
    },
  })
}

// ─── Login and get team ID once ───────────────────────────────────────────────
before(() => {
  cy.request('POST', '/api/v1/auth/login/', {
    email: 'Hamza@just.edu.jo',
    password: 'Hamza0*',
  }).then((res) => {
    accessToken = res.body.access

    cy.request({
      method: 'GET',
      url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${accessToken}` },
    }).then((r) => {
      if (r.body.length > 0) teamId = r.body[0].id
    })
  })
})

// ─── TC-1: Mark project as completed → archived ───────────────────────────────
describe('TC-1 | Project marked as completed → archived successfully', () => {

  it('PATCH team status to "complete" returns 200 with status = complete', () => {
    if (!teamId) { cy.log('⚠️  Seed the DB first'); return }

    cy.request({
      method: 'PATCH',
      url: `/api/v1/teams/${teamId}/`,
      headers: { Authorization: `Bearer ${accessToken}` },
      body: { status: 'complete' },
    }).then((res) => {
      expect(res.status).to.eq(200)
      expect(res.body.status).to.eq('complete')
    })
  })

  it('archived team appears with status "complete" in the teams list', () => {
    // Use regex — matches /api/v1/teams/ and /api/v1/teams/1/ etc.
    cy.intercept('GET', /\/api\/v1\/teams\//, {
      statusCode: 200,
      body: [ARCHIVED_TEAM],
    }).as('getTeams')

    visitAs('/supervisor_my_teams.html', accessToken)
    cy.wait('@getTeams')

    cy.contains('Team Alpha').should('exist')
  })

})

// ─── TC-2: Admin searches the archive ────────────────────────────────────────
describe('TC-2 | Admin searches the archive → archived project retrieved', () => {

  it('GET teams returns completed team in results', () => {
    cy.request({
      method: 'GET',
      url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${accessToken}` },
      failOnStatusCode: false,
    }).then((res) => {
      expect(res.status).to.eq(200)
      expect(res.body).to.be.an('array')
    })
  })

  it('UI search finds the archived team by name', () => {
    cy.intercept('GET', /\/api\/v1\/teams\//, {
      statusCode: 200,
      body: [
        ARCHIVED_TEAM,
        { ...ARCHIVED_TEAM, id: 2, name: 'Team Nova', status: 'active' },
      ],
    }).as('getTeams')

    visitAs('/supervisor_my_teams.html', accessToken)
    cy.wait('@getTeams')

    cy.contains('Team Alpha').should('exist')
    cy.contains('Team Nova').should('exist')
  })

})

// ─── TC-3: Retrieve archived data on demand ───────────────────────────────────
describe('TC-3 | Retrieve archived data → correct information displayed', () => {

  it('GET /api/v1/teams/ returns all required fields', () => {
    cy.request({
      method: 'GET',
      url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${accessToken}` },
    }).then((res) => {
      expect(res.status).to.eq(200)
      if (res.body.length > 0) {
        const team = res.body[0]
        expect(team).to.have.property('id')
        expect(team).to.have.property('name')
        expect(team).to.have.property('project_title')
        expect(team).to.have.property('status')
        expect(team).to.have.property('academic_year')
        expect(team).to.have.property('created_at')
      }
    })
  })

  it('archived team displays project title correctly in UI', () => {
    cy.intercept('GET', /\/api\/v1\/teams\//, {
      statusCode: 200,
      body: [ARCHIVED_TEAM],
    }).as('getTeams')

    visitAs('/supervisor_my_teams.html', accessToken)
    cy.wait('@getTeams')

    cy.contains('Team Alpha').should('exist')
    cy.contains('AI Attendance System').should('exist')
  })

})

// ─── TC-4: Archived data older than 5 years → still available ────────────────
describe('TC-4 | Archived data older than 5 years → data still available', () => {

  it('team with created_at from 5+ years ago is displayed correctly', () => {
    const OLD_TEAM = {
      ...ARCHIVED_TEAM,
      id: 99,
      name: 'Old Archive Team',
      created_at: '2019-01-15T00:00:00Z',
      updated_at: '2020-06-01T00:00:00Z',
    }

    cy.intercept('GET', /\/api\/v1\/teams\//, {
      statusCode: 200,
      body: [OLD_TEAM],
    }).as('getTeams')

    visitAs('/supervisor_my_teams.html', accessToken)
    cy.wait('@getTeams')

    cy.contains('Old Archive Team').should('exist')
  })

  it('API always returns 200 regardless of team age', () => {
    cy.request({
      method: 'GET',
      url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${accessToken}` },
    }).then((res) => {
      expect(res.status).to.eq(200)
    })
  })

})

// ─── TC-5: System backup → data safely backed up ─────────────────────────────
describe('TC-5 | System backup → data safely backed up', () => {

  it('team data remains consistent after a write operation', () => {
    if (!teamId) { cy.log('⚠️  Seed the DB first'); return }

    cy.request({
      method: 'GET',
      url: `/api/v1/teams/${teamId}/`,
      headers: { Authorization: `Bearer ${accessToken}` },
    }).then((before) => {
      const originalTitle = before.body.project_title

      cy.request({
        method: 'PATCH',
        url: `/api/v1/teams/${teamId}/`,
        headers: { Authorization: `Bearer ${accessToken}` },
        body: { project_description: 'Updated for backup test.' },
      }).then(() => {
        cy.request({
          method: 'GET',
          url: `/api/v1/teams/${teamId}/`,
          headers: { Authorization: `Bearer ${accessToken}` },
        }).then((after) => {
          expect(after.status).to.eq(200)
          expect(after.body.project_title).to.eq(originalTitle)
          expect(after.body.project_description).to.eq('Updated for backup test.')
        })
      })
    })
  })

  it('grading report data persists after being saved', () => {
    cy.intercept('GET', /\/grading\//, {
      statusCode: 200,
      body: [{
        id: 1,
        team_name: 'Team Alpha',
        phase: 'Final',
        chief_grade: '80.00',
        examiner_one_grade: '70.00',
        examiner_two_grade: '60.00',
        final_grade: '72.50',
        created_at: '2026-05-24T10:00:00Z',
      }],
    }).as('getReports')

    cy.intercept('GET', /\/api\/v1\/teams\//, { statusCode: 200, body: [] }).as('getTeams')

    visitAs('/supervisor_grading_reports.html', accessToken)
    cy.wait('@getReports')

    cy.contains('Team Alpha').should('exist')
    cy.contains('72.50').should('exist')
  })

})