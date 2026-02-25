import { render, screen, waitFor } from '@testing-library/react'
import Page from '../src/app/page'

// Mock global fetch
global.fetch = jest.fn(() =>
    Promise.resolve({
        json: () => Promise.resolve({ locations: [], cuisines: [] }),
    })
) as jest.Mock;

describe('Next.js Zomato UI Home', () => {
    beforeEach(() => {
        (global.fetch as jest.Mock).mockClear();
    });

    it('renders a beautiful heading', async () => {
        render(<Page />)
        const heading = screen.getByRole('heading', { level: 2 })
        expect(heading).toBeInTheDocument()
        expect(heading).toHaveTextContent("Can't decide? Ask Zomato AI.")
    })

    it('contains the search prompt input', async () => {
        render(<Page />)
        const prompts = screen.getAllByRole('textbox')
        expect(prompts.length).toBeGreaterThan(0)
        // The second textbox is our AI prompt
        expect(prompts[1]).toBeDefined()
    })

    it('renders the initial empty state message instead of mock cards', async () => {
        render(<Page />)
        await waitFor(() => {
            const emptyState = screen.getByText(/Pick some filters and click "Find with AI"/i)
            expect(emptyState).toBeInTheDocument()
        });
    })

    it('renders the "Find with AI" button', async () => {
        render(<Page />)
        const button = screen.getByRole('button', { name: /Find with AI/i })
        expect(button).toBeInTheDocument()
    })
})
