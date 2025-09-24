/**
 * 🐰 Example Usage of Recursive Catalog System
 *
 * Shows how to catalog the MMPA development journey
 */

import { catalog, CatalogCategory } from './RecursiveCatalogSystem';

// Example: Cataloging today's MMPA analysis session
export function catalogMMPASession() {
    console.log("🫖 Starting Tea Party Session: MMPA-2025-267");

    // Main analysis entry
    const mainAnalysis = catalog.createEntry(
        "MMPA Universal Signal to Form Engine - Complete Analysis",
        `Synthesis of mathematical rigor (IFS, toroidal flow, subdivision surfaces),
         archetypal storytelling (Låy-Z lore), and embodied interface design (theremin navigation).
         Rams principles + IxDF ergonomics create the "centaur breath" of grounded emergence.`,
        CatalogCategory.ANALYSIS_LOG,
        ["MMPA", "analysis", "synthesis", "complete-vision"],
        undefined,
        "MMPA-2025-267"
    );

    // Nested design philosophy entry
    const designPhilosophy = catalog.createEntry(
        "Ergonomic Design Principles Integration",
        `Mapping Dieter Rams' Ten Principles to IxDF ergonomics for recursive AI worlds.
         Key insight: "Unobtrusive" + "Recognition over Recall" = consistent portal metaphors
         across all recursion levels. Creates intuitive navigation in infinite spaces.`,
        CatalogCategory.PRINCIPLES,
        ["Rams", "IxDF", "ergonomics", "design-philosophy"],
        mainAnalysis.deweyCode,
        "MMPA-2025-267"
    );

    // Nested mathematical foundation
    const mathFoundation = catalog.createEntry(
        "IFS + Toroidal Flow Implementation Strategy",
        `Iterated Function Systems where player actions become transformation functions.
         Toroidal flow ensures nested environment experiences flow back to transform
         parent environments. Creates "centaur breath" - cyclical causality.`,
        CatalogCategory.IFS,
        ["IFS", "toroidal-flow", "recursion", "emergence"],
        mainAnalysis.deweyCode,
        "MMPA-2025-267"
    );

    // Nested interface design
    const thereminNav = catalog.createEntry(
        "Antenna Theremin Navigation System",
        `Evolved antenna combining theremin field with gesture recognition.
         Phase 1: Webcam + theremin simulation
         Phase 2: IMU sensor fusion
         Phase 3: Physical theremin hardware integration`,
        CatalogCategory.THEREMIN,
        ["theremin", "navigation", "embodied-interface", "gesture"],
        mainAnalysis.deweyCode,
        "MMPA-2025-267"
    );

    // Deep dive into Låy-Z integration
    const layzIntegration = catalog.createEntry(
        "HAL Orb as Theremin Field Manifestation",
        `HAL morphing orb becomes visual representation of invisible theremin field.
         Orb glow intensity = hand proximity. Morph state = navigation mode.
         Bridges mathematical precision with archetypal intuition.`,
        CatalogCategory.MYTHOLOGY,
        ["HAL", "orb", "visual-feedback", "archetypal"],
        thereminNav.deweyCode,
        "MMPA-2025-267"
    );

    // Implementation priorities
    const implementation = catalog.createEntry(
        "Phase 1 Implementation: HAL Orb Integration",
        `Immediate next steps:
         1. Add HAL orb to MainDisplayPanel with proximity response
         2. Create basic thinker kitchen data structure
         3. Implement simple cube-to-sphere morph demonstration
         4. Map gestures to IFS functions`,
        CatalogCategory.IMPLEMENTATION,
        ["implementation", "phase-1", "HAL-orb", "priorities"],
        mainAnalysis.deweyCode,
        "MMPA-2025-267"
    );

    // Create looking glass references
    catalog.createLookingGlassRef(designPhilosophy.deweyCode, mathFoundation.deweyCode);
    catalog.createLookingGlassRef(thereminNav.deweyCode, layzIntegration.deweyCode);
    catalog.createLookingGlassRef(mathFoundation.deweyCode, implementation.deweyCode);

    console.log("🎩 Mad Hatter says: 'The catalog grows curiouser and curiouser!'");
    return mainAnalysis.deweyCode;
}

// Example: Searching the catalog
export function demonstrateSearch() {
    console.log("\n🔍 Searching through the Looking Glass...");

    // Search for MMPA-related entries
    const mmpaEntries = catalog.search("MMPA", {
        categories: [CatalogCategory.ANALYSIS_LOG, CatalogCategory.IMPLEMENTATION],
        maxDepth: 2
    });

    console.log(`Found ${mmpaEntries.length} MMPA entries:`);
    mmpaEntries.forEach(entry => {
        console.log(`  ${entry.deweyCode} - ${entry.title}`);
        console.log(`    ${entry.naptime.naptime} | ${entry.naptime.dreamState}`);
    });

    // Search for theremin entries
    const thereminEntries = catalog.search("theremin");
    console.log(`\nFound ${thereminEntries.length} theremin entries:`);
    thereminEntries.forEach(entry => {
        console.log(`  ${entry.deweyCode} - ${entry.title}`);
    });
}

// Example: Export full catalog
export function exportCatalogExample() {
    console.log("\n📖 Exporting complete catalog...");
    const catalogMarkdown = catalog.exportCatalog();

    // In a real implementation, you'd write this to a file
    console.log("Catalog exported to markdown format");
    console.log("Sample excerpt:");
    console.log(catalogMarkdown.substring(0, 500) + "...");
}

// Run the examples
if (require.main === module) {
    console.log("🐰 Welcome to Wonderland - Recursive Catalog Demo");
    console.log("=" .repeat(50));

    const mainEntryCode = catalogMMPASession();
    console.log(`\n📝 Created main entry: ${mainEntryCode}`);

    demonstrateSearch();
    exportCatalogExample();

    console.log("\n🃏 The Queen of Hearts commands: 'Catalog all the things!'");
}