// Login via API and set tokens in localStorage
Cypress.Commands.add('loginAs', (email, password) => {
  cy.request('POST', '/api/v1/auth/login/', { email, password }).then(({ body }) => {
    localStorage.setItem('access', body.access)
    localStorage.setItem('refresh', body.refresh)
    localStorage.setItem('user', JSON.stringify(body.user))
    return body.access
  })
})

// Leave all teams the user is in — recursive until /my/ returns 404
Cypress.Commands.add('leaveAllTeams', (token) => {
  cy.request({
    method: 'GET', url: '/api/v1/teams/my/',
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  }).then(res => {
    if (res.status === 404) return
    cy.request({
      method: 'POST', url: `/api/v1/teams/${res.body.id}/leave/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false,
    }).then(() => cy.leaveAllTeams(token))
  })
})

// Create a team via API — leaves all existing teams first
Cypress.Commands.add('createTeamViaAPI', (token, name = 'Cypress Test Team', description = 'Created by Cypress tests') => {
  cy.leaveAllTeams(token).then(() =>
    cy.request({
      method: 'POST',
      url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description },
      failOnStatusCode: false,
    })
  )
})
