/**
 * Test Suite — Team Management Features
 * Covers TC-T1 through TC-T9
 *
 * Students used:
 *   seham@cit.just.edu.jo  — used for create-team page tests (TC-T1,T2,T4,T8)
 *   omar@cit.just.edu.jo   — gets a team created for dashboard tests (TC-T3,T5,T6,T7)
 */

const CREATE_STUDENT  = { email: 'seham@cit.just.edu.jo',  password: 'Seham0*'  }
const TEAM_STUDENT    = { email: 'omar@cit.just.edu.jo',   password: 'Omar0*'   }

// Helper: login then leave all teams (tokens already set in localStorage by loginAs)
function loginAndLeave(email, password) {
  return cy.loginAs(email, password).then(token => cy.leaveAllTeams(token))
}

// ─── TC-T1  Team Formation Page ───────────────────────────────────────────────
describe('TC-T1 | Team Formation Page loads correctly', () => {
  beforeEach(() => { loginAndLeave(CREATE_STUDENT.email, CREATE_STUDENT.password) })

  it('page loads with all required UI elements', () => {
    cy.visit('/create-team/')
    cy.get('.card').should('be.visible')
    cy.contains('h2', 'Create New Project Team').should('be.visible')
    cy.contains('You will become the team leader').should('be.visible')
    cy.get('#teamName').should('be.visible')
    cy.get('#desc').should('be.visible')
    cy.get('#createBtn').should('be.visible').and('contain', 'Create Team')
    cy.contains('Cancel and back').should('be.visible')
  })
})

// ─── TC-T2  Team Name Field ────────────────────────────────────────────────────
describe('TC-T2 | Team Name Field accepts valid input', () => {
  beforeEach(() => { loginAndLeave(CREATE_STUDENT.email, CREATE_STUDENT.password) })

  it('accepts a valid team name', () => {
    cy.visit('/create-team/')
    cy.get('#teamName').type('Smart City System')
    cy.get('#teamName').should('have.value', 'Smart City System')
  })

  it('shows error when team name is empty on submit', () => {
    cy.visit('/create-team/')
    cy.get('#desc').type('Some description')
    cy.get('#createBtn').click()
    cy.get('#errBox').should('be.visible').and('contain', 'Please enter a team name')
  })
})

// ─── TC-T4  Team Description Field accepts valid input
describe('TC-T4 | Team Description Field accepts valid input', () => {
  beforeEach(() => { loginAndLeave(CREATE_STUDENT.email, CREATE_STUDENT.password) })

  it('accepts a valid description', () => {
    cy.visit('/create-team/')
    cy.get('#desc').type('This project aims to build a smart city monitoring system.')
    cy.get('#desc').should('have.value', 'This project aims to build a smart city monitoring system.')
  })

  it('shows error when description is empty on submit', () => {
    cy.visit('/create-team/')
    cy.get('#teamName').type('My Team')
    cy.get('#createBtn').click()
    cy.get('#errBox').should('be.visible').and('contain', 'Please enter a project description')
  })
})

// ─── TC-T8  UI Consistency — Refresh resets form ──────────────────────────────
describe('TC-T8 | Refresh page resets form fields correctly', () => {
  beforeEach(() => { loginAndLeave(CREATE_STUDENT.email, CREATE_STUDENT.password) })

  it('entered data is cleared after page refresh', () => {
    cy.visit('/create-team/')
    cy.get('#teamName').type('Temp Team Name')
    cy.get('#desc').type('Temp Description')
    cy.reload()
    cy.get('#teamName').should('have.value', '')
    cy.get('#desc').should('have.value', '')
  })
})

// ─── Shared setup: create a team for TEAM_STUDENT ─────────────────────────────
describe('Team Dashboard Tests (TC-T3, TC-T5, TC-T6, TC-T7)', () => {
  let token

  before(() => {
    cy.loginAs(TEAM_STUDENT.email, TEAM_STUDENT.password).then(t => {
      token = t
      cy.createTeamViaAPI(token, 'Omar Test Team', 'Team for Cypress tests')
    })
  })

  beforeEach(() => {
    cy.loginAs(TEAM_STUDENT.email, TEAM_STUDENT.password)
  })

  // ─── TC-T6  Team Admin Display ──────────────────────────────────────────────
  it('TC-T6 | Logged-in student is displayed as Team Leader', () => {
    cy.visit('/team-dashboard/')
    cy.get('#membersList', { timeout: 8000 }).should('be.visible')
    cy.get('.leader-tag').should('be.visible').and('contain', 'Leader')
  })

  // ─── TC-T5  Notifications Panel ─────────────────────────────────────────────
  it('TC-T5 | Clicking notifications bell opens the notifications panel', () => {
    cy.visit('/team-dashboard/')
    cy.get('.notif-panel').should('not.have.class', 'open')
    cy.get('.notif-btn').click()
    cy.get('.notif-panel').should('have.class', 'open')
    cy.get('.notif-header h3').should('contain', 'Notifications')
    cy.get('.notif-close').click()
    cy.get('.notif-panel').should('not.have.class', 'open')
  })

  // ─── TC-T3  Team Chat ────────────────────────────────────────────────────────
  it('TC-T3 | Clicking Chat navigates to chat page and displays chat UI', () => {
    cy.visit('/team-dashboard/')
    cy.contains('a', 'Chat').click()
    cy.url().should('include', '/chat')
    cy.get('.chat-header').should('be.visible')
    cy.get('.messages').should('be.visible')
    cy.get('.input-area input[placeholder]').first().should('be.visible')
  })

  // ─── TC-T7  Request Supervisor Button ───────────────────────────────────────
  it('TC-T7 | Supervisor request page loads and Request button is visible', () => {
    cy.visit('/supervisors-list/')
    cy.get('.list', { timeout: 8000 }).should('be.visible')
    cy.get('.req-btn').first().should('be.visible')
  })
})

// ─── TC-T9  Responsiveness ────────────────────────────────────────────────────
describe('TC-T9 | Responsiveness — layout usable at mobile viewport', () => {
  beforeEach(() => { loginAndLeave(CREATE_STUDENT.email, CREATE_STUDENT.password) })

  it('login page is usable at 375x667 (iPhone SE)', () => {
    cy.clearLocalStorage()
    cy.viewport(375, 667)
    cy.visit('/')
    cy.get('.login-container').should('be.visible')
    cy.get('#email').should('be.visible')
    cy.get('#password').should('be.visible')
    cy.get('#loginBtn').should('be.visible')
  })

  it('create-team page is usable at 768x1024 (tablet)', () => {
    cy.viewport(768, 1024)
    cy.visit('/create-team/')
    cy.get('.card').should('be.visible')
    cy.get('#teamName').should('be.visible')
    cy.get('#desc').should('be.visible')
    cy.get('#createBtn').should('be.visible')
  })
})
