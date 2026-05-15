/**
 * WhatsApp Flow JSON Validator runner
 * Shims Facebook's __d() module system to run the extracted validator in Node.js
 */
const path = require('path');
const fs = require('fs');
const jsep = require(path.join(__dirname, 'node_modules/jsep'));
const Ajv = require(path.join(__dirname, 'node_modules/ajv'));

// ── Module registry ──────────────────────────────────────────────────────────
const modules = {};
const factories = {};

function __d(name, deps, factory, _priority) {
  factories[name] = { deps, factory };
}

// ── npm / utility shims ──────────────────────────────────────────────────────
// Converts internal integer version (703) → string "7.3"
function intVersionToString(n) {
  const major = Math.floor(n / 100);
  const minor = n % 100;
  return `${major}.${minor}`;
}

// All versions defined by the validator chain modules present in the file
const ALL_VERSIONS = [300, 500, 501, 502, 600, 601, 602, 603, 700, 701, 702, 703];

const NPM_SHIMS = {
  // ── Core npm packages ────────────────────────────────────────────────────
  ajv: Ajv,
  Mjv: Ajv,

  // ── Facebook utility shims ───────────────────────────────────────────────
  invariant: (cond, msg) => { if (!cond) throw new Error(typeof msg === 'string' ? msg : `invariant failed: ${msg}`); },
  err: (msg) => new Error(msg),
  getErrorSafe: (e) => e instanceof Error ? e : new Error(String(e)),
  isPlainObject: (v) => v !== null && typeof v === 'object' && Object.getPrototypeOf(v) === Object.prototype,
  unsafeCast: (v) => v,
  justknobx: { getValue: () => false, isKnobEnabled: () => false, _: () => false },
  react: { createElement: () => null, Component: class {} },
  RelayHooks: {},

  '$InternalEnum': Object.assign(
    (obj) => {
      const values = Object.values(obj);
      const result = Object.assign(Object.create(null), obj, {
        members: () => values,
        cast:    (v) => values.includes(v) ? v : null,
        isValid: (v) => values.includes(v),
      });
      return Object.freeze(result);
    },
    {
      Mirrored: (arr) => {
        const obj = arr.reduce((o, k) => { o[k] = k; return o; }, {});
        const values = arr.slice();
        return Object.freeze(Object.assign(Object.create(null), obj, {
          members: () => values,
          cast:    (v) => values.includes(v) ? v : null,
          isValid: (v) => values.includes(v),
        }));
      }
    }
  ),

  // ── WAFlowJSONBaseValidator is defined in the validator source ──────────
  // The circular dep cycle is broken by the early-registration in require_module
  // (modules[name] = exports before factory runs), so no pre-shim needed here.

  // ── Type utilities ───────────────────────────────────────────────────────
  WATypeUtils: {
    isString: (v) => typeof v === 'string',
    isBoolean: (v) => typeof v === 'boolean',
    isNumber: (v) => typeof v === 'number',
  },
  'WAFlowsTypeGuards': {
    isString: (v) => typeof v === 'string',
  },
  isObject: (v) => v !== null && typeof v === 'object' && !Array.isArray(v),
  filterNulls: (arr) => (Array.isArray(arr) ? arr : []).filter(v => v != null),
  isValidHttpURL: (url) => {
    try { const u = new URL(url); return u.protocol === 'http:' || u.protocol === 'https:'; }
    catch { return false; }
  },
  tryParseJSONMixed: (s) => { try { return JSON.parse(s); } catch { return null; } },

  // ── Version utilities ────────────────────────────────────────────────────
  WAFlowsVersionUtils: {
    // intToString: 703 → "7.3"
    intToString: (n) => intVersionToString(n),
    // convertVersion: "7.3" → 703
    convertVersion: (v) => {
      if (typeof v === 'number') return v;
      const parts = String(v).split('.');
      if (parts.length === 2) return parseInt(parts[0]) * 100 + parseInt(parts[1]);
      return parseInt(v);
    },
  },

  // WhatsAppFlowsTemplateVersion: enum-like object for version int values
  WhatsAppFlowsTemplateVersion: {
    members: () => ALL_VERSIONS,
    cast: (v) => (ALL_VERSIONS.includes(v) ? v : null),
  },

  // ── Dynamic data / expression utilities ─────────────────────────────────
  WAFlowsDynamicDataUtils: {
    // Pattern for backtick string interpolation: `'...' ${...}`
    DYNAMIC_DATA_STRING_INTERPOLATION_PATTERN: /^`[^`]*\$\{[^}]+\}[^`]*`$/,
    // Is value a ${...} binding?
    isBindingValue: (v) => typeof v === 'string' && v.startsWith('${') && v.endsWith('}'),
    // Is value a local binding (${data.x} or ${form.x})?
    isLocalBindingValue: (v) => typeof v === 'string' &&
      (v.startsWith('${data.') || v.startsWith('${form.')) && v.endsWith('}'),
    // Is value a backtick expression?
    isNestedExpressionValue: (v) => typeof v === 'string' && v.startsWith('`') && v.endsWith('`'),
    // Get key array from ${data.x.y} → ['x', 'y']
    getBindingKeyArray: (v) => {
      if (typeof v !== 'string') return [];
      const m = v.match(/^\$\{(?:(?:screen\.[^.]+\.|)data\.|form\.)(.+)\}$/);
      return m ? m[1].split('.') : [];
    },
  },

  // jsep expression parser
  jsep,

  // AST parser: cleans backtick expression for jsep
  WAFlowsASTParser: {
    cleanExpressionForJSEP: (expr) => {
      if (typeof expr !== 'string') return expr;
      // Remove surrounding backticks
      let e = expr.startsWith('`') && expr.endsWith('`') ? expr.slice(1, -1) : expr;
      // Replace ${...} with placeholder identifiers for jsep
      e = e.replace(/\$\{([^}]+)\}/g, (_, inner) => inner.replace(/[.\-]/g, '_'));
      return e.trim();
    },
  },

  // Conditional rendering operator constants
  WAFlowsConditionalRenderingTypes: {
    AND: '&&',
    OR: '||',
    NOT: '!',
    EQUALS: '==',
    NOT_EQUALS: '!=',
    GREATER_THAN: '>',
    GREATER_THAN_OR_EQUALS: '>=',
    LESS_THAN: '<',
    LESS_THAN_OR_EQUALS: '<=',
    OPENING_PARENTHESIS: '(',
    CLOSING_PARENTHESIS: ')',
    OPENING_CURLY_BRACES: '{',
    CLOSING_CURLY_BRACES: '}',
    DYNAMIC_VARIABLE_START: '${',
    EMPTY_STRING: '',
  },

  // Schema validation utilities
  WAFlowsSchemaValidationUtils: {
    isTypeMatchingComponentSchema: (schema, type) => {
      if (!schema || !type) return false;
      const schemaType = schema.type || (schema.properties && schema.properties.type);
      return schemaType === type;
    },
  },

  // Flow component/layout name maps (used for schema generation and validation)
  // Keys match what the validator code accesses (e.g. WA_FLOWS_COMPONENT_NAMES.FOOTER)
  WAFlowsTypes: {
    WA_FLOWS_COMPONENT_NAMES: {
      TEXT_INPUT:        'TextInput',
      TEXT_AREA:         'TextArea',
      TEXT_BODY:         'TextBody',
      TEXT_CAPTION:      'TextCaption',
      TEXT_HEADING:      'TextHeading',
      TEXT_SUBHEADING:   'TextSubheading',
      FORM:              'Form',
      FOOTER:            'Footer',
      IMAGE:             'Image',
      OPT_IN:            'OptIn',
      CHECKBOX_GROUP:    'CheckboxGroup',
      RADIOBUTTONS_GROUP:'RadioButtonsGroup',
      DROPDOWN:          'Dropdown',
      DATE_PICKER:       'DatePicker',
      CALENDAR_PICKER:   'CalendarPicker',
      EMBEDDED_LINK:     'EmbeddedLink',
      PHOTO_PICKER:      'PhotoPicker',
      DOCUMENT_PICKER:   'DocumentPicker',
      NAVIGATION_LIST:   'NavigationList',
      CHIPS_SELECTOR:    'ChipsSelector',
      IMAGE_CAROUSEL:    'ImageCarousel',
      IF:                'If',
      SWITCH:            'Switch',
      RICH_TEXT:         'RichText',
    },
    WA_FLOWS_LAYOUT_NAMES: {
      SINGLE_COLUMN:  'SingleColumnLayout',
      CART:           'CartLayout',
      CATEGORY_LIST:  'CategoryListLayout',
      ITEM_DETAIL:    'ItemDetailLayout',
      ITEM_LIST:      'ItemListLayout',
    },
  },

  // Date utilities for CalendarPicker validation
  LocalDate: {
    fromISOString: (s) => {
      const m = String(s).match(/^(\d{4})-(\d{2})-(\d{2})$/);
      if (!m) return null;
      const yr = +m[1], mo = +m[2], dy = +m[3];
      return {
        year: yr, month: mo, day: dy,
        toString: () => s,
        // toInstant(timezone) → Unix seconds (used for min-date/max-date comparisons)
        toInstant: (_tz) => Date.UTC(yr, mo - 1, dy) / 1000,
      };
    },
  },
  Timezone: {
    UTC: 'UTC',
  },

  // React components (not needed for validation logic — stub as empty)
  'WAFlowsImageCarousel.react': {},
  'WAMFlowsFlowProvider.react': {},

  // DocumentPicker MIME types
  WAFlowsDocumentPickerAllowedMIMEType: {
    values: () => ['application/pdf', 'image/jpeg', 'image/png', 'text/plain'],
  },

  // WhatsAppFlowsTemplateVersionState: maps V703 → "V703_PUBLISHED" etc.
  // The file defines this with i.default = obj, but callers access ["V703"] directly,
  // so we shim it to return the flat object.
  'WhatsAppFlowsTemplateVersionState': Object.freeze({
    V100: 'V100_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V101: 'V101_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V200: 'V200_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V201: 'V201_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V300: 'V300_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V301: 'V301_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V400: 'V400_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V401: 'V401_ARCHIVED',
    V500: 'V500_PUBLISHED_WITH_DISABLED_FUNCTIONALITY',
    V501: 'V501_PUBLISHED',
    V502: 'V502_PUBLISHED',
    V600: 'V600_PUBLISHED',
    V601: 'V601_PUBLISHED',
    V602: 'V602_PUBLISHED',
    V603: 'V603_PUBLISHED',
    V700: 'V700_PUBLISHED',
    V701: 'V701_PUBLISHED',
    V702: 'V702_PUBLISHED',
    V703: 'V703_PUBLISHED',
  }),
};

function require_module(name) {
  if (modules[name] !== undefined) return modules[name];

  if (NPM_SHIMS[name] !== undefined) {
    modules[name] = NPM_SHIMS[name];
    return modules[name];
  }

  if (!factories[name]) throw new Error(`Unknown module: ${name}`);

  const { deps: depNames, factory } = factories[name];
  const exports = {};
  const module = { exports };

  // Register early to break circular dependency cycles (same as Node's CommonJS)
  modules[name] = exports;

  // Facebook Metro bundler __d convention:
  // factory(globalObj, require, importDefault, importAll, module, exports, exports)
  // - arg[1] n = require (full module object)
  // - arg[2] r = importDefault (returns module.default if set, else module itself)
  // - arg[3] o = require (same as arg[1] — full module object for named exports)
  // - args[4] a = module object
  // - args[5] i = exports object
  // - args[6] l = exports object (same as i)
  // deps array in __d is for static analysis only; accessed lazily via require() calls
  factory({}, require_module, import_default, require_module, module, exports, exports);

  // Some factories replace module.exports entirely — use that if so
  if (module.exports !== exports) {
    modules[name] = module.exports;
  } else {
    modules[name] = exports;
  }
  return modules[name];
}

// importDefault: returns module.default if the export has one, otherwise the module itself.
// This is Metro's second factory arg (r in most factories), used for default-import style.
function import_default(name) {
  const m = require_module(name);
  if (m && typeof m === 'object' && 'default' in m) return m.default;
  return m;
}

// ── Browser globals shim ─────────────────────────────────────────────────────
if (typeof window === 'undefined') global.window = global;

// ── babelHelpers shim ────────────────────────────────────────────────────────
global.babelHelpers = {
  extends: Object.assign,
  objectSpread2: (...args) => Object.assign({}, ...args),
  defineProperty: (obj, key, desc) => { Object.defineProperty(obj, key, desc); return obj; },
  classCallCheck: () => {},
  createClass: (Ctor, protoProps) => {
    if (protoProps) protoProps.forEach(d => { Object.defineProperty(Ctor.prototype, d.key, d); });
    return Ctor;
  },
  inherits: (Child, Parent) => {
    Child.prototype = Object.create(Parent.prototype, { constructor: { value: Child } });
    Object.setPrototypeOf(Child, Parent);
  },
  // Babel class-style inheritance used in validator
  inheritsLoose: (Child, Parent) => {
    Child.prototype = Object.create(Parent.prototype);
    Child.prototype.constructor = Child;
    Child.__proto__ = Parent;
  },
  possibleConstructorReturn: (self, call) => call && typeof call === 'object' ? call : self,
  getPrototypeOf: Object.getPrototypeOf,
  assertThisInitialized: (self) => self,
  wrapNativeSuper: (Class) => Class,
  taggedTemplateLiteral: (strings) => strings,
  slicedToArray: (arr, n) => arr,
  toConsumableArray: (arr) => Array.from(arr),
  arrayLikeToArray: (arr, len) => {
    if (len == null || len > arr.length) len = arr.length;
    const o = new Array(len);
    for (let i = 0; i < len; i++) o[i] = arr[i];
    return o;
  },
  typeof: (obj) => typeof obj,
  objectWithoutPropertiesLoose: (source, excluded) => {
    if (source == null) return {};
    const target = {};
    for (const key of Object.keys(source)) {
      if (!excluded.includes(key)) target[key] = source[key];
    }
    return target;
  },
  objectWithoutProperties: (source, excluded) => {
    if (source == null) return {};
    const target = {};
    for (const key of Object.keys(source)) {
      if (!excluded.includes(key)) target[key] = source[key];
    }
    return target;
  },
  createForOfIteratorHelper: (arr) => {
    if (!Array.isArray(arr)) arr = Array.from(arr);
    let i = 0;
    return {
      s: () => {},
      n: () => i < arr.length ? { done: false, value: arr[i++] } : { done: true },
      e: (e) => { throw e; },
      f: () => {},
    };
  },
};

// ── Load validator source ────────────────────────────────────────────────────
const VALIDATOR_PATH = path.join(__dirname, 'WAFlowJSONValidator.js');

if (!fs.existsSync(VALIDATOR_PATH)) {
  console.error('⚠️  WAFlowJSONValidator.js not found at: ' + VALIDATOR_PATH);
  console.error('');
  console.error('To obtain the binary:');
  console.error('  1. Open https://business.facebook.com/wa/manage/flows/ in Chrome (logged in)');
  console.error('  2. DevTools → Sources → Search (Ctrl+Shift+F) → search "WAFlowJSONValidator"');
  console.error('  3. Open the bundle file that contains it');
  console.error('  4. Copy the full __d("WAFlowJSONValidator", ...) block');
  console.error('  5. Save as scripts/WAFlowJSONValidator.js');
  console.error('');
  console.error('See scripts/README.md for full instructions.');
  process.exit(2);
}

const src = fs.readFileSync(VALIDATOR_PATH, 'utf8');
eval(src);

// ── Export validateFlowJSON ──────────────────────────────────────────────────
const validator = require_module('WAFlowJSONValidation');

function validate(flowJson, version) {
  // validateFlowJSON expects a JSON string (uses it for line/column position tracking)
  const flowStr = typeof flowJson === 'string' ? flowJson : JSON.stringify(flowJson);
  const parsed  = typeof flowJson === 'string' ? JSON.parse(flowJson) : flowJson;
  version = version || parsed.version || '7.3';
  const result = validator.validateFlowJSON(flowStr, version);
  return result;
}

// ── CLI usage ────────────────────────────────────────────────────────────────
if (require.main === module) {
  const inputFile = process.argv[2];
  const version   = process.argv[3];

  if (!inputFile) {
    console.error('Usage: node run_validator.js <flow.json> [version]');
    process.exit(1);
  }

  const flow = JSON.parse(fs.readFileSync(inputFile, 'utf8'));
  try {
    const result = validate(flow, version);
    console.log(JSON.stringify(result, null, 2));
  } catch (e) {
    console.error('Validator error:', e.message);
    console.error(e.stack);
    process.exit(1);
  }
}

module.exports = { validate };
