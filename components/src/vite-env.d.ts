/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_INCLUDE_MOCK: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare const __WIDGET_EXTERNAL_LINK_URL__: string;
