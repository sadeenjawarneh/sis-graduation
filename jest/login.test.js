const { login, MAX_ATTEMPTS, LOCKOUT_TIME } = require("./login");

/* STUDENT LOGIN TESTS  */

// TC-1
test("TC-1: Student valid login", () => {
  const r = login("sadeen@cit.just.edu.jo", "Sadeen0*");
  expect(r.success).toBe(true);
  expect(r.role).toBe("student");
});

// TC-2
test("TC-2: Student invalid username and password", () => {
  const r = login("wrong@cit.just.edu.jo", "wrong");
  expect(r.success).toBe(false);
});

// TC-3
test("TC-3: Student invalid password", () => {
  const r = login("sadeen@cit.just.edu.jo", "wrong");
  expect(r.success).toBe(false);
});

// TC-4
test("TC-4: Student invalid username", () => {
  const r = login("fake@cit.just.edu.jo", "Sadeen0*");
  expect(r.success).toBe(false);
});

// TC-5
test("TC-5: Student empty username", () => {
  const r = login("", "Sadeen0*");
  expect(r.success).toBe(false);
});

// TC-6
test("TC-6: Student empty password", () => {
  const r = login("sadeen@cit.just.edu.jo", "");
  expect(r.success).toBe(false);
});

/* SUPERVISOR LOGIN TESTS  */

// TC-7
test("TC-7: Supervisor valid login", () => {
  const r = login("hamza@just.edu.jo", "Hamza0*");
  expect(r.success).toBe(true);
  expect(r.role).toBe("supervisor");
});

// TC-8
test("TC-8: Supervisor invalid username and password", () => {
  const r = login("wrong@just.edu.jo", "wrong");
  expect(r.success).toBe(false);
});

// TC-9
test("TC-9: Supervisor invalid password", () => {
  const r = login("hamza@just.edu.jo", "wrong");
  expect(r.success).toBe(false);
});

// TC-10
test("TC-10: Supervisor invalid username", () => {
  const r = login("fake@just.edu.jo", "Hamza0*");
  expect(r.success).toBe(false);
});

// TC-11
test("TC-11: Supervisor empty username", () => {
  const r = login("", "Hamza0*");
  expect(r.success).toBe(false);
});

// TC-12
test("TC-12: Supervisor empty password", () => {
  const r = login("hamza@just.edu.jo", "");
  expect(r.success).toBe(false);
});

/* SECURITY / ACCOUNT LOCKOUT TEST */

// TC-13
test("TC-13: Account locked after 5 failed attempts for 10 minutes", () => {
  const fakeNow = 1_000_000;

  const r = login(
    "sadeen@cit.just.edu.jo",
    "wrong",
    MAX_ATTEMPTS - 1,
    fakeNow
  );

  expect(r.success).toBe(false);
  expect(r.locked).toBe(true);
  expect(r.lockoutUntil).toBe(fakeNow + LOCKOUT_TIME);
});
