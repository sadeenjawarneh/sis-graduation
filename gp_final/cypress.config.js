const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    // Base URL of the backend which also serves the frontend
    baseUrl: 'http://localhost:8000',
    // Location of test files
    specPattern: 'cypress/e2e/**/*.cy.js',
    // Folder for fixtures (test data)
    fixturesFolder: 'cypress/fixtures',
    // Default command timeout (ms)
    defaultCommandTimeout: 6000,
    setupNodeEvents(on, config) {
      // Add plugins here if needed
    },
  },
})
