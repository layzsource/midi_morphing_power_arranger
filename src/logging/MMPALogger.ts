/**
 * MMPA Logger - Biomimicry Protocol Compliant
 *
 * Implements naptime/dreamstate/recall logging format for session continuity
 * and total recall capabilities across different Claude instances.
 */

export type DreamState = 'baseline' | 'iteration' | 'release';

export interface LogEntry {
    naptime: string;          // ISO timestamp + description
    dreamstate: string;       // state + status description
    recall: string[];         // keywords for searching
    message?: string;         // optional detailed message
    level: 'info' | 'warn' | 'error' | 'debug' | 'success';
}

export class MMPALogger {
    private logs: LogEntry[] = [];
    private currentSession: string = '';
    private currentDreamState: DreamState = 'baseline';

    constructor() {
        this.initializeSession();
    }

    private initializeSession() {
        const now = new Date().toISOString();
        this.currentSession = `MMPA session ${now.split('T')[0]}`;

        this.log('info', 'MMPA Logger initialized', {
            dreamstate: 'baseline',
            description: 'logging system startup',
            recall: ['logger', 'initialization', 'startup', 'biomimicry_protocol']
        });
    }

    /**
     * Main logging method with biomimicry protocol format
     */
    public log(
        level: LogEntry['level'],
        message: string,
        options: {
            dreamstate?: DreamState;
            description?: string;
            recall: string[];
        }
    ) {
        const now = new Date();
        const timestamp = now.toISOString();

        // Update current dream state if provided
        if (options.dreamstate) {
            this.currentDreamState = options.dreamstate;
        }

        const entry: LogEntry = {
            naptime: `${timestamp} - ${options.description || message}`,
            dreamstate: `${this.currentDreamState} - ${this.getStateDescription()}`,
            recall: options.recall,
            message,
            level
        };

        this.logs.push(entry);
        this.outputToConsole(entry);

        // Also maintain logs directory requirement from protocol
        this.writeToLogFile(entry);
    }

    /**
     * Specialized logging methods for common MMPA operations
     */
    public logMIDI(ccNumber: number, value: number, viewport: string) {
        this.log('info', `MIDI CC${ccNumber}: ${value}`, {
            description: `MIDI control input to ${viewport}`,
            recall: ['MIDI', `CC${ccNumber}`, viewport, 'control_input', 'realtime']
        });
    }

    public logMorph(amount: number, target: string) {
        this.log('info', `Morph to ${target}: ${Math.round(amount * 100)}%`, {
            description: `cube morphing operation`,
            recall: ['morph', target, 'PERIAKTOS', 'transformation', 'cube_sphere']
        });
    }

    public logPanelToggle(panelName: string, visible: boolean) {
        this.log('info', `${panelName}: ${visible ? 'shown' : 'hidden'}`, {
            description: `UI panel visibility change`,
            recall: ['panel', 'UI', panelName, visible ? 'show' : 'hide', 'toolbar']
        });
    }

    public logSystemEvent(event: string, details: string, state: DreamState = 'iteration') {
        this.log('info', event, {
            dreamstate: state,
            description: details,
            recall: ['system', event, 'engine_event', details.replace(/\s+/g, '_').toLowerCase()]
        });
    }

    public logError(error: string, context: string) {
        this.log('error', error, {
            dreamstate: 'iteration',
            description: `error in ${context}`,
            recall: ['error', context, 'bug', 'debugging', 'troubleshoot']
        });
    }

    public logSuccess(achievement: string, context: string) {
        this.log('success', achievement, {
            dreamstate: 'iteration',
            description: `completed ${context}`,
            recall: ['success', context, 'completed', 'achievement', 'milestone']
        });
    }

    /**
     * Session management
     */
    public startIteration(description: string) {
        this.currentDreamState = 'iteration';
        this.log('info', `Starting iteration: ${description}`, {
            dreamstate: 'iteration',
            description: `begin work on ${description}`,
            recall: ['iteration_start', description.replace(/\s+/g, '_'), 'work_begin']
        });
    }

    public completeIteration(description: string) {
        this.log('success', `Completed iteration: ${description}`, {
            dreamstate: 'release',
            description: `finished work on ${description}`,
            recall: ['iteration_complete', description.replace(/\s+/g, '_'), 'work_complete', 'release']
        });
        this.currentDreamState = 'baseline';
    }

    /**
     * Export logs for session continuity
     */
    public generateSessionLog(): string {
        const header = `# MMPA Session Log\n**Generated:** ${new Date().toISOString()}\n**Session:** ${this.currentSession}\n\n---\n\n`;

        const logEntries = this.logs.map(entry => {
            return `## ${this.getLevelEmoji(entry.level)} ${entry.message}\n\n` +
                   `**naptime:** ${entry.naptime}\n` +
                   `**dreamstate:** ${entry.dreamstate}\n` +
                   `**recall:** ${entry.recall.join(', ')}\n\n`;
        }).join('\n');

        return header + logEntries;
    }

    /**
     * Search logs by recall keywords
     */
    public searchLogs(keywords: string[]): LogEntry[] {
        return this.logs.filter(entry =>
            keywords.some(keyword =>
                entry.recall.some(recallItem =>
                    recallItem.toLowerCase().includes(keyword.toLowerCase())
                )
            )
        );
    }

    private getStateDescription(): string {
        switch (this.currentDreamState) {
            case 'baseline': return 'system ready, monitoring';
            case 'iteration': return 'active development, making changes';
            case 'release': return 'completion, stable state achieved';
            default: return 'unknown state';
        }
    }

    private getLevelEmoji(level: LogEntry['level']): string {
        switch (level) {
            case 'info': return '📝';
            case 'warn': return '⚠️';
            case 'error': return '❌';
            case 'debug': return '🔍';
            case 'success': return '✅';
            default: return '📋';
        }
    }

    private outputToConsole(entry: LogEntry) {
        const emoji = this.getLevelEmoji(entry.level);
        const style = this.getConsoleStyle(entry.level);

        console.group(`%c${emoji} ${entry.message}`, style);
        console.log(`🕐 naptime: ${entry.naptime}`);
        console.log(`🌙 dreamstate: ${entry.dreamstate}`);
        console.log(`🧠 recall: ${entry.recall.join(', ')}`);
        console.groupEnd();
    }

    private getConsoleStyle(level: LogEntry['level']): string {
        switch (level) {
            case 'info': return 'color: #00ffff; font-weight: bold;';
            case 'warn': return 'color: #ffff00; font-weight: bold;';
            case 'error': return 'color: #ff0000; font-weight: bold;';
            case 'debug': return 'color: #888888; font-weight: normal;';
            case 'success': return 'color: #00ff00; font-weight: bold;';
            default: return 'color: #ffffff; font-weight: normal;';
        }
    }

    private writeToLogFile(entry: LogEntry) {
        // Create log entry for potential file writing
        // In browser environment, we'll store in localStorage for persistence
        try {
            const existingLogs = localStorage.getItem('mmpa_session_logs') || '[]';
            const logs = JSON.parse(existingLogs);
            logs.push(entry);

            // Keep only last 1000 entries to prevent storage bloat
            if (logs.length > 1000) {
                logs.splice(0, logs.length - 1000);
            }

            localStorage.setItem('mmpa_session_logs', JSON.stringify(logs));
        } catch (error) {
            console.warn('Could not persist log to localStorage:', error);
        }
    }

    /**
     * Load previous session logs from localStorage
     */
    public loadPersistedLogs(): LogEntry[] {
        try {
            const existingLogs = localStorage.getItem('mmpa_session_logs') || '[]';
            return JSON.parse(existingLogs);
        } catch (error) {
            console.warn('Could not load persisted logs:', error);
            return [];
        }
    }

    /**
     * Export logs as downloadable file
     */
    public downloadSessionLog() {
        const logContent = this.generateSessionLog();
        const blob = new Blob([logContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `MMPA_Session_Log_${new Date().toISOString().split('T')[0]}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Global instance for use throughout the application
export const mmpaLogger = new MMPALogger();