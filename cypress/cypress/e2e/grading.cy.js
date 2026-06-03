/**
 * Grading System — E2E Tests (Cypress)
 *
 * TC-1  Three grades submitted        → final grade calculated correctly
 * TC-2  Boundary grades 0 and 100     → accepted / out-of-range rejected
 * TC-3  Weight distribution 50/25/25  → formula verified with exact values
 * TC-4  One grade field missing       → calculation blocked (validation error)
 *
 * Formula: final = chief * 0.50 + examiner_one * 0.25 + examiner_two * 0.25
 *
 * Credentials (seed_data.py):
 *   Supervisor : Hamza@just.edu.jo  / Hamza0*
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

// ─── Helpers ──────────────────────────────────────────────────────────────────

function previewGrade(chief, examiner_one, examiner_two) {
  return cy.request({
    method: 'POST',
    url: '/api/v1/grading/preview/',
    headers: { Authorization: `Bearer ${accessToken}` },
    body: { chief_grade: chief, examiner_one_grade: examiner_one, examiner_two_grade: examiner_two },
  })
}

function previewGradeExpectFail(body) {
  return cy.request({
    method: 'POST',
    url: '/api/v1/grading/preview/',
    headers: { Authorization: `Bearer ${accessToken}` },
    body,
    failOnStatusCode: false,
  })
}

/** Visit the grading page with auth tokens set before any page JS runs. */
function visitGradingPage() {
  cy.intercept('GET', /\/teams\//, { statusCode: 200, body: [{ id: 1, name: 'Team Alpha' }] }).as('teams')
  cy.intercept('GET', /\/grading\/(?!preview)/, { statusCode: 200, body: [] }).as('reports')

  cy.visit('/supervisor_grading_reports.html', {
    onBeforeLoad(win) {
      win.localStorage.setItem('access', accessToken)
      win.localStorage.setItem('user', JSON.stringify({ role: 'supervisor', display_name: 'Hamza' }))
    },
  })
}

// ─── TC-1: Three grades → correct final ──────────────────────────────────────
describe('TC-1 | Three grades submitted → final grade calculated correctly', () => {

  it('calculates final grade using 50/25/25 weights via API', () => {
    // 80*0.50 + 70*0.25 + 60*0.25 = 40 + 17.5 + 15 = 72.5
    previewGrade(80, 70, 60).then((res) => {
      expect(res.status).to.eq(200)
      expect(parseFloat(res.body.final_grade)).to.eq(72.5)
    })
  })

  it('shows the computed final grade in the UI preview box', () => {
    // Intercept the preview endpoint regardless of prefix (/api/v1/ or /api/v1/supervisor/)
    cy.intercept('POST', /\/grading\/preview\//, {
      statusCode: 200,
      body: { final_grade: 72.5 },
    }).as('preview')

    visitGradingPage()

    cy.get('input[name="chief_grade"]').type('80')
    cy.get('input[name="examiner_one_grade"]').type('70')
    cy.get('input[name="examiner_two_grade"]').type('60')

    cy.wait('@preview')

    cy.get('#preview-final').should('contain.text', '72.5')
  })

})

// ─── TC-2: Boundary grades 0 and 100 ─────────────────────────────────────────
describe('TC-2 | Boundary grades → accepted or rejected', () => {

  it('accepts all grades = 0  → final grade = 0', () => {
    previewGrade(0, 0, 0).then((res) => {
      expect(res.status).to.eq(200)
      expect(parseFloat(res.body.final_grade)).to.eq(0)
    })
  })

  it('accepts all grades = 100 → final grade = 100', () => {
    previewGrade(100, 100, 100).then((res) => {
      expect(res.status).to.eq(200)
      expect(parseFloat(res.body.final_grade)).to.eq(100)
    })
  })

  it('rejects grade below 0 (−1) → 400 validation error', () => {
    previewGradeExpectFail({
      chief_grade: -1, examiner_one_grade: 50, examiner_two_grade: 50,
    }).then((res) => {
      expect(res.status).to.eq(400)
    })
  })

  it('rejects grade above 100 (101) → 400 validation error', () => {
    previewGradeExpectFail({
      chief_grade: 101, examiner_one_grade: 50, examiner_two_grade: 50,
    }).then((res) => {
      expect(res.status).to.eq(400)
    })
  })

})

// ─── TC-3: Verify 50/25/25 weight distribution ────────────────────────────────
describe('TC-3 | Weight distribution 50 / 25 / 25 verified', () => {

  it('chief=100, e1=0, e2=0 → final = 50  (chief carries 50%)', () => {
    previewGrade(100, 0, 0).then((res) => {
      expect(parseFloat(res.body.final_grade)).to.eq(50)
    })
  })

  it('chief=0, e1=100, e2=0 → final = 25  (examiner 1 carries 25%)', () => {
    previewGrade(0, 100, 0).then((res) => {
      expect(parseFloat(res.body.final_grade)).to.eq(25)
    })
  })

  it('chief=0, e1=0, e2=100 → final = 25  (examiner 2 carries 25%)', () => {
    previewGrade(0, 0, 100).then((res) => {
      expect(parseFloat(res.body.final_grade)).to.eq(25)
    })
  })

  it('all equal grades → final equals same value (weights sum to 1)', () => {
    previewGrade(60, 60, 60).then((res) => {
      expect(parseFloat(res.body.final_grade)).to.eq(60)
    })
  })

})

// ─── TC-4: Missing grade → calculation blocked ────────────────────────────────
describe('TC-4 | One grade missing → calculation blocked', () => {

  it('API blocks preview when chief_grade is missing → 400', () => {
    previewGradeExpectFail({
      examiner_one_grade: 70, examiner_two_grade: 60,
    }).then((res) => { expect(res.status).to.eq(400) })
  })

  it('API blocks preview when examiner_one_grade is missing → 400', () => {
    previewGradeExpectFail({
      chief_grade: 80, examiner_two_grade: 60,
    }).then((res) => { expect(res.status).to.eq(400) })
  })

  it('API blocks preview when examiner_two_grade is missing → 400', () => {
    previewGradeExpectFail({
      chief_grade: 80, examiner_one_grade: 70,
    }).then((res) => { expect(res.status).to.eq(400) })
  })

  it('UI form blocks submission when a grade field is empty (HTML required)', () => {
    visitGradingPage()

    cy.get('input[name="chief_grade"]').type('80')
    cy.get('input[name="examiner_one_grade"]').type('70')
    // examiner_two_grade left empty intentionally

    cy.get('button[type="submit"]').click()

    // Preview must still show — (form not submitted)
    cy.get('#preview-final').should('contain.text', '—')
    cy.url().should('include', 'grading_reports')
  })

})