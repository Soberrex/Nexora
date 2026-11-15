import { expect, test } from '@playwright/test'

test.describe('app shell smoke', () => {
  test('overview shows live API status', async ({ page }) => {
    await page.route('**/api/v1/health', (route) =>
      route.fulfill({ json: { status: 'ok', version: '0.1.0' } }),
    )
    await page.goto('/')
    await expect(page.getByRole('heading', { level: 1, name: 'Overview' })).toBeVisible()
    await expect(page.getByText('API connected (version 0.1.0)')).toBeVisible()
  })

  test('shows an error with retry when the API is down', async ({ page }) => {
    await page.route('**/api/v1/health', (route) =>
      route.fulfill({ status: 503, json: { detail: 'Service unavailable', code: null } }),
    )
    await page.goto('/')
    await expect(page.getByRole('alert')).toContainText('Service unavailable')
    await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible()
  })

  test('deep links work and navigation moves between modules', async ({ page }) => {
    await page.route('**/api/v1/health', (route) =>
      route.fulfill({ json: { status: 'ok', version: '0.1.0' } }),
    )
    await page.goto('/incidents')
    await expect(page.getByRole('heading', { level: 1, name: 'Incidents' })).toBeVisible()
    await page.getByRole('navigation', { name: 'Primary' }).getByRole('link', { name: 'Overview' }).click()
    await expect(page).toHaveURL('/')
  })
})
