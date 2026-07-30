import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const context = vm.createContext({ window: {} });
for (const filename of [
  "portfolio-data.js",
  "idea-explanations.js",
  "idea-comparisons.js",
  "direction-literature-data.js",
]) {
  const source = fs.readFileSync(path.join(root, filename), "utf8");
  vm.runInContext(source, context, { filename });
}

const payload = {
  directions: context.window.RESEARCH_DIRECTIONS || [],
  ideas: context.window.PAPER_IDEAS || [],
  tracks: context.window.PAPER_TRACKS || [],
  explanations: context.window.IDEA_EXPLANATIONS || {},
  comparisons: context.window.IDEA_COMPARISONS || {},
  literature: context.window.DIRECTION_LITERATURE || {},
  audit: context.window.IDEA_AUDIT || {},
};
process.stdout.write(JSON.stringify(payload));
