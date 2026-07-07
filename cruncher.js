const fs = require('fs');
const path = require('path');

const dataFilePath = path.join(__dirname, 'data.js');

if (!fs.existsSync(dataFilePath)) {
    console.error("Could not find data.js in this folder.");
    process.exit(1);
}

console.log("Reading data.js file script content...");
let fileContent = fs.readFileSync(dataFilePath, 'utf8');

// Identify the variable name used in your file
let arrayVarName = 'relayResults'; 
if (fileContent.includes('const relayResults')) arrayVarName = 'relayResults';
else if (fileContent.includes('var relayResults')) arrayVarName = 'relayResults';
else if (fileContent.includes('const results')) arrayVarName = 'results';
else {
    // Fallback search: look for whatever is before the main opening bracket
    const match = fileContent.match(/(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*\[/);
    if (match && match[1]) {
        arrayVarName = match[1];
    }
}

console.log(`Detected array variable name: "${arrayVarName}"`);

// Safely append a CommonJS export to the script string in-memory and evaluate it
fileContent += `\nmodule.exports = { dataTarget: ${arrayVarName} };`;

// Write to a temporary file to require it safely
const tempFilePath = path.join(__dirname, '_temp_data_load.js');
fs.writeFileSync(tempFilePath, fileContent, 'utf8');

const { dataTarget } = require(tempFilePath);
const data = dataTarget;

// Clean up the temporary file immediately
if (fs.existsSync(tempFilePath)) fs.unlinkSync(tempFilePath);

if (!data || !Array.isArray(data)) {
    console.error(`Failed to extract array from variable "${arrayVarName}".`);
    process.exit(1);
}

console.log(`Successfully loaded ${data.length} records from data.js. Crunching metrics...`);

// Analytical data structures
const clubStats = {};
const stageAnalysis = {};
const yearSummary = {};

data.forEach(row => {
    if (!row || !row.year || !row.stage || !row.position) return;
    
    const year = row.year;
    const stage = row.stage;
    const pos = parseInt(row.position, 10);
    
    // Quick normalize function inline to clean team suffixes out
    let club = row.club ? row.club.toString().trim() : 'Independent';
    club = club.replace(/\s*[\(\s]([A-D]|\d+)\s*$/, '').trim();
    club = club.replace(/\s*(?:Running Club|RC|Harriers|Roadents|Runners)$/i, '').trim();

    if (pos === 1) {
        if (!clubStats[club]) clubStats[club] = { totalStageWins: 0, winsByYear: {} };
        clubStats[club].totalStageWins++;
        clubStats[club].winsByYear[year] = (clubStats[club].winsByYear[year] || 0) + 1;

        if (!stageAnalysis[stage]) stageAnalysis[stage] = { stageNum: stage, winners: [] };
        stageAnalysis[stage].winners.push({ year, club });
    }

    if (!yearSummary[year]) yearSummary[year] = { year, totalRows: 0, winningClubs: new Set() };
    yearSummary[year].totalRows++;
    if (pos === 1) yearSummary[year].winningClubs.add(club);
});

Object.keys(yearSummary).forEach(y => {
    yearSummary[y].uniqueStageWinnersCount = yearSummary[y].winningClubs.size;
    delete yearSummary[y].winningClubs;
});

const reportSummary = {
    meta: { totalRecordsProcessed: data.length, extractedAt: new Date().toISOString() },
    clubLeaderboard: Object.entries(clubStats)
        .map(([name, stats]) => ({ name, totalWins: stats.totalStageWins, eraProfile: stats.winsByYear }))
        .sort((a, b) => b.totalWins - a.totalWins),
    yearByYearSpread: Object.values(yearSummary).sort((a,b) => b.year - a.year),
    stageProfiles: Object.values(stageAnalysis)
};

fs.writeFileSync(
    path.join(__dirname, 'racked_summary.json'), 
    JSON.stringify(reportSummary, null, 2)
);

console.log("Success! Open 'racked_summary.json' to view your condensed data packet.");