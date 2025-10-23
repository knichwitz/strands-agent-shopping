import { describe, it, expect, beforeAll } from 'vitest';
import { RohlikAPI } from '../src/rohlik-api.js';

describe('Handover Cart', () => {
    let api: RohlikAPI;

    beforeAll(async () => {
        api = new RohlikAPI();
        await api.loadSession();
    });

    it('should return session cookie', () => {
        const sessionCookie = api.getSessionCookie();

        expect(typeof sessionCookie).toBe('string');

        // If session exists, it should not be empty
        if (sessionCookie) {
            expect(sessionCookie.length).toBeGreaterThan(0);
            console.log('Session cookie available for handover');
        } else {
            console.log('No session cookie found (expected if no session file exists)');
        }
    });

    it('should have session cookie after API operations', async () => {
        // Perform a search to ensure we have a session
        await api.searchProducts('milk', 1);

        const sessionCookie = api.getSessionCookie();

        expect(typeof sessionCookie).toBe('string');
        expect(sessionCookie.length).toBeGreaterThan(0);

        console.log('Session cookie length:', sessionCookie.length);
    });
});
