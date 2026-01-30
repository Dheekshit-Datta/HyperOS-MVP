/// <reference types="vite/client" />

/**
 * HyperOS Electron API type declarations
 */

interface HyperOSAPI {
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

interface LegacyIPC {
    setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => void;
    on: (channel: string, callback: (...args: unknown[]) => void) => void;
    off: (channel: string, callback: (...args: unknown[]) => void) => void;
    send: (channel: string, ...args: unknown[]) => void;
    invoke: (channel: string, ...args: unknown[]) => Promise<unknown>;
}

declare global {
    interface Window {
        hyperOS: HyperOSAPI;
        ipcRenderer: LegacyIPC;
    }
}

export { };
