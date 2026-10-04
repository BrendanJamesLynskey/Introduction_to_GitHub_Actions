// The JavaScript port of stats.mean, read from stdin as a JSON list.
let s = "";
process.stdin.on("data", (d) => (s += d));
process.stdin.on("end", () => {
  const xs = JSON.parse(s);
  console.log(JSON.stringify(xs.reduce((a, b) => a + b, 0) / xs.length));
});
