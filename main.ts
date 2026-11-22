import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('./entry.png', import.meta.url));
const outputDir = resolve(process.env.MAKEFUN_OUTPUT_DIR || '/output');
const destination = join(outputDir, 'entry.png');

mkdirSync(dirname(destination), { recursive: true });
// Preserve the PNG bytes exactly, including when invoked from another directory.
// A destination equal to the source is already complete.
if (resolve(source) !== destination) {
  copyFileSync(source, destination);
}
