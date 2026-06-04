/// <reference types="cypress" />
it('project 1', ()=>{


cy.visit('http://127.0.0.1:5500/login.html')


 cy.get("input[type='email'], input[name='email']").clear().type("hamam@cit.just.edu.jo");


    cy.get("input[type='password'], input[name='password']").clear().type("Hamam0*");



    cy.get('#loginBtn').click({ force: true });
 
    cy.get(':nth-child(1) > .card-body > .btn-fancy', { timeout: 10000 }).should("be.visible");
 
    cy.get(':nth-child(1) > .card-body > .btn-fancy').click({ force: true });
 
    cy.get(':nth-child(1) > input').clear().type("My Team");
 
    cy.get('textarea').clear().type("This is the best graduation team ever.");
 
    cy.get('.primary-btn').click({ force: true });
 
    cy.get('.green-btn').click({ force: true });
})