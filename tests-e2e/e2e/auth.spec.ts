import { expect, test } from '@playwright/test'

import { mockBackend, resetEmulator, signUp } from './helpers'

test.beforeEach(async ({ request }) => resetEmulator(request))

test('protected pages redirect to sign in', async ({ page }) => {
  await mockBackend(page)
  await page.goto('/incidents')
  await expect(page).toHaveURL(/\/sign-in\?next=%2Fincidents/)
})

test('sign up, see the organization, sign out', async ({ page }) => {
  await mockBackend(page)
  await signUp(page, 'e2e@example.com')
  await expect(page.getByRole('heading', { level: 1, name: 'Overview' })).toBeVisible()
  await expect(page.getByLabel('Organization')).toHaveValue('org-a')
  await page.getByRole('button', { name: 'Sign out' }).click()
  await expect(page.getByRole('heading', { name: 'Sign in to Nexora' })).toBeVisible()
})

test('API requests carry the token and organization header', async ({ page }) => {
  await mockBackend(page)
  const orgsRequest = page.waitForRequest('**/api/v1/me/organizations')
  await signUp(page, 'headers@example.com')
  const request = await orgsRequest
  expect(request.headers()['authorization']).toMatch(/^Bearer .+/)
})

test('user without organizations sees the empty state', async ({ page }) => {
  await mockBackend(page, { data: [] })
  await signUp(page, 'lonely@example.com')
  await expect(page.getByRole('heading', { name: 'No organization yet' })).toBeVisible()
})

test('wrong password shows an error', async ({ page }) => {
  await mockBackend(page)
  await signUp(page, 'pw@example.com')
  await page.getByRole('button', { name: 'Sign out' }).click()
  await page.getByLabel('Email').fill('pw@example.com')
  await page.getByLabel('Password').fill('nope-nope')
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page.getByRole('alert')).toContainText('Incorrect email or password')
})
