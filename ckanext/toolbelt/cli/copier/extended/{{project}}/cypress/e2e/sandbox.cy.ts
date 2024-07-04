const ckan = () => cy.window({ log: false }).then((win) => win["ckan"]);

const sandbox = () => ckan().invoke({ log: false }, "sandbox");

const intercept = (
    action: string,
    alias: string = "request",
    result: any = {},
    success: boolean = true,
) =>
    cy
        .intercept("/api/action/" + action, (req) =>
            req.reply(
                Object.assign(
                    { success },
                    success ? { result } : { error: result },
                ),
            ),
        )
        .as(alias);

beforeEach(() => {
    cy.login();
    cy.visit("/");
});

describe("Feature", () => {
    it("can do things", () => {
        ckan()
            .its("things")
            .should("have.all.keys", "can", "do");
    });
    it("cannot do other things", () => {

    });
});
