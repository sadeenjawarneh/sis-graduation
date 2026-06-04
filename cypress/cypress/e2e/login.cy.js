/**
 * Login Page — E2E Tests (Cypress)
 *
 * TC-1  Student    valid credentials             → redirect to Student Dashboard
 * TC-2  Student    invalid email AND password    → error message
 * TC-3  Student    valid email / wrong password  → error message
 * TC-4  Student    wrong email / valid password  → error message
 * TC-5  Student    empty email field             → validation message
 * TC-6  Student    empty password field          → validation message
 * TC-7  Supervisor valid credentials             → redirect to Supervisor Dashboard
 * TC-8  Supervisor invalid email AND password    → error message
 * TC-9  Supervisor valid email / wrong password  → error message
 * TC-10 Supervisor wrong email / valid password  → error message
 * TC-11 Supervisor empty email field             → validation message
 * TC-12 Supervisor empty password field          → validation message
 * TC-13 Security   5 wrong attempts              → account locked for 10 minutes
 *
 * Credentials (seed_data.py):
 *   Supervisor : Hamza@just.edu.jo       / Hamza0*
 *   Student    : sadeen@cit.just.edu.jo  / Sadeen0*
 */

const SUPERVISOR = { email: 'Hamza@just.edu.jo',        password: 'Hamza0*'   }
const STUDENT    = { email: 'sadeen@cit.just.edu.jo',   password: 'Sadeen0*'  }
const WRONG      = { email: 'notexist@just.edu.jo',     password: 'Wrong123!' }

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fillAndSubmit(email, password) {
  if (email)    cy.get('#email').type(email)
  if (password) cy.get('#password').type(password)
  cy.get('#loginBtn').click()
}

// ─── Student Tests ────────────────────────────────────────────────────────────

describe('Login — Student', () => {

  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('/login.html')
  })

  it('TC-1 | valid credentials → redirect to Student Dashboard', () => {
    fillAndSubmit(STUDENT.email, STUDENT.password)

    cy.window().its('localStorage').invoke('getItem', 'access').should('exist')
    cy.url().should('match', /student_dashboard|team_dashboard/)
  })

  it('TC-2 | invalid email AND password → error message', () => {
    fillAndSubmit(WRONG.email, WRONG.password)

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-3 | valid email / wrong password → error message', () => {
    fillAndSubmit(STUDENT.email, 'WrongPass999!')

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-4 | wrong email / valid password → error message', () => {
    fillAndSubmit(WRONG.email, STUDENT.password)

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-5 | empty email field → validation message', () => {
    cy.get('#loginBtn').click()

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-6 | empty password field → validation message', () => {
    cy.get('#email').type(STUDENT.email)
    cy.get('#loginBtn').click()

    cy.get('#password-error').should('be.visible')
    cy.url().should('include', 'login')
  })

})

// ─── Supervisor Tests ─────────────────────────────────────────────────────────

describe('Login — Supervisor', () => {

  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('/login.html')
  })

  it('TC-7 | valid credentials → redirect to Supervisor Dashboard', () => {
    fillAndSubmit(SUPERVISOR.email, SUPERVISOR.password)

    cy.window().its('localStorage').invoke('getItem', 'access').should('exist')
    cy.url().should('include', 'Supervisor_dashboard')
  })

  it('TC-8 | invalid email AND password → error message', () => {
    fillAndSubmit(WRONG.email, WRONG.password)

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-9 | valid email / wrong password → error message', () => {
    fillAndSubmit(SUPERVISOR.email, 'WrongPass999!')

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-10 | wrong email / valid password → error message', () => {
    fillAndSubmit(WRONG.email, SUPERVISOR.password)

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-11 | empty email field → validation message', () => {
    cy.get('#loginBtn').click()

    cy.get('#email-error').should('be.visible')
    cy.url().should('include', 'login')
  })

  it('TC-12 | empty password field → validation message', () => {
    cy.get('#email').type(SUPERVISOR.email)
    cy.get('#loginBtn').click()

    cy.get('#password-error').should('be.visible')
    cy.url().should('include', 'login')
  })

})

// ─── Security Tests ───────────────────────────────────────────────────────────

describe('Login — Security', () => {

  beforeEach(() => {
    cy.clearLocalStorage()
    cy.visit('/login.html')
  })

  it('TC-13 | 5 wrong attempts → account locked for 10 minutes', () => {
    for (let i = 0; i < 5; i++) {
      cy.get('#email').clear().type(SUPERVISOR.email)
      cy.get('#password').clear().type('WrongPass!')
      cy.get('#loginBtn').click()
      cy.get('#email-error').should('be.visible')
    }

    // Button must be disabled and lockout message shown
    cy.get('#loginBtn').should('be.disabled')
    cy.get('#email-error').should('be.visible')
      .and('contain.text', 'blocked')
  })

})
