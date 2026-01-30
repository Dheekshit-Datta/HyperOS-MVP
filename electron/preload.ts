/**
 * HyperOS Electron Preload Script
 * Exposes safe IPC bridge to renderer via contextBridge
 * 
 * Security: contextIsolation is enabled, no direct Node.js access
 */

import { contextBridge, ipcRenderer } from 'electron';

/**
 * Type definitions for the exposed API
 */
export interface HyperOSAPI {
    /** Enable or disable click-through mode */
    setClickThrough: (enabled: boolean) => void;

    /** Get the application version */
    getAppVersion: () => Promise<string>;

    /** Get current window visibility state */
    getVisibility: () => Promise<boolean>;

    /** Show the main window */
    showWindow: () => void;

    /** Hide the main window */
    hideWindow: () => void;

    /** Quit the application */
    quitApp: () => void;

    /** Platform identifier */
    platform: NodeJS.Platform;
}

/**
 * Legacy IPC API for backward compatibility
 */
export interface LegacyIPC {
    setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => void;
    on: (channel: string, callback: (...args: any[]) => void) => void;
    off: (channel: string, callback: (...args: any[]) => void) => void;
    send: (channel: string, ...args: any[]) => void;
    invoke: (channel: string, ...args: any[]) => Promise<any>;
}

// Expose HyperOS API to renderer
contextBridge.exposeInMainWorld('hyperOS', {
    /**
     * Set click-through mode
     * When enabled, mouse events pass through to underlying windows
     */
    setClickThrough: (enabled: boolean): void => {
        ipcRenderer.send('set-click-through', enabled);
    },

    /**
     * Get application version
     */
    getAppVersion: (): Promise<string> => {
        return ipcRenderer.invoke('get-app-version');
    },

    /**
     * Get window visibility state
     */
    getVisibility: (): Promise<boolean> => {
        return ipcRenderer.invoke('get-visibility');
    },

    /**
     * Show the main window
     */
    showWindow: (): void => {
        ipcRenderer.send('show-window');
    },

    /**
     * Hide the main window
     */
    hideWindow: (): void => {
        ipcRenderer.send('hide-window');
    },

    /**
     * Quit the application
     */
    quitApp: (): void => {
        ipcRenderer.send('quit-app');
    },

    /**
     * Platform identifier
     */
    platform: process.platform,
} as HyperOSAPI);

// Expose legacy ipcRenderer API for backward compatibility
contextBridge.exposeInMainWorld('ipcRenderer', {
    /**
     * Set ignore mouse events (legacy API)
     */
    setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }): void => {
        ipcRenderer.send('set-click-through', ignore);
    },

    /**
     * Listen to IPC events
     */
    on: (channel: string, callback: (...args: any[]) => void) => {
        const validChannels = ['window-visibility-changed', 'shortcut-triggered'];
        if (validChannels.includes(channel)) {
            ipcRenderer.on(channel, (event, ...args) => callback(...args));
        }
    },

    /**
     * Remove IPC event listener
     */
    off: (channel: string, callback: (...args: any[]) => void) => {
        ipcRenderer.removeListener(channel, callback);
    },

    /**
     * Send IPC message
     */
    send: (channel: string, ...args: any[]): void => {
        const validChannels = ['set-click-through', 'show-window', 'hide-window', 'quit-app'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, ...args);
        }
    },

    /**
     * Invoke IPC method with response
     */
    invoke: (channel: string, ...args: any[]): Promise<any> => {
        const validChannels = ['get-app-version', 'get-visibility'];
        if (validChannels.includes(channel)) {
            return ipcRenderer.invoke(channel, ...args);
        }
        return Promise.reject(new Error(`Invalid channel: ${channel}`));
    },
} as LegacyIPC);

// Log preload completion
console.log('HyperOS preload script loaded');
