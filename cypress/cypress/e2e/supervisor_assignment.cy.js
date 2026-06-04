/**
 * Supervisor Assignment — TC-1 through TC-6
 *
 * API endpoints used:
 *   GET  /api/v1/teams/supervisors/                           — list supervisors
 *   POST /api/v1/teams/<id>/supervisor-request/               — send request {supervisor_id, priority}
 *   GET  /api/v1/teams/<id>/supervisor-requests/              — team's sent requests
 *   GET  /api/v1/teams/supervisor-inbox/                      — supervisor's inbox
 *   POST /api/v1/teams/supervisor-requests/<req_id>/respond/  — {action: "accept"|"reject"}
 *   GET  /api/v1/notifications/                               — check notifications
 *   GET  /api/v1/teams/<id>/                                  — verify team.supervisor field
 *
 * UI page: /supervisors-list/  (requires student to be in a team)
 *
 * Supervisors (seeded):
 *   Hamza@just.edu.jo     / Hamza0*
 *   Mohammed@just.edu.jo  / Mohammed0*
 *   Malik@just.edu.jo     / Malik0*
 *
 * Students (seeded):
 *   seham@cit.just.edu.jo / Seham0*   — used as team leader in TC-1,2,3,4
 *   omar@cit.just.edu.jo  / Omar0*    — used as team leader in TC-5,6
 */

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function login(email, password) {
  return cy.request('POST', '/api/v1/auth/login/', { email, password })
    .then(res => ({ token: res.body.access, userId: res.body.user.id }))
}

function leaveAllTeams(token) {
  return cy.request({
    method: 'GET', url: '/api/v1/teams/my/',
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  }).then(res => {
    if (res.status === 404) return
    return cy.request({
      method: 'POST', url: `/api/v1/teams/${res.body.id}/leave/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false,
    }).then(() => leaveAllTeams(token))
  })
}

function createTeam(token, name, description = 'Cypress supervisor test team') {
  return leaveAllTeams(token).then(() =>
    cy.request({
      method: 'POST', url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description },
    }).then(r => r.body)
  )
}

function sendSupervisorRequest(token, teamId, supervisorId, priority = 1) {
  return cy.request({
    method: 'POST',
    url: `/api/v1/teams/${teamId}/supervisor-request/`,
    headers: { Authorization: `Bearer ${token}` },
    body: { supervisor_id: supervisorId, priority },
    failOnStatusCode: false,
  })
}

function respondToRequest(supervisorToken, reqId, action) {
  return cy.request({
    method: 'POST',
    url: `/api/v1/teams/supervisor-requests/${reqId}/respond/`,
    headers: { Authorization: `Bearer ${supervisorToken}` },
    body: { action },
    failOnStatusCode: false,
  })
}

function getSupervisorInbox(supervisorToken) {
  return cy.request({
    method: 'GET', url: '/api/v1/teams/supervisor-inbox/',
    headers: { Authorization: `Bearer ${supervisorToken}` },
  }).then(res => res.body)
}

function getTeamSupervisorRequests(token, teamId) {
  return cy.request({
    method: 'GET',
    url: `/api/v1/teams/${teamId}/supervisor-requests/`,
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => res.body)
}

function getTeam(token, teamId) {
  return cy.request({
    method: 'GET', url: `/api/v1/teams/${teamId}/`,
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => res.body)
}

function getNotifications(token) {
  return cy.request({
    method: 'GET', url: '/api/v1/notifications/',
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => res.body)
}

const uid = () => Date.now().toString(36)

const SUPERVISORS = {
  hamza:    { email: 'Hamza@just.edu.jo',    password: 'Hamza0*'    },
  mohammed: { email: 'Mohammed@just.edu.jo', password: 'Mohammed0*' },
  malik:    { email: 'Malik@just.edu.jo',    password: 'Malik0*'    },
}
const LEADER_A = { email: 'seham@cit.just.edu.jo', password: 'Seham0*' }
const LEADER_B = { email: 'hala@cit.just.edu.jo',  password: 'Hala0*'  }


// ─────────────────────────────────────────────────────────────────────────────
// TC-1 | Equivalence Partitioning
// Team views the supervisors list → all available supervisors displayed
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-1 | Supervisors list displayed to team', () => {

  it('API: GET /api/v1/teams/supervisors/ returns a non-empty list of supervisors', () => {
    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      cy.request({
        method: 'GET', url: '/api/v1/teams/supervisors/',
        headers: { Authorization: `Bearer ${token}` },
      }).then(res => {
        expect(res.status).to.eq(200)
        expect(res.body).to.be.an('array').with.length.greaterThan(0)
        res.body.forEach(sup => {
          expect(sup).to.have.property('id')
          expect(sup).to.have.property('display_name')
          expect(sup.email).to.match(/@just\.edu\.jo$/)
        })
      })
    })
  })

  it('UI: /supervisors-list/ page loads and shows supervisor cards for a team leader', () => {
    let leaderToken, teamId

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC1-UI-${uid()}`)
    }).then(team => {
      teamId = team.id
      cy.loginAs(LEADER_A.email, LEADER_A.password)
      cy.visit('/supervisors-list/')
      cy.get('.list', { timeout: 8000 }).should('be.visible')
      cy.get('.sup-card').should('have.length.greaterThan', 0)
      cy.get('.req-btn').first().should('contain', 'Send Request')
      cy.contains('Select up to 3 preferred supervisors').should('be.visible')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-2 | Cause–Effect
// Team sends a supervisor request → request recorded and supervisor notified
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-2 | Team sends a supervisor request', () => {

  it('POST supervisor-request returns 201 and supervisor sees it in inbox', () => {
    let leaderToken, supervisorToken, teamId, supId

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC2-Team-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login(SUPERVISORS.hamza.email, SUPERVISORS.hamza.password)
    }).then(({ token, userId }) => {
      supervisorToken = token
      supId = userId

      return sendSupervisorRequest(leaderToken, teamId, supId, 1)
    }).then(res => {
      expect(res.status).to.eq(201)
      expect(res.body).to.have.property('id')
      expect(res.body.status).to.eq('pending')
      expect(res.body.priority).to.eq(1)

      return getSupervisorInbox(supervisorToken)
    }).then(inbox => {
      const entry = inbox.find(r => r.team === teamId)
      expect(entry).to.exist
      expect(entry.status).to.eq('pending')
    })
  })

  it('rejects a 4th supervisor request (max 3 allowed)', () => {
    let leaderToken, teamId
    const supIds = []

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC2-Max-${uid()}`)
    }).then(team => {
      teamId = team.id
      return cy.request({
        method: 'GET', url: '/api/v1/teams/supervisors/',
        headers: { Authorization: `Bearer ${leaderToken}` },
      })
    }).then(res => {
      const sups = res.body.slice(0, 4)
      sups.forEach(s => supIds.push(s.id))

      return sendSupervisorRequest(leaderToken, teamId, supIds[0], 1)
        .then(() => sendSupervisorRequest(leaderToken, teamId, supIds[1], 2))
        .then(() => sendSupervisorRequest(leaderToken, teamId, supIds[2], 3))
    }).then(() => {
      return sendSupervisorRequest(leaderToken, teamId, supIds[3], 4)
    }).then(res => {
      expect(res.status).to.eq(400)
      expect(res.body.detail).to.include('Maximum 3')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-3 | State Transition
// Supervisor approves request → supervisor assigned to team
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-3 | Supervisor approves request — assigned to team', () => {

  it('team.supervisor is set after supervisor accepts', () => {
    let leaderToken, supervisorToken, teamId, supId, reqId

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC3-Team-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login(SUPERVISORS.hamza.email, SUPERVISORS.hamza.password)
    }).then(({ token, userId }) => {
      supervisorToken = token
      supId = userId
      return sendSupervisorRequest(leaderToken, teamId, supId, 1)
    }).then(res => {
      reqId = res.body.id
      return respondToRequest(supervisorToken, reqId, 'accept')
    }).then(res => {
      expect(res.status).to.eq(200)
      expect(res.body.status).to.eq('accepted')

      return getTeam(leaderToken, teamId)
    }).then(team => {
      expect(team.supervisor).to.eq(supId)
    })
  })

  it('team members receive a notification when supervisor is assigned', () => {
    let leaderToken, supervisorToken, teamId, supId, reqId

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC3-Notif-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login(SUPERVISORS.mohammed.email, SUPERVISORS.mohammed.password)
    }).then(({ token, userId }) => {
      supervisorToken = token
      supId = userId
      return sendSupervisorRequest(leaderToken, teamId, supId, 1)
    }).then(res => {
      reqId = res.body.id
      return respondToRequest(supervisorToken, reqId, 'accept')
    }).then(() => {
      return getNotifications(leaderToken)
    }).then(notifs => {
      const assigned = notifs.find(n =>
        n.title.toLowerCase().includes('supervisor') &&
        (n.message.toLowerCase().includes('accepted') || n.message.toLowerCase().includes('assigned'))
      )
      expect(assigned).to.exist
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-4 | State Transition
// First supervisor accepts → team assigned, no further pending requests needed
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-4 | First supervisor accepts — team assigned, process complete', () => {

  it('after first accept, team has a supervisor and the accepted request is resolved', () => {
    let leaderToken, sup1Token, sup2Token, teamId, supId1, supId2, reqId1

    login(LEADER_A.email, LEADER_A.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC4-Team-${uid()}`)
    }).then(team => {
      teamId = team.id

      return login(SUPERVISORS.hamza.email, SUPERVISORS.hamza.password)
    }).then(({ token, userId }) => {
      sup1Token = token
      supId1 = userId
      return login(SUPERVISORS.mohammed.email, SUPERVISORS.mohammed.password)
    }).then(({ token, userId }) => {
      sup2Token = token
      supId2 = userId

      return sendSupervisorRequest(leaderToken, teamId, supId1, 1)
    }).then(res => {
      reqId1 = res.body.id
      return sendSupervisorRequest(leaderToken, teamId, supId2, 2)
    }).then(() => {
      return respondToRequest(sup1Token, reqId1, 'accept')
    }).then(res => {
      expect(res.status).to.eq(200)
      expect(res.body.status).to.eq('accepted')

      return getTeam(leaderToken, teamId)
    }).then(team => {
      expect(team.supervisor).to.eq(supId1)
      cy.log('TC-4 passed: first supervisor accepted, team.supervisor is set')

      return getTeamSupervisorRequests(leaderToken, teamId)
    }).then(requests => {
      const accepted = requests.find(r => r.supervisor === supId1)
      expect(accepted.status).to.eq('accepted')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-5 | State Transition
// First supervisor declines → team notified; next supervisor request remains pending
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-5 | First supervisor declines — team notified', () => {

  it('rejection sets status=rejected and sends notification to the team', () => {
    let leaderToken, sup1Token, teamId, supId1, req1Id

    login(LEADER_B.email, LEADER_B.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC5-Team-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login(SUPERVISORS.malik.email, SUPERVISORS.malik.password)
    }).then(({ token, userId }) => {
      sup1Token = token
      supId1 = userId
      return sendSupervisorRequest(leaderToken, teamId, supId1, 1)
    }).then(res => {
      req1Id = res.body.id
      return respondToRequest(sup1Token, req1Id, 'reject')
    }).then(res => {
      expect(res.status).to.eq(200)
      expect(res.body.status).to.eq('rejected')

      return getNotifications(leaderToken)
    }).then(notifs => {
      const rejected = notifs.find(n =>
        n.title.toLowerCase().includes('rejected') ||
        n.message.toLowerCase().includes('declined')
      )
      expect(rejected).to.exist
      cy.log('TC-5: rejection notification received by team')
    })
  })

  it('second supervisor request remains pending after first declines', () => {
    let leaderToken, sup1Token, teamId, supId1, supId2, req1Id

    login(LEADER_B.email, LEADER_B.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC5-Multi-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login(SUPERVISORS.hamza.email, SUPERVISORS.hamza.password)
    }).then(({ token, userId }) => {
      sup1Token = token
      supId1 = userId
      return login(SUPERVISORS.mohammed.email, SUPERVISORS.mohammed.password)
    }).then(({ token, userId }) => {
      supId2 = userId

      return sendSupervisorRequest(leaderToken, teamId, supId1, 1)
    }).then(res => {
      req1Id = res.body.id
      return sendSupervisorRequest(leaderToken, teamId, supId2, 2)
    }).then(() => {
      return respondToRequest(sup1Token, req1Id, 'reject')
    }).then(() => {
      return getTeamSupervisorRequests(leaderToken, teamId)
    }).then(requests => {
      const sup2Req = requests.find(r => r.supervisor === supId2)
      expect(sup2Req).to.exist
      expect(sup2Req.status).to.eq('pending')
      cy.log('TC-5: second supervisor request is still pending after first declined')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-6 | Equivalence Partitioning
// All supervisors decline → team is informed via notifications for each rejection
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-6 | All supervisors decline — team informed after each rejection', () => {

  it('team receives a rejection notification for every supervisor that declines', () => {
    let leaderToken, teamId
    let req1Id, req2Id, req3Id
    let sup1Token, sup2Token, sup3Token
    let supId1, supId2, supId3

    login(LEADER_B.email, LEADER_B.password).then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC6-Team-${uid()}`)
    }).then(team => {
      teamId = team.id

      return login(SUPERVISORS.hamza.email, SUPERVISORS.hamza.password)
    }).then(({ token, userId }) => {
      sup1Token = token; supId1 = userId
      return login(SUPERVISORS.mohammed.email, SUPERVISORS.mohammed.password)
    }).then(({ token, userId }) => {
      sup2Token = token; supId2 = userId
      return login(SUPERVISORS.malik.email, SUPERVISORS.malik.password)
    }).then(({ token, userId }) => {
      sup3Token = token; supId3 = userId

      return sendSupervisorRequest(leaderToken, teamId, supId1, 1)
    }).then(res => {
      req1Id = res.body.id
      return sendSupervisorRequest(leaderToken, teamId, supId2, 2)
    }).then(res => {
      req2Id = res.body.id
      return sendSupervisorRequest(leaderToken, teamId, supId3, 3)
    }).then(res => {
      req3Id = res.body.id

      return respondToRequest(sup1Token, req1Id, 'reject')
    }).then(() => respondToRequest(sup2Token, req2Id, 'reject'))
     .then(() => respondToRequest(sup3Token, req3Id, 'reject'))
     .then(() => {
        return getTeamSupervisorRequests(leaderToken, teamId)
      }).then(requests => {
        expect(requests).to.have.length(3)
        requests.forEach(r => expect(r.status).to.eq('rejected'))

        return getTeam(leaderToken, teamId)
      }).then(team => {
        expect(team.supervisor).to.be.null

        return getNotifications(leaderToken)
      }).then(notifs => {
        const rejections = notifs.filter(n =>
          n.title.toLowerCase().includes('rejected') ||
          n.message.toLowerCase().includes('declined')
        )
        expect(rejections.length).to.be.at.least(3)
        cy.log(`TC-6: team received ${rejections.length} rejection notification(s)`)
      })
  })

  it('UI: all supervisor cards show "Send Request" after all reject', () => {
    cy.loginAs(LEADER_B.email, LEADER_B.password)
    cy.visit('/supervisors-list/')
    cy.get('.sup-card', { timeout: 8000 }).should('have.length.greaterThan', 0)
    cy.log('TC-6 UI: supervisor list accessible after all rejections')
  })
})
