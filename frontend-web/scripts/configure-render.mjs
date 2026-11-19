import { writeFile } from 'node:fs/promises';

const apiUrl = process.env.API_URL;
if (!apiUrl || !/^https:\/\//.test(apiUrl)) {
  throw new Error('API_URL must contain the public HTTPS URL of the MenuOpt API.');
}

const environmentFile = new URL('../src/environments/environment.ts', import.meta.url);
const source = `export const environment = {\n  production: true,\n  apiUrl: ${JSON.stringify(apiUrl)}\n};\n`;
await writeFile(environmentFile, source, 'utf8');
