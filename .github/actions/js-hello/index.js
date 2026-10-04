// Inputs arrive as INPUT_<NAME> environment variables; outputs go to the $GITHUB_OUTPUT file.
const fs = require("fs");
const who = process.env.INPUT_WHO || "world";
const greeting = `Hello, ${who}, from Node ${process.version}`;
console.log(greeting);
fs.appendFileSync(process.env.GITHUB_OUTPUT, `greeting=${greeting}\n`);
