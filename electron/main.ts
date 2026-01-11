import { app, BrowserWindow, screen, globalShortcut, ipcMain } from 'electron'
import path from 'node:path'

let win: BrowserWindow | null

process.env.DIST = path.join(__dirname, '../dist')
process.env.VITE_PUBLIC = app.isPackaged ? process.env.DIST : path.join(__dirname, '../public')

const VITE_DEV_SERVER_URL = process.env['VITE_DEV_SERVER_URL']

function createWindow() {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize

    win = new BrowserWindow({
        width,
        height,
        frame: false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: true,
        },
    })

    // Enable click-through by default for the whole window
    // We will toggle this in the renderer based on whether we are over the chat box
    win.setIgnoreMouseEvents(true, { forward: true })

    if (VITE_DEV_SERVER_URL) {
        win.loadURL(VITE_DEV_SERVER_URL)
    } else {
        win.loadFile(path.join(process.env.DIST ?? '', 'index.html'))
    }

    win.on('closed', () => {
        win = null
    })
}

ipcMain.on('set-ignore-mouse-events', (event, ignore, options) => {
    const webContents = event.sender
    const win = BrowserWindow.fromWebContents(webContents)
    win?.setIgnoreMouseEvents(ignore, options)
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

app.whenReady().then(() => {
    createWindow()

    // Global Hotkey: Ctrl+Space to toggle window visibility or focus
    globalShortcut.register('CommandOrControl+Space', () => {
        if (win) {
            if (win.isVisible()) {
                win.hide()
            } else {
                win.show()
                win.focus()
            }
        }
    })
})
