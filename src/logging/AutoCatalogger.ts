/**
 * 🎩 Auto-Catalogger - "The Mad Hatter's Commit Chronicler"
 *
 * Automatically catalogs git commits, file changes, and development sessions
 * using the Recursive Dewey Decimal system with Naptime timestamps
 */

import { catalog, CatalogCategory } from './RecursiveCatalogSystem';
import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

export interface CommitInfo {
    hash: string;
    message: string;
    author: string;
    date: string;
    files: string[];
}

export interface SessionInfo {
    startTime: Date;
    endTime?: Date;
    sessionId: string;
    activities: string[];
    filesModified: string[];
}

export class AutoCatalogger {
    private currentSession: SessionInfo | null = null;
    private catalogFile: string;

    constructor(catalogPath: string = './RECURSIVE_CATALOG.md') {
        this.catalogFile = catalogPath;
        this.initializeCatalogger();
    }

    private initializeCatalogger() {
        console.log("🎩 Mad Hatter's Auto-Catalogger activated!");
        console.log("🕰️  All development activities will be catalogued...");
    }

    /**
     * Start a new development session - "Begin the Tea Party"
     */
    public startSession(sessionName: string): string {
        const sessionId = `${sessionName}-${Date.now()}`;
        this.currentSession = {
            startTime: new Date(),
            sessionId,
            activities: [],
            filesModified: []
        };

        const entry = catalog.createEntry(
            `Development Session: ${sessionName}`,
            `Active development session started. All commits and changes during this session will be nested under this entry.`,
            CatalogCategory.SESSION_LOG,
            ["session", "development", "active"],
            undefined,
            sessionId
        );

        console.log(`🫖 Tea Party started: ${sessionId}`);
        return entry.deweyCode;
    }

    /**
     * End current session - "Pack up the Tea Set"
     */
    public endSession(): void {
        if (!this.currentSession) return;

        this.currentSession.endTime = new Date();
        const duration = this.currentSession.endTime.getTime() - this.currentSession.startTime.getTime();
        const durationMinutes = Math.round(duration / (1000 * 60));

        const sessionSummary = `
Session Duration: ${durationMinutes} minutes
Activities: ${this.currentSession.activities.length}
Files Modified: ${this.currentSession.filesModified.length}
Files: ${this.currentSession.filesModified.join(', ')}
        `.trim();

        catalog.createEntry(
            `Session Summary: ${this.currentSession.sessionId}`,
            sessionSummary,
            CatalogCategory.SESSION_LOG,
            ["session-summary", "completed"],
            undefined,
            this.currentSession.sessionId
        );

        console.log(`🍃 Tea Party concluded: ${this.currentSession.sessionId} (${durationMinutes}m)`);
        this.currentSession = null;
    }

    /**
     * Catalog a git commit - "Chronicle the White Rabbit's Journey"
     */
    public catalogCommit(commitHash?: string): string {
        try {
            // Get latest commit if none specified
            const hash = commitHash || execSync('git rev-parse HEAD').toString().trim().substring(0, 8);
            const message = execSync(`git log -1 --pretty=format:"%s" ${hash}`).toString().trim();
            const author = execSync(`git log -1 --pretty=format:"%an" ${hash}`).toString().trim();
            const date = execSync(`git log -1 --pretty=format:"%ad" ${hash}`).toString().trim();
            const files = execSync(`git diff-tree --no-commit-id --name-only -r ${hash}`)
                .toString().trim().split('\n').filter(f => f);

            const commitInfo: CommitInfo = { hash, message, author, date, files };

            // Determine category based on files and commit message
            const category = this.categorizeCommit(commitInfo);

            // Create catalog entry
            const entry = catalog.createEntry(
                `Commit: ${message}`,
                this.formatCommitContent(commitInfo),
                category,
                this.extractTagsFromCommit(commitInfo),
                this.getSessionParentCode(),
                this.currentSession?.sessionId
            );

            // Track in current session
            if (this.currentSession) {
                this.currentSession.activities.push(`commit:${hash}`);
                this.currentSession.filesModified.push(...files);
            }

            console.log(`📝 Commit cataloged: ${hash} - ${message}`);
            return entry.deweyCode;

        } catch (error) {
            console.error("❌ Failed to catalog commit:", error);
            return '';
        }
    }

    /**
     * Catalog file changes - "Track the Cheshire Cat's Disappearing Acts"
     */
    public catalogFileChange(filePath: string, changeType: 'created' | 'modified' | 'deleted'): string {
        const fileName = path.basename(filePath);
        const category = this.categorizeFileChange(filePath, changeType);

        const content = `
File: ${filePath}
Change Type: ${changeType}
${changeType === 'deleted' ? 'Cheshire Status: vanished' : 'Cheshire Status: stable'}
        `.trim();

        const entry = catalog.createEntry(
            `${changeType.toUpperCase()}: ${fileName}`,
            content,
            category,
            [changeType, fileName.split('.').pop() || 'unknown', 'file-change'],
            this.getSessionParentCode(),
            this.currentSession?.sessionId
        );

        // Mark as Cheshire if deleted
        if (changeType === 'deleted') {
            catalog.markCheshire(entry.deweyCode, 'vanished');
        }

        return entry.deweyCode;
    }

    /**
     * Auto-catalog based on git status - "Survey Wonderland"
     */
    public autoCatalogChanges(): void {
        try {
            // Check for uncommitted changes
            const status = execSync('git status --porcelain').toString().trim();
            if (status) {
                const lines = status.split('\n');
                for (const line of lines) {
                    const [statusCode, filePath] = [line.substring(0, 2), line.substring(3)];

                    if (statusCode.includes('A')) {
                        this.catalogFileChange(filePath, 'created');
                    } else if (statusCode.includes('M')) {
                        this.catalogFileChange(filePath, 'modified');
                    } else if (statusCode.includes('D')) {
                        this.catalogFileChange(filePath, 'deleted');
                    }
                }
            }

            // Catalog recent commits
            const recentCommits = execSync('git log --oneline -5').toString().trim().split('\n');
            for (const commitLine of recentCommits) {
                const [hash] = commitLine.split(' ');
                // Only catalog if not already cataloged (you might want to track this)
                // this.catalogCommit(hash);
            }

        } catch (error) {
            console.error("❌ Auto-catalog failed:", error);
        }
    }

    /**
     * Export catalog with Alice-themed formatting
     */
    public exportCatalog(): void {
        const catalogContent = catalog.exportCatalog();

        const aliceHeader = `# 🐰 Down the Rabbit Hole - Development Chronicles

*"We're all mad here. I'm mad. You're mad."* - The Cheshire Cat

Welcome to Wonderland, where development logs grow fractally and time flows in Naptime...

${catalogContent}

---

*"Begin at the beginning," the King said gravely, "and go on till you come to the end: then stop."*
`;

        fs.writeFileSync(this.catalogFile, aliceHeader);
        console.log(`📖 Catalog exported to ${this.catalogFile}`);
    }

    /**
     * Search and commit recommendations - "Ask the Caterpillar"
     */
    public suggestCommitMessage(stagedFiles: string[]): string {
        const categories = stagedFiles.map(file => this.categorizeFileByPath(file));
        const mainCategory = this.getMostCommonCategory(categories);

        const suggestions = {
            [CatalogCategory.INTERFACE]: "✨ enhance UI",
            [CatalogCategory.MATHEMATICS]: "🔬 refine algorithms",
            [CatalogCategory.IMPLEMENTATION]: "🔧 implement feature",
            [CatalogCategory.DOCUMENTATION]: "📝 update docs",
            [CatalogCategory.TESTING]: "🧪 add tests",
            [CatalogCategory.OPTIMIZATION]: "⚡ optimize performance"
        };

        return suggestions[mainCategory] || "🎭 make changes";
    }

    // Private helper methods
    private categorizeCommit(commit: CommitInfo): CatalogCategory {
        const message = commit.message.toLowerCase();
        const files = commit.files;

        // Analyze commit message keywords
        if (message.includes('doc') || message.includes('readme')) return CatalogCategory.DOCUMENTATION;
        if (message.includes('test') || message.includes('spec')) return CatalogCategory.TESTING;
        if (message.includes('fix') || message.includes('bug')) return CatalogCategory.DEBUGGING;
        if (message.includes('ui') || message.includes('interface')) return CatalogCategory.INTERFACE;
        if (message.includes('math') || message.includes('algorithm')) return CatalogCategory.MATHEMATICS;
        if (message.includes('perf') || message.includes('optimize')) return CatalogCategory.OPTIMIZATION;

        // Analyze file types
        if (files.some(f => f.includes('.md'))) return CatalogCategory.DOCUMENTATION;
        if (files.some(f => f.includes('.test.') || f.includes('.spec.'))) return CatalogCategory.TESTING;
        if (files.some(f => f.includes('UI') || f.includes('interface'))) return CatalogCategory.INTERFACE;

        return CatalogCategory.IMPLEMENTATION;
    }

    private categorizeFileChange(filePath: string, changeType: string): CatalogCategory {
        return this.categorizeFileByPath(filePath);
    }

    private categorizeFileByPath(filePath: string): CatalogCategory {
        if (filePath.includes('.md')) return CatalogCategory.DOCUMENTATION;
        if (filePath.includes('.test.') || filePath.includes('.spec.')) return CatalogCategory.TESTING;
        if (filePath.includes('UI') || filePath.includes('interface')) return CatalogCategory.INTERFACE;
        if (filePath.includes('math') || filePath.includes('algorithm')) return CatalogCategory.MATHEMATICS;
        if (filePath.includes('.ts') || filePath.includes('.js')) return CatalogCategory.TYPESCRIPT;
        if (filePath.includes('.glsl') || filePath.includes('shader')) return CatalogCategory.SHADERS;
        return CatalogCategory.IMPLEMENTATION;
    }

    private formatCommitContent(commit: CommitInfo): string {
        return `
Commit Hash: ${commit.hash}
Author: ${commit.author}
Date: ${commit.date}
Files Changed: ${commit.files.length}

Files:
${commit.files.map(f => `  - ${f}`).join('\n')}
        `.trim();
    }

    private extractTagsFromCommit(commit: CommitInfo): string[] {
        const tags = ['git-commit'];

        // Add file extension tags
        const extensions = commit.files
            .map(f => path.extname(f).substring(1))
            .filter(ext => ext);
        tags.push(...extensions);

        // Add keyword tags from commit message
        const message = commit.message.toLowerCase();
        if (message.includes('feat')) tags.push('feature');
        if (message.includes('fix')) tags.push('bugfix');
        if (message.includes('refactor')) tags.push('refactoring');
        if (message.includes('style')) tags.push('styling');

        return [...new Set(tags)]; // Remove duplicates
    }

    private getSessionParentCode(): string | undefined {
        // If there's an active session, find its catalog entry
        if (this.currentSession) {
            // Search for session entry (in a real implementation, you'd track this)
            const sessionEntries = catalog.search(this.currentSession.sessionId);
            return sessionEntries[0]?.deweyCode;
        }
        return undefined;
    }

    private getMostCommonCategory(categories: CatalogCategory[]): CatalogCategory {
        const counts = categories.reduce((acc, cat) => {
            acc[cat] = (acc[cat] || 0) + 1;
            return acc;
        }, {} as Record<CatalogCategory, number>);

        return Object.entries(counts)
            .sort(([,a], [,b]) => b - a)[0]?.[0] as CatalogCategory || CatalogCategory.IMPLEMENTATION;
    }
}

// Singleton instance
export const autoCatalogger = new AutoCatalogger();