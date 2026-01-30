/**
 * Type declarations for HyperOS Electron IPC APIs
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

export interface LegacyIPC {
    setIgnoreMouseEvents: (ignore: boolean, options?: { forward: boolean }) => void;
    on: (channel: string, callback: (...args: any[]) => void) => void;
    off: (channel: string, callback: (...args: any[]) => void) => void;
    send: (channel: string, ...args: any[]) => void;
    invoke: (channel: string, ...args: any[]) => Promise<any>;
}

declare global {
    interface Window {
        hyperOS: HyperOSAPI;
        ipcRenderer: LegacyIPC;
    }
}

export { };
