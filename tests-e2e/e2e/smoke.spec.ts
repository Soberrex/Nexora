import { expect, test } from '@playwright/test'

import { mockBackend, resetEmulator, signUp } from './helpers'

test.beforeEach(async ({ request, page }) => {
  await resetEmulator(request)
  await mockBackend(page)
  await signUp(page, 'smoke@example.com')
  await expect(page.getByRole('heading', { level: 1, name: 'Overview' })).toBeVisible()
})

test('overview shows live API status', async ({ page }) => {
  await expect(page.getByText('API connected (version 0.1.0)')).toBeVisible()
})

test('navigation moves between modules', async ({ page }) => {
  await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Incidents' }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Incidents' })).toBeVisible()
})
