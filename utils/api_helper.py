import json


def create_mock_user(page, email: str, password: str) -> dict:
    def handle(route):
        route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps({"id": "mock-user-1", "email": email}),
        )

    page.route("**/api/test-users", handle)
    page.evaluate(
        """async (u) => {
          const r = await fetch('/api/test-users', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(u),
          });
          return r.json();
        }""",
        {"email": email, "password": password},
    )
    page.unroute("**/api/test-users", handle)
    return {"email": email, "password": password}
