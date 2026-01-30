/**
 * HyperOS Electron Security Module
 * CSP, IPC validation, and security hardening
 */

import { session, app, shell } from 'electron';

export const CSP_POLICY = [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob:",
    "connect-src 'self' http://127.0.0.1:8000 http://localhost:8000",
    "frame-src 'none'",
    "object-src 'none'",
].join('; ');

export const VALID_CHANNELS = {
    send: ['set-click-through', 'show-window', 'hide-window', 'quit-app'],
    invoke: ['get-app-version', 'get-visibility'],
};

export function isValidChannel(channel: string, type: 'send' | 'invoke'): boolean {
    return VALID_CHANNELS[type].includes(channel);
}

export function applySecurityHeaders(): void {
    session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
        callback({
            responseHeaders: {
                ...details.responseHeaders,
                'Content-Security-Policy': [CSP_POLICY],
                'X-Content-Type-Options': ['nosniff'],
                'X-Frame-Options': ['DENY'],
            },
        });
    });
}

export function disableDangerousFeatures(): void {
    app.on('web-contents-created', (_, contents) => {
        contents.on('will-navigate', (event, url) => {
            if (url.startsWith('javascript:') || url.startsWith('data:')) {
                event.preventDefault();
            }
        });
        contents.setWindowOpenHandler(({ url }) => {
            if (url.startsWith('http')) shell.openExternal(url);
            return { action: 'deny' };
        });
    });
}

export function initializeSecurity(): void {
    applySecurityHeaders();
    disableDangerousFeatures();
    console.log('Security initialized');
}
