import { writeFile } from 'node:fs/promises';

const apiUrl = process.env.API_URL;
if (!apiUrl || !/^https:\/\//.test(apiUrl)) {
  throw new Error('API_URL must contain the public HTTPS URL of the MenuOpt API.');
}

const environmentFile = new URL('../src/environments/environment.ts', import.meta.url);
let firebase = {};
if (process.env.FIREBASE_WEB_CONFIG_JSON) {
  try {
    firebase = JSON.parse(process.env.FIREBASE_WEB_CONFIG_JSON);
  } catch {
    throw new Error('FIREBASE_WEB_CONFIG_JSON must be valid JSON from the Firebase Web app config.');
  }
}
const vapidKey = process.env.FIREBASE_WEB_VAPID_KEY || '';
const config = {
  apiKey: firebase.apiKey || '',
  authDomain: firebase.authDomain || '',
  projectId: firebase.projectId || '',
  messagingSenderId: firebase.messagingSenderId || '',
  appId: firebase.appId || '',
  vapidKey
};
const source = `export const environment = {\n  production: true,\n  apiUrl: ${JSON.stringify(apiUrl)},\n  firebase: ${JSON.stringify(config)}\n};\n`;
await writeFile(environmentFile, source, 'utf8');
const workerConfig = `self.MENUOPT_FIREBASE_CONFIG = ${JSON.stringify(config)};\n`;
await writeFile(new URL('../public/firebase-messaging-config.js', import.meta.url), workerConfig, 'utf8');
