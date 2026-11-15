import type { Page, APIRequestContext } from '@playwright/test'

export const ORGS = { data: [{ id: 'org-a', name: 'Acme IT', role: 'org_admin' }] }

export async function resetEmulator(request: APIRequestContext) {
  await request.delete('http://127.0.0.1:9099/emulator/v1/projects/demo-nexora/accounts')
}

export async function mockBackend(page: Page, orgs: unknown = ORGS) {
  await page.route('**/api/v1/health', (r) => r.fulfill({ json: { status: 'ok', version: '0.1.0' } }))
  await page.route('**/api/v1/me/organizations', (r) => r.fulfill({ json: orgs }))
}

export async function signUp(page: Page, email: string) {
  await page.goto('/sign-in')
  await page.getByRole('button', { name: 'Create an account' }).click()
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill('password1')
  await page.getByRole('button', { name: 'Create account' }).click()
}
