describe('Admin Panel', () => {

  

it('Create Team Successfully', () => {

  const teamName = 'Cypress Team ' + Date.now()

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Teams').click()

  cy.contains('+ Add Team').click()

  cy.get('#add-team-form input[name="name"]')
    .type(teamName)

  cy.get('#add-team-form input[name="project_title"]')
    .type('Graduation Project')

  cy.get('#add-team-form button[type="submit"]')
    .click()

  // Verify team appears in table
  cy.contains(teamName).should('exist')

})
it('Edit First Team Successfully', () => {

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Teams').click()

  cy.get('button[title="Edit"]')
    .first()
    .click()

  cy.get('#edit-team-form input[name="name"]')
    .clear()
    .type('Updated Team Cypress')

  cy.get('#edit-team-form button[type="submit"]')
    .click()

  cy.contains('Updated Team Cypress')
    .should('exist')

})

it('Create Supervisor Successfully', () => {

  const email = `cypress${Date.now()}@just.edu.jo`

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Supervisors').click()

  cy.contains('+ Add Supervisor').click()

  cy.get('#add-supervisor-form input[name="first_name"]')
    .type('Cypress')

  cy.get('#add-supervisor-form input[name="last_name"]')
    .type('Tester')

  cy.get('#add-supervisor-form input[name="email"]')
    .type(email)

  cy.get('#add-supervisor-form input[name="department"]')
    .type('Software Engineering')

  cy.get('#add-supervisor-form input[name="capacity"]')
    .type('3')

  cy.get('#supervisor-modal-submit-btn')
    .click()

  cy.contains('Cypress')
    .should('exist')

})

it(' Create Student Successfully', () => {

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Students').click()

  cy.get('#btn-open-add-student')
    .should('exist')
    .should('be.visible')
    .click({ force: true })

})

it('Grades Data Loads Successfully', () => {

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Grades').click()

  cy.get('button[title="Edit Grade"]')
    .should('have.length.greaterThan', 0)

})

it('Defense Schedule Form Exists', () => {

  cy.visit('http://127.0.0.1:5500/admin.html')

  cy.contains('Defense Schedule').click()

  cy.get('#schedule-defense-form')
    .should('exist')

  cy.get('input[name="team_id"]')
    .should('exist')

  cy.get('input[name="date"]')
    .should('exist')

  cy.get('input[name="time"]')
    .should('exist')

  cy.get('input[name="location"]')
    .should('exist')

})



})
describe('Admin Panel Navigation Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Dashboard visible', () => {
    cy.contains('Welcome, Admin').should('exist')
  })

  it('Open Teams Section', () => {
    cy.contains('Teams').click()
    cy.contains('Teams Management').should('exist')
  })

  it('Open Proposals Section', () => {
    cy.contains('Project Proposals').click()
    cy.contains('+ Add Proposal').should('exist')
  })

  it('Open Supervisors Section', () => {
    cy.contains('Supervisors').click()
    cy.contains('+ Add Supervisor').should('exist')
  })

  it('Open Students Section', () => {
    cy.contains('Students').click()
    cy.contains('+ Add Student').should('exist')
  })

  it('Open Defense Section', () => {
    cy.contains('Defense Schedule').click()
    cy.contains('+ Schedule Defense').should('exist')
  })

  it('Open Grades Section', () => {
    cy.contains('Grades').click()
    cy.get('#grades-search').should('exist')
  })

  it('Open Activity Section', () => {
    cy.contains('Activity Log').click()
    cy.get('#activity-search').should('exist')
  })

})
describe('Search Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Teams Search Exists', () => {
    cy.contains('Teams').click()
    cy.get('#teams-search').should('exist')
  })

  it('Teams Search Accept Text', () => {
    cy.contains('Teams').click()
    cy.get('#teams-search').type('AI')
  })

  it('Proposals Search Exists', () => {
    cy.contains('Project Proposals').click()
    cy.get('#proposals-search').should('exist')
  })

  it('Proposals Search Accept Text', () => {
    cy.contains('Project Proposals').click()
    cy.get('#proposals-search').type('Project')
  })

  it('Supervisors Search Exists', () => {
    cy.contains('Supervisors').click()
    cy.get('#supervisors-search').should('exist')
  })

  it('Supervisors Search Accept Text', () => {
    cy.contains('Supervisors').click()
    cy.get('#supervisors-search').type('Doctor')
  })

  it('Students Search Exists', () => {
    cy.contains('Students').click()
    cy.get('#students-search').should('exist')
  })

  it('Students Search Accept Text', () => {
    cy.contains('Students').click()
    cy.get('#students-search').type('2022')
  })

  it('Grades Search Exists', () => {
    cy.contains('Grades').click()
    cy.get('#grades-search').should('exist')
  })

  it('Activity Search Exists', () => {
    cy.contains('Activity Log').click()
    cy.get('#activity-search').should('exist')
  })

})

describe('Buttons Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Add Team Button Exists', () => {
    cy.contains('Teams').click()
    cy.get('#btn-open-add-team').should('exist')
  })

  it('Add Proposal Button Exists', () => {
    cy.contains('Project Proposals').click()
    cy.get('#btn-open-add-proposal').should('exist')
  })

  it('Add Supervisor Button Exists', () => {
    cy.contains('Supervisors').click()
    cy.get('#btn-open-add-supervisor').should('exist')
  })

  it('Add Student Button Exists', () => {
    cy.contains('Students').click()
    cy.get('#btn-open-add-student').should('exist')
  })

  it('Schedule Defense Button Exists', () => {
    cy.contains('Defense Schedule').click()
    cy.get('#btn-open-schedule-defense').should('exist')
  })

  it('Notification Button Exists', () => {
    cy.get('.notif-btn').should('exist')
  })

  it('Logout Button Exists', () => {
    cy.get('.logout-btn').should('exist')
  })

  it('Dashboard Teams Counter Exists', () => {
    cy.get('#dashboard-total-teams').should('exist')
  })

  it('Dashboard Students Counter Exists', () => {
    cy.get('#dashboard-total-students').should('exist')
  })

  it('Dashboard Supervisors Counter Exists', () => {
    cy.get('#dashboard-total-supervisors').should('exist')
  })

})
describe('Statistics Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Total Teams Card Exists', () => {
    cy.get('#dashboard-total-teams').should('exist')
  })

  it('Total Students Card Exists', () => {
    cy.get('#dashboard-total-students').should('exist')
  })

  it('Total Supervisors Card Exists', () => {
    cy.get('#dashboard-total-supervisors').should('exist')
  })

  it('Total Projects Card Exists', () => {
    cy.get('#dashboard-total-projects').should('exist')
  })

  it('Approved Projects Counter Exists', () => {
    cy.get('#dashboard-approved-proposals').should('exist')
  })

  it('Pending Projects Counter Exists', () => {
    cy.get('#dashboard-pending-proposals').should('exist')
  })

  it('Rejected Projects Counter Exists', () => {
    cy.get('#dashboard-rejected-proposals').should('exist')
  })

  it('Pending Actions Card Exists', () => {
    cy.contains('Pending Actions').should('exist')
  })

  it('Recent Activity Card Exists', () => {
    cy.contains('Recent Activity').should('exist')
  })

  it('Upcoming Defense Sessions Exists', () => {
    cy.contains('Upcoming Defense Sessions').should('exist')
  })

})
describe('Forms Existence Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Add Team Form Exists', () => {
    cy.get('#add-team-form').should('exist')
  })

  it('Edit Team Form Exists', () => {
    cy.get('#edit-team-form').should('exist')
  })

  it('Add Supervisor Form Exists', () => {
    cy.get('#add-supervisor-form').should('exist')
  })

  it('Add Student Form Exists', () => {
    cy.get('#add-student-form').should('exist')
  })

  it('Add Proposal Form Exists', () => {
    cy.get('#add-proposal-form').should('exist')
  })

  it('Defense Schedule Form Exists', () => {
    cy.get('#schedule-defense-form').should('exist')
  })

  it('Add Grade Form Exists', () => {
    cy.get('#add-grade-form').should('exist')
  })

  it('Notification Badge Exists', () => {
    cy.get('#notification-badge').should('exist')
  })

  it('Notification Panel Exists', () => {
    cy.get('#notification-panel').should('exist')
  })

  it('Feedback Area Exists', () => {
    cy.get('#ui-feedback').should('exist')
  })

})
describe('Tables Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Teams Table Exists', () => {
    cy.get('#teams-table').should('exist')
  })

  it('Teams Table Body Exists', () => {
    cy.get('#teams-table-body').should('exist')
  })

  it('Proposals Table Exists', () => {
    cy.get('#proposals-table').should('exist')
  })

  it('Proposals Body Exists', () => {
    cy.get('#proposals-body').should('exist')
  })

  it('Students Table Exists', () => {
    cy.get('#students-table').should('exist')
  })

  it('Students Body Exists', () => {
    cy.get('#students-body').should('exist')
  })

  it('Grades Table Body Exists', () => {
    cy.get('#grades-tbody').should('exist')
  })

  it('Supervisor Grid Exists', () => {
    cy.get('#supervisor-grid').should('exist')
  })

  it('Defense List Exists', () => {
    cy.get('#defense-list').should('exist')
  })

  it('Activity List Exists', () => {
    cy.get('#activity-list').should('exist')
  })

})
describe('Modal Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Add Team Modal Exists', () => {
    cy.get('#add-team-modal').should('exist')
  })

  it('Edit Team Modal Exists', () => {
    cy.get('#edit-team-modal').should('exist')
  })

  it('Add Supervisor Modal Exists', () => {
    cy.get('#add-supervisor-modal').should('exist')
  })

  it('Delete Supervisor Modal Exists', () => {
    cy.get('#delete-supervisor-modal').should('exist')
  })

  it('Schedule Defense Modal Exists', () => {
    cy.get('#schedule-defense-modal').should('exist')
  })

  it('Add Proposal Modal Exists', () => {
    cy.get('#add-proposal-modal').should('exist')
  })

  it('Delete Proposal Modal Exists', () => {
    cy.get('#delete-proposal-modal').should('exist')
  })

  it('Add Student Modal Exists', () => {
    cy.get('#add-student-modal').should('exist')
  })

  it('Delete Student Modal Exists', () => {
    cy.get('#delete-student-modal').should('exist')
  })

  it('Add Grade Modal Exists', () => {
    cy.get('#add-grade-modal').should('exist')
  })

})
describe('Navigation Elements Tests', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:5500/admin.html')
  })

  it('Sidebar Exists', () => {
    cy.get('.sidebar').should('exist')
  })

  it('Sidebar Logo Exists', () => {
    cy.contains('GP Manager').should('exist')
  })

  it('Dashboard Menu Exists', () => {
    cy.contains('Dashboard').should('exist')
  })

  it('Teams Menu Exists', () => {
    cy.contains('Teams').should('exist')
  })

  it('Proposals Menu Exists', () => {
    cy.contains('Project Proposals').should('exist')
  })

  it('Supervisors Menu Exists', () => {
    cy.contains('Supervisors').should('exist')
  })

  it('Students Menu Exists', () => {
    cy.contains('Students').should('exist')
  })

  it('Defense Menu Exists', () => {
    cy.contains('Defense Schedule').should('exist')
  })

  it('Grades Menu Exists', () => {
    cy.contains('Grades').should('exist')
  })

  it('Activity Menu Exists', () => {
    cy.contains('Activity Log').should('exist')
  })

})