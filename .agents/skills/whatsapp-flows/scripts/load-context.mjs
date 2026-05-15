#!/usr/bin/env node
/**
 * load-context.mjs
 * Reads or initialises .whatsapp-flows-config in the CWD.
 * Prints the config as JSON so Claude can consume it.
 *
 * Usage: node load-context.mjs [--set-language pt-BR|en] [--set-register static|endpoint]
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const CONFIG_FILE = resolve(process.cwd(), '.whatsapp-flows-config');

const DEFAULTS = {
  language: null,      // null = not yet set; will prompt
  register: null,      // null = not yet set; will prompt
};

function load() {
  if (!existsSync(CONFIG_FILE)) return { ...DEFAULTS };
  try {
    return JSON.parse(readFileSync(CONFIG_FILE, 'utf8'));
  } catch {
    return { ...DEFAULTS };
  }
}

function save(config) {
  writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2) + '\n', 'utf8');
}

const args = process.argv.slice(2);
const config = load();

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--set-language' && args[i + 1]) {
    config.language = args[++i];
  }
  if (args[i] === '--set-register' && args[i + 1]) {
    config.register = args[++i];
  }
}

save(config);

console.log(JSON.stringify({
  language: config.language,
  register: config.register,
  languageSet: config.language !== null,
  registerSet: config.register !== null,
  configFile: CONFIG_FILE,
}, null, 2));
