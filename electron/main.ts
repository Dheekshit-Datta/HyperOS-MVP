/**
 * HyperOS Electron Main Process
 * Creates a transparent, always-on-top overlay window for the AI agent
 */

import {
    app,
    BrowserWindow,
    screen,
    globalShortcut,
    ipcMain,
    Tray,
    Menu,
    shell,
    nativeImage
} from 'electron';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { initializeSecurity } from './security.js';

// ESM dirname equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Environment configuration
const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
const VITE_DEV_SERVER_URL = 'http://localhost:5173';

// Paths
const DIST_PATH = path.join(__dirname, '../dist');
const PUBLIC_PATH = isDev ? path.join(__dirname, '../public') : DIST_PATH;

// Window state persistence
interface WindowState {
    x?: number;
    y?: number;
    width: number;
    height: number;
    isVisible: boolean;
}

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let windowState: WindowState = {
    width: 0,
    height: 0,
    isVisible: true
};

/**
 * Prevent multiple instances of the app
 */
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    console.log('Another instance is already running. Exiting.');
    app.quit();
} else {
    app.on('second-instance', () => {
        // Focus the window if user tries to open another instance
        if (mainWindow) {
            if (!mainWindow.isVisible()) {
                mainWindow.show();
            }
            mainWindow.focus();
        }
    });
}

/**
 * Create the main transparent overlay window
 */
function createWindow(): void {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    // Use saved position if available, otherwise use defaults
    const windowConfig = {
        x: windowState.x,
        y: windowState.y,
        width: windowState.width || width,
        height: windowState.height || height,
    };

    mainWindow = new BrowserWindow({
        ...windowConfig,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        resizable: false,
        movable: false,
        hasShadow: false,
        backgroundColor: '#00000000',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true,
            sandbox: true,
            webSecurity: true,
        },
    });

    // Enable click-through by default
    mainWindow.setIgnoreMouseEvents(true, { forward: true });

    // Prevent the window from being closed, just hide it
    mainWindow.on('close', (event) => {
        if (!(app as any).isQuitting) {
            event.preventDefault();
            mainWindow?.hide();
            windowState.isVisible = false;
        }
    });

    // Save window state on move/resize
    mainWindow.on('moved', () => {
        if (mainWindow) {
            const bounds = mainWindow.getBounds();
            windowState.x = bounds.x;
            windowState.y = bounds.y;
        }
    });

    mainWindow.on('resized', () => {
        if (mainWindow) {
            const bounds = mainWindow.getBounds();
            windowState.width = bounds.width;
            windowState.height = bounds.height;
        }
    });

    // Handle external links - open in default browser
    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        if (url.startsWith('http://') || url.startsWith('https://')) {
            shell.openExternal(url);
        }
        return { action: 'deny' };
    });

    // Prevent navigation to external URLs
    mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
        const parsedUrl = new URL(navigationUrl);

        if (isDev && parsedUrl.origin === 'http://localhost:5173') {
            return; // Allow Vite HMR navigation
        }

        if (parsedUrl.protocol !== 'file:') {
            event.preventDefault();
            shell.openExternal(navigationUrl);
        }
    });

    // Load the app
    if (isDev) {
        mainWindow.loadURL(VITE_DEV_SERVER_URL);
        // Open DevTools in development (detached)
        mainWindow.webContents.openDevTools({ mode: 'detach' });
    } else {
        mainWindow.loadFile(path.join(DIST_PATH, 'index.html'));
    }

    console.log(`HyperOS window created (${isDev ? 'development' : 'production'} mode)`);
}

/**
 * Create system tray icon with menu
 */
function createTray(): void {
    // Create tray icon (use a small icon, 16x16 or 32x32)
    const iconPath = path.join(PUBLIC_PATH, 'icon.png');

        try {
            // Create a simple icon if file doesn't exist
            let trayIcon: ReturnType<typeof nativeImage.createEmpty>;

        try {
            trayIcon = nativeImage.createFromPath(iconPath);
            if (trayIcon.isEmpty()) {
                throw new Error('Icon not found');
            }
        } catch {
            // Create a fallback icon (blue circle)
            trayIcon = nativeImage.createEmpty();
        }

        tray = new Tray(trayIcon.isEmpty() ?
            nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAEwSURBVDiNpZM9TsNAEIW/WXuDFHdIKWhoKLgAHIAz0NJRcAI4AjU1DQ0VHSUFIqGgoKGh4QLZxPaOKYId/wTxSiON9r2Z2Z0dqCpVxVobicgukPe8NgKuVHW+OMxjDcALcCYiB8aYE+AcuO55fgm8qupC1TyKgALnqvpujLkFJsaYY+C857UN3Kvql4hwnpDngKq6NMZ8iMgNMI6z7AG3qvohIpwDAOCAL1W9B0bACbBT0k7VdRqGYb+m01YVqGoQBL8iZ8BO2TYAgKrSbrfp9XrEcRxorT8jIoJpmg5EZId/2C4AJ0myFgTBQlXnzjlE5BV4BqrH/m8ZwJq6Tj8Lw/DNOZcCWWPMIfD8v/4AINdaL601H865JM97AJ7+8j9VV8cH/zLGzAE78PkNOjKDLv7DbisAAAAASUVORK5CYII=')
            : trayIcon
        );

        tray.setToolTip('HyperOS - AI Desktop Agent');

        const contextMenu = Menu.buildFromTemplate([
            {
                label: 'Show/Hide (Ctrl+Space)',
                click: () => toggleWindow(),
            },
            {
                type: 'separator',
            },
            {
                label: 'About HyperOS',
                click: () => {
                    shell.openExternal('https://github.com/your-repo/hyperos');
                },
            },
            {
                type: 'separator',
            },
            {
                label: 'Quit HyperOS',
                click: () => {
                    (app as any).isQuitting = true;
                    app.quit();
                },
            },
        ]);

        tray.setContextMenu(contextMenu);

        // Double-click to toggle window
        tray.on('double-click', () => {
            toggleWindow();
        });

        console.log('System tray created');
    } catch (error) {
        console.error('Failed to create tray:', error);
    }
}

/**
 * Toggle main window visibility
 */
function toggleWindow(): void {
    if (!mainWindow) return;

    if (mainWindow.isVisible()) {
        mainWindow.hide();
        windowState.isVisible = false;
        console.log('Window hidden');
    } else {
        mainWindow.show();
        mainWindow.focus();
        windowState.isVisible = true;
        console.log('Window shown');
    }
}

/**
 * Register global keyboard shortcuts
 */
function registerShortcuts(): void {
    // Ctrl+Space to toggle window
    const shortcut = process.platform === 'darwin' ? 'Command+Space' : 'Control+Space';

    const registered = globalShortcut.register(shortcut, () => {
        toggleWindow();
    });

    if (registered) {
        console.log(`Global shortcut registered: ${shortcut}`);
    } else {
        console.error(`Failed to register global shortcut: ${shortcut}`);
    }
}

/**
 * Set up IPC handlers for renderer communication
 */
function setupIPC(): void {
    // Toggle click-through mode
    ipcMain.on('set-click-through', (event, enabled: boolean) => {
        const win = BrowserWindow.fromWebContents(event.sender);
        if (win) {
            win.setIgnoreMouseEvents(enabled, { forward: true });
            console.log(`Click-through: ${enabled ? 'enabled' : 'disabled'}`);
        }
    });

    // Get app version
    ipcMain.handle('get-app-version', () => {
        return app.getVersion();
    });

    // Get window visibility state
    ipcMain.handle('get-visibility', () => {
        return mainWindow?.isVisible() ?? false;
    });

    // Show window
    ipcMain.on('show-window', () => {
        if (mainWindow && !mainWindow.isVisible()) {
            mainWindow.show();
            mainWindow.focus();
        }
    });

    // Hide window
    ipcMain.on('hide-window', () => {
        if (mainWindow && mainWindow.isVisible()) {
            mainWindow.hide();
        }
    });

    // Quit app
    ipcMain.on('quit-app', () => {
        (app as any).isQuitting = true;
        app.quit();
    });

    console.log('IPC handlers registered');
}

/**
 * App lifecycle handlers
 */
app.whenReady().then(() => {
    initializeSecurity();
    createWindow();
    createTray();
    registerShortcuts();
    setupIPC();

    // macOS: Recreate window when dock icon is clicked
    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        } else if (mainWindow && !mainWindow.isVisible()) {
            mainWindow.show();
        }
    });
});

app.on('window-all-closed', () => {
    // On macOS, keep the app running in the tray
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('will-quit', () => {
    // Unregister all shortcuts
    globalShortcut.unregisterAll();
    console.log('Global shortcuts unregistered');
});

app.on('before-quit', () => {
    (app as any).isQuitting = true;
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
});

process.on('unhandledRejection', (reason) => {
    console.error('Unhandled rejection:', reason);
});
