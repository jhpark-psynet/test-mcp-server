/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_INCLUDE_MOCK: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
