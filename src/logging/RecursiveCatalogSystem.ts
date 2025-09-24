/**
 * 🐰 Recursive Dewey Decimal Cataloging System
 *
 * "Down the Rabbit Hole" - A fractal approach to organizing development logs
 * Using Naptime temporal system and recursive classification
 *
 * Alice Literary References:
 * - Rabbit Hole = deeper recursion levels
 * - Tea Party = collaborative sessions
 * - Looking Glass = reflection/analysis phases
 * - Cheshire = disappearing/appearing features
 * - Mad Hatter = experimental/chaotic development
 */

export interface NaptimeStamp {
    naptime: string;        // "Naptime 2025.267.15:45"
    dreamState: string;     // "Deep REM", "Light Doze", "Lucid", "Awakening"
    rabbitHoleDepth: number; // Recursion level (0 = surface, deeper = more nested)
    teaPartySession?: string; // Collaborative session ID
}

export interface CatalogEntry {
    deweyCode: string;      // Recursive: 100.110.115.120...
    naptime: NaptimeStamp;
    title: string;
    category: CatalogCategory;
    content: string;
    tags: string[];
    lookingGlassRefs: string[]; // References to related entries
    rabbitHoleParent?: string;  // Parent entry if this is nested
    cheshireStatus: 'appearing' | 'stable' | 'fading' | 'vanished';
}

export enum CatalogCategory {
    // 100 Series - Philosophy & Conceptual
    VISION = "100",           // Overall vision and philosophy
    ARCHITECTURE = "110",     // System architecture
    PRINCIPLES = "120",       // Design principles (Rams, IxDF)
    MYTHOLOGY = "130",        // Låy-Z lore and archetypes

    // 200 Series - Mathematics & Algorithms
    MATHEMATICS = "200",      // Core mathematical concepts
    IFS = "210",             // Iterated Function Systems
    SUBDIVISION = "220",      // Subdivision surfaces
    GEOMETRY = "230",         // Sacred geometry, spirals

    // 300 Series - Interface & Interaction
    INTERFACE = "300",        // UI/UX design
    GESTURES = "310",        // Gesture recognition and mapping
    THEREMIN = "320",        // Antenna theremin navigation
    HAPTICS = "330",         // Tactile feedback systems

    // 400 Series - Implementation & Code
    IMPLEMENTATION = "400",   // Technical implementation
    TYPESCRIPT = "410",      // TypeScript/JavaScript code
    SHADERS = "420",         // GPU shaders and materials
    OPTIMIZATION = "430",     // Performance optimization

    // 500 Series - Integration & Systems
    INTEGRATION = "500",     // System integration
    API = "510",             // API design and endpoints
    DATA = "520",            // Data structures and formats
    WORKFLOW = "530",        // Development workflow

    // 600 Series - Testing & Quality
    TESTING = "600",         // Testing and validation
    DEBUGGING = "610",       // Bug fixes and debugging
    ANALYSIS = "620",        // Performance analysis
    REVIEW = "630",          // Code and design review

    // 700 Series - Documentation & Communication
    DOCUMENTATION = "700",   // Documentation and specs
    ANALYSIS_LOG = "710",    // Analysis and planning logs
    SESSION_LOG = "720",     // Development session logs
    COMMUNICATION = "730",   // Team communication logs

    // 800 Series - Creative & Artistic
    CREATIVE = "800",        // Creative exploration
    VISUALS = "810",         // Visual design and aesthetics
    AUDIO = "820",          // Audio design and synthesis
    NARRATIVE = "830",       // Storytelling and narrative

    // 900 Series - Meta & Reflection
    META = "900",           // Meta-development and process
    REFLECTION = "910",     // Reflection and retrospective
    EVOLUTION = "920",      // System evolution tracking
    EMERGENCE = "930"       // Emergent behavior documentation
}

export class RecursiveCatalogSystem {
    private entries: Map<string, CatalogEntry> = new Map();
    private hierarchyMap: Map<string, string[]> = new Map(); // parent -> children

    constructor() {
        this.initializeSystem();
    }

    /**
     * Generate Naptime timestamp
     */
    private generateNaptime(): NaptimeStamp {
        const now = new Date();
        const year = now.getFullYear();
        const dayOfYear = Math.floor((now.getTime() - new Date(year, 0, 0).getTime()) / (1000 * 60 * 60 * 24));
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');

        const dreamStates = ["Light Doze", "Deep REM", "Lucid", "Awakening", "Tea Party", "Looking Glass"];
        const dreamState = dreamStates[Math.floor(Math.random() * dreamStates.length)];

        return {
            naptime: `Naptime ${year}.${dayOfYear.toString().padStart(3, '0')}.${hours}:${minutes}`,
            dreamState,
            rabbitHoleDepth: 0 // Will be set based on hierarchy
        };
    }

    /**
     * Generate recursive Dewey code
     * Each level adds 3 digits: 100 -> 100.110 -> 100.110.115
     */
    private generateDeweyCode(category: CatalogCategory, parentCode?: string): string {
        if (!parentCode) {
            return category;
        }

        // Count existing children to get next sequence number
        const siblings = this.hierarchyMap.get(parentCode) || [];
        const nextNumber = siblings.length + 1;
        const lastSegment = parseInt(category) + (nextNumber * 5); // Space out by 5s

        return `${parentCode}.${lastSegment.toString().padStart(3, '0')}`;
    }

    /**
     * Calculate rabbit hole depth based on Dewey code nesting
     */
    private calculateRabbitHoleDepth(deweyCode: string): number {
        return deweyCode.split('.').length - 1;
    }

    /**
     * Create new catalog entry - "Down the Rabbit Hole"
     */
    public createEntry(
        title: string,
        content: string,
        category: CatalogCategory,
        tags: string[] = [],
        parentCode?: string,
        teaPartySession?: string
    ): CatalogEntry {
        const deweyCode = this.generateDeweyCode(category, parentCode);
        const naptime = this.generateNaptime();
        naptime.rabbitHoleDepth = this.calculateRabbitHoleDepth(deweyCode);
        naptime.teaPartySession = teaPartySession;

        const entry: CatalogEntry = {
            deweyCode,
            naptime,
            title,
            category,
            content,
            tags,
            lookingGlassRefs: [],
            rabbitHoleParent: parentCode,
            cheshireStatus: 'appearing'
        };

        this.entries.set(deweyCode, entry);

        // Update hierarchy
        if (parentCode) {
            if (!this.hierarchyMap.has(parentCode)) {
                this.hierarchyMap.set(parentCode, []);
            }
            this.hierarchyMap.get(parentCode)!.push(deweyCode);
        }

        console.log(`📝 ${naptime.naptime} | ${naptime.dreamState} | Rabbit Hole Depth: ${naptime.rabbitHoleDepth}`);
        console.log(`🏷️  Dewey: ${deweyCode} | ${title}`);

        return entry;
    }

    /**
     * Search entries - "Through the Looking Glass"
     */
    public search(query: string, options: {
        categories?: CatalogCategory[];
        maxDepth?: number;
        dreamStates?: string[];
        cheshireStatus?: string[];
    } = {}): CatalogEntry[] {
        const results: CatalogEntry[] = [];

        for (const entry of this.entries.values()) {
            // Filter by options
            if (options.categories && !options.categories.includes(entry.category)) continue;
            if (options.maxDepth && entry.naptime.rabbitHoleDepth > options.maxDepth) continue;
            if (options.dreamStates && !options.dreamStates.includes(entry.naptime.dreamState)) continue;
            if (options.cheshireStatus && !options.cheshireStatus.includes(entry.cheshireStatus)) continue;

            // Search in title, content, and tags
            const searchText = `${entry.title} ${entry.content} ${entry.tags.join(' ')}`.toLowerCase();
            if (searchText.includes(query.toLowerCase())) {
                results.push(entry);
            }
        }

        return results.sort((a, b) => a.deweyCode.localeCompare(b.deweyCode));
    }

    /**
     * Get entry lineage - "Follow the White Rabbit"
     */
    public getLineage(deweyCode: string): CatalogEntry[] {
        const lineage: CatalogEntry[] = [];
        let currentCode = deweyCode;

        while (currentCode) {
            const entry = this.entries.get(currentCode);
            if (entry) {
                lineage.unshift(entry);
                currentCode = entry.rabbitHoleParent || '';
            } else {
                break;
            }
        }

        return lineage;
    }

    /**
     * Get children entries - "Mad Hatter's Tea Party"
     */
    public getChildren(deweyCode: string): CatalogEntry[] {
        const childCodes = this.hierarchyMap.get(deweyCode) || [];
        return childCodes
            .map(code => this.entries.get(code))
            .filter(entry => entry !== undefined) as CatalogEntry[];
    }

    /**
     * Create looking glass reference between entries
     */
    public createLookingGlassRef(fromCode: string, toCode: string): void {
        const fromEntry = this.entries.get(fromCode);
        const toEntry = this.entries.get(toCode);

        if (fromEntry && toEntry) {
            fromEntry.lookingGlassRefs.push(toCode);
            console.log(`🪞 Looking Glass: ${fromCode} ←→ ${toCode}`);
        }
    }

    /**
     * Mark entry as Cheshire (fading/vanishing for deprecated features)
     */
    public markCheshire(deweyCode: string, status: 'fading' | 'vanished'): void {
        const entry = this.entries.get(deweyCode);
        if (entry) {
            entry.cheshireStatus = status;
            console.log(`😸 Cheshire ${status}: ${deweyCode} - ${entry.title}`);
        }
    }

    /**
     * Export catalog as formatted markdown
     */
    public exportCatalog(): string {
        let output = "# 🐰 Recursive Development Catalog\n\n";
        output += `*Generated at ${this.generateNaptime().naptime}*\n\n`;

        // Group by top-level categories
        const topLevel = Array.from(this.entries.values())
            .filter(entry => !entry.rabbitHoleParent)
            .sort((a, b) => a.deweyCode.localeCompare(b.deweyCode));

        for (const entry of topLevel) {
            output += this.formatEntryWithChildren(entry, 0);
        }

        return output;
    }

    private formatEntryWithChildren(entry: CatalogEntry, indent: number): string {
        const prefix = "  ".repeat(indent);
        let output = `${prefix}## ${entry.deweyCode} - ${entry.title}\n`;
        output += `${prefix}**${entry.naptime.naptime}** | *${entry.naptime.dreamState}* | Depth: ${entry.naptime.rabbitHoleDepth}\n\n`;
        output += `${prefix}${entry.content}\n\n`;

        if (entry.tags.length > 0) {
            output += `${prefix}*Tags: ${entry.tags.join(', ')}*\n\n`;
        }

        if (entry.lookingGlassRefs.length > 0) {
            output += `${prefix}*Looking Glass: ${entry.lookingGlassRefs.join(', ')}*\n\n`;
        }

        // Add children recursively
        const children = this.getChildren(entry.deweyCode);
        for (const child of children) {
            output += this.formatEntryWithChildren(child, indent + 1);
        }

        return output;
    }

    private initializeSystem(): void {
        console.log("🍄 Initializing Recursive Catalog System");
        console.log("🐰 Welcome to the Rabbit Hole - where logs grow fractally");
        console.log("🫖 Tea Party sessions for collaboration");
        console.log("🪞 Looking Glass references for connections");
        console.log("😸 Cheshire status for feature lifecycle");
    }
}

// Singleton instance
export const catalog = new RecursiveCatalogSystem();