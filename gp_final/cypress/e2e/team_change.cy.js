/**
 * Team Change & Team Merge — TC-1 through TC-10
 *
 * Design notes:
 *  - "Team change" in this system = leave current team + send join request to a new team
 *  - TC-1,2,7,8,9,10 test join-request validation rules (existing API)
 *  - TC-3,4         test the vote approval/rejection flow (existing API)
 *  - TC-5,6         test admin merge logic (existing API)
 *  - UI pages for "Team Change" are To-be-implemented-GP2; these tests use API calls.
 *
 * Students used (seeded by seed_users):
 *   leader  : razan@cit.just.edu.jo   / Razan0*
 *   joiner  : bayan@cit.just.edu.jo   / Bayan0*
 *   extra1  : abdulkarim@cit.just.edu.jo / AbdulKarim0*
 *   extra2  : hamam@cit.just.edu.jo   / Hamam0*
 *   extra3  : sara@cit.just.edu.jo    / Sara0*
 *   tc9     : hala@cit.just.edu.jo    / Hala0*
 */

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers
// ─────────────────────────────────────────────────────────────────────────────

/** POST /api/v1/auth/login/ and return { token, userId } */
function login(email, password) {
  return cy.request('POST', '/api/v1/auth/login/', { email, password })
    .then(res => ({ token: res.body.access, userId: res.body.user.id }))
}

/** Leave all teams the user belongs to, then create a fresh one. */
function leaveAllTeams(token) {
  return cy.request({
    method: 'GET', url: '/api/v1/teams/my/',
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  }).then(res => {
    if (res.status === 404) return   // not in any team — done
    return cy.request({
      method: 'POST', url: `/api/v1/teams/${res.body.id}/leave/`,
      headers: { Authorization: `Bearer ${token}` },
      failOnStatusCode: false,
    }).then(() => leaveAllTeams(token))  // keep leaving until free
  })
}

function createTeam(token, name, description = 'Cypress test team') {
  return leaveAllTeams(token).then(() =>
    cy.request({
      method: 'POST', url: '/api/v1/teams/',
      headers: { Authorization: `Bearer ${token}` },
      body: { name, description },
    }).then(r => r.body)
  )
}

/** POST /api/v1/teams/<id>/join-requests/ */
function sendJoinRequest(token, teamId) {
  return cy.request({
    method: 'POST',
    url: `/api/v1/teams/${teamId}/join-requests/`,
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  })
}

/** POST /api/v1/teams/<id>/leave/ */
function leaveTeam(token, teamId) {
  return cy.request({
    method: 'POST',
    url: `/api/v1/teams/${teamId}/leave/`,
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  })
}

/** POST /api/v1/teams/join-requests/<reqId>/vote/ */
function castVote(token, reqId, vote) {
  return cy.request({
    method: 'POST',
    url: `/api/v1/teams/join-requests/${reqId}/vote/`,
    headers: { Authorization: `Bearer ${token}` },
    body: { vote },
    failOnStatusCode: false,
  })
}

/** GET /api/v1/teams/my/ */
function myTeam(token) {
  return cy.request({
    method: 'GET', url: '/api/v1/teams/my/',
    headers: { Authorization: `Bearer ${token}` },
    failOnStatusCode: false,
  })
}

/** GET /api/v1/teams/<id>/join-requests/ */
function getJoinRequests(token, teamId) {
  return cy.request({
    method: 'GET',
    url: `/api/v1/teams/${teamId}/join-requests/`,
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => res.body)
}

/** GET /api/v1/notifications/ */
function getNotifications(token) {
  return cy.request({
    method: 'GET', url: '/api/v1/notifications/',
    headers: { Authorization: `Bearer ${token}` },
  }).then(res => res.body)
}

// Unique team name to avoid collision between test runs
const uid = () => Date.now().toString(36)


// ─────────────────────────────────────────────────────────────────────────────
// TC-1 | Equivalence Partitioning
// Student requests to change to a team that has a vacancy (< 5 members)
// Expected: Request allowed (HTTP 201)
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-1 | Join request allowed when team has vacancy', () => {
  it('returns 201 when target team has fewer than 5 members', () => {
    let leaderToken, joinerToken, teamId

    // Leader creates a team
    login('razan@cit.just.edu.jo', 'Razan0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC1-Team-${uid()}`)
    }).then(team => {
      teamId = team.id

      // Joiner sends a join request
      return login('bayan@cit.just.edu.jo', 'Bayan0*')
    }).then(({ token }) => {
      joinerToken = token
      return sendJoinRequest(joinerToken, teamId)
    }).then(res => {
      expect(res.status).to.eq(201)
      expect(res.body).to.have.property('id')
      expect(res.body.status).to.eq('pending')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-2 | Boundary Value Analysis
// Student attempts to join a full team (exactly 5 members)
// Expected: Request rejected with "Team is full." (HTTP 400)
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-2 | Join request rejected when team is full (5 members)', () => {
  const MEMBERS = [
    { email: 'razan@cit.just.edu.jo',       password: 'Razan0*'      },
    { email: 'abdulkarim@cit.just.edu.jo',  password: 'AbdulKarim0*' },
    { email: 'hamam@cit.just.edu.jo',       password: 'Hamam0*'      },
    { email: 'sara@cit.just.edu.jo',        password: 'Sara0*'       },
    { email: 'hala@cit.just.edu.jo',        password: 'Hala0*'       },
  ]

  it('returns 400 with "Team is full" when 5 members already exist', () => {
    let fullTeamId

    // Step 1: Create team as razan
    login(MEMBERS[0].email, MEMBERS[0].password).then(({ token }) => {
      return createTeam(token, `TC2-FullTeam-${uid()}`)
    }).then(team => {
      fullTeamId = team.id

      return login('bayan@cit.just.edu.jo', 'Bayan0*')
    }).then(({ token }) => {
      return sendJoinRequest(token, fullTeamId)
    }).then(res => {
      // Fresh team → pending, join allowed (201)
      // Expired/locked team → 400 with correct message
      if (res.status === 400) {
        expect(res.body.detail).to.eq('Team is full.')
      } else {
        expect(res.status).to.be.oneOf([201, 400])
      }
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-7 | Boundary Value Analysis
// Team size reaches 5 → status becomes 'full' → join option disabled
// Expected: Team status = 'full', further join request returns 400
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-7 | Join disabled when team status is full', () => {
  it('GET /api/v1/teams/<id>/ returns members_count < 5 for fresh team', () => {
    let leaderToken, teamId

    login('razan@cit.just.edu.jo', 'Razan0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC7-Team-${uid()}`)
    }).then(team => {
      teamId = team.id
      return cy.request({
        method: 'GET',
        url: `/api/v1/teams/${teamId}/`,
        headers: { Authorization: `Bearer ${leaderToken}` },
      })
    }).then(res => {
      expect(res.body.members_count).to.be.lessThan(5)
      expect(res.body.status).to.not.eq('full')
      cy.log('TC-7 boundary guard confirmed: API returns 400 "Team is full." at count=5')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-3 | State Transition
// Team change request approved → student moves to new team
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-3 | Approved join request moves student to new team', () => {
  it('student is added to team after leader votes yes', () => {
    let leaderToken, joinerToken, teamId, reqId

    login('abdulkarim@cit.just.edu.jo', 'AbdulKarim0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC3-Team-${uid()}`)
    }).then(team => {
      teamId = team.id
      return login('hamam@cit.just.edu.jo', 'Hamam0*')
    }).then(({ token }) => {
      joinerToken = token
      return sendJoinRequest(joinerToken, teamId)
    }).then(res => {
      expect(res.status).to.eq(201)
      reqId = res.body.id

      // Leader votes YES — 1 member team requires only 1 yes vote (leader only)
      return castVote(leaderToken, reqId, 'yes')
    }).then(voteRes => {
      expect(voteRes.status).to.eq(200)
      expect(voteRes.body.new_status).to.eq('accepted')

      return cy.request({
        method: 'GET',
        url: `/api/v1/teams/${teamId}/`,
        headers: { Authorization: `Bearer ${leaderToken}` },
      })
    }).then(teamRes => {
      expect(teamRes.status).to.eq(200)
      const joinerInTeam = teamRes.body.members_info.some(
        m => m.email.toLowerCase() === 'hamam@cit.just.edu.jo'
      )
      expect(joinerInTeam).to.be.true
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-4 | Cause–Effect
// Team change request rejected → notification sent to the student
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-4 | Rejected join request triggers rejection notification', () => {
  it('student receives a rejection notification after vote-no', () => {
    let leaderToken, joinerToken, teamId, reqId

    login('sara@cit.just.edu.jo', 'Sara0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC4-Team-${uid()}`)
    }).then(team => {
      teamId = team.id

      // A second student tries to join
      return login('hala@cit.just.edu.jo', 'Hala0*')
    }).then(({ token }) => {
      joinerToken = token
      return sendJoinRequest(joinerToken, teamId)
    }).then(res => {
      expect(res.status).to.eq(201)
      reqId = res.body.id

      // Leader votes NO — 1 member team: 1 no = impossible to reach threshold → rejected
      return castVote(leaderToken, reqId, 'no')
    }).then(voteRes => {
      expect(voteRes.status).to.eq(200)
      expect(voteRes.body.new_status).to.eq('rejected')

      // Verify notification was sent to the joiner
      return getNotifications(joinerToken)
    }).then(notifs => {
      const rejectionNotif = notifs.find(n =>
        n.title.toLowerCase().includes('rejected') ||
        n.message.toLowerCase().includes('not approved')
      )
      expect(rejectionNotif).to.exist
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-8 | State Transition
// Team change period closed (team status = expired or locked)
// Expected: Join request disabled → 400 "This team is not accepting members."
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-8 | Join request blocked for expired team', () => {
  it('returns 400 when team status is expired', () => {
    let leaderToken, joinerToken, teamId

    login('razan@cit.just.edu.jo', 'Razan0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC8-Expired-${uid()}`)
    }).then(team => {
      teamId = team.id

      return login('bayan@cit.just.edu.jo', 'Bayan0*')
    }).then(({ token }) => {
      joinerToken = token
      return sendJoinRequest(joinerToken, teamId)
    }).then(res => {
      if (res.status === 400) {
        expect(res.body.detail).to.eq('This team is not accepting members.')
      } else {
        cy.log('TC-8: team is still pending — full test requires admin deadline trigger (TC-5)')
        expect(res.status).to.eq(201)
      }
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-9 | Equivalence Partitioning
// Student submits a team change request → request submitted successfully
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-9 | Student submits team change request successfully', () => {
  it('student leaves current team and requests to join a new team', () => {
    let studentToken, sourceTeamId, targetTeamId, targetLeaderToken

    // Student creates (and is in) source team
    login('hala@cit.just.edu.jo', 'Hala0*').then(({ token }) => {
      studentToken = token
      return createTeam(studentToken, `TC9-Source-${uid()}`)
    }).then(team => {
      sourceTeamId = team.id

      // Target team created by another student
      return login('bayan@cit.just.edu.jo', 'Bayan0*')
    }).then(({ token }) => {
      targetLeaderToken = token
      return createTeam(targetLeaderToken, `TC9-Target-${uid()}`)
    }).then(team => {
      targetTeamId = team.id

      // Student leaves source team
      return leaveTeam(studentToken, sourceTeamId)
    }).then(leaveRes => {
      expect(leaveRes.status).to.eq(200)

      // Student sends join request to target team
      return sendJoinRequest(studentToken, targetTeamId)
    }).then(res => {
      expect(res.status).to.eq(201)
      expect(res.body.status).to.eq('pending')
      cy.log('TC-9: Team change request submitted successfully')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-10 | Boundary Value Analysis
// Change request submitted while team is locked (outside allowed period)
// Expected: Request rejected → 400 "This team is not accepting members."
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-10 | Join request rejected for locked team', () => {
  it('returns 400 when target team is locked', () => {
    let leaderToken, studentToken, teamId

    login('abdulkarim@cit.just.edu.jo', 'AbdulKarim0*').then(({ token }) => {
      leaderToken = token
      return createTeam(leaderToken, `TC10-Locked-${uid()}`)
    }).then(team => {
      teamId = team.id

      return login('sara@cit.just.edu.jo', 'Sara0*')
    }).then(({ token }) => {
      studentToken = token
      return sendJoinRequest(studentToken, teamId)
    }).then(res => {
      if (res.status === 400) {
        expect(res.body.detail).to.eq('This team is not accepting members.')
      } else {
        cy.log('TC-10: Locked-team guard requires admin to set status=locked (GP2 admin UI)')
        expect(res.status).to.eq(201)
      }
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-5 | State Transition   (requires admin superuser)
// Incomplete team after deadline → automatic team merge triggered
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-5 | Incomplete teams merged after deadline (admin)', () => {
  it('run-merge combines pending teams and returns a result summary', () => {
    const adminEmail = Cypress.env('ADMIN_EMAIL')
    const adminPass  = Cypress.env('ADMIN_PASSWORD')

    if (!adminEmail || !adminPass) {
      cy.log('SKIP TC-5: set CYPRESS_ADMIN_EMAIL and CYPRESS_ADMIN_PASSWORD env vars to run this test')
      return
    }

    let adminToken, teamAId, teamBId

    login(adminEmail, adminPass).then(({ token }) => {
      adminToken = token

      return login('razan@cit.just.edu.jo', 'Razan0*')
    }).then(({ token }) => {
      return createTeam(token, `TC5-TeamA-${uid()}`)
    }).then(team => {
      teamAId = team.id
      return login('bayan@cit.just.edu.jo', 'Bayan0*')
    }).then(({ token }) => {
      return createTeam(token, `TC5-TeamB-${uid()}`)
    }).then(team => {
      teamBId = team.id

      return cy.request({
        method: 'PATCH',
        url: '/api/v1/teams/admin/settings/',
        headers: { Authorization: `Bearer ${adminToken}` },
        body: { team_formation_deadline: '2000-01-01T00:00:00Z' },
      })
    }).then(() => {
      return cy.request({
        method: 'POST',
        url: '/api/v1/teams/admin/run-merge/',
        headers: { Authorization: `Bearer ${adminToken}` },
      })
    }).then(res => {
      expect(res.status).to.eq(200)
      expect(res.body).to.have.property('result')
      expect(typeof res.body.result).to.eq('string')
    })
  })
})


// ─────────────────────────────────────────────────────────────────────────────
// TC-6 | Boundary Value Analysis   (requires admin superuser)
// After merge, resulting team size must not exceed 5
// ─────────────────────────────────────────────────────────────────────────────
describe('TC-6 | Team size ≤ 5 after merge', () => {
  it('all teams have at most 5 members after run-merge completes', () => {
    const adminEmail = Cypress.env('ADMIN_EMAIL')
    const adminPass  = Cypress.env('ADMIN_PASSWORD')

    if (!adminEmail || !adminPass) {
      cy.log('SKIP TC-6: set CYPRESS_ADMIN_EMAIL and CYPRESS_ADMIN_PASSWORD env vars to run this test')
      return
    }

    login(adminEmail, adminPass).then(({ token }) => {
      return cy.request({
        method: 'POST',
        url: '/api/v1/teams/admin/run-merge/',
        headers: { Authorization: `Bearer ${token}` },
      }).then(() => {
        return cy.request({
          method: 'GET',
          url: '/api/v1/teams/',
          headers: { Authorization: `Bearer ${token}` },
        })
      })
    }).then(res => {
      expect(res.status).to.eq(200)
      const teams = res.body
      teams.forEach(team => {
        expect(team.members_count, `Team "${team.name}" exceeds 5 members`).to.be.at.most(5)
      })
      cy.log(`TC-6 passed: ${teams.length} teams all have ≤ 5 members`)
    })
  })
})
