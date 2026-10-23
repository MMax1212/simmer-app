import { defineConfig } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
const database = join(mkdtempSync(join(tmpdir(), "simmer-e2e-")), "test.db");
const executable = process.env.E2E_PYTHON ?? "python";
const python = process.platform === "win32"
    ? '"' + executable.replace(/"/g, '""') + '"'
    : "'" + executable.replace(/'/g, "'\"'\"'") + "'";
export default defineConfig({
    testDir: "./e2e",
    workers: 1,
    timeout: 30000,
    use: { baseURL: "http://127.0.0.1:5174", trace: "retain-on-failure" },
    webServer: [
        {
            command: python + " -m alembic upgrade head && " + python + " -m uvicorn app.main:app --host 127.0.0.1 --port 8001",
            cwd: "../backend",
            url: "http://127.0.0.1:8001/api/health",
            reuseExistingServer: false,
            env: {
                DATABASE_URL: "sqlite:///" + database,
                SECRET_KEY: "e2e-only-secret-not-for-deployment",
                CORS_ORIGINS: '["http://127.0.0.1:5174"]',
            },
        },
        {
            command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort",
            url: "http://127.0.0.1:5174",
            reuseExistingServer: false,
            env: { VITE_API_URL: "http://127.0.0.1:8001" },
        },
    ],
});
