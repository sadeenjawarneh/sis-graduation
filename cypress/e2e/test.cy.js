describe('template spec', () => {
  it('passes', () => {

  })
});

it('create teem', function() {
  describe("Graduation Project - Create Team Page Test", () => {
  
    it("Test team creation and supervisor request", () => {
              cy.visit("http://127.0.0.1:5500/create_team.html");
          
          
          
      
      
    });
  
  });
  
  
});

it('test', function() {
      describe("Graduation Project - Login and Create Team Test", () => {
      
        it("Login with Hamam and create a team", () => {
      
          // 1️⃣ زيارة صفحة Login
          cy.visit("http://127.0.0.1:5500/login.html");
      
          // 2️⃣ تعبئة الايميل
          cy.get("input[type='email'], input[name='email']").clear().type("hamam@cit.just.edu.jo");
      
          // 3️⃣ تعبئة كلمة السر
          cy.get("input[type='password'], input[name='password']").clear().type("Hamam0*");
      
          // 4️⃣ الضغط على زر Login
          cy.contains("Log in, Login, Sign in").click({ force: true });
      
          // 5️⃣ تأكد الصفحة الجديدة ظهرت (مثلاً Create Team زر)
          cy.contains("Create Team", { timeout: 10000 }).should("be.visible");
      
          // 6️⃣ الضغط على Create Team
          cy.contains("Create Team").click({ force: true });
      
          // 7️⃣ تعبئة اسم الفريق
          cy.get("input#teamName, input[name='teamName']").clear().type("My Awesome Team");
      
          // 8️⃣ تعبئة وصف الفريق
          cy.get("textarea#teamDescription, textarea[name='teamDescription']").clear().type("This is the best graduation team ever.");
      
          // 9️⃣ تحقق من ظهور النصوص المهمة
          cy.contains("My Awesome Team", { timeout: 10000 }).should("be.visible");
          cy.contains("This is the best graduation team ever.", { timeout: 10000 }).should("be.visible");
      
          // 10️⃣ Optional: اضغط على Request Now لو موجود
          cy.contains("Request Now").click({ force: true });
      
        });
      
      });
      
});

it('tester', function() {
     cy.visit('https://example.cypress.io')
    
});